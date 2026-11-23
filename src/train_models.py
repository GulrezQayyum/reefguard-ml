import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "modeling"
REPORT_DIR = PROJECT_ROOT / "reports"
MODEL_DIR = PROJECT_ROOT / "models"

TARGET = "Percent_Bleached"
FEATURES = [
    "Depth_m",
    "ClimSST",
    "Temperature_Mean",
    "SSTA",
    "SSTA_DHW",
    "TSA",
    "TSA_DHW",
    "Windspeed",
]


def metrics(actual, predicted):
    return {
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "R2": r2_score(actual, predicted),
        "Bias": float(np.mean(actual - predicted)),
    }


def format_metrics(values):
    return ", ".join(f"{name}={value:.6f}" for name, value in values.items())


def main():
    train = pd.read_csv(DATA_DIR / "train_v1.csv")
    test = pd.read_csv(DATA_DIR / "test_v1.csv")
    metadata = pd.read_csv(DATA_DIR / "split_metadata_v1.csv")

    missing_columns = [column for column in FEATURES + [TARGET] if column not in train.columns or column not in test.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    X_train = train[FEATURES]
    y_train = train[TARGET]
    X_test = test[FEATURES]
    y_test = test[TARGET]

    if len(train) == 0 or len(test) == 0:
        raise ValueError("Training and test sets must both be non-empty")
    if len(test) != 193:
        raise ValueError(f"Expected 193 test rows, found {len(test)}")

    median_baseline = float(y_train.median())
    median_predictions = np.full(len(y_test), median_baseline)

    linear_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", LinearRegression()),
    ])
    linear_pipeline.fit(X_train, y_train)
    linear_predictions = linear_pipeline.predict(X_test)

    forest_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("model", RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            min_samples_leaf=2,
            n_jobs=-1,
        ),),
    ])
    forest_pipeline.fit(X_train, y_train)
    forest_predictions = forest_pipeline.predict(X_test)

    prediction_arrays = {
        "Median baseline prediction": median_predictions,
        "Linear Regression prediction": linear_predictions,
        "Random Forest prediction": forest_predictions,
    }
    for name, predictions in prediction_arrays.items():
        if len(predictions) != len(test):
            raise AssertionError(f"Prediction length mismatch for {name}")
        if not np.isfinite(predictions).all():
            raise AssertionError(f"Non-finite prediction found for {name}")

    metric_rows = []
    for model_name, predictions in {
        "Median Baseline": median_predictions,
        "Linear Regression": linear_predictions,
        "Random Forest": forest_predictions,
    }.items():
        values = metrics(y_test.to_numpy(), predictions)
        metric_rows.append({
            "Model": model_name,
            "MAE": values["MAE"],
            "RMSE": values["RMSE"],
            "R2": values["R2"],
            "Bias": values["Bias"],
        })

    comparison = pd.DataFrame(metric_rows).sort_values("MAE", ascending=True).reset_index(drop=True)

    predictions_output = pd.DataFrame({
        "Actual Percent_Bleached": y_test,
        "Median baseline prediction": median_predictions,
        "Linear Regression prediction": linear_predictions,
        "Random Forest prediction": forest_predictions,
    })

    forest_model = forest_pipeline.named_steps["model"]
    importance = pd.DataFrame({
        "Feature": FEATURES,
        "Importance": forest_model.feature_importances_,
    }).sort_values("Importance", ascending=False).reset_index(drop=True)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    predictions_output.to_csv(DATA_DIR / "model_predictions_v1.csv", index=False)
    comparison.to_csv(REPORT_DIR / "model_comparison_v1.csv", index=False)
    importance.to_csv(REPORT_DIR / "random_forest_feature_importance_v1.csv", index=False)
    joblib.dump(linear_pipeline, MODEL_DIR / "linear_regression_v1.joblib")
    joblib.dump(forest_pipeline, MODEL_DIR / "random_forest_v1.joblib")

    baseline_row = comparison.loc[comparison["Model"] == "Median Baseline"].iloc[0]
    linear_row = comparison.loc[comparison["Model"] == "Linear Regression"].iloc[0]
    forest_row = comparison.loc[comparison["Model"] == "Random Forest"].iloc[0]
    best_row = comparison.iloc[0]

    train_metadata = metadata.loc[metadata["split"] == "train", "Date_Year"]
    test_metadata = metadata.loc[metadata["split"] == "test", "Date_Year"]
    train_year_range = f"{int(train_metadata.min())}–{int(train_metadata.max())}"
    test_year_range = f"{int(test_metadata.min())}–{int(test_metadata.max())}"

    ml_improved = (
        min(float(linear_row["MAE"]), float(forest_row["MAE"]))
        < float(baseline_row["MAE"])
    )

    report = f"""# ReefGuard-ML — First ML Model Training Report

## Models and features

- Median Baseline: training-target median ({median_baseline:.6f}), repeated for every test observation
- Linear Regression: scikit-learn `LinearRegression` with training-fitted median imputation
- Random Forest: scikit-learn `RandomForestRegressor` with `n_estimators=300`, `random_state=42`, `min_samples_leaf=2`, and `n_jobs=-1`, with training-fitted median imputation

Features:

"""
    report += "".join(f"- `{feature}`\n" for feature in FEATURES)

    report += f"""

Identifiers, dates, and outcome-derived fields were not used as predictors.

## Dataset sizes and temporal split

- Training observations: {len(train)}
- Test observations: {len(test)}
- Training year range: {train_year_range}
- Test year range: {test_year_range}
- Identical test observations were used for all three models.

## Evaluation results

| Model | MAE | RMSE | R² | Bias |
|---|---:|---:|---:|---:|
"""
    for _, row in comparison.iterrows():
        report += f"| {row['Model']} | {row['MAE']:.6f} | {row['RMSE']:.6f} | {row['R2']:.6f} | {row['Bias']:.6f} |\n"

    report += f"""

- The training-target median was **{median_baseline:.6f}**.
- Best model by MAE: **{best_row['Model']}** ({best_row['MAE']:.6f}).
- {'At least one ML model improved over the median baseline.' if ml_improved else 'Neither ML model improved over the median baseline.'}

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
"""

    with (REPORT_DIR / "model_training_report_v1.md").open("w", encoding="utf-8") as report_file:
        report_file.write(report)

    print("ReefGuard-ML first model comparison")
    print(f"Training rows: {len(train)}; test rows: {len(test)}")
    print(f"Training median: {median_baseline:.6f}")
    print(comparison.to_string(index=False, formatters={
        "MAE": lambda value: f"{value:.6f}",
        "RMSE": lambda value: f"{value:.6f}",
        "R2": lambda value: f"{value:.6f}",
        "Bias": lambda value: f"{value:.6f}",
    }))
    print(f"Best by MAE: {best_row['Model']} ({best_row['MAE']:.6f})")


if __name__ == "__main__":
    main()
