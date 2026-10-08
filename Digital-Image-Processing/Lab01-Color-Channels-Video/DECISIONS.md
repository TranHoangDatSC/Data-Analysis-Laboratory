# Giải thích quyết định – DIP Lab 01

## 1. Đối chiếu đề bài → code
| Yêu cầu | Code |
|---|---|
| Input: video + ảnh nhỏ PNG/JPG | `data/input.mkv` + `data/icon_big.png` (90×90, có alpha) |
| Overlay ảnh nhỏ lên video | Hàm `overlay()`: alpha blending tại góc (20, 20) |
| Cửa sổ 4 subplot: gốc + 3 kênh, **đều có icon** | Trong notebook: lưới 2×2 bằng `plt.subplots` cho các frame mẫu. Xem realtime: hàm `play()` ghép 4 ảnh thành lưới 2×2 trong một cửa sổ `cv2.imshow`. Chèn icon **trước** khi tách kênh nên cả 4 hình đều có icon |

## 2. Các quyết định & lý do
| Quyết định | Lý do |
|---|---|
| Chèn icon **trước** `cv2.split` | Đề yêu cầu "3 clips for 3 channels **with overlay image**". Chèn một lần trên frame gốc là mỗi kênh tự có phần icon của nó |
| Đọc icon bằng `IMREAD_UNCHANGED` + alpha blending | Icon PNG có nền trong suốt. Nếu đọc mặc định, kênh alpha bị bỏ và nền trong suốt hiện thành một ô vuông màu. Blending giữ đúng hình dạng icon |
| Cắt icon theo kích thước còn lại của frame | Tránh lỗi khi icon lớn hơn vùng còn lại (đổi vị trí hoặc dùng video nhỏ) |
| Hiển thị mỗi kênh dưới dạng **ảnh màu** (2 kênh kia = 0) | Kênh đỏ hiện màu đỏ, nhìn trực quan ngay. Hiển thị 3 kênh bằng ảnh xám thì trông gần giống nhau |
| Đảo `frame[..., ::-1]` | OpenCV lưu theo BGR, Matplotlib hiển thị theo RGB |
| Resize về 640×360 | Kích thước cố định cho 4 ô, lưới 2×2 vừa màn hình (1280×720) và nhẹ khi phát realtime |
| Notebook hiển thị **3 frame mẫu** (đầu, giữa, gần cuối video) | Notebook không phát được video realtime. Vài frame mẫu đủ để kiểm tra kết quả, và output vẫn xem được trên GitHub |
| `play()`: ghép lưới bằng `np.hstack`/`np.vstack` + `cv2.imshow` | Một cửa sổ duy nhất chứa cả 4 hình như đề yêu cầu. OpenCV hiển thị nhanh hơn Matplotlib nhiều nên theo kịp tốc độ video. Trước khi `imshow` phải đổi lại RGB → BGR |
| `cv2.waitKey(1000 / fps)` + phím **q** | Phát đúng tốc độ gốc của video, có cách thoát rõ ràng |
| Lấy mẫu frame cách cuối video ≥ 1 giây | Số frame trong metadata (`CAP_PROP_FRAME_COUNT`) chỉ là ước lượng, nên frame cuối theo metadata có thể không đọc được |

## 3. Mở rộng nếu cần
- Ghi ra file video thay vì hiển thị: dùng `cv2.VideoWriter` với ảnh lưới 2×2 trong `play()`.
