# ReefGuard-ML — Prediction Error Analysis

## Scope and method

Analysis uses the existing 193 test prediction rows only. No models were retrained, predictions changed, or training decisions made from these test results.
Prediction error is defined as `actual - predicted`: a negative error is an overestimate, a positive error is an underestimate, and zero is an exact prediction. Absolute error is `|actual - predicted|`.
The prediction file contains no sample identifier. `Test row` below is the 1-based row position in the existing prediction CSV, not an identifier and not a claim about a specific site.

## Overall error summary

| Model | Mean absolute error | Median absolute error | Overestimates | Underestimates | Exact | Largest absolute error |
|---|---:|---:|---:|---:|---:|---:|
| Median Baseline | 7.3684 | 6.4100 | 96 | 96 | 1 | 67.5200 |
| Linear Regression | 9.0416 | 7.9735 | 137 | 56 | 0 | 58.5870 |
| Random Forest | 9.7521 | 7.7027 | 127 | 66 | 0 | 58.9994 |

The model with the highest mean absolute error was **Random Forest** (9.7521). The single largest absolute error occurred for **Median Baseline** (67.5200). These summarize different aspects of error; the existing overall comparison also ranks the baseline best by MAE.

## Error by observed bleaching range

Ranges are mutually exclusive: low includes 0 and 10; moderate is greater than 10 through 30; high is greater than 30 through 100. Counts refer to actual observed target values.

| Observed bleaching range | Observations | Median Baseline MAE | Linear Regression MAE | Random Forest MAE |
|---|---:|---:|---:|---:|
| Low (0–10%) | 94 | 6.1827 | 11.9829 | 12.1818 |
| Moderate (>10–30%) | 93 | 6.8391 | 4.8629 | 6.0942 |
| High (>30–100%) | 6 | 34.1500 | 27.7303 | 28.3837 |

Across the three models, the highest average group MAE was in **High (>30–100%)** (unweighted mean of the three within-range MAEs: 30.0880). Group MAEs describe errors on these test observations only; they do not explain why errors occurred.

## Ten largest absolute errors per model

Rows are ranked by absolute error within each model.

### Median Baseline

| Rank | Test row | Actual | Predicted | Error (actual − predicted) | Absolute error |
|---:|---:|---:|---:|---:|---:|
| 1 | 106 | 77.7800 | 10.2600 | 67.5200 | 67.5200 |
| 2 | 77 | 50.0000 | 10.2600 | 39.7400 | 39.7400 |
| 3 | 42 | 41.6700 | 10.2600 | 31.4100 | 31.4100 |
| 4 | 123 | 33.3300 | 10.2600 | 23.0700 | 23.0700 |
| 5 | 84 | 32.4300 | 10.2600 | 22.1700 | 22.1700 |
| 6 | 148 | 31.2500 | 10.2600 | 20.9900 | 20.9900 |
| 7 | 133 | 29.5800 | 10.2600 | 19.3200 | 19.3200 |
| 8 | 126 | 28.5700 | 10.2600 | 18.3100 | 18.3100 |
| 9 | 131 | 27.7800 | 10.2600 | 17.5200 | 17.5200 |
| 10 | 80 | 27.1900 | 10.2600 | 16.9300 | 16.9300 |

### Linear Regression

| Rank | Test row | Actual | Predicted | Error (actual − predicted) | Absolute error |
|---:|---:|---:|---:|---:|---:|
| 1 | 106 | 77.7800 | 19.1930 | 58.5870 | 58.5870 |
| 2 | 77 | 50.0000 | 14.8296 | 35.1704 | 35.1704 |
| 3 | 95 | 0.0000 | 28.5577 | -28.5577 | 28.5577 |
| 4 | 66 | 1.1200 | 29.5979 | -28.4779 | 28.4779 |
| 5 | 97 | 2.8000 | 29.2592 | -26.4592 | 26.4592 |
| 6 | 42 | 41.6700 | 16.3740 | 25.2960 | 25.2960 |
| 7 | 183 | 7.5300 | 29.7713 | -22.2413 | 22.2413 |
| 8 | 5 | 0.0000 | 21.2592 | -21.2592 | 21.2592 |
| 9 | 127 | 0.0000 | 20.5504 | -20.5504 | 20.5504 |
| 10 | 118 | 9.2300 | 29.6324 | -20.4024 | 20.4024 |

### Random Forest

| Rank | Test row | Actual | Predicted | Error (actual − predicted) | Absolute error |
|---:|---:|---:|---:|---:|---:|
| 1 | 106 | 77.7800 | 18.7806 | 58.9994 | 58.9994 |
| 2 | 77 | 50.0000 | 10.2167 | 39.7833 | 39.7833 |
| 3 | 141 | 0.0000 | 39.4950 | -39.4950 | 39.4950 |
| 4 | 161 | 0.0000 | 39.0044 | -39.0044 | 39.0044 |
| 5 | 163 | 4.1700 | 42.1057 | -37.9357 | 37.9357 |
| 6 | 143 | 4.7600 | 38.0625 | -33.3025 | 33.3025 |
| 7 | 145 | 7.4100 | 39.7406 | -32.3306 | 32.3306 |
| 8 | 182 | 1.6900 | 33.6336 | -31.9436 | 31.9436 |
| 9 | 162 | 5.4900 | 36.9862 | -31.4962 | 31.4962 |
| 10 | 142 | 7.5200 | 38.7227 | -31.2027 | 31.2027 |

## Random Forest feature importance

The three highest features in the existing importance file are:

- `TSA_DHW`: 0.3101
- `TSA`: 0.1303
- `SSTA_DHW`: 0.1250

This importance score describes how the fitted Random Forest used features for its predictions (the provided values are normalized tree-based importance scores). It does not show that a feature causes bleaching, nor does it by itself establish scientific or practical importance. Correlated predictors can share or distort importance, and the scores depend on this fitted model and dataset.

## Interpretation and next step

The error analysis confirms the first comparison: the median baseline remains the strongest of these three by overall MAE, while both ML models have larger overall mean absolute errors. Errors differ by observed bleaching range, and some individual test rows have much larger errors than the averages. These are descriptive findings from one 2016 temporal test set, with no causal interpretation.

A sensible next step is to review the largest-error rows and input data quality with domain context, then design a separate validation strategy or additional held-out period before considering any training changes. Keep this 2016 test set untouched for unbiased reporting; do not tune against these error patterns.

## Output

- Detailed summary CSV: `reports/prediction_error_summary_v1.csv` (overall model summaries, bleaching-range summaries, and each model’s ten largest absolute errors).
