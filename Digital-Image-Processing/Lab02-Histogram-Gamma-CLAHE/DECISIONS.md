# Giải thích quyết định – DIP Lab 02

## 1. Đối chiếu đề bài → code
| Yêu cầu | Code |
|---|---|
| 1. Gamma: giống `Contrast_gamma.png` nhất + PSNR | Tìm γ cho PSNR lớn nhất → γ = 1.50, **PSNR = ∞** (MSE = 0) |
| 2a. Histogram `brain.jpg` | `cv2.calcHist` |
| 2b. Histogram Equalization | `cv2.equalizeHist` |
| 2c. AHE, ≥ 2 tùy chọn (window size / method) | 2 kích thước cửa sổ: `tileGridSize` 8×8 và 16×16 |
| 2d. CLAHE, ≥ 2 giá trị `clipLimit` | 3 giá trị: 2, 5, 10 |

## 2. Các quyết định & lý do
| Quyết định | Lý do |
|---|---|
| **Tối ưu PSNR** thay vì chọn γ bằng mắt | Đề muốn ảnh "giống ảnh tham chiếu nhất", và PSNR đo chính xác điều đó. Bài toán trở thành tìm γ cho PSNR lớn nhất |
| Quét **hai tầng**: thô (bước 0.1, khoảng 0.1–2.5) rồi mịn (bước 0.01 quanh điểm tốt nhất) | Quét thô nhanh, tìm đúng vùng. Quét mịn để không bỏ lỡ γ nằm giữa hai bước. Kết quả: tầng mịn vẫn chọn 1.50, xác nhận đây là giá trị đúng |
| Cài gamma bằng **LUT có làm tròn** (`np.round`, `cv2.LUT`) | Ảnh 8-bit chỉ có 256 mức, nên tính sẵn 256 giá trị rồi tra bảng sẽ nhanh hơn nhiều lần so với lũy thừa từng pixel. **Làm tròn** thay vì cắt phần thập phân: chính điều này giúp kết quả trùng khớp tuyệt đối (MSE = 0); nếu cắt (`np.uint8(x)`) thì vẫn lệch MSE ≈ 0.45 |
| γ = 1.5 (> 1) | Ảnh tham chiếu tối hơn và tương phản hơn ảnh gốc. γ > 1 kéo các mức xám trung bình xuống |
| PSNR tự cài `10·log10(255²/MSE)`, xử lý trường hợp MSE = 0 | Thể hiện hiểu công thức; MSE = 0 thì PSNR = ∞ (tránh chia cho 0) |
| **AHE = CLAHE với `clipLimit=40`** | OpenCV không có hàm AHE riêng. CLAHE với `clipLimit` rất lớn gần như không cắt histogram, tức tương đương AHE |
| 2c thay đổi `tileGridSize`, 2d thay đổi `clipLimit` | Mỗi câu **chỉ thay đổi một tham số** nên thấy rõ tác dụng của từng tham số |
| Ảnh xám cho phần 2 | Histogram equalization áp dụng trên 1 kênh độ sáng. Ảnh MRI vốn là ảnh xám |

## 3. Đọc kết quả
- **Gamma:** ảnh tham chiếu thực chất được tạo bằng đúng γ = 1.5, vì kết quả trùng từng pixel.
- **AHE (clipLimit 40):** nếp cuộn não rất rõ, nhưng **nền đen bị biến thành nhiễu dạng khối xám**. Đây là nhược điểm kinh điển của AHE: ô gần như đồng nhất cũng bị kéo giãn ra hết dải mức xám. Lưới 16×16 (ô nhỏ hơn) cho chi tiết cục bộ mạnh hơn 8×8, và nhiễu cũng nhiều hơn.
- **CLAHE:** `clipLimit` 2 cho kết quả tự nhiên nhất, nền vẫn đen. Tăng lên 5 rồi 10 thì tương phản tăng, nhiễu nền bắt đầu xuất hiện, tức tiến dần về AHE. Đây là minh chứng trực tiếp cho vai trò của `clipLimit`.

## 4. Ghi chú
Phần **Luyện tập thêm** ở cuối notebook là bài tập trên lớp (color space, log/gamma, histogram matching, nội suy ảnh), không thuộc yêu cầu của lab.
