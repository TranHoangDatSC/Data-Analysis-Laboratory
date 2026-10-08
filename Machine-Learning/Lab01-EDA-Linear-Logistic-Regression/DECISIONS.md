# Giải thích quyết định – ML Lab 01

## 1. Đối chiếu đề bài → code
| Yêu cầu | Bước trong notebook |
|---|---|
| Cleaning data | Bước 2: đếm thiếu/trùng, bỏ `User ID`. Điền thiếu bằng median nằm trong Pipeline (bước 6–7) |
| Heatmap, không chọn target | Bước 4: chỉ các feature (`Profit`, `Purchased` không có mặt) |
| Mean, mode, median, variance | Bước 3: bảng thống kê cho mọi cột số + cột phân loại |
| Normalization | Bước 5: `StandardScaler` fit trên train, minh họa trước/sau. Dùng thật trong Pipeline của 2 mô hình |
| Linear Regression → RMSE | Bước 6: **11 943.48** |
| Logistic Regression → F1 + Confusion Matrix | Bước 7: **F1 0.7451**, `[[48, 3], [10, 19]]` |

## 2. Làm sạch dữ liệu
| Quyết định | Lý do |
|---|---|
| **Không** điền thiếu trước khi thống kê | Nếu điền bằng mean rồi mới thống kê, giá trị vừa điền trở thành **mode** giả và kéo median về mean. Ví dụ: 3 ô `Administration` cùng bằng mean sẽ làm mode = mean |
| Điền bằng **median**, đặt trong Pipeline | Median ít bị ảnh hưởng bởi giá trị cực trị hơn mean. Đặt trong Pipeline để median được tính từ tập **train** (tránh rò rỉ dữ liệu) |
| Bỏ `User ID` | Là mã định danh, không mang thông tin dự đoán. Thống kê của nó (mean, skew…) vô nghĩa |
| Giữ nguyên các số 0 ở `R&D Spend` (2 dòng), `Marketing Spend` (3 dòng) | Có thể là "không chi" thật hoặc dữ liệu thiếu bị ghi thành 0. Không có căn cứ để sửa nên chỉ ghi nhận |

## 3. Thống kê mô tả
| Quyết định | Lý do |
|---|---|
| Đánh giá độ lệch bằng **hệ số skewness** | So sánh mean với median phụ thuộc đơn vị đo: chênh 1 000 đồng là nhỏ với lương nhưng lớn với tuổi. Skewness không có đơn vị: \|skew\| < 0.5 gần đối xứng, 0.5–1 lệch vừa, > 1 lệch mạnh |
| Mode ghi "không có" khi mọi giá trị khác nhau | Với biến liên tục, "giá trị xuất hiện nhiều nhất" thường không tồn tại. Ghi kèm số lần lặp (vd. `35.00 (×32)`) để biết mode có ý nghĩa hay không |
| Biến nhị phân `Purchased` chỉ báo tỉ lệ (35.8 %) | Mean/variance/skew của biến 0/1 không cần thiết. Tỉ lệ lớp mới là thông tin quan trọng (quyết định dùng F1 + stratify) |
| Thêm `value_counts` cho `State`, `Gender` | Cột phân loại cũng là một phần của "hiểu dữ liệu" |
| Thêm histogram + boxplot | Nhìn hình nhanh hơn đọc bảng: thấy được dạng phân phối và outlier |

Nhận xét chính: hầu hết các cột gần đối xứng. `Administration` lệch trái vừa (skew −0.56). `Profit` có 1 outlier (giá trị nhỏ nhất 14 681).

## 4. Chuẩn hóa
| Quyết định | Lý do |
|---|---|
| Chuẩn hóa **feature**, không chuẩn hóa **target** | Target là đại lượng cần dự đoán, giữ nguyên đơn vị để RMSE đọc được (đơn vị: đô la) |
| **Chia train/test trước**, fit scaler trên train | Nếu fit trên toàn bộ dữ liệu, mean/std đã "nhìn thấy" tập test → đánh giá lạc quan. Vì thế mean/std của test sau chuẩn hóa không đúng 0/1 tuyệt đối (0.23 / 0.89 với `Age`), đây là điều bình thường |
| `StandardScaler` (z-score) thay vì Min-Max | Không có outlier cực đoan. Z-score là lựa chọn mặc định cho Linear/Logistic Regression |

## 5. Linear Regression
| Quyết định | Lý do |
|---|---|
| Feature: 3 cột chi tiêu, **bỏ `State`** | 5-fold CV trên train: thêm `State` làm RMSE tăng từ 14 756 lên 16 372. Với chỉ 40 mẫu train, 2 cột one-hot thêm vào chủ yếu làm tăng nhiễu |
| Vẫn chuẩn hóa dù OLS không cần | Dự đoán không đổi, nhưng hệ số trở nên **so sánh được**: R&D (31 186) ≫ Marketing (11 230) ≫ Administration (2 046) |
| Chia 80/20, `random_state=42` | Chuẩn mực của lớp. Tập test chỉ có 10 mẫu nên RMSE test dao động mạnh; CV (±6 460) cho cái nhìn trung thực hơn |

## 6. Logistic Regression
| Quyết định | Lý do |
|---|---|
| Feature: `Age`, `EstimatedSalary`, **không** dùng `Gender` | CV F1: 0.7589 (không Gender) so với 0.7538 (có Gender). Gender không giúp gì |
| Chia **stratified** | Lớp "Mua" chỉ chiếm 35.8 %. Stratify giữ đúng tỉ lệ đó ở cả train và test |
| Chuẩn hóa trong Pipeline | Logistic Regression của sklearn có regularization L2 (`C=1`), mức phạt phụ thuộc thang đo. Chuẩn hóa giúp phạt đều các feature và solver hội tụ nhanh |
| Báo cả F1 test và F1 CV | F1 test (0.7451) nằm trong khoảng CV (0.7589 ± 0.0727), chứng tỏ kết quả ổn định |

Đọc kết quả: mô hình nhận diện tốt người **không mua** (recall 0.94), nhưng bỏ sót 1/3 người **mua** (recall 0.66). Nguyên nhân: ranh giới thật giữa hai lớp trên mặt phẳng Age–Salary là đường cong, một đường thẳng không tách hết được. Kiểm chứng bằng 5-fold CV trên cùng tập train:

| Mô hình | CV F1 |
|---|---|
| Logistic Regression (đề yêu cầu) | 0.7589 |
| Logistic + đặc trưng bậc 2 (`PolynomialFeatures(2)`) | 0.8537 |
| KNN (k = 5) | 0.8536 |
| Decision Tree (depth 4) | 0.8617 |

Chỉ cần thêm đặc trưng bậc 2 (Age², Salary², Age×Salary), Logistic đã tăng gần 0.1 F1. Đề yêu cầu Logistic Regression nên bài giữ mô hình tuyến tính; bảng trên là hướng cải thiện.
