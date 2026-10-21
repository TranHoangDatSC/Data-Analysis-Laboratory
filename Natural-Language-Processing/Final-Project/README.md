# Final Project – Phân tích cảm xúc theo khía cạnh (ABSA) trên đánh giá nhà hàng

Đồ án cuối kỳ môn Xử lý ngôn ngữ tự nhiên (ĐH Sư phạm TP.HCM, 2026, GVHD ThS. Trần Quang Huy), nhóm Ba Sáu.
Repo này giữ bản gốc của nhóm (notebook 03, báo cáo PDF đã nộp) và bản **làm lại đúng quy trình** (notebook 04, 05) để hiểu và đánh giá trung thực.

## Đề bài
Cho một câu đánh giá nhà hàng và một **khía cạnh** (category dạng `ENTITY#ATTRIBUTE`, ví dụ `FOOD#QUALITY`), dự đoán cảm xúc của câu với khía cạnh đó: positive / negative / neutral. Dữ liệu: **SemEval-2016 Task 5, Restaurant (Res16)**, 2 507 cặp (câu, khía cạnh) train và 859 test.

Mô hình đề xuất dựa trên CABiLSTM-BERT (He et al., 2025), thay 2 tầng BiLSTM bằng GRU → BiLSTM:

```
[CLS] aspect [SEP] câu [SEP] → BERT-base (đóng băng)
  → GRU 128 → BiLSTM 128 (giữ riêng chiều xuôi F và ngược B)
  → Multi-head self-attention (4 head) trên {V, H_GRU, F, B} + residual + LayerNorm
  → Concat → Dense 256 → Conv1D 128 → Mean pooling → Dense 512 → 256 → softmax 3 lớp
```

## Phân công (theo báo cáo)
| Thành viên | Phụ trách |
|---|---|
| Ngô Quang Khánh (trưởng nhóm) | Tiền xử lý, **huấn luyện mô hình trên Res16**, vẽ kiến trúc, viết chương phương pháp và kết quả |
| Trần Hoàng Đạt | Tổng hợp biểu diễn từ (BoW, TF-IDF, CBOW, Skip-gram, FastText), viết mục 3.3, tham gia xây dựng mô hình, **ablation backbone** (RoBERTa, DeBERTa); **phân tích dữ liệu** (2 notebook EDA) |
| Bùi Minh Tín | Trực quan hóa dữ liệu (Twitter US Airline, IMDB, AWARE, Res16), viết mục 4.1 |
| Lý Tiểu Mẫn | Tổng hợp phương pháp hybrid, thống kê dữ liệu, viết mục 3.1 |
| Nguyễn Đặng Đại Nam | Tổng hợp Transformer, viết phần độ đo, **ablation cấu hình** (bỏ GRU/BiLSTM/CNN) |

## Cấu trúc
| File | Nội dung |
|---|---|
| [notebooks/01_eda_res16.ipynb](notebooks/01_eda_res16.ipynb) | EDA Res16 (đọc thẳng XML): không gian nhãn, phân bố cảm xúc theo khía cạnh và theo split, độ dài câu theo token, target ngầm định, kiểm chứng emoji/URL |
| [notebooks/02_eda_aware.ipynb](notebooks/02_eda_aware.ipynb) | EDA bộ AWARE (đánh giá ứng dụng mạng xã hội); bộ này **không được dùng để huấn luyện** |
| [notebooks/03_model_gru_bilstm_res16.ipynb](notebooks/03_model_gru_bilstm_res16.ipynb) | **Bản gốc của nhóm**, giữ để đối chiếu: parse XML, trích đặc trưng BERT đóng băng, mô hình đề xuất, huấn luyện 50 epoch (Kaggle, 2× Tesla T4). Không dùng 86,61% làm kết quả chính |
| [src/absa_common.py](src/absa_common.py) | Hàm dùng chung: parse XML, tách train/val theo review, tính metric (giao thức đánh giá cho notebook 04 trở đi) |
| [notebooks/04_baseline_tfidf_res16.ipynb](notebooks/04_baseline_tfidf_res16.ipynb) | Baseline BoW/TF-IDF + LR/SVM, 5 seed, chọn tham số trên validation (không dùng test), phân tích lỗi |
| [src/absa_torch.py](src/absa_torch.py) | Mô hình lai PyTorch có mask (GRU/BiLSTM/Attention/CNN bật-tắt được), fine-tune BERT+[CLS], vòng huấn luyện chọn epoch trên validation |
| [notebooks/05_deep_models_res16.ipynb](notebooks/05_deep_models_res16.ipynb) | BERT fine-tune, mô hình lai, ablation thành phần và backbone (RoBERTa, DeBERTa-v3), 5 seed, và đo hai điểm yếu của notebook 03 (mục G) |
| `results/` | Kết quả notebook 05: `deep_results_runs.json` (từng lần chạy), `deep_results_summary.csv` (bảng tổng hợp), `h1_epoch_selection.csv` (mục G1), `deep_preds.pkl` (dự đoán test, dùng để vẽ ma trận nhầm lẫn). Notebook 05 đọc các file này để không chạy lại phần đã xong |
| [docs/FinalReport-NLP-ABSA-submitted.pdf](docs/FinalReport-NLP-ABSA-submitted.pdf) | Báo cáo đã nộp (giữ nguyên) |
| [docs/FinalReport-NLP-ABSA-Remastered.docx](docs/FinalReport-NLP-ABSA-Remastered.docx) | Báo cáo viết lại sau khi nộp; **chưa cập nhật theo kết quả notebook 04–05** |

## Giao thức đánh giá (notebook 04 và 05)
- Validation tách từ **train** theo *review* (không để câu cùng review nằm ở cả train và validation), stratify theo polarity. Res16 không có sẵn tập dev.
- Siêu tham số (C, epoch) chọn bằng **Macro F1 trên validation**; tập test chỉ đo một lần.
- Chạy nhiều seed (seed đổi cách tách train/validation): 5 seed cho baseline và mô hình đóng băng, 3 seed cho BERT fine-tune (chạy chậm). Báo cáo trung bình ± độ lệch chuẩn.
- So sánh giữa hai cấu hình dùng hiệu **ghép cặp theo seed** kèm khoảng tin cậy 95% theo phân phối t. Số seed ít và có nhiều phép so sánh cùng lúc, nên chỉ mô tả xu hướng, không viết "có ý nghĩa thống kê".
- Chỉ số chính là **Macro F1** (neutral chỉ 4,0% ở train và 5,1% ở test); Accuracy chỉ để tham khảo.

## Kết quả (test 859 mẫu, %, trung bình ± độ lệch chuẩn)
| Mô hình | Accuracy | Macro F1 | F1 neutral | #seed |
|---|---:|---:|---:|---:|
| Đoán luôn positive | 71,13 | 27,71 | 0,00 | – |
| TF-IDF chỉ câu · LR | 78,18 | 55,67 ± 0,73 | 19,19 | 5 |
| TF-IDF + one-hot khía cạnh (S+A) · LR | 80,23 | 57,27 ± 0,35 | 17,82 | 5 |
| TF-IDF S+A · LR, cân bằng lớp | 78,42 | **60,51 ± 1,84** | 29,65 | 5 |
| TF-IDF câu × khía cạnh (S×A) · LR | 80,35 | 55,51 ± 1,36 | 12,86 | 5 |
| TF-IDF S×A · LR, cân bằng lớp | 78,16 | 58,89 ± 2,65 | 25,76 | 5 |
| TF-IDF S×A · LinearSVC, cân bằng lớp | 81,47 | 59,60 ± 1,93 | 22,31 | 5 |
| BoW nhị phân S×A · LR, cân bằng lớp | 78,84 | 58,67 ± 1,64 | 25,54 | 5 |
| *Notebook 03 gốc (1 lần chạy, chọn epoch trên test)* | *86,61* | *59,67* | *8,51* | *1* |
| Mô hình lai, BERT đóng băng | 83,73 | 63,61 ± 5,56 | 24,67 | 5 |
| Mô hình lai, BERT đóng băng + class weight | 82,89 | 66,60 ± 1,42 | 35,16 | 5 |
| Đầu đơn giản (mean-pool + MLP), BERT đóng băng + class weight | 81,51 | 62,25 ± 1,11 | 25,07 | 5 |
| Mô hình lai, RoBERTa đóng băng + class weight | 84,80 | 70,03 ± 2,16 | 40,70 | 5 |
| Mô hình lai, DeBERTa-v3 đóng băng + class weight | 85,70 | 69,86 ± 1,77 | 39,28 | 5 |
| BERT fine-tune + [CLS] | 87,78 | 70,01 ± 1,49 | 36,65 | 3 |
| BERT fine-tune + [CLS] + class weight | 87,50 | **72,81 ± 2,10** | 45,79 | 3 |

**Kết luận chính**
1. **Baseline cổ điển mạnh nhất đạt Macro F1 ≈ 59–61%.** Các cấu hình cân bằng lớp chênh nhau dưới ~2 điểm (cỡ độ lệch chuẩn) nên coi là ngang nhau. Chọn C trên validation khá nhiễu (validation chỉ khoảng 356 mẫu, cỡ 15 mẫu neutral).
2. **Mô hình của nhóm ở notebook 03 (Macro F1 59,7) ngang baseline TF-IDF**, không hơn, vì gần như không nhận ra lớp neutral (recall 4,5%). Accuracy 86,61% cao nhưng Macro F1 thấp.
3. **Class weight là thay đổi có tác động lớn nhất**: với TF-IDF, Macro F1 +3,2 đến +3,4 và F1 neutral +12 đến +13 điểm, đổi lại mất ~2 điểm Accuracy. Với mô hình sâu, F1 neutral tăng ~9–10 điểm nhưng mức tăng Macro F1 có khoảng tin cậy chứa 0.
4. **Mô hình lai (BERT đóng băng) hơn TF-IDF mạnh nhất 6,09 điểm Macro F1 (66,60 so với 60,51)**, nhưng **không hơn BERT fine-tune đơn giản** (70,01–72,81). Phép so sánh này đổi cả đầu phân loại lẫn chế độ backbone (đóng băng so với fine-tune).
5. **Ablation thật** (Δ Macro F1 so với mô hình lai đầy đủ, CI 95%, n = 5):

| Bỏ | Macro F1 | Δ [CI 95%] |
|---|---:|---|
| GRU | 67,10 | +0,49 [−2,99; +3,98] |
| BiLSTM | 65,75 | −0,85 [−3,25; +1,55] |
| **Attention** | 62,10 | **−4,50 [−7,66; −1,34]** |
| CNN | 66,75 | +0,14 [−3,58; +3,87] |
| Tất cả (mean-pool + MLP) | 62,25 | −4,35 [−5,34; −3,36] |

   Toàn bộ lợi thế của đầu lai so với đầu đơn giản đến từ **Attention**; GRU, BiLSTM và CNN chưa có bằng chứng đóng góp (CI chứa 0), trái với kết luận "cả ba thành phần đều đóng góp" của báo cáo cũ.
6. **Đổi backbone** (đóng băng, cùng đầu lai): RoBERTa +3,42 [+0,47; +6,38] và DeBERTa-v3 +3,26 [+0,39; +6,13] so với BERT. RoBERTa và DeBERTa không phân biệt được với nhau; cận dưới của CI sát 0 nên chỉ là xu hướng.
7. **Lớp neutral vẫn là điểm yếu chung**: F1 neutral cao nhất chỉ 45,79, bất kể mô hình.

## Hai điểm yếu của notebook 03, đo bằng số thật (notebook 05, mục G)
Đo bằng đầu lai của notebook 05, nên đây là ước lượng độ lớn, không phải tái hiện con số 86,61%.

| Điểm yếu | Kết quả đo được |
|---|---|
| **Chọn epoch trên tập test** (`validation_data=(X_test, y_test)`) | Làm số đẹp hơn khoảng **+1,09 điểm Accuracy** [−0,26; +2,44] và **+2,62 điểm Macro F1** [−0,87; +6,11] so với chọn trên validation (5 seed; chọn epoch theo test luôn cho giá trị ≥ chuẩn, nên chỉ đọc độ lớn). Có thật nhưng không giải thích hết khoảng cách giữa 86,61% và Accuracy ≈ 83% của mô hình lai ở đây |
| **Không mask padding** (đệm cứng, ~90% vị trí là padding) | **Không đo được tác hại**: bỏ mask cho Macro F1 67,54 ± 2,08 so với 66,60 ± 1,42 khi có mask, Δ = +0,94 [−2,91; +4,79], CI chứa 0. Mask vẫn đúng về phương pháp, nhưng không nên viết "thiếu mask làm giảm hiệu năng" |

Phần còn lại của khoảng cách (class weight, lr, chuẩn hóa, độ dài đệm 256 so với 128…) chưa được tách riêng.

## Các vấn đề khác của bản gốc (rà soát 10/2026)
**1. Tập test được dùng làm tập validation** (xem bảng trên): `ModelCheckpoint(monitor='val_accuracy')` giữ epoch có accuracy trên test cao nhất, nên 86,61% là con số đã được chọn trên chính tập test.

**2. Không có mask cho phần padding** (xem bảng trên): GRU, self-attention, Conv1D và mean pooling nhận cả ~90% vị trí padding mà không có mask. Đây là lỗi phương pháp, dù ảnh hưởng đo được ở thiết lập này là nhỏ.

**3. Số liệu ablation của báo cáo cũ không có code.** Bảng so sánh backbone (RoBERTa, DeBERTa) và bỏ thành phần (w/o GRU, w/o BiLSTM, w/o CNN) không có mã nguồn hay output trong repo. Bản Remastered tự ghi rằng cấu hình w/o BiLSTM "còn thiếu trong mã nguồn" nhưng bảng vẫn có số liệu. Notebook 05 chạy lại các ablation này thật, 5 seed.

**4. Kết luận ablation cũ vượt quá dữ liệu.** Mỗi cấu hình chạy một lần, không cố định seed. Chênh lệch 0,58 điểm % trên 859 mẫu chỉ là **5 câu**, nằm trong dao động ngẫu nhiên giữa các lần chạy. Bỏ CNN còn làm Macro F1 **tăng** (61,02 so với 59,67), vậy mà báo cáo kết luận "cả ba thành phần đều đóng góp tích cực, chứng minh tính hiệu quả của kiến trúc".

**5. Báo cáo không khớp code.**

| Báo cáo | Code / output |
|---|---|
| Learning rate 3×10⁻⁵ | `Adam(1e-5)` |
| Tiền xử lý: bỏ ký tự đặc biệt, tách từ, lemmatization, stemming | Chỉ lowercase, bỏ URL, `emoji.demojize` (và không nên làm thêm: BERT cần câu gốc có dấu câu) |
| Negative nhận đúng 183/204 (89,7%) | Recall negative 0,833 (≈ 170/204) |
| Câu trung bình 80–100 ký tự (bản Remastered) | 67,9 ký tự (trung vị 58) |
| Res16: 98,5% câu có ký tự đặc biệt, 22,2% có emoji, 25% target ngầm định (bản nộp) | Không có trong notebook nào; tỉ lệ emoji này không hợp với Res16 |

**6. Nội dung chép sai ngữ cảnh.** Mục 2.1 (SMOTE) chép từ một bài báo về **phát hiện trầm cảm**, không liên quan ABSA. Ví dụ minh họa tiền xử lý ("IT professional… battery management") lấy từ bộ AWARE, không phải Res16. Ví dụ tính độ đo ở mục 4.2 của bản nộp có ma trận nhầm lẫn không khớp phân bố đã nêu (hàng Negative cộng ra 18 chứ không phải 20) và tính FP theo hàng thay vì theo cột.

**7. Bản Remastered còn sót ghi chú kiểu reviewer** ("nhóm nên bổ sung một đoạn thảo luận…", "như đã chỉ ra ở Phần B", "SourceCode.ipynb"), chương kết luận vẫn nói "nghiên cứu trên hai bộ dữ liệu AWARE và Res16" dù AWARE không được huấn luyện, và đánh số mục nhảy từ 4.4.1 sang 4.5.2.

**8. So sánh SOTA không cùng điều kiện.** Các con số ATAE-LSTM, ASGCN-DG, UIKA-BERT, CABiLSTM-BERT được chép từ bài báo, mỗi bài có giao thức riêng (các mô hình họ BERT trong đó được **fine-tune**); mô hình của nhóm dùng BERT **đóng băng** và chọn epoch trên tập test. Accuracy bằng đúng CABiLSTM-BERT (86,61) là trùng hợp; Macro F1 (59,7) thấp hơn 14 điểm so với CABiLSTM-BERT gốc (73,54) nên không thể gọi là "tương đương".

## Phần dữ liệu (EDA)
Hai notebook EDA (phần của Trần Hoàng Đạt) chạy được và số liệu khớp với báo cáo ở các bảng phân bố. Đã sửa (10/2026):
- Notebook 01 trước đây đọc `restaurants_*_sb1.csv` (dạng wide từ Kaggle, **không có** trong `data/`); nay đọc thẳng XML bằng `src/absa_common.py`, số liệu giữ nguyên (2 507 / 859 cặp).
- Notebook 02: ô thống kê target ngầm định bị `KeyError: 'sentiment'` (cột đã đổi tên `polarity`) và đếm 0 trường hợp vì term thiếu là `NaN`, không phải chuỗi `N/A`. Nay: 18/3 118 (0,58%) ngầm định chặt, 199 (6,4%) nếu tính cả term chung chung ("app", "version"…).
- Đã bổ sung cho Res16: target ngầm định **25,0% train / 24,3% test**; token dài nhất cận trên ≈133, 97% câu ≤ 64 token (nên `MAX_LEN=256` thừa ~90% padding; notebook 05 dùng 128); Res16 **không có emoji hay URL** (nên "22,2% câu có emoji" trong báo cáo là sai); test lệch nhẹ so với train (negative 23,7% so với 29,9%).
- Dữ liệu: 3 366 cặp, 12 khía cạnh, mất cân bằng nặng 2 268 positive : 953 negative : 145 neutral (4,3%); câu trung bình 68 ký tự; 32% câu có hơn một khía cạnh.
- Còn lại: biểu đồ Plotly (sunburst, sankey) vẫn không hiển thị trên GitHub; các biểu đồ matplotlib tương đương đã thay cho biểu đồ tần suất category.

## Kiến thức cần nhớ
- **ABSA** dạng aspect-category: đầu vào là cặp câu + khía cạnh, `[CLS] aspect [SEP] câu [SEP]`, token_type_ids phân biệt hai đoạn.
- **Không bao giờ chọn mô hình/epoch trên tập test.** Train / validation / test phải tách riêng; nếu bộ dữ liệu chỉ có train/test thì cắt validation từ train (có `stratify`, và tách theo review để không rò rỉ).
- **Padding nên đi kèm mask** ở mọi tầng sau BERT, vì đó là cách làm đúng. Nhưng hãy đo thay vì giả định: ở thí nghiệm này, bỏ mask không gây khác biệt đo được.
- Với mất cân bằng nặng (neutral 4–5%): báo cáo Macro F1, thử class weight / focal loss, và xem ma trận nhầm lẫn từng lớp. Accuracy một mình đánh lừa: luôn đoán positive đã được 71%.
- **Ablation và so sánh mô hình** cần nhiều seed, trung bình ± độ lệch chuẩn, và hiệu ghép cặp kèm khoảng tin cậy; chênh lệch nhỏ hơn dao động giữa các seed thì không kết luận được. Khi chênh lệch tập trung ở một thành phần (ở đây là Attention), hãy kiểm tra thêm với bản "bỏ tất cả".
- Chọn siêu tham số trên validation nhỏ khá nhiễu; kết quả baseline có thể đổi cả ~1–2 điểm khi đổi lưới tham số.
- So sánh với SOTA chỉ có nghĩa khi cùng giao thức (cùng split, cùng cách chọn mô hình, cùng chỉ số, cùng chế độ backbone).
- Tiền xử lý cho Transformer nên tối thiểu: tokenizer của BERT đã xử lý chữ hoa/thường (uncased) và dấu câu; lemmatization hay bỏ dấu câu làm mất thông tin.

## Chạy
Dữ liệu không có trên GitHub, xem [data/README.md](data/README.md).
- `01`, `02`, `04`: chạy local hoặc Colab, đọc file từ `data/`. `04` chạy trong vài phút trên CPU.
- `03`: viết cho **Kaggle** (GPU); tự đọc `/kaggle/input/...` nếu có, nếu không thì đọc `data/*.xml`. Trích đặc trưng BERT tạo mảng 3 366 × 256 × 768 float32 (~2,6 GB RAM), cần GPU để chạy trong thời gian hợp lý.
- `05`: cần `src/absa_common.py` và `src/absa_torch.py`. Trên GPU T4 khoảng 30–60 phút; trên CPU mỗi lần fine-tune BERT khoảng 1,5–2 giờ (6 lần ≈ 10 giờ, nằm ở mục A). Với DeBERTa-v3 cần `pip install sentencepiece tiktoken protobuf` rồi khởi động lại kernel. Kết quả được lưu vào `results/` sau từng cấu hình; chạy lại sẽ bỏ qua phần đã xong. Sau khi sửa `src/absa_torch.py`, phải Restart kernel vì Python lưu cache module.