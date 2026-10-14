# Giải thích quyết định – DIP Lab 03

## 1. Đối chiếu đề bài → code
| Yêu cầu | Code | PSNR |
|---|---|---|
| 1. Denoise, ≥ 2 bộ lọc trong gợi ý | Median + Bilateral | 32.73 / 32.28 dB |
| 2. Sharpen: Unsharp + 1 bộ lọc khác | Unsharp masking + Laplacian | 45.81 / 43.48 dB (kèm độ đo độ nét) |
| 3. Frequency filtering (band stop) | Gaussian notch reject trong miền FFT | 31.96 dB |

## 2. Bài 1 – Khử nhiễu
| Quyết định | Lý do (đã kiểm chứng) |
|---|---|
| Median kernel 5 | k = 3 / **5** / 7 cho PSNR 30.92 / **32.73** / 30.82 dB. Kernel nhỏ khử chưa sạch, kernel lớn làm mờ chi tiết |
| Bilateral `d=9, σ_color=300, σ_space=50` | σ_color = 75 / 150 / **300** cho 22.44 / 27.15 / **32.28** dB. Nhiễu có biên độ lớn, nên σ_color phải lớn thì pixel nhiễu mới được coi là "giống" pixel xung quanh và được làm mượt |
| Không dùng Non-local Means | Đề chỉ cần 2 bộ lọc. NLM chậm hơn nhiều |

## 3. Bài 2 – Làm nét
**Phát hiện quan trọng về ảnh chuẩn:** `cat_sharpened.jpg` gần như **giống hệt** ảnh mờ đầu vào:

| So sánh | Giá trị |
|---|---|
| PSNR(ảnh mờ, ảnh chuẩn) | **51.75 dB** (chênh lệch tối đa chỉ 5 mức xám) |
| Độ nét ảnh mờ (phương sai Laplacian) | 4.4 |
| Độ nét ảnh "chuẩn" | **3.6** (còn kém nét hơn ảnh mờ) |

Hệ quả: **làm nét càng mạnh thì PSNR càng giảm**. PSNR cao nhất đạt được khi... không làm gì. Vì vậy bài này **không chọn tham số bằng PSNR** như Lab02, mà làm như sau:

| Quyết định | Lý do |
|---|---|
| Dùng **tham số kinh điển**: unsharp σ = 1, amount = 1; Laplacian amount = 1 | Mức làm nét tiêu chuẩn trong giáo trình, không bị "chỉnh" theo một ảnh chuẩn có vấn đề |
| Vẫn báo PSNR | Đề yêu cầu |
| Thêm **độ nét = phương sai Laplacian** (không cần ảnh tham chiếu) | Chứng minh ảnh thực sự nét hơn: 4.4 → 15.4 (unsharp) và 63.8 (Laplacian) |
| Unsharp tính bằng **float**: `img + amount·(img − blur)` | Hiệu `img − blur` có cả giá trị âm (phía tối của mép). Nếu trừ trên `uint8` (`cv2.subtract`), phần âm bị cắt về 0 và mép chỉ được làm sáng mà không được làm tối, tức chỉ làm nét được "một nửa" |
| Laplacian 4-connected, **trừ** Laplacian | Kernel có tâm dương (+4) nên `sharp = img − ∇²img` |
| `np.clip(0, 255)` trước khi đổi sang `uint8` | Tránh tràn số |

Đọc kết quả: Laplacian làm nét mạnh hơn unsharp nhiều (63.8 so với 15.4), nhưng phóng to sẽ thấy các vùng phẳng bị nổi hạt nhiễu mịn. Laplacian là bộ lọc thông cao thuần túy nên khuếch đại mọi biến thiên nhỏ. Unsharp chỉ cộng thêm phần chi tiết đã qua Gaussian nên cho ảnh tự nhiên hơn.

## 4. Bài 3 – Lọc miền tần số
| Quyết định | Lý do (đã kiểm chứng) |
|---|---|
| `fft2` → `fftshift` | Dời tần số 0 về giữa để dễ xác định vị trí nhiễu |
| Chặn **2 điểm đối xứng** tại (tâm, tâm ± 25) | Các đỉnh mạnh nhất của phổ `xray_noisy.jpg` (bỏ vùng tâm) nằm đúng tại **(±25, 0)**, tức trên trục dọc, cách tâm 25 → D0 = 25 |
| **Notch reject** thay vì band-reject cả vòng | Nhiễu chỉ tập trung ở 2 điểm. Chặn cả vòng bán kính 25 sẽ xóa luôn thông tin hữu ích ở mọi hướng khác |
| Dạng **Gaussian** `1 − exp(−D²/2W²)`, W = 5 | Ideal cắt "cứng" gây gợn sóng (ringing). W = 3 / **5** / 8 cho 30.61 / **31.96** / 28.50 dB |
| Nhân 2 mặt nạ `H = H1·H2` | Mỗi mặt nạ chặn một điểm, nhân lại để chặn cả hai |
| Đưa về 0–255 bằng **min-max** (`cv2.normalize`) | Min-max cho 31.96 dB, còn cắt thẳng (`clip`) chỉ 24.41 dB. Dải sáng của ảnh chuẩn khớp với kiểu kéo giãn min-max hơn |

Kết quả: PSNR tăng từ **19.77 dB** (ảnh nhiễu) lên **31.96 dB**.
