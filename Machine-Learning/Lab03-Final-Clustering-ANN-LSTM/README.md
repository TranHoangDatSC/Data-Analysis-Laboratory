# Lab 03 (Final) – Clustering, ANN Regression/Classification, Bi-LSTM

| Bài | Bài toán | Dữ liệu | Mô hình | Chỉ số |
|---|---|---|---|---|
| 1 | Clustering | `wine-clustering.csv` (178 mẫu, 13 feature) | StandardScaler → K-Means (+ PCA để so sánh, trực quan hóa) | Silhouette |
| 2 | Regression | `50_Startups.csv` (target `Profit`) | ANN 64-32-16-1 (Keras) | MSE, RMSE |
| 3 | Classification | `Dry_Bean_Dataset.xlsx` (target `Class`) | MLPClassifier (100, 50) | F1, Confusion Matrix |
| 4 | Sentiment | `Reviews_dataset.csv` (1 000 câu, nhãn 0/1) | TextVectorization → Embedding → Bi-LSTM(64) | F1, Confusion Matrix |

## Kết quả
| Bài | Kết quả | Chi tiết |
|---|---|---|
| Bài 1 | **K = 3**, Silhouette **0.2849** (13 chiều). PCA không làm cụm tốt hơn | [report](outputs/ex1_wine_clustering_report.md) |
| Bài 2 | RMSE **12 854.74**, tốt hơn baseline Linear Regression (14 691.64) | [report](outputs/ex2_ann_regression_result.md) |
| Bài 3 | F1 weighted **0.9019** | [report](outputs/ex3_ann_classification_report.md) |
| Bài 4 | F1 macro **0.8499**, confusion `[[87, 13], [17, 83]]` | [report](outputs/ex4_lstm_sentiment_report.md) |

Mọi kết quả đều **tái lập được**: cố định seed (`42`), riêng TensorFlow bật thêm op determinism.

![Clusters](outputs/ex1_clusters_pca2d.png)

> 🧭 Vì sao làm như vậy, kiểm chứng tham số và các điểm cần lưu ý: xem [DECISIONS.md](DECISIONS.md)

## Kiến thức cần nhớ
**Clustering**
- Phải **chuẩn hóa** trước K-Means: Proline (std ~315) lấn át mọi feature khác. Không chuẩn hóa thì kết quả trùng hệt phân cụm chỉ theo Proline (ARI = 1.0).
- Chọn K: **Elbow** (inertia giảm chậm lại) + **Silhouette** (càng gần 1 càng tốt).
- **Silhouette** = (b − a) / max(a, b): a = khoảng cách trung bình trong cụm, b = tới cụm gần nhất.
- ⚠️ Silhouette chỉ so sánh được khi đo trên **cùng một không gian**. Ở Wine, đo trong không gian PCA càng ít chiều thì số càng cao (2D: 0.56 so với 0.28 khi đo trên 13 chiều).

**ANN**
- Hồi quy: lớp cuối 1 nơ-ron, không activation, loss MSE. **Chuẩn hóa cả target**, rồi `inverse_transform` khi đánh giá. Không chuẩn hóa thì RMSE ~34 000, ngang việc đoán hằng số.
- Phân loại đa lớp: softmax + cross-entropy (MLPClassifier tự xử lý).
- **EarlyStopping** + tập validation tách từ train giúp chống overfitting và tự chọn số epoch.

**Bi-LSTM**
- Pipeline văn bản: chuẩn hóa chữ → tách từ → ánh xạ sang số → đệm/cắt về cùng độ dài → Embedding → LSTM.
- **Bidirectional** đọc câu theo 2 chiều để nắm ngữ cảnh trước và sau ("not good").
- `mask_zero=True` để LSTM bỏ qua phần đệm.

## Chạy
Mở [lab03_clustering_ann_lstm.ipynb](lab03_clustering_ann_lstm.ipynb) (Jupyter / VS Code) – notebook đã có sẵn output, xem được ngay trên GitHub. Muốn chạy lại: đặt dữ liệu vào `data/` (xem [data/README.md](data/README.md)) rồi **Run All**; hình và bảng kết quả được lưu vào `outputs/`.

Bài 2 và 4 cần `tensorflow`. Toàn bộ notebook chạy vài phút trên CPU.
