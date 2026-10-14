# DECISIONS – Final Project v2

Vì sao bản làm lại (`notebook-v2/`) chọn cách làm như vậy, và vì sao khác bản đã nộp (`notebook-v1/`).

## 1. Ý nghĩa của tiền két và chỉ số `cash_flow_gap`
**Quyết định:** coi `actual_cash_in_drawer` là **tổng tiền trong két** và dùng `gap = két_t − (két_lần_đếm_trước + tiền_mặt_bán_t)`.

**Căn cứ:**
- Tác giả hệ thống POS xác nhận: cột này là tổng tiền đếm trong két, và **không có nơi nào ghi tiền rút/nạp**.
- Dữ liệu xác nhận: két lớn gần 3 lần tiền mặt bán trong ca, tương quan chỉ r = 0,13; với các ca chiều, `két_chiều ≈ két_sáng + tiền mặt chiều` ở những ngày không rút tiền giữa ca.
- Thử giả thuyết "tiền rút là số tròn 50k/100k, phần lẻ còn lại là sai lệch thật": phần lẻ phân bố đều nên giả thuyết bị bác bỏ, không tách được tiền rút khỏi sai lệch.

**Hệ quả:** `gap < 0` không thể kết luận là thất thoát; chỉ `gap > 0` (tiền vào không có hóa đơn) là tín hiệu có căn cứ.

## 2. Làm sạch dữ liệu
| Vấn đề | Cách xử lý | Lý do |
|---|---|---|
| Tiền két 480–1.270 đ (5 ca) | Nhân 1000, gắn cờ DQ1 | Rõ ràng gõ theo đơn vị nghìn; sau khi sửa rơi vào phân vị 1–58% của phân phối két |
| Dòng mở ca ghi 0 đ (3 dòng) | Bỏ khi tìm lần đếm trước | Ca trước vừa chốt 550k–840k, nên 0 nghĩa là "không đếm" |
| Dòng mở ca trùng số ca trước (2 dòng) | Giữ (không ảnh hưởng) | Cùng giá trị nên `gap` không đổi |
| `is_morning_shift` sai (2 ca) | Suy nhãn ca từ giờ chốt (< 14h là sáng), gắn cờ DQ2 | Giờ chốt tách 2 cụm rõ (11–12h và 17–18h) |
| Sai số đếm két | `TOL = 10.000 đ` | ~98% số tiền két là bội số 10.000 đ |

## 3. Đối soát hóa đơn – chốt ca
Khớp 100% vì POS tính số chốt ca từ hóa đơn. **Không dùng làm feature** (`Payment_Mismatch` của v1 luôn bằng 0) và ghi rõ đây không phải kiểm tra độc lập.

## 4. Mô hình thói quen rút tiền (Vòng 2)
- **Huber regression** `két ~ két_kỳ_vọng + qua_đêm` thay vì OLS: các ca bất thường không kéo lệch đường hồi quy.
- **Robust z = (phần dư − trung vị) / (1,4826 · MAD)**, ngưỡng |z| > 3 (tương đương ~3 độ lệch chuẩn nếu phân phối chuẩn).
- Kết quả: hệ số 0,515 (rút khoảng một nửa phần tăng thêm), MAD ≈ 435k → lượng rút quá thất thường, chỉ 1 ca vượt ngưỡng. Ghi rõ giới hạn này thay vì hạ ngưỡng để "có nhiều cảnh báo hơn".

## 5. Isolation Forest chỉ là ý kiến thứ hai
Chạy 20 seed, lấy ca bị đánh dấu ở ≥ 50% số seed. 13 ca bị đánh dấu chủ yếu là ca đông khách (két kỳ vọng cao rồi rút mạnh), chỉ 1 ca trùng mô hình thói quen. **Không dùng làm luật** vì không có diễn giải nghiệp vụ.

## 6. Phân cụm (Vòng 2)
- Biến: log doanh thu, số bill, tỉ lệ tiền mặt, giá trị bill trung bình. **Bỏ** `Payment_Mismatch` (hằng số) và các biến dòng tiền két (chứa tiền rút không ghi nhận, sẽ làm cụm phản ánh hành vi rút tiền của chủ quán).
- Chọn k: trong các k có **ARI bootstrap ≥ 0,75** và cụm nhỏ nhất ≥ 10 ca, lấy k có Silhouette cao nhất → k = 5 (k = 4 của v1 chỉ ổn định 0,69).
- Silhouette ≈ 0,30 ở mọi k → ghi rõ cấu trúc yếu, chỉ dùng để mô tả.

## 7. Gom tên khách (Vòng 3)
- Chuẩn hóa: bỏ dấu, tách phần ghi chú tiền, `n9 → ng`, bỏ danh xưng (c, a, chú, cô, bố, bạn, ông…) và hậu tố chung (`pt`, `nu`).
- Khoảng cách `1 − SequenceMatcher.ratio()`, liên kết average, cắt ở **t = 0,4** (độ giống ≥ 0,6, mặc định của `difflib.get_close_matches`). Đã thử tiêu chí "đoạn phẳng dài nhất" nhưng đường số nhóm có nhiều đoạn phẳng ngắn ngang nhau, chọn ra t = 0,2 với 16 nhóm (tách nhầm cùng một khách).
- Kiểm chứng: ARI 0,99 so với bảng gom tay của v1; ổn định khi t ∈ [0,35; 0,45].
- **Ẩn danh** ngay sau khi gom; file đầu ra và output notebook không chứa tên/ghi chú gốc.

## 8. Thói quen thanh toán
Chỉ xét khách ≥ 5 đơn, và chỉ coi là "lệch phương thức" khi thói quen ≥ 80%. v1 gắn cờ cả khách trả 63/37 nên báo động giả nhiều (21 đơn → 12 đơn ở v2).

## 9. Rule Engine (Vòng 4)
- **Lỗi dữ liệu tách khỏi cảnh báo nghiệp vụ**: ca gõ sai đơn vị không còn bị gọi là "thất thoát".
- **F1 > 100.000 đ là mức Cao**: tiền vào nhỏ (trung vị 34k) có thể là đơn lẻ chưa nhập hoặc làm tròn khi đếm; từ 100k trở lên là khoản khó giải thích. Bảng độ nhạy: 50k → 17 ca, 100k → 10, 200k → 4.
- Không có luật "tiền ra lớn = thất thoát" vì không có căn cứ (mục 1).

## 10. Đối chiếu đề → code
| Câu hỏi | Trả lời trong v2 |
|---|---|
| Phát hiện ca bất thường bằng phương pháp không giám sát | Vòng 2: Huber + robust z, Isolation Forest, K-Means có kiểm tra ổn định |
| Nhận diện khách quen từ ghi chú viết tắt | Vòng 3: chuẩn hóa + phân cụm phân cấp, ARI 0,99 so với gom tay |
| Rule Engine không cần LLM | Vòng 4: 7 luật, báo cáo f-string theo ca và theo tháng |

## 11. Điểm cần lưu ý khi ôn
- Kết quả "đẹp" của v1 (11 ca thất thoát, 4 cụm rõ nghĩa) đến từ một công thức sai và lỗi nhập liệu chưa làm sạch. Luôn tự hỏi *"con số này có hợp lý ngoài đời không?"* trước khi diễn giải.
- 6/10 ca mức Cao là ca sáng: có thể chỉ là chủ quán nạp tiền lẻ đầu ngày. Cảnh báo ≠ kết luận.
