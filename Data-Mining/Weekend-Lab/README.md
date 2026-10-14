# Weekend Lab – Bài tập thực hành cuối tuần

| Notebook | Tuần | Chủ đề | Dữ liệu | Trạng thái |
|---|---|---|---|---|
| [W1.ipynb](W1.ipynb) | 1 | Thống kê mẫu, chuẩn hóa, χ², độ đo khoảng cách | Mẫu 20 giá trị age/weight + các bảng cho sẵn | ✅ Hoàn thành Bài 1–10 |
| [W2_3.ipynb](W2_3.ipynb) | 2–3 | EDA → KNN → Linear/Ridge Regression → GridSearchCV | OpenML `vehicle` (846 xe, 18 feature, 4 lớp) | ✅ Hoàn thành Bài 1–28 + Homework |
| [W4_5.ipynb](W4_5.ipynb) | 4–5 | Gọi REST API → EDA → K-Means, DBSCAN, Hierarchical, PCA | [PokeAPI](https://pokeapi.co/) – 50 Pokemon đầu tiên | ✅ Hoàn thành Bài 1–20 |

## Đề bài
**W1 – Chuẩn hóa và các kiểu dữ liệu**
1. Thống kê mẫu: mean/median/mode, phương sai, xác suất, histogram, vector trung bình + ma trận hiệp phương sai, range normalization, Z-score.
2. Tính robust của mean, median, std với outlier.
3. Phân tích tính độc lập bằng contingency table; tính χ² sau khi rời rạc hóa `X1` thành 3 bin.
4. Độ đo khoảng cách (bất đẳng thức tam giác), mean absolute deviation, correlation, bảng 3 chiều, dữ liệu hỗn hợp.

**W2_3 – Supervised Learning (Vehicle Silhouettes)**
- Tuần 1: tải dữ liệu, kiểm tra missing, thống kê mô tả, histogram/heatmap/scatter, mã hóa nhãn, chia train/test, `StandardScaler`, KNN (k = 1…9), classification report, confusion matrix.
- Tuần 2: dự đoán `SCALED_VARIANCE_MAJOR` bằng Linear Regression (MSE, RMSE, R²), `GridSearchCV` cho KNN và Ridge, viết lại full pipeline.

**W4_5 – Clustering of Pokemons**
- Tuần 1: gọi PokeAPI lấy height, weight, type, 6 chỉ số; EDA; `LabelEncoder`; `StandardScaler`.
- Tuần 2: K-Means, Elbow, Silhouette, DBSCAN, dendrogram (Ward), PCA, re-cluster sau PCA, full pipeline.

## Kết quả
**W1**
| Bài | Kết quả |
|---|---|
| 1 | mean X = 71.45, median 71.5, mode 74; Var(Y) = 1 369.2 (chia n) / 1 441.3 (chia n − 1); P(X ≥ 70) = 0.65; tương quan X–Y = 0.889 |
| 2, 7 | Thêm một outlier 300 vào X: mean 71.45 → 82.33, std 3.72 → 48.81, MAD quanh mean 3.25 → 20.73, median gần như không đổi |
| 5 | Sau khi chia 3 bin: χ² = 3.889 < 5.991 (q = 2) ⇒ X1 và X2 **độc lập** |
| 6 | d(p2,p3) ∈ [1, 3], d(p1,p4) ∈ [1, 3], d(p2,p4) ∈ (0, 4]; cần tính thêm d(p1,p4); p4 **có thể** gần p2 hơn p3 |
| 8 | ρ = 0 ⇔ b = (a + c) / 2 |
| 9 | Cộng dồn theo X: χ² = 0.957 < 3.841 (q = 1) ⇒ Y và Z **độc lập** |
| 10 | Mean vector (0, 0.6, 0.4) khi mã hóa X2 bằng vector chỉ thị |

**W2_3**
| Bài toán | Mô hình | Kết quả (test 170 mẫu) |
|---|---|---|
| Phân loại 4 loại xe | KNN k = 5 (tốt nhất trong k = 1…9) | Accuracy **0.765**; bus gần hoàn hảo, nhầm chủ yếu giữa opel và saab |
| | GridSearchCV KNN | `k = 5, weights = 'distance'`, CV accuracy 0.715 |
| | Random Forest / SVC (HW) | 0.771 / 0.747 |
| Hồi quy `SCALED_VARIANCE_MAJOR` | Linear Regression | R² **0.981**, RMSE 4.54 |
| | Ridge tuned (α ≈ 0.03) | R² 0.981 (α = 1: 0.979) |
| Wine quality (HW) | KNN phân loại thấp/cao · Linear hồi quy | Accuracy 0.757 · R² 0.265 |

**W4_5**
| Bước | Kết quả |
|---|---|
| Dữ liệu | 50 Pokemon, không có missing; type nhiều nhất: poison (21), bug (10) |
| K-Means (height, weight, type) | Silhouette cao nhất ở k = 2 (0.487) |
| DBSCAN (eps = 0.5, min_samples = 3) | 5 cụm + 13 điểm nhiễu |
| PCA (3 feature) | PC1 + PC2 giữ 91 % phương sai |
| Full pipeline (8 feature) | k = 2: Silhouette **0.346** trên 8 chiều → **0.480** sau khi giữ 2 PC |

⚠️ Hai số Silhouette ở dòng cuối đo trên **hai không gian khác nhau** (8 chiều và 2 chiều) nên không so sánh trực tiếp được. Giảm chiều luôn làm Silhouette tăng, không có nghĩa là cụm tốt hơn.

## Lưu ý
- **W1:** câu b ban đầu tính nhầm `np.var(X)`, Bài 5 ban đầu lập bảng chéo trên giá trị gốc; cả hai đã được sửa.
- **W2_3:** bản `wine-quality-white` trên OpenML mã hóa lại `quality` 3–9 thành 1–7, notebook đã đưa về thang gốc trước khi áp ngưỡng "≤ 5 là thấp".
- **W4_5:** phần Homework (SpectralClustering, GMM, dò `eps` của DBSCAN, 200 Pokemon, pairplot) chưa làm.

## Kiến thức cần nhớ
- **Mean, std không robust**: một outlier kéo lệch cả hai. **Median, IQR robust** hơn.
- **Range normalization** `(x − min) / (max − min)` về [0, 1]; **Z-score** `(x − μ) / σ` về mean 0, std 1.
- **χ² độc lập**: so sánh tần số quan sát với tần số kỳ vọng `E = (tổng hàng × tổng cột) / n`. Bậc tự do `(r − 1)(c − 1)`; p < 0.05 thì bác bỏ giả thuyết độc lập.
- **Scaler chỉ fit trên train**, rồi transform cả train lẫn test, nếu không sẽ rò rỉ thông tin test.
- **Contingency table**: truyền vào `chi2_contingency` bảng không có hàng/cột tổng; với bảng 2×2 nhớ để ý hiệu chỉnh Yates (`correction`).
- **Metric** thỏa bất đẳng thức tam giác ⇒ `|d(x,y) − d(y,z)| ≤ d(x,z)`, dùng để chặn trên/dưới các khoảng cách chưa biết.
- **Đa cộng tuyến**: feature tương quan gần ±1 làm hệ số hồi quy khó diễn giải; Ridge giúp ổn định hệ số.
- Chọn k cho K-Means: **Elbow** + **Silhouette**. DBSCAN không cần k nhưng nhạy với `eps`; điểm nhãn `-1` là nhiễu.

## Chạy
Mở notebook bằng Jupyter / VS Code. W2_3 tự tải dữ liệu từ OpenML, W4_5 gọi PokeAPI (cần Internet), W1 dùng dữ liệu nhập sẵn trong code.
