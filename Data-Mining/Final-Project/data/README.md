# Dữ liệu – Final Project

Dữ liệu vận hành thật của một quán F&B (hệ thống POS do tác giả tự viết), 20/12/2025 – 30/04/2026. Có ghi chú tên khách nên **không đưa lên GitHub**. Mô tả chi tiết từng cột có trong `docs/Data Dictionary Document.pdf`.

```
data/
├── raw/                         # đầu vào duy nhất cần có
│   ├── MainLog.csv              # 242 dòng – 236 lần chốt ca + 6 lần mở ca
│   └── DetailsTransaction.csv   # 5 412 hóa đơn
├── processed_v2/                # do notebook-v2/ sinh ra
│   ├── shifts_v2.csv            # Vòng 1 – 236 ca, tiền két đã sửa lỗi đơn vị, cash_flow_gap
│   ├── bills_v2.csv             # Vòng 1 – hóa đơn kèm shift_id (còn ghi chú gốc)
│   ├── shifts_scored_v2.csv     # Vòng 2 – thêm habit_z, Isolation Forest, cluster
│   ├── customer_txn_v2.csv      # Vòng 3 – 101 đơn có ghi chú, chỉ có mã khách KHxx
│   └── rule_report_v2.csv       # Vòng 4 – mức cảnh báo, luật, báo cáo text từng ca
└── processed/                   # do notebook-v1/ sinh ra (bản đã nộp)
    ├── Audit_Merged_Data.csv
    ├── Clustered_Shifts.csv
    ├── Customer_Pattern.csv
    ├── Rule_Engine_Report.csv
    └── POS_Master.csv           # bảng tổng hợp 34 cột, không do 4 notebook sinh ra
```

| File | Cột |
|---|---|
| `MainLog.csv` | `timestamp`, `total_revenue`, `transfer_amount`, `cash_amount`, `is_morning_shift`, `actual_cash_in_drawer` |
| `DetailsTransaction.csv` | `transaction_at`, `total_revenue`, `transfer_payment`, `cash_payment`, `notes` |

Lưu ý khi dùng:
- Thời gian dạng `M/D/YYYY H:MM:SS`.
- `actual_cash_in_drawer` là **tổng tiền đếm trong két** (gồm tiền tồn), đếm tròn 10.000 đ; 5 ca bị gõ theo đơn vị nghìn (< 10.000 đ).
- Dòng mở ca có `total_revenue = 0`; 3 dòng ghi két = 0 nghĩa là không đếm.
- Không có dữ liệu tiền rút/nạp két.
