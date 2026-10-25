# Lab 03 – Bag-of-Words, TF-IDF, N-gram, Cosine Similarity

## Đề bài
- **Bài 1:** thêm 2 câu vào corpus, nhận xét thay đổi của BoW; vì sao vector thưa.
- **Bài 2:** so sánh giá trị từ "AI" giữa BoW và TF-IDF; vì sao TF-IDF giảm trọng số từ phổ biến.
- **Bài 3:** văn bản nào giống nhau nhất (cosine); so sánh kết quả khi dùng BoW và TF-IDF.
- Phân loại văn bản AI/NLP bằng TF-IDF + Logistic Regression.

## Kết quả
Notebook: [notebooks/lab03_bow_tfidf_cosine.ipynb](notebooks/lab03_bow_tfidf_cosine.ipynb). Bản đã sửa và chạy lại: tính cosine cho cả BoW và TF-IDF, giải thích IDF theo `smooth_idf`, đánh giá phân loại bằng stratify và leave-one-out.

| Phần | Kết quả |
|---|---|
| Bài 1 | Vocabulary 13 → 16 từ (thêm *and, are, related*), ma trận 6×13 → 8×16 |
| Bài 2 | "AI" trong TF-IDF: `[0; 0,603; 0; 0,517; 0,305; 0; 0,325; 0]` (đúng với output) |
| Bài 3 | Cặp giống nhất: "I love NLP" – "I love AI" (cosine TF-IDF **0,636**); kế đến "AI is powerful" – "Deep learning is powerful" (0,590) |
| So sánh BoW và TF-IDF (Bài 3) | Cặp cao nhất theo BoW: "AI is powerful" – "Deep learning is powerful" (0,577); theo TF-IDF: "I love NLP" – "I love AI" (0,636). TF-IDF đổi thứ hạng vì giảm trọng số từ phổ biến "is" |
| Phân loại | Cách chia cũ: Accuracy **0,0** trên 2 văn bản test (cả hai cùng nhãn NLP); chia có stratify: 2/2 đúng; leave-one-out: **0,33**, tức không học được gì đáng tin từ 6 câu |

## Vấn đề trong phần trả lời
- ✅ (đã sửa) Bài 3 giải thích hai câu "chia sẻ 2/3 từ vựng 'I', 'love'", nhưng `CountVectorizer`/`TfidfVectorizer` mặc định bỏ token 1 ký tự (`token_pattern=r"(?u)\b\w\w+\b"`), vocabulary không có "i". Hai câu chỉ chung đúng một từ "love".
- ✅ (đã sửa) Đề yêu cầu so sánh cosine giữa BoW và TF-IDF nhưng notebook chỉ tính cosine trên TF-IDF; phần so sánh là lý thuyết, không có số liệu.
- ✅ (đã sửa) Bài 2 trình bày IDF = log(N/n) nên từ có mặt ở mọi văn bản có IDF = 0. scikit-learn mặc định dùng `smooth_idf`: IDF = ln((1+N)/(1+n)) + 1, **không bao giờ bằng 0**, nên từ phổ biến chỉ bị giảm trọng số chứ không bị triệt tiêu.
- ✅ (đã sửa) Accuracy = 0 trên 2 mẫu test không nói lên gì về mô hình. Với 6 văn bản nên dùng `stratify=labels` hoặc leave-one-out cross-validation.

## Kiến thức cần nhớ
- BoW/TF-IDF là ma trận **thưa** (sparse): mỗi văn bản chỉ chứa vài từ trong vocabulary.
- TF-IDF = tần suất trong văn bản × độ hiếm trên toàn corpus; mỗi hàng được chuẩn hóa L2 nên cosine = tích vô hướng.
- Đọc kỹ tham số mặc định của vectorizer (`token_pattern`, `lowercase`, `smooth_idf`, `norm`) trước khi giải thích kết quả.
- N-gram (`ngram_range=(2,2)`) giữ được thứ tự cục bộ ("not good") nhưng làm vocabulary tăng nhanh.