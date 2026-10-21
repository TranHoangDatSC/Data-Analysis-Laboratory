# Dữ liệu – NLP Final Project

| File | Dùng ở | Nguồn |
|---|---|---|
| `restaurants_train_sb1.xml`, `restaurants_test_sb1.xml` | `03_model_gru_bilstm_res16.ipynb` | SemEval-2016 Task 5 (Subtask 1, Restaurant), bản trên Kaggle: [fouadaurag20/semeval-2016-absa-task5](https://www.kaggle.com/datasets/fouadaurag20/semeval-2016-absa-task5) |
| `restaurants_train_sb1.csv`, `restaurants_test_sb1.csv` | `01_eda_res16.ipynb` | Cùng dữ liệu Res16 nhưng ở dạng CSV "wide" (mỗi hàng là một review, cột dạng `sentences/sentence/{i}/text`), chuyển từ XML; notebook không ghi nguồn bản CSV này |
| `AWARE_Social_Networking.csv` | `02_eda_aware.ipynb` | AWARE: ABSA Warehouse of App REviews (Alturaief et al., 2021), miền ứng dụng mạng xã hội, 3 118 opinion |

Đặt các file vào thư mục này. Notebook 03 khi chạy trên Kaggle sẽ đọc thẳng từ `/kaggle/input/...`.
