"""Hàm dùng chung cho các notebook ABSA (SemEval-2016 Task 5, Restaurant, subtask 1).

Giao thức đánh giá (mọi mô hình trong repo đều dùng đúng các hàm này):
  * Tập test chỉ dùng để báo cáo, KHÔNG dùng để chọn epoch / siêu tham số.
  * Validation được tách từ train, tách THEO REVIEW (rid) để các câu cùng một bài đánh giá
    không nằm ở cả train lẫn val (tránh rò rỉ), có stratify theo nhãn polarity.
  * Mỗi cấu hình chạy nhiều seed; báo cáo trung bình ± độ lệch chuẩn.
"""
import os
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_recall_fscore_support
from sklearn.model_selection import StratifiedGroupKFold

LABELS = ["negative", "neutral", "positive"]  # thứ tự cố định cho mọi báo cáo


def find_data_dir():
    for cand in ["/kaggle/input/datasets/fouadaurag20/semeval-2016-absa-task5", "../data", "data"]:
        if os.path.exists(os.path.join(cand, "restaurants_train_sb1.xml")):
            return cand
    raise FileNotFoundError("Không thấy restaurants_train_sb1.xml; đặt file XML vào thư mục data/")


def parse_xml(path):
    """Mỗi dòng = một cặp (câu, category) với polarity. Giữ thêm rid, sid, target.

    Lưu ý: câu không có Opinion bị bỏ (giống notebook 03 của nhóm) nên số dòng khớp 2507 / 859.
    """
    root = ET.parse(path).getroot()
    rows = []
    for review in root.findall("Review"):
        rid = review.get("rid")
        sentences = review.find("sentences")
        if sentences is None:
            continue
        for sent in sentences.findall("sentence"):
            text_el = sent.find("text")
            ops = sent.find("Opinions")
            if text_el is None or ops is None:
                continue
            text = (text_el.text or "").strip()
            for op in ops.findall("Opinion"):
                rows.append(dict(
                    rid=rid, sid=sent.get("id"), sentence=text,
                    category=op.get("category"), polarity=op.get("polarity"),
                    target=op.get("target"),
                ))
    return pd.DataFrame(rows)


def load_res16(data_dir=None):
    data_dir = data_dir or find_data_dir()
    train = parse_xml(os.path.join(data_dir, "restaurants_train_sb1.xml"))
    test = parse_xml(os.path.join(data_dir, "restaurants_test_sb1.xml"))
    return train, test


def aspect_text(cat):
    """FOOD#QUALITY -> 'food quality' (giống notebook 03)."""
    return cat.replace("#", " ").replace("_", " ").lower()


def split_train_val(train_df, seed, val_frac=0.15):
    """Tách train/val theo review, stratify theo polarity. Trả về (train_idx, val_idx).

    Dùng StratifiedGroupKFold với k ≈ 1/val_frac, lấy fold đầu; seed quyết định cách xáo trộn.
    """
    k = max(2, round(1 / val_frac))
    sgkf = StratifiedGroupKFold(n_splits=k, shuffle=True, random_state=seed)
    y = train_df["polarity"].values
    groups = train_df["rid"].values
    tr, va = next(sgkf.split(np.zeros(len(train_df)), y, groups))
    assert set(groups[tr]).isdisjoint(set(groups[va])), "rò rỉ review giữa train và val"
    return tr, va


def metrics(y_true, y_pred):
    """Accuracy, Macro F1 và P/R/F1 từng lớp (thứ tự LABELS)."""
    p, r, f, s = precision_recall_fscore_support(y_true, y_pred, labels=LABELS, zero_division=0)
    out = dict(acc=accuracy_score(y_true, y_pred),
               macro_f1=f1_score(y_true, y_pred, labels=LABELS, average="macro", zero_division=0))
    for i, lab in enumerate(LABELS):
        out[f"p_{lab}"], out[f"r_{lab}"], out[f"f1_{lab}"] = p[i], r[i], f[i]
    return out


def summarize(runs, cols=("acc", "macro_f1", "f1_negative", "f1_neutral", "f1_positive")):
    """runs: list[dict] -> chuỗi 'mean ± std' cho từng chỉ số."""
    df = pd.DataFrame(runs)
    return {c: f"{df[c].mean()*100:.2f} ± {df[c].std(ddof=1)*100:.2f}" for c in cols}


def xml_overview(path):
    """Thống kê thô của một file XML SemEval: số review, câu, câu có/không có nhãn, target ngầm định.

    Dùng để biết parse_xml đã bỏ bao nhiêu câu (câu không có Opinion không có nhãn nên không dùng được).
    """
    root = ET.parse(path).getroot()
    n_rev = n_sent = n_sent_labeled = n_op = n_null = 0
    for review in root.findall("Review"):
        n_rev += 1
        sentences = review.find("sentences")
        if sentences is None:
            continue
        for sent in sentences.findall("sentence"):
            n_sent += 1
            ops = sent.find("Opinions")
            if ops is None:
                continue
            n_sent_labeled += 1
            for op in ops.findall("Opinion"):
                n_op += 1
                n_null += op.get("target") == "NULL"
    return dict(reviews=n_rev, sentences=n_sent, sentences_with_opinion=n_sent_labeled,
                sentences_without_opinion=n_sent - n_sent_labeled, opinions=n_op,
                implicit_target=n_null, implicit_target_pct=100 * n_null / max(n_op, 1))


def save_plotly(fig, name, fig_dir="../figures"):
    """Lưu biểu đồ Plotly thành ảnh tĩnh (GitHub không hiển thị Plotly tương tác).

    Cần `pip install kaleido` và một trình duyệt Chrome/Chromium. Nếu không có thì chỉ bỏ qua,
    biểu đồ tương tác vẫn hiện bình thường trong notebook.
    """
    try:
        os.makedirs(fig_dir, exist_ok=True)
        fig.write_image(os.path.join(fig_dir, f"{name}.png"), scale=2)
        print(f"[đã lưu ảnh tĩnh] {fig_dir}/{name}.png")
    except Exception as e:  # noqa: BLE001
        print(f"[bỏ qua ảnh tĩnh cho {name}] {type(e).__name__}: chạy `plotly_get_chrome` hoặc cài Chrome nếu muốn xuất ảnh")