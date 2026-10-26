# Giải thích quyết định – DIP Lab 04 (Final)

## 1. Đối chiếu đề bài → code
| Bước trong đề | Code (notebook) |
|---|---|
| 1. Gray → Binary (Otsu) | `_otsu_threshold_scratch`, **tự cài** |
| 2. QR detector → `qrcode_mask` | `cv2.QRCodeDetector().detect()` + padding 5 px |
| 3. Xóa QR khỏi binary | `cv2.subtract(binary, qrcode_mask)` |
| 4. Tách photo bằng morphology (SE, `morphologyEx`, `findContours`) | `_get_structuring_element_scratch`, `_morphology_ex_closing_scratch`, `_find_contours_scratch`, đều **tự cài** |
| 5. Tách text = binary − photo − QR | `cv2.subtract(binary_no_qr, photo_mask)` |
| 6. Vẽ bounding box | `_draw_bbox_with_text`: TITLE / PHOTO / TEXT / QR CODE |
| "Try to do better" so với `reference_output.png` | Tách riêng vùng **TITLE**, thêm 4 ảnh tách riêng từng vùng (text, text + title, photo, QR) |

## 2. Các quyết định & lý do
| Quyết định | Lý do |
|---|---|
| **Tự cài** Otsu, dilate/erode, closing, contour (BFS), bounding rect | Thể hiện hiểu thuật toán thay vì chỉ gọi hàm. Đánh đổi: chạy ~1 phút vì dùng vòng lặp Python |
| Binary **đảo**: pixel ≤ ngưỡng → 255 | Chữ và ảnh tối trên nền sáng. Đảo lại để chúng thành **vùng trắng (foreground)**, vì morphology và tìm contour đều làm việc trên vùng trắng |
| `detect()` thay vì `detectAndDecode()` | Chỉ cần **vị trí** QR, không cần đọc nội dung |
| Padding 5 px quanh QR | Nới rộng vùng xóa để mép QR không sót lại trong ảnh nhị phân |
| Trừ mask bằng **`cv2.subtract`** (bão hòa) | Với `uint8`, `cv2.subtract` cho `0 − 255 = 0`. Nếu dùng `np.subtract` thì phép trừ tràn vòng: `0 − 255 = 1`, để lại pixel "gần trắng" (254 sau khi đảo màu) trong vùng QR ở ảnh text-only |
| **Closing 15×15** để tìm photo | Ảnh tô canh gồm nhiều mảng rời nhau, closing (dilate rồi erode) gộp thành một khối liền. Như đề nhấn mạnh, **kích thước SE là then chốt**: quá nhỏ thì không gộp được, quá lớn thì gộp luôn cả chữ bên cạnh |
| Chọn contour **lớn nhất**, diện tích > 1 % ảnh, nằm dưới 15 % chiều cao | Ảnh là khối lớn nhất trang. Điều kiện vị trí loại tiêu đề chữ to ở đầu trang |
| Phân TITLE / CONTENT theo **vị trí so với photo** | Ở bố cục này, tiêu đề nằm **trên** ảnh, nội dung nằm **dưới** ảnh |
| Ảnh "photo only": SE **ngang 40×3** + lọc tỉ lệ rộng/cao > 3 để tìm dòng chữ → trừ đi → lấy khối lớn nhất → closing 50×50 để lấp kín | SE ngang nối các ký tự trong cùng dòng thành thanh dài. Dòng chữ thì dài và thấp, còn ảnh thì không, nên phân biệt được |
| Bỏ contour diện tích < 50–100 px | Loại đốm nhiễu nhỏ |

## 3. Giới hạn
- Cách tách TITLE/CONTENT theo vị trí photo là **heuristic theo bố cục** của `document.png`. Tài liệu có bố cục khác (ảnh ở cuối, nhiều cột…) cần quy tắc khác, ví dụ dựa vào chiều cao chữ (tiêu đề chữ to hơn).
- Các thuật toán tự cài chạy chậm (~1 phút). Thay bằng `cv2.threshold(..., THRESH_OTSU)`, `cv2.morphologyEx`, `cv2.findContours` sẽ cho kết quả tương đương trong vài mili-giây.
- Hàm Otsu tự cài tối đa hóa phương sai giữa lớp `ω0·ω1·(μ0 − μ1)²`. Kiểm chứng: so với `cv2.threshold(gray, 0, 255, THRESH_BINARY_INV + THRESH_OTSU)` thì cùng ngưỡng **151**, **0 / 527 177** pixel khác nhau.
