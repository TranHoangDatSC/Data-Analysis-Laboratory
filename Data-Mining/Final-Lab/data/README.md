# Dữ liệu – Final Lab

Dataset quá lớn nên không đưa lên repo. Các notebook **tự tải dữ liệu khi chạy** (khuyến nghị Google Colab), không cần đặt file vào thư mục này.

| Phần | Dataset | Nguồn | Cách notebook tải |
|---|---|---|---|
| 1 | Fashion-MNIST | Keras | `tensorflow.keras.datasets.fashion_mnist.load_data()` |
| 1 | New Plant Diseases Dataset (~2.7 GB) | [Kaggle](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) | `kaggle datasets download -d vipoooool/new-plant-diseases-dataset --unzip` |
| 2 | Credit Card Fraud Detection (`creditcard.csv`, 66 MB zip) | [Kaggle](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud) | `kaggle datasets download -d mlg-ulb/creditcardfraud --unzip` |
| 3 | IMDB Dataset of 50K Movie Reviews | [Kaggle](https://www.kaggle.com/datasets/lakshmi25npathi/imdb-dataset-of-50k-movie-reviews) | `kagglehub.dataset_download(...)`, lấy 1 000 dòng đầu |
| 4 | AAPL 02/01/2019 – 31/12/2020 | Yahoo Finance ([bản tham khảo trên Kaggle](https://www.kaggle.com/datasets/khoongweihao/aaplcsv)) | `yfinance.download("AAPL", start="2019-01-01", end="2021-01-01")` |

Phần 1 và 2 cần Kaggle API key (`kaggle.json`), xem mục **Chạy** trong [README](../README.md#chạy).
