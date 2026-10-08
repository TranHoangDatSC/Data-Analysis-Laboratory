# Kết quả phân loại Dry Bean

|               |   F1-Score (Weighted) |   AUC (OvR) |
|:--------------|----------------------:|------------:|
| KNN           |                0.9030 |      0.9755 |
| Decision Tree |                0.8810 |      0.9807 |
| AdaBoost      |                0.8802 |      0.9701 |
| Naive Bayes   |                0.8737 |      0.9870 |

## KNN

```
          BARBUNYA  BOMBAY  CALI  DERMASON  HOROZ  SEKER  SIRA
BARBUNYA       224       0    27         0      2      3     9
BOMBAY           0     104     0         0      0      0     0
CALI            15       0   302         0      5      2     2
DERMASON         0       0     0       642      0     15    52
HOROZ            1       0     5         4    362      1    13
SEKER            1       0     0         9      0    386    10
SIRA             2       0     1        69      5     11   439
```

## Naive Bayes

```
          BARBUNYA  BOMBAY  CALI  DERMASON  HOROZ  SEKER  SIRA
BARBUNYA       181       0    67         0      4      1    12
BOMBAY           0     104     0         0      0      0     0
CALI            30       0   287         0      8      1     0
DERMASON         0       0     0       613      0     23    73
HOROZ            1       0     5         7    360      0    13
SEKER            4       0     0         4      0    380    18
SIRA             8       0     0        37     15     12   455
```

## Decision Tree

```
          BARBUNYA  BOMBAY  CALI  DERMASON  HOROZ  SEKER  SIRA
BARBUNYA       172       0    65         0     15      3    10
BOMBAY           0     104     0         0      0      0     0
CALI            21       0   291         0     11      2     1
DERMASON         0       0     0       653      0     15    41
HOROZ            0       0     6         7    364      0     9
SEKER            2       0     0         8      0    381    15
SIRA             0       0     0        66     11     11   439
```

## AdaBoost

```
          BARBUNYA  BOMBAY  CALI  DERMASON  HOROZ  SEKER  SIRA
BARBUNYA       201       0    50         0      2      1    11
BOMBAY           0     104     0         0      0      0     0
CALI            50       0   266         0      5      2     3
DERMASON         0       0     0       648      0     14    47
HOROZ            3       0     7         6    359      0    11
SEKER            1       0     0        10      0    376    19
SIRA             2       0     2        60      8     12   443
```

