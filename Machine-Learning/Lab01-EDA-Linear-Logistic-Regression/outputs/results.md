# Kết quả ML Lab 01

| Bài | Chỉ số | Giá trị |
|---|---|---|
| Linear Regression | RMSE (test) | 11,943.48 |
| Logistic Regression | F1 (test) | 0.7451 |
| Logistic Regression | F1 (5-fold CV trên train) | 0.7589 ± 0.0727 |

Confusion Matrix Logistic Regression `[[TN, FP], [FN, TP]]`:

```
[[48  3]
 [10 19]]
```

Hệ số Linear Regression (feature đã chuẩn hóa):

|                 |     Hệ số |
|:----------------|----------:|
| R&D Spend       | 31,186.25 |
| Administration  |  2,046.26 |
| Marketing Spend | 11,230.15 |
