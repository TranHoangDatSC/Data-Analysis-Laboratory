"""Mô hình và vòng huấn luyện PyTorch cho ABSA aspect-category (Res16).

Khác bản Keras trong notebook 03 ở những điểm có chủ đích (xem README):
  * Có MASK cho padding ở mọi tầng sau backbone: RNN dùng pack_padded_sequence, attention có key-padding mask,
    mean pooling có trọng số mask, Conv1D thấy 0 ở vị trí padding.
  * Padding động theo batch (không đệm cứng 256 token).
  * Chọn epoch bằng Macro F1 trên VALIDATION (tách từ train); test chỉ đo một lần ở epoch tốt nhất.
  * BatchNorm thay bằng LayerNorm (BatchNorm thống kê trên cả vị trí padding, không mask được gọn).
  * Cho phép bật/tắt từng thành phần (GRU / BiLSTM / Attention / CNN) để làm ablation thật.
"""
import copy
import math
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from absa_common import LABELS, aspect_text, metrics

LABEL2ID = {l: i for i, l in enumerate(LABELS)}


def set_seed(seed):
    random.seed(seed); np.random.seed(seed)
    torch.manual_seed(seed); torch.cuda.manual_seed_all(seed)


def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


# ───────────────────────────── mã hoá & batch ─────────────────────────────
def encode_pairs(tok, aspects, sentences, max_len=128):
    """[CLS] aspect [SEP] câu [SEP]; giữ câu gốc (không lemmatize / bỏ dấu câu)."""
    enc = tok([aspect_text(a) for a in aspects], list(sentences),
              truncation=True, max_length=max_len, padding=False)
    keys = [k for k in ("input_ids", "attention_mask", "token_type_ids") if k in enc]
    return [{k: enc[k][i] for k in keys} for i in range(len(sentences))]


def collate_ids(items, pad_id, pad_to=None):
    """Đệm theo câu dài nhất trong batch; nếu pad_to được cho thì đệm cố định đến pad_to (kiểu notebook 03)."""
    B, L = len(items), (pad_to or max(len(x["input_ids"]) for x in items))
    out = {}
    for k in items[0]:
        t = torch.full((B, L), pad_id if k == "input_ids" else 0, dtype=torch.long)
        for i, x in enumerate(items):
            t[i, : len(x[k])] = torch.tensor(x[k])
        out[k] = t
    return out


@torch.no_grad()
def extract_features(backbone, items, pad_id, device, bs=32, pad_to=None):
    """Backbone ĐÓNG BĂNG: tính last_hidden_state một lần.

    Mặc định (pad_to=None): lưu theo độ dài thật, không đệm → đầu phân loại thấy đúng các token thật.
    pad_to=N: đệm cố định đến N token và GIỮ NGUYÊN cả vị trí padding (vector BERT tại [PAD]) như notebook 03;
    khi đó collate_feats sẽ coi mọi vị trí là hợp lệ, tức là *không mask* — dùng để đo tác động của việc thiếu mask.
    """
    backbone.eval().to(device)
    order = np.argsort([len(x["input_ids"]) for x in items])
    res = [None] * len(items)
    for s in range(0, len(items), bs):
        idx = order[s : s + bs]
        batch = {k: v.to(device) for k, v in collate_ids([items[i] for i in idx], pad_id, pad_to).items()}
        h = backbone(**batch).last_hidden_state.float().cpu()
        for j, i in enumerate(idx):
            res[i] = h[j].clone() if pad_to else h[j, : len(items[i]["input_ids"])].clone()
    return res


def collate_feats(feats):
    B, L, H = len(feats), max(f.size(0) for f in feats), feats[0].size(1)
    x = torch.zeros(B, L, H)
    mask = torch.zeros(B, L, dtype=torch.bool)
    for i, f in enumerate(feats):
        x[i, : f.size(0)] = f
        mask[i, : f.size(0)] = True
    return x, mask


# ───────────────────────────── mô hình lai ─────────────────────────────
class MHA(nn.Module):
    """Multi-head self-attention kiểu Keras (num_heads, key_dim) có key-padding mask."""

    def __init__(self, d, heads=4, key_dim=64):
        super().__init__()
        self.h, self.k = heads, key_dim
        self.q, self.kk, self.v = (nn.Linear(d, heads * key_dim) for _ in range(3))
        self.o = nn.Linear(heads * key_dim, d)

    def forward(self, x, mask):
        B, L, _ = x.shape
        sp = lambda t: t.view(B, L, self.h, self.k).transpose(1, 2)          # B,h,L,k
        q, k, v = sp(self.q(x)), sp(self.kk(x)), sp(self.v(x))
        s = q @ k.transpose(-1, -2) / math.sqrt(self.k)                       # B,h,L,L
        s = s.masked_fill(~mask[:, None, None, :], float("-inf"))
        a = torch.softmax(s, dim=-1)
        out = (a @ v).transpose(1, 2).reshape(B, L, self.h * self.k)
        return self.o(out)


def run_rnn(rnn, x, lengths):
    """RNN trên chuỗi có độ dài thật: padding không đi vào RNN (chiều ngược bắt đầu từ token thật cuối)."""
    L = x.size(1)
    packed = pack_padded_sequence(x, lengths.cpu(), batch_first=True, enforce_sorted=False)
    out, _ = rnn(packed)
    out, _ = pad_packed_sequence(out, batch_first=True, total_length=L)
    return out


class HybridHead(nn.Module):
    """GRU → BiLSTM(F,B tách riêng) → MHA trên {V,H,F,B} (+residual+LN) → Dense → Conv1D → masked mean → MLP."""

    def __init__(self, in_dim=768, hid=128, use_gru=True, use_bilstm=True, use_attn=True, use_cnn=True,
                 heads=4, key_dim=64, drop1=0.3, drop2=0.2, n_cls=3):
        super().__init__()
        self.use_gru, self.use_bilstm, self.use_attn, self.use_cnn = use_gru, use_bilstm, use_attn, use_cnn
        dims = [in_dim]
        rnn_in = in_dim
        if use_gru:
            self.gru = nn.GRU(in_dim, hid, batch_first=True); dims.append(hid); rnn_in = hid
        if use_bilstm:
            self.bilstm = nn.LSTM(rnn_in, hid, batch_first=True, bidirectional=True); dims += [hid, hid]
        self.hid = hid
        if use_attn:
            self.atts = nn.ModuleList(MHA(d, heads, key_dim) for d in dims)
            self.att_ln = nn.ModuleList(nn.LayerNorm(d) for d in dims)
        self.fuse = nn.Linear(sum(dims), 256)
        self.fuse_ln = nn.LayerNorm(256)
        feat = 256
        if use_cnn:
            self.conv = nn.Conv1d(256, 128, kernel_size=3, padding=1)
            self.conv_ln = nn.LayerNorm(128)
            feat = 128
        self.cls = nn.Sequential(nn.Linear(feat, 512), nn.ReLU(), nn.Dropout(drop1),
                                 nn.Linear(512, 256), nn.ReLU(), nn.Dropout(drop2), nn.Linear(256, n_cls))

    def forward(self, x, mask):
        lengths = mask.sum(1)
        m = mask.unsqueeze(-1).float()
        groups = [x]
        h = x
        if self.use_gru:
            h = run_rnn(self.gru, x, lengths); groups.append(h)
        if self.use_bilstm:
            o = run_rnn(self.bilstm, h, lengths)
            groups += [o[..., : self.hid], o[..., self.hid :]]
        if self.use_attn:
            groups = [ln(g + att(g, mask)) for g, att, ln in zip(groups, self.atts, self.att_ln)]
        z = torch.relu(self.fuse(torch.cat(groups, -1)))
        z = self.fuse_ln(z) * m
        if self.use_cnn:
            z = torch.relu(self.conv(z.transpose(1, 2))).transpose(1, 2)
            z = self.conv_ln(z) * m
        pooled = z.sum(1) / m.sum(1).clamp(min=1)                              # masked mean pooling
        return self.cls(pooled)


# ───────────────────────────── huấn luyện ─────────────────────────────
def _class_weights(y, device):
    cnt = np.bincount(y, minlength=len(LABELS)).astype(float)
    w = cnt.sum() / (len(LABELS) * np.maximum(cnt, 1))
    return torch.tensor(w, dtype=torch.float, device=device)


def _predict(model, feats, bs, device):
    model.eval(); preds = []
    with torch.no_grad():
        for s in range(0, len(feats), bs):
            x, mask = collate_feats(feats[s : s + bs])
            preds.append(model(x.to(device), mask.to(device)).argmax(-1).cpu())
    return torch.cat(preds).numpy()


def train_head(head_kwargs, Ftr, ytr, Fva, yva, Fte, yte, seed, epochs=30, patience=8, lr=5e-4, bs=32,
               class_weight=False, device=None, track_test=False):
    """Huấn luyện đầu phân loại trên đặc trưng đóng băng. Chọn epoch theo Macro F1 trên val; đo test một lần.

    track_test=True: ghi thêm đường cong test theo epoch vào r['curve'] CHỈ ĐỂ BÁO CÁO (không dùng để chọn epoch,
    không ảnh hưởng huấn luyện) — dùng cho thí nghiệm "chọn epoch trên test lạc quan bao nhiêu". Khi dùng, nên đặt
    patience = epochs để mọi epoch đều được ghi.
    """
    device = device or get_device()
    set_seed(seed)
    in_dim = Ftr[0].size(1)
    model = HybridHead(in_dim=in_dim, **head_kwargs).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    wt = _class_weights(np.asarray(ytr), device) if class_weight else None
    rng = np.random.RandomState(seed)
    best = dict(f1=-1, acc=-1, state=None, epoch=-1); bad = 0
    ytr_t = torch.tensor(ytr)
    curve = []
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(len(Ftr))
        for s in range(0, len(perm), bs):
            idx = perm[s : s + bs]
            x, mask = collate_feats([Ftr[i] for i in idx])
            logits = model(x.to(device), mask.to(device))
            loss = F.cross_entropy(logits, ytr_t[idx].to(device), weight=wt)
            opt.zero_grad(); loss.backward(); opt.step()
        pv = _predict(model, Fva, bs, device)
        mv = metrics([LABELS[i] for i in yva], [LABELS[i] for i in pv])
        if track_test:
            mt = metrics([LABELS[i] for i in yte], [LABELS[i] for i in _predict(model, Fte, bs, device)])
            curve.append(dict(epoch=ep, val_acc=mv["acc"], val_macro_f1=mv["macro_f1"],
                              test_acc=mt["acc"], test_macro_f1=mt["macro_f1"]))
        if (mv["macro_f1"], mv["acc"]) > (best["f1"], best["acc"]):
            best = dict(f1=mv["macro_f1"], acc=mv["acc"], state=copy.deepcopy(model.state_dict()), epoch=ep); bad = 0
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best["state"])
    pt = _predict(model, Fte, bs, device)
    r = metrics([LABELS[i] for i in yte], [LABELS[i] for i in pt])
    r.update(seed=seed, best_epoch=best["epoch"], val_macro_f1=best["f1"], n_params=sum(p.numel() for p in model.parameters()))
    if track_test:
        r["curve"] = curve
    return r, pt


class BertCLS(nn.Module):
    """Baseline: backbone fine-tune toàn bộ + vector [CLS] → Dropout → Linear."""

    def __init__(self, backbone, n_cls=3, drop=0.1):
        super().__init__()
        self.backbone = backbone
        self.drop = nn.Dropout(drop)
        self.fc = nn.Linear(backbone.config.hidden_size, n_cls)

    def forward(self, batch):
        h = self.backbone(**batch).last_hidden_state[:, 0]
        return self.fc(self.drop(h))


def _predict_cls(model, items, pad_id, bs, device):
    model.eval(); out = []
    with torch.no_grad():
        for s in range(0, len(items), bs):
            b = {k: v.to(device) for k, v in collate_ids(items[s : s + bs], pad_id).items()}
            out.append(model(b).argmax(-1).cpu())
    return torch.cat(out).numpy()


def finetune_cls(backbone_factory, pad_id, Itr, ytr, Iva, yva, Ite, yte, seed, epochs=6, patience=3, lr=2e-5,
                 bs=16, class_weight=False, device=None):
    from transformers import get_linear_schedule_with_warmup
    device = device or get_device()
    set_seed(seed)
    model = BertCLS(backbone_factory()).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-2)
    steps = epochs * math.ceil(len(Itr) / bs)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    wt = _class_weights(np.asarray(ytr), device) if class_weight else None
    rng = np.random.RandomState(seed); ytr_t = torch.tensor(ytr)
    best = dict(f1=-1, acc=-1, state=None, epoch=-1); bad = 0
    for ep in range(epochs):
        model.train()
        perm = rng.permutation(len(Itr))
        for s in range(0, len(perm), bs):
            idx = perm[s : s + bs]
            b = {k: v.to(device) for k, v in collate_ids([Itr[i] for i in idx], pad_id).items()}
            loss = F.cross_entropy(model(b), ytr_t[idx].to(device), weight=wt)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sch.step()
        pv = _predict_cls(model, Iva, pad_id, 64, device)
        mv = metrics([LABELS[i] for i in yva], [LABELS[i] for i in pv])
        if (mv["macro_f1"], mv["acc"]) > (best["f1"], best["acc"]):
            best = dict(f1=mv["macro_f1"], acc=mv["acc"], epoch=ep,
                        state={k: v.detach().cpu().clone() for k, v in model.state_dict().items()}); bad = 0
        else:
            bad += 1
            if bad >= patience:
                break
    model.load_state_dict(best["state"])
    pt = _predict_cls(model, Ite, pad_id, 64, device)
    r = metrics([LABELS[i] for i in yte], [LABELS[i] for i in pt])
    r.update(seed=seed, best_epoch=best["epoch"], val_macro_f1=best["f1"])
    return r, pt


# ───────────────────────────── chế độ smoke test (không cần mạng) ─────────────────────────────
def make_smoke_backbone(texts, hidden=32):
    """Backbone BERT nhỏ khởi tạo ngẫu nhiên + tokenizer dựng từ dữ liệu — CHỈ để kiểm tra code chạy đúng,
    không cho kết quả có ý nghĩa. Dùng khi không tải được bert-base-uncased.

    Dựng tokenizer bằng thư viện `tokenizers` (không phụ thuộc cách từng phiên bản transformers đọc vocab.txt)."""
    import re
    from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, processors
    from transformers import BertConfig, BertModel, PreTrainedTokenizerFast
    words = sorted({w for t in texts for w in re.findall(r"\w+|[^\w\s]", t.lower())})
    vocab_list = ["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] + words
    vocab = {w: i for i, w in enumerate(vocab_list)}
    tk = Tokenizer(models.WordPiece(vocab, unk_token="[UNK]"))
    tk.normalizer = normalizers.BertNormalizer(lowercase=True)
    tk.pre_tokenizer = pre_tokenizers.BertPreTokenizer()
    tk.post_processor = processors.TemplateProcessing(
        single="[CLS] $A [SEP]", pair="[CLS] $A [SEP] $B:1 [SEP]:1",
        special_tokens=[("[CLS]", vocab["[CLS]"]), ("[SEP]", vocab["[SEP]"])])
    tok = PreTrainedTokenizerFast(tokenizer_object=tk, unk_token="[UNK]", pad_token="[PAD]", cls_token="[CLS]",
                                  sep_token="[SEP]", mask_token="[MASK]",
                                  model_input_names=["input_ids", "token_type_ids", "attention_mask"])
    cfg = BertConfig(vocab_size=len(vocab_list), hidden_size=hidden, num_hidden_layers=2, num_attention_heads=2,
                     intermediate_size=64, max_position_embeddings=256)
    return tok, (lambda: BertModel(cfg))