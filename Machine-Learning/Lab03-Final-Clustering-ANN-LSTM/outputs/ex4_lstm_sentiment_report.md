# Bài 4 – Bi-LSTM Sentiment Classification

- Train / Validation / Test: 720 / 80 / 200
- Seed: 42 · Epoch đã chạy: 10/30 · Epoch tốt nhất: 5
- **F1-Score (Macro): 0.8499**

## Confusion Matrix [[TN, FP], [FN, TP]]

```
[[87 13]
 [17 83]]
```

## Classification Report

```
              precision    recall  f1-score   support

0 (Negative)       0.84      0.87      0.85       100
1 (Positive)       0.86      0.83      0.85       100

    accuracy                           0.85       200
   macro avg       0.85      0.85      0.85       200
weighted avg       0.85      0.85      0.85       200
```
