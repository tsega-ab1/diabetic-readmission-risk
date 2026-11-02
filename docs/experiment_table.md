| Run | Stage | Selected | ROC-AUC | PR-AUC | Recall | Precision | F1 |
|---|---|---|---|---|---|---|---|
| LogisticRegression (baseline) | validation |  | 0.6670 | 0.2225 | 0.5466 | 0.1849 | 0.2763 |
| RandomForest | validation |  | 0.6643 | 0.2102 | 0.5221 | 0.1868 | 0.2752 |
| HistGradientBoosting (tuned) | validation |  | 0.6673 | 0.2270 | 0.5501 | 0.1806 | 0.2719 |
| XGBoost | validation |  | 0.6739 | 0.2332 | 0.5675 | 0.1868 | 0.2811 |
| LightGBM | validation | yes | 0.6743 | 0.2378 | 0.5262 | 0.1944 | 0.2839 |
| FINAL LightGBM (held-out test) | test | yes | 0.6856 | 0.2390 | 0.5289 | 0.2014 | 0.2917 |
