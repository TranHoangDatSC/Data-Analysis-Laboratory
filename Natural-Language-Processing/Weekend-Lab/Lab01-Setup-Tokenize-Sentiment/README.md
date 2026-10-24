# Lab 01 – Cài đặt môi trường, tách từ, phân loại cảm xúc

## Đề bài
1. Cài đặt môi trường (Colab hoặc local với `requirements.txt`: `nltk`, `spacy`, `scikit-learn`, `transformers`).
2. Tách từ một câu tiếng Anh bằng NLTK và loại stopword.
3. Phân loại cảm xúc vài câu bằng mô hình có sẵn của Hugging Face.

## Cách làm & kết quả
Bài gốc chỉ có **báo cáo Word** ([docs/lab01_report.docx](docs/lab01_report.docx)). Notebook [notebooks/lab01_cai_dat_tach_tu_cam_xuc.ipynb](notebooks/lab01_cai_dat_tach_tu_cam_xuc.ipynb) dựng lại các bước đó từ ảnh chụp code trong báo cáo (chưa chạy trên máy tác giả; kết quả kỳ vọng ghi ngay trong notebook), kèm [requirements.txt](requirements.txt).
- `word_tokenize("I love studying Natural Language Processing")` → 6 token; loại stopword sau khi `lower()` vì danh sách stopword của NLTK viết thường.
- `pipeline("sentiment-analysis")` tải mô hình mặc định (DistilBERT fine-tune trên SST-2), trả về POSITIVE/NEGATIVE kèm điểm tin cậy; câu tích cực rõ ràng đạt ≈ 0,9999.

## Kiến thức cần nhớ
- `punkt_tab` là mô hình tách câu/tách từ của NLTK; phải `nltk.download` trước khi dùng.
- So sánh với stopword phải đưa token về chữ thường (Python phân biệt hoa/thường).
- `pipeline(...)` không chỉ định mô hình thì Hugging Face tự chọn mô hình mặc định, chỉ có 2 nhãn (không có trung tính); khi làm thật nên ghi rõ tên mô hình để tái lập; notebook ghi rõ `distilbert-base-uncased-finetuned-sst-2-english`.
- Lỗi nhỏ trong báo cáo Word (không ảnh hưởng kết quả): gõ nhầm `work_tokenize` (đúng là `word_tokenize`), câu mẫu "I love you so muchP" và "go to shool" có lỗi chính tả. Notebook đã sửa các câu mẫu.
- Câu trung tính "The book is on the table" bị gán POSITIVE (~0,988) vì mô hình SST-2 chỉ có 2 nhãn; `top_k=None` cho thấy điểm của cả hai nhãn.