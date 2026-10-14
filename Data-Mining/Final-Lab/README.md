# Final Lab – Tiền xử lý dữ liệu cho 4 loại dữ liệu

Bài tập nhóm môn Khai thác dữ liệu và ứng dụng (ĐH Sư phạm TP.HCM, 2025–2026, GVHD TS. Nguyễn Tấn Trung), nộp ngày 27/05/2026.

| Thành viên | MSSV |
|---|---|
| Trần Hoàng Đạt | 49.01.104.030 |
| Võ Văn Minh | 50.01.104.090 |
| Nguyễn Trần Bảo Thái | 49.01.104.133 |

## Đề bài
Áp dụng các kỹ thuật tiền xử lý cho từng loại dữ liệu; mỗi kỹ thuật trình bày **lý do áp dụng · cách triển khai · kết quả và phân tích**.

| Phần | Loại dữ liệu | Dataset | Yêu cầu |
|---|---|---|---|
| 1 | Ảnh | Fashion-MNIST (70 000 ảnh xám 28×28) + [New Plant Diseases](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) (~87 000 ảnh RGB, 38 lớp) | Bắt buộc |
| 2 | Bảng | [Credit Card Fraud Detection](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) (284 807 giao dịch, 31 cột, gian lận ≈ 0.17 %) | Bắt buộc (≥ 5 thuộc tính, ≥ 10 000 dòng) |
| 3 | Văn bản | [IMDB 50K Movie Reviews](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) (lấy 1 000 review) | Điểm cộng |
| 4 | Chuỗi thời gian | Giá cổ phiếu AAPL 2019–2020 qua `yfinance` (505 phiên) | Điểm cộng |

## Cách làm
| Phần | Kỹ thuật |
|---|---|
| 1 – Ảnh | Resize 128×128 (OpenCV), chuyển ảnh xám, chuẩn hóa về [0, 1], standardization (mean 0, std 1), phát hiện cạnh Canny |
| 2 – Bảng | Giả lập 1 % missing (MCAR) ở `Amount` → so sánh Mean / Median / KNN imputation; Min-Max, Standard, Robust scaler; tạo feature giả để minh họa Ordinal + One-Hot encoding; chọn feature bằng Correlation, Variance Threshold, Random Forest importance; under-sampling rồi train SVM, KNN, Random Forest, Decision Tree |
| 3 – Văn bản | Tách câu/tách từ (NLTK), bỏ stop word + dấu câu, Porter Stemmer so với WordNet Lemmatizer, TF-IDF (`max_features=1000`) |
| 4 – Chuỗi thời gian | Parse datetime, reindex theo ngày để lộ khoảng trống, ffill/bfill/linear/polynomial/spline, đặc trưng thời gian (thứ, mùa, ngày lễ, mã hóa sin/cos, số ngày từ đáy COVID 23/03/2020), resample tuần/tháng/quý và lên theo giờ, lag 1/2/5, rolling mean/std, autocorrelation |

## Kết quả
**Phần 2 – Credit Card Fraud** (test 56 962 giao dịch, 98 gian lận; train đã under-sampling còn 394 + 394)

| Mô hình | Precision (gian lận) | Recall (gian lận) | F1 (gian lận) | Accuracy |
|---|---|---|---|---|
| SVM | 0.06 | **0.92** | 0.11 | 0.98 |
| KNN | **0.07** | 0.91 | **0.13** | 0.98 |
| Random Forest | 0.05 | 0.92 | 0.09 | 0.97 |
| Decision Tree | 0.02 | 0.92 | 0.03 | 0.91 |

- Feature chọn cuối: **top 15 theo Random Forest** (V17, V12, V10, V16, V9…). Correlation và Variance Threshold không loại feature nào vì V1–V28 là thành phần PCA, vốn trực giao.
- Under-sampling giúp bắt gần hết giao dịch gian lận (recall ~0.92) nhưng đổi lại báo nhầm rất nhiều (precision ≤ 0.07). Accuracy cao chỉ vì lớp hợp lệ chiếm 99.8 %.
- ⚠️ Bảng tổng hợp viết tay trong notebook (SVM precision 0.23, F1 0.36…) khác với output đang lưu, nhiều khả năng do được ghi từ **một lần chạy khác**. Thứ tự dòng của `creditcard.csv` khi tải bằng lệnh có thể khác nhau, mà mặt nạ missing, `sample`, `train_test_split` và under-sampling đều chọn theo vị trí dòng, nên kết quả thay đổi giữa các lần chạy. Precision lớp gian lận đặc biệt nhạy vì sau under-sampling chỉ giữ 394 giao dịch hợp lệ. Notebook đã thêm `sort_values` để cố định thứ tự; bảng ở đây lấy theo output đang lưu.

**Các phần khác**
- Phần 1: sau standardization mean ≈ 0, std = 1 (cả Fashion-MNIST lẫn ảnh lá cây).
- Phần 3: câu mẫu 19 token → 9 token sau khi bỏ stop word; ma trận TF-IDF 1 000 × 1 000 dạng thưa. Chọn Lemmatization vì giữ được từ có nghĩa (`studies → study`, Porter cho ra `studi`).
- Phần 4: reindex theo ngày lộ ra 225 / 730 ngày trống (cuối tuần, ngày lễ). Giá đóng cửa tự tương quan cao ở mọi lag (không dừng), còn lợi suất ngày gần như không tự tương quan.

## Kiến thức cần nhớ
- **Missing data:** MCAR (ngẫu nhiên hoàn toàn), MAR (phụ thuộc biến khác), MNAR (phụ thuộc chính giá trị bị thiếu). Median imputation bền hơn mean khi có outlier.
- **Scaler:** Min-Max nhạy outlier; Standard dùng mean/std; **Robust** dùng median/IQR, hợp với cột lệch nặng như `Amount`.
- **Encoding:** Ordinal khi có thứ tự, One-Hot khi không có thứ tự; nhiều giá trị (high-cardinality) thì dùng Target/Frequency encoding.
- **Dữ liệu mất cân bằng:** đừng nhìn accuracy; xem precision/recall/F1 của lớp hiếm. Chỉ resample trên **train**, không đụng vào test.
- **Stemming** cắt đuôi theo luật (nhanh, có thể ra từ vô nghĩa); **Lemmatization** tra từ điển (chậm hơn, ra từ đúng).
- **TF-IDF** = tần suất từ trong văn bản × độ hiếm của từ trên toàn tập.
- **Đặc trưng chu kỳ** (thứ, tháng) mã hóa bằng sin/cos để thứ 7 và thứ 2 nằm gần nhau.
- **Lag, rolling** dùng `shift`/`rolling` theo quá khứ, không được nhìn trước tương lai.

## Chạy
| Notebook | Nội dung |
|---|---|
| [01 _image_preprocessing.ipynb](notebooks/01%20_image_preprocessing.ipynb) | Phần 1 – Ảnh |
| [02 _tabular_preprocessing.ipynb](notebooks/02%20_tabular_preprocessing.ipynb) | Phần 2 – Bảng |
| [03 _text_preprocessing.ipynb](notebooks/03%20_text_preprocessing.ipynb) | Phần 3 – Văn bản |
| [04 _temporal_preprocessing.ipynb](notebooks/04%20_temporal_preprocessing.ipynb) | Phần 4 – Chuỗi thời gian |

Notebook đã có sẵn output, xem được ngay trên GitHub. Muốn chạy lại thì nên dùng **Google Colab**: mỗi notebook tự tải dữ liệu (Kaggle CLI, `kagglehub`, `yfinance`, Keras). Dataset không có trong repo, xem [data/README.md](data/README.md).

1. `pip install -r requirements.txt`
2. Phần 1 và 2 cần Kaggle API: tải `kaggle.json` ở <https://www.kaggle.com/settings/account>, đặt vào `~/.kaggle/kaggle.json` (Windows: `C:\Users\<user>\.kaggle\kaggle.json`).
3. Mở từng notebook và **Run All**. Phần 1 tải ~2.7 GB ảnh lá cây.
