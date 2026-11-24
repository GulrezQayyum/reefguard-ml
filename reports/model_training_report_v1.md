# ReefGuard-ML — First ML Model Training Report

## Models and features

- Median Baseline: training-target median (10.260000), repeated for every test observation
- Linear Regression: scikit-learn `LinearRegression` with training-fitted median imputation
- Random Forest: scikit-learn `RandomForestRegressor` with `n_estimators=300`, `random_state=42`, `min_samples_leaf=2`, and `n_jobs=-1`, with training-fitted median imputation

Features:

- `Depth_m`
- `ClimSST`
- `Temperature_Mean`
- `SSTA`
- `SSTA_DHW`
- `TSA`
- `TSA_DHW`
- `Windspeed`


Identifiers, dates, and outcome-derived fields were not used as predictors.

## Dataset sizes and temporal split

- Training observations: 2201
- Test observations: 193
- Training year range: 2005–2015
- Test year range: 2016–2016
- Identical test observations were used for all three models.

## Evaluation results

| Model | MAE | RMSE | R² | Bias |
|---|---:|---:|---:|---:|
| Median Baseline | 7.368446 | 10.072642 | -0.018123 | 1.343886 |
| Linear Regression | 9.041619 | 11.435854 | -0.312353 | -4.702714 |
| Random Forest | 9.752122 | 13.191134 | -0.746135 | -3.965381 |


- The training-target median was **10.260000**.
- Best model by MAE: **Median Baseline** (7.368446).
- Neither ML model improved over the median baseline.

Bias is defined as `mean(actual - predicted)`. Positive bias means underprediction on average; negative bias means overprediction on average.

## Random Forest feature importance

Feature importance was saved to `reports/random_forest_feature_importance_v1.csv`. Feature importance describes how the fitted model uses features; it does not establish that a feature causes coral bleaching.

## Outputs and limitations

- Predictions: `data/modeling/model_predictions_v1.csv`
- Comparison: `reports/model_comparison_v1.csv`
- Trained Linear Regression pipeline: `models/linear_regression_v1.joblib`
- Trained Random Forest pipeline: `models/random_forest_v1.joblib`

Important limitations:

- This is an observational, temporal-prototype comparison, not a future-forecasting or causal system.
- The test split repeats 22 sites from the training period, so observations are not fully independent across time.
- `ClimSST = 262.15` has an unresolved data-quality interpretation and remains in the dataset.
- Environmental units and temporal windows require further scientific documentation.
- No hyperparameter tuning was performed.
- A positive R² should not be considered success in isolation; the models should be compared directly with the median baseline on the same test rows.
e