# ReefGuard-ML — Time-Aware Model Validation

## Method

Only the existing 2,201 training observations from 2005–2015 were used. Rows were sorted by calendar year; years were kept intact within each fold. Each fold uses an expanding training period followed by later validation years. All candidate models use the same validation rows in each fold. The validation-fold median and each imputer were fitted using that fold's training observations only.

The script does not read the 2016 test dataset. The 2016 results were inspected in earlier analyses and therefore should not be described as a completely untouched holdout.

## Folds and observation counts

| Fold | Training years (n) | Validation years (n) |
|---|---:|---:|
| Fold 1 | 2005–2009 (891) | 2010–2011 (524) |
| Fold 2 | 2005–2011 (1415) | 2012–2013 (335) |
| Fold 3 | 2005–2013 (1750) | 2014–2015 (451) |

## Candidate configurations

| Configuration | n_estimators | max_depth | min_samples_leaf |
|---|---:|---:|---:|
| RF-1 | 100 | None | 2 |
| RF-2 | 200 | None | 5 |
| RF-3 | 200 | 10 | 2 |
| RF-4 | 300 | 10 | 5 |

All Random Forests use `random_state=42`, `n_jobs=-1`, and the same `SimpleImputer(strategy="median")` → `RandomForestRegressor` pipeline. MAE is the primary selection metric.

## Aggregate comparison

Metrics below are arithmetic means of the three fold-level metrics; fold MAEs are shown individually. Positive MAE improvement means lower MAE than the baseline.

| Model/configuration | Mean MAE | Mean RMSE | Mean bias | Fold 1 MAE | Fold 2 MAE | Fold 3 MAE | Folds better than baseline | Mean MAE improvement vs baseline |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Median Baseline — Training-fold median | 13.9795 | 17.4603 | 8.9857 | 7.7939 | 5.9178 | 28.2266 | 0 | 0.0000 |
| Random Forest — RF-1 | 12.6196 | 15.9591 | 5.5034 | 8.5196 | 6.0151 | 23.3242 | 1 | 1.3598 |
| Random Forest — RF-2 | 12.6002 | 15.9845 | 5.7636 | 8.4173 | 5.9260 | 23.4574 | 1 | 1.3792 |
| Random Forest — RF-3 | 12.6318 | 15.9745 | 5.5446 | 8.5125 | 6.0684 | 23.3146 | 1 | 1.3476 |
| Random Forest — RF-4 | 12.6179 | 15.9884 | 5.7521 | 8.3904 | 6.0100 | 23.4532 | 1 | 1.3616 |

## Model selection

The best Random Forest by mean validation MAE was **RF-2** (12.6002), compared with the fold-median baseline at 13.9795.

It improved mean MAE by 1.3792 (9.9%), but beat the baseline in only 1 of 3 folds. Its mean advantage comes from Fold 3; its MAE was 0.6234 worse in Fold 1 and 0.0082 worse in Fold 2. Treat RF-2 as a candidate for independent validation, not as the selected model. Retain the median baseline as the current reference.

## Limitations and next step

- These are only three expanding-window folds within 2005–2015; the periods and sample sizes differ.
- This validation is useful for model comparison but does not prove future forecasting ability.
- The candidate set is deliberately small; results can vary with the particular historical periods.
- The existing 2016 results have already been examined and must not be treated as a pristine, untouched final test.

Keep the median baseline as the reference and gather an additional independent time period. If that is not available, revisit data quality and validation design before further model changes; do not treat the already inspected 2016 scores as an independent confirmation.
