# 🎬 Video Mining – Phát hiện xe máy trong video giao thông bằng YOLOv8

Đồ án tự luyện cá nhân (07–08/10/2026): pipeline khai phá dữ liệu ảnh từ **kiểm tra dữ liệu → làm sạch → huấn luyện → phân tích lỗi** cho bài toán phát hiện xe máy trên frame cắt từ video camera cố định.

## Đề bài
- **Bài toán:** object detection 1 lớp (`motobike`), mỗi ảnh trả về các bounding box kèm confidence.
- **Dữ liệu:** Roboflow [`motobike-detection-otper-h43mq` v1](https://universe.roboflow.com/dat-tran-hoang/motobike-detection-otper-h43mq/dataset/1) (CC BY 4.0), export định dạng YOLOv8. Không đưa lên repo (~85 MB), tải theo hướng dẫn ở mục [Chạy](#chạy).

| Thuộc tính | Giá trị |
|---|---|
| Số ảnh | 1 355 frame từ 13 video |
| Train / Valid / Test | 1 152 / 136 / 67 (**test không có nhãn**) |
| Kích thước | 640×640 (Roboflow auto-orient + resize *stretch*) |
| Nhãn | YOLO txt `class cx cy w h` (chuẩn hóa 0–1) |

## Cách làm
| Bước | Nội dung |
|---|---|
| 1. EDA nhãn | Số box/ảnh, kích thước & tỉ lệ box, heatmap vị trí tâm, số ảnh theo video × split |
| 2. Chất lượng ảnh | Độ sáng (mean xám), độ tương phản (std xám), độ nét (phương sai Laplacian) |
| 3. Kiểm tra nhãn | Box tràn/suy biến/trùng, class lỗi, ảnh không nhãn |
| 4. Trùng lặp & rò rỉ | So pixel thumbnail 64×64 (trùng chính xác) + dHash 64-bit (gần trùng), gom nhóm bằng union-find |
| 5. Preprocessing | Tạo 2 dataset: **A** = split gốc Roboflow, **B** = làm sạch + loại trùng + `GroupShuffleSplit` **theo video** |
| 6. Huấn luyện | YOLOv8s, 100 epoch, imgsz 640, patience 25, cùng siêu tham số và augmentation cho A và B |
| 7. Đánh giá | So sánh A vs B, chọn ngưỡng confidence theo F1, ghép dự đoán–GT (IoU ≥ 0.5) để đếm TP/FP/FN |
| 8. Inference | Dự đoán tập test, xuất `best.pt`, `.onnx`, CSV kết quả |

Augmentation chọn theo EDA: mosaic + scale + translate (ít bối cảnh), lật ngang nhưng **không lật dọc**, xoay ±5°, HSV (ánh sáng), mixup nhẹ, `close_mosaic=10`.

## Kết quả
Chạy trên Kaggle (Tesla T4, ultralytics 8.4.174), 08/10/2026.

**Kiểm tra dữ liệu**
| Phát hiện | Số liệu |
|---|---|
| Box | ~1,5 box/ảnh, cao & hẹp (h/w ≈ 3,8), gần như toàn bộ là vật **lớn** theo COCO |
| Ảnh | Sáng ≈ 100/255, tương phản ≈ 26, train/valid/test không lệch phân bố |
| Nhãn | Chỉ 1 ảnh train có nhãn rỗng (giữ làm ảnh nền) |
| Ảnh trùng chính xác | 45 nhóm / 90 ảnh, **12 nhóm vắt qua các split** |
| Gần trùng với train | valid 24,3 %, test 40,3 % (frame liền kề cùng video) |
| Nhiễu nhãn | IoU giữa 2 lần gán nhãn cùng ảnh chỉ ≈ 0,89 |

**So sánh A và B (validation, `best.pt`)**
| Dataset | Train / Val | Precision | Recall | mAP@0.5 | mAP@0.75 | mAP@0.5:0.95 |
|---|---|---|---|---|---|---|
| A – split gốc (rò rỉ) | 1 152 / 136 | 0.964 | 0.970 | 0.990 | 0.968 | 0.806 |
| **B – sạch, chia theo video** | 1 062 / 189 | 0.924 | 0.946 | **0.980** | 0.950 | **0.775** |

- Rò rỉ chỉ làm mAP@0.5:0.95 tăng nhẹ (+0.031). Val B gồm 2 video chưa thấy (`7817`, `7825`) và đông xe hơn (1,95 so với 1,41 box/ảnh), nên chênh lệch này gồm cả rò rỉ lẫn độ khó.
- Ngưỡng tối ưu theo F1: **conf = 0.268** → TP 355, FP 85, FN 14 (P 0.807, R 0.962). Phần lớn FP thực chất là xe máy có thật nhưng bị **bỏ sót khi gán nhãn**.
- Test: 67 ảnh → 119 box, không ảnh nào trống; 8 ảnh test trùng y hệt ảnh train nên kết quả trên các ảnh đó đẹp hơn thực tế.

## Kiến thức cần nhớ
**Dữ liệu từ video**
- Frame liền nhau gần như giống hệt → chia train/val **ngẫu nhiên theo ảnh là rò rỉ**. Phải chia **theo video** (`GroupShuffleSplit`/`GroupKFold` với `groups=video`).
- Không tin tên file: 182 nhóm trùng tên frame nhưng chỉ 43 nhóm trùng pixel. Kiểm tra trùng bằng **nội dung ảnh** (thumbnail, perceptual hash).
- **dHash**: resize về 9×8 xám, so sánh từng pixel với pixel bên phải → 64 bit; khoảng cách Hamming nhỏ = ảnh gần giống.
- Độ nét = **phương sai Laplacian**, thấp nghĩa là ảnh mờ.

**Object detection**
- **IoU** = diện tích giao / diện tích hợp; TP khi IoU ≥ ngưỡng (thường 0.5).
- **mAP@0.5** chỉ cần định vị đúng tương đối; **mAP@0.5:0.95** trung bình trên 10 ngưỡng IoU nên đòi hỏi box rất khít. Khi nhãn tự nhiễu (IoU ≈ 0,89) thì chỉ số này có **trần tự nhiên**.
- Chọn ngưỡng confidence theo **F1 max** thay vì để mặc định 0.25.
- Roboflow resize **stretch** còn Ultralytics mặc định **letterbox** → khi chạy trên video gốc phải tiền xử lý giống lúc train.
- Nhiều FP có thể là **lỗi nhãn** chứ không phải lỗi mô hình → luôn xem ảnh sai trước khi kết luận.

## Chạy
| Notebook | Ghi chú |
|---|---|
| [motorbike-detection-english.ipynb](motorbike-detection-english.ipynb) | Bản tiếng Anh, **đã có sẵn output** lần chạy Kaggle |
| [motorbike_detection-viet.ipynb](motorbike_detection-viet.ipynb) | Bản tiếng Việt, đồng bộ 1–1 từng cell với bản tiếng Anh (chưa có output) |

**Tải dữ liệu:** vào [trang dataset trên Roboflow](https://universe.roboflow.com/dat-tran-hoang/motobike-detection-otper-h43mq/dataset/1) → **Download Dataset** → chọn định dạng **YOLOv8** → tải file zip rồi giải nén (có `data.yaml`, `train/`, `valid/`, `test/`). Nếu dùng Kaggle thì upload thư mục đó làm dataset input.

Nên chạy trên **Kaggle / Colab có GPU**: chuẩn bị dữ liệu như trên rồi **Run All**. Notebook tự tìm `data.yaml` trong `DATA_DIR`, `/kaggle/input`, thư mục hiện tại hoặc `data/`. Hai lần huấn luyện mất khoảng 45 phút trên T4. Muốn chạy thử nhanh trên CPU: đặt biến môi trường `QUICK_TEST=1` (YOLOv8n, 1 epoch, 10 % dữ liệu).
