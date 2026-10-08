# Giải thích quyết định – ML Lab 02 (Dry Bean)

## 1. Đối chiếu đề bài → code
| Yêu cầu | Code |
|---|---|
| ≥ 7 feature | 8 feature hình học cơ bản |
| KNN, AdaBoost/Cascade, Naive Bayes, Decision Tree | Đủ 4 mô hình (chọn AdaBoost) |
| Split 80/20 hoặc 70/30 | 80/20, `stratify=y`, `random_state=42` |
| F1, Confusion Matrix, AUC cho **mọi** mô hình | Bảng F1 + AUC, `confusion_matrices.png` (4 mô hình), ROC gộp |
| (Tùy chọn) visualize + clean | Kiểm tra thiếu/trùng, biểu đồ phân bố lớp |

## 2. Các quyết định & lý do
| Quyết định | Lý do |
|---|---|
| 8 feature: `Area, Perimeter, MajorAxisLength, MinorAxisLength, AspectRation, Eccentricity, ConvexArea, EquivDiameter` | Là các đo đạc trực tiếp về kích thước/hình dạng, dễ giải thích, dư điều kiện ≥ 7. `ShapeFactor1–4`, `roundness`, `Compactness`… được tính ra từ chính các đại lượng này nên phần lớn trùng thông tin |
| **Chia trước, chuẩn hóa sau** (`make_pipeline(StandardScaler(), model)`) | Scaler chỉ học mean/std từ train, tránh rò rỉ thông tin của test |
| `StandardScaler` cho cả 4 mô hình | Bắt buộc với KNN (`Area` ~50 000 sẽ lấn át `Eccentricity` ~0.7). Không ảnh hưởng tới cây quyết định/AdaBoost, nhưng giữ chung một pipeline cho gọn |
| `stratify=y` | Lớp mất cân bằng (3 546 so với 522). Stratify giữ đúng tỉ lệ mỗi lớp trong train và test |
| F1 **weighted** | Trung bình F1 các lớp có trọng số theo số mẫu, phản ánh hiệu năng tổng thể khi lớp lệch |
| AUC **One-vs-Rest** + `label_binarize` | AUC gốc chỉ cho 2 lớp. Với 7 lớp: tính 7 AUC "lớp i so với phần còn lại" rồi lấy trung bình |
| ROC **macro-average** | Nội suy TPR của 7 đường ROC lên cùng lưới FPR rồi lấy trung bình đều, khớp với cách tính AUC macro ở trên |
| KNN `k=5, weights='distance'` | Láng giềng gần có tiếng nói lớn hơn, giảm nhầm lẫn ở vùng biên |
| Decision Tree `max_depth=6` | Giới hạn độ sâu để tránh học thuộc lòng dữ liệu train |
| AdaBoost: 100 cây `max_depth=2`, `learning_rate=0.5` | Boosting cần **weak learner** (cây nông). `learning_rate` nhỏ giúp mỗi cây đóng góp vừa phải, ổn định hơn |
| Gaussian NB | Feature là số liên tục, giả định phân phối chuẩn cho từng lớp |

## 3. Đọc kết quả
- **KNN có F1 cao nhất (0.9030)**, nhưng **Naive Bayes có AUC cao nhất (0.9870)**. AUC đo khả năng **xếp hạng xác suất** trên mọi ngưỡng, còn F1 chỉ đo tại ngưỡng mặc định. NB xếp hạng tốt, nhưng nhãn cuối cùng hay sai vì giả định "độc lập" bị vi phạm nặng: `Area`, `ConvexArea`, `EquivDiameter`, `Perimeter` gần như tỉ lệ thuận với nhau.
- Mọi mô hình đều nhầm nhiều nhất ở cặp **DERMASON ↔ SIRA** (hai loại có hình dạng gần giống; KNN nhầm 52 + 69 mẫu). **BOMBAY** luôn đúng 100 % vì kích thước lớn vượt trội.
- Decision Tree và AdaBoost cho kết quả xấp xỉ nhau: với depth 6, một cây đơn đã đủ mạnh cho 8 feature.
