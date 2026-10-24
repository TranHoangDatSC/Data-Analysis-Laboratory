# Lab 02 – Tiền xử lý văn bản

## Đề bài
Xây dựng pipeline tiền xử lý: chuẩn hóa → chữ thường → làm sạch ký tự → tách từ → loại stopword → gắn nhãn từ loại → stemming/lemmatization, có giải thích từng bước.

## Cách làm
| File | Nội dung |
|---|---|
| [notebooks/lab02_text_preprocessing_vi.ipynb](notebooks/lab02_text_preprocessing_vi.ipynb) | Pipeline trên câu tiếng Việt "Sinh viên!!! Đang học NLP tại Trường Đại Học Sư Phạm TP.HCM" (bản đã sửa: tách từ bằng `underthesea`, POS tiếng Việt, ghi rõ không cần lemmatization, đã chạy) |
| [notebooks/lab02_text_preprocessing_en.ipynb](notebooks/lab02_text_preprocessing_en.ipynb) | Dựng lại từ ảnh chụp trong báo cáo (câu tiếng Anh): chữ thường, làm sạch, tách từ, stopword, POS, Porter Stemmer, WordNet Lemmatizer. Chưa chạy trên máy tác giả (cần tải dữ liệu NLTK) |
| [docs/lab02_report.docx](docs/lab02_report.docx) | Báo cáo giải thích pipeline trên câu **tiếng Anh** (Natural Language Processing…), có so sánh Porter Stemmer và WordNet Lemmatizer |

Notebook tiếng Anh tương ứng với báo cáo đã được dựng lại ở trên. Cài thư viện bằng `requirements.txt`.

## Kết quả và vấn đề
- Chuẩn hóa `unicodedata.normalize('NFC')`, lowercase và regex giữ chữ cái tiếng Việt chạy đúng: `'sinh viên đang học nlp tại trường đại học sư phạm tp hcm'`.
- ✅ (đã sửa trong notebook) **Tách từ sai đơn vị:** `nltk.word_tokenize` tách theo khoảng trắng nên ra âm tiết `['sinh', 'viên', 'đang', 'học', …]`. Tiếng Việt là ngôn ngữ đơn lập, từ có thể gồm nhiều âm tiết ("sinh viên", "đại học", "sư phạm"), cần công cụ tách từ tiếng Việt như `underthesea` hoặc `pyvi` → `['sinh_viên', 'đang', 'học', 'nlp', 'tại', 'trường', 'đại_học', 'sư_phạm', …]`.
- ✅ (đã sửa) **POS tagger tiếng Anh cho tiếng Việt:** `nltk.pos_tag` gắn `'nlp'` là JJ, `'đại'` là NNP… các nhãn này vô nghĩa. Cần `underthesea.pos_tag`.
- ✅ (đã sửa) **Không có lemmatization:** ô cuối chỉ gán `lemmas = tokens_nostop`. Tiếng Việt không biến hình nên bước này thực ra không cần; nên ghi rõ thay vì để như đã làm.
- ✅ (đã sửa) Ô tách từ gọi `word_tokenize` nhưng notebook không `from nltk.tokenize import word_tokenize`; output có được là nhờ trạng thái kernel từ lần chạy trước. Chạy lại từ đầu sẽ lỗi `NameError`.

## Kiến thức cần nhớ
- **NFC** (Normalization Form Composed) gộp ký tự và dấu thành một mã Unicode duy nhất (ví dụ: `"a"` + dấu = `"á"`). Văn bản tiếng Việt sao chép từ nhiều nguồn khác nhau có thể bị lẫn lộn giữa NFC và NFD, do đó bắt buộc phải chuẩn hóa trước khi tiến hành so khớp.
- **NFD** (Normalization Form Decomposed) là quá trình tách một ký tự có dấu thành ký tự gốc và dấu riêng biệt (ví dụ: `"á"` tách thành `"a"` + `◌́` [dấu sắc]).
- **Stemming** cắt hậu tố theo luật (nhanh, có thể ra "advanc"); **lemmatization** (phân rã từ gốc) tra từ điển và cần biết từ loại (`pos='v'`) để ra đúng dạng gốc.
- Pipeline tiền xử lý phụ thuộc ngôn ngữ: tiếng Anh cần lemmatization, tiếng Việt cần **tách từ** (word segmentation).
- Kiểm tra stopword bằng `set` (O(1)) thay vì `list` (O(n)).
- Trong báo cáo tiếng Anh: regex `[^a-z\s]` xoá dấu gạch nên "real-world" thành "realworld"; danh sách từ bị loại ghi "has, and, now, an, in" nhưng "and" xuất hiện hai lần (24 token → 18 token sau khi loại 6); POS tag sau khi loại stopword kém chính xác hơn gắn nhãn trên câu đầy đủ ("nlp" bị gắn RB, "like" bị gắn IN). Lemmatization không chỉ định `pos` coi mọi từ là danh từ nên "advanced" giữ nguyên.