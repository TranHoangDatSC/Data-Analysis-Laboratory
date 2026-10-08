# Giải thích quyết định – ML Lab 03 (Final)

## Bài 1 – Wine clustering (K-Means)
| Quyết định | Lý do |
|---|---|
| `StandardScaler` trước tiên | Thang đo chênh nhau rất xa: `Proline` mean ~747 / std ~315, trong khi `Hue` mean ~0.96 / std ~0.23. Kiểm chứng trong notebook: K-Means trên dữ liệu thô **trùng khớp hoàn toàn** với K-Means chỉ dùng mỗi Proline (ARI = 1.0), tức 12 feature còn lại bị bỏ qua |
| Chọn K trong 2–6 bằng **Elbow + Silhouette** trên 13 feature | Hai tiêu chí bổ trợ nhau: inertia luôn giảm khi K tăng nên cần tìm "khuỷu"; Silhouette có cực đại rõ ràng. Cả hai cùng chỉ ra **K = 3**: inertia giảm −381 từ K = 2 → 3 rồi chỉ còn −103, −68, −61; Silhouette cực đại 0.2849 |
| `n_init=20`, `random_state=42` | K-Means phụ thuộc điểm khởi tạo: chạy 20 lần lấy kết quả tốt nhất, cố định seed để tái lập |
| So sánh có/không PCA với Silhouette **đo trên cùng 13 chiều** | Silhouette đo trong không gian PCA 2D lên tới 0.5611, nhưng chỉ vì khoảng cách được tính trên ít chiều hơn. Đo công bằng trên 13 chiều thì mọi cấu hình PCA đều ≈ 0.28, **không tốt hơn** dữ liệu gốc |
| Mô hình cuối: K-Means trên 13 feature (không PCA) | PCA không cải thiện chất lượng cụm mà làm mất thông tin (PCA 2D chỉ giữ 55.4 % variance). Đơn giản hơn và giữ đủ thông tin |
| PCA 2D **chỉ để vẽ** | Không thể vẽ 13 chiều. Chiếu lên 2 thành phần chính để nhìn thấy 3 cụm tách nhau |
| Báo tâm cụm theo **giá trị gốc** | Để đọc được ý nghĩa: cụm Proline cao (~1 100) + Flavanoids cao; cụm Color Intensity cao (~7.2) + Hue thấp; cụm Proline thấp (~510) + màu nhạt |

Đối chiếu ngoài: theo mô tả gốc của bộ UCI Wine, dữ liệu đến từ 3 giống nho, khớp với K = 3. File `wine-clustering.csv` không có nhãn nên notebook không kiểm chứng trực tiếp điều này.

## Bài 2 – ANN Regression (50_Startups)
| Quyết định | Lý do |
|---|---|
| Điền thiếu bằng median + chuẩn hóa X + one-hot `State` (`drop_first`), fit trên train | Giống quy trình của ML Lab01. `drop_first` tránh bẫy đa cộng tuyến (dummy trap) |
| **Chuẩn hóa cả target** `Profit` | Profit ~112 000. Lớp output khởi tạo quanh 0 với learning rate 0.001 thì rất khó "với" tới. Thí nghiệm đối chứng trong notebook (cùng mạng, cùng seed): để nguyên target thì chạy 311 epoch, RMSE 34 072.55, ngang việc đoán hằng số bằng trung bình (33 776.69). Chuẩn hóa target thì RMSE 12 854.74. Sau đó `inverse_transform` về đô la để tính RMSE |
| Mạng 64-32-16-1, ReLU, lớp cuối không activation | Cấu trúc phễu điển hình. Hồi quy cần đầu ra tuyến tính |
| `batch_size=8`, tối đa 500 epoch, EarlyStopping (patience 30) trên `validation_split=0.2` | Chỉ có 40 mẫu train: batch nhỏ cho nhiều bước cập nhật hơn. EarlyStopping tự dừng (dừng ở epoch 44) và khôi phục trọng số tốt nhất. Validation lấy từ train, test không bị đụng tới |
| So với baseline Linear Regression trên cùng tiền xử lý | Để biết ANN có đáng dùng không: ANN 12 854.74 so với LR 14 691.64 |

⚠️ Tập test chỉ có 10 mẫu, nên chênh lệch giữa ANN và Linear Regression có thể thay đổi với cách chia khác. Với dữ liệu nhỏ, gần tuyến tính như thế này (tương quan R&D Spend – Profit 0.971), Linear Regression vẫn là lựa chọn hợp lý vì đơn giản và dễ giải thích.

## Bài 3 – ANN Classification (Dry Bean)
| Quyết định | Lý do |
|---|---|
| Dùng **cùng 8 feature, cùng cách chia** như ML Lab02 | So sánh công bằng với các mô hình cổ điển |
| Chia trước, `StandardScaler` fit trên train | MLP rất nhạy với thang đo; fit trên train để tránh rò rỉ |
| `MLPClassifier(100, 50)`, ReLU, Adam | Hai lớp ẩn là đủ cho dữ liệu bảng 8 chiều |
| `early_stopping=True` | Tự tách 10 % train làm validation, dừng ở vòng 43/300 |
| F1 weighted | Lớp mất cân bằng: DERMASON 3 546 mẫu so với BOMBAY 522 (~6.8 lần) |

Kết quả: MLP **0.9019** ≈ KNN 0.9030 (Lab02). Với dữ liệu bảng ít feature, mạng nơ-ron không vượt trội so với mô hình đơn giản.

## Bài 4 – Bi-LSTM sentiment (Reviews)
| Quyết định | Lý do |
|---|---|
| Chia **train / validation / test = 720 / 80 / 200**, stratified | Validation dùng cho EarlyStopping. Test hoàn toàn đứng ngoài quá trình huấn luyện nên F1 test là đánh giá khách quan |
| `TextVectorization` (Keras 3) | Lớp chuẩn hiện hành: lowercase + bỏ dấu câu + tách từ + đệm/cắt trong một bước. Từ điển chỉ học từ train (1 693 từ); từ lạ ở test được map vào `[UNK]` |
| `MAX_LEN = 100` | Câu review ngắn: trung bình 10.9 từ, dài nhất 32 từ, nên 100 token không cắt mất từ nào |
| Embedding 96 chiều, `input_dim` = kích thước từ điển thực tế, `mask_zero=True` | Không tạo vector thừa cho các chỉ số không bao giờ xuất hiện. Mask giúp LSTM bỏ qua phần đệm |
| **Bidirectional** LSTM(64) | Đọc câu theo 2 chiều để nắm phủ định / ngữ cảnh phía sau |
| Dropout 0.5 + EarlyStopping (patience 5, khôi phục trọng số tốt nhất) | Chỉ có 720 câu train nên rất dễ overfit: val_loss tốt nhất ở epoch 5 (train acc 0.986 so với val acc 0.775), dừng ở epoch 10 |
| F1 **macro** | Hai lớp cân bằng (100/100 ở test), macro = trung bình đều hai lớp |
| Seed 42 + `enable_op_determinism()` | Mạng nơ-ron khởi tạo ngẫu nhiên. Với dữ liệu nhỏ, đổi seed có thể làm F1 dao động vài điểm phần trăm. Cố định seed để kết quả tái lập được |

Đọc kết quả: hai lớp được nhận diện cân bằng (recall 0.87 / 0.83). Mô hình hơi thiên về đoán "tiêu cực" (17 câu tích cực bị đoán sai thành tiêu cực, so với 13 câu theo chiều ngược lại).
