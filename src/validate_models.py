from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "modeling"
REPORT_DIR = PROJECT_ROOT / "reports"

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

FOLDS = [
    {"name": "Fold 1", "train_end": 2009, "validation_start": 2010, "validation_end": 2011},
    {"name": "Fold 2", "train_end": 2011, "validation_start": 2012, "validation_end": 2013},
    {"name": "Fold 3", "train_end": 2013, "validation_start": 2014, "validation_end": 2015},
]

CONFIGURATIONS = [
    {"name": "RF-1", "n_estimators": 100, "max_depth": None, "min_samples_leaf": 2},
    {"name": "RF-2", "n_estimators": 200, "max_depth": None, "min_samples_leaf": 5},
    {"name": "RF-3", "n_estimators": 200, "max_depth": 10, "min_samples_leaf": 2},
    {"name": "RF-4", "n_estimators": 300, "max_depth": 10, "min_samples_leaf": 5},
]


def calculate_metrics(actual, predicted):
    return {
        "MAE": mean_absolute_error(actual, predicted),
        "RMSE": np.sqrt(mean_squared_error(actual, predicted)),
        "Bias": float(np.mean(actual - predicted)),
    }


def build_pipeline(configuration):
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=configuration["n_estimators"],
                    max_depth=configuration["max_depth"],
                    min_samples_leaf=configuration["min_samples_leaf"],
                    random_state=42,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def main():
    train = pd.read_csv(DATA_DIR / "train_v1.csv")
    metadata = pd.read_csv(DATA_DIR / "split_metadata_v1.csv")

    required_features = FEATURES + [TARGET]
    missing_columns = [column for column in required_features if column not in train.columns]
    required_metadata = {"Date_Year", "split"}
    missing_metadata = sorted(required_metadata - set(metadata.columns))
    if missing_columns:
        raise ValueError(f"Training data is missing columns: {', '.join(missing_columns)}")
    if missing_metadata:
        raise ValueError(f"Split metadata is missing columns: {', '.join(missing_metadata)}")

    train_metadata = metadata.loc[metadata["split"] == "train"].reset_index(drop=True)
    if len(train) != len(train_metadata):
        raise ValueError(
            "Training data and training metadata row counts do not match "
            f"({len(train)} versus {len(train_metadata)})"
        )

    years = train_metadata["Date_Year"].to_numpy()
    expected_years = set(range(2005, 2016))
    if set(years) != expected_years:
        raise ValueError(
            "Expected complete training years 2005–2015; found "
            + ", ".join(str(year) for year in sorted(set(years)))
        )

    # The preparation outputs preserve source-row ordering; align those rows to year metadata,
    # then use a stable sort so observations from each year remain together.
    order = np.argsort(years, kind="stable")
    years = years[order]
    train = train.iloc[order].reset_index(drop=True)
    X = train[FEATURES]
    y = train[TARGET]

    fold_results = []
    fold_specs = []
    for fold in FOLDS:
        training_mask = years <= fold["train_end"]
        validation_mask = (
            (years >= fold["validation_start"])
            & (years <= fold["validation_end"])
        )
        training_years = set(years[training_mask])
        validation_years = set(years[validation_mask])
        if not training_mask.any() or not validation_mask.any():
            raise ValueError(f"{fold['name']} has an empty training or validation period")
        if training_years & validation_years:
            raise AssertionError(f"{fold['name']} shares calendar years across its split")
        if max(training_years) >= min(validation_years):
            raise AssertionError(f"{fold['name']} trains on a year in or after validation")

        X_fit, y_fit = X.loc[training_mask], y.loc[training_mask]
        X_validation, y_validation = X.loc[validation_mask], y.loc[validation_mask]
        fold_specs.append(
            {
                **fold,
                "training_count": int(training_mask.sum()),
                "validation_count": int(validation_mask.sum()),
            }
        )

        baseline_prediction = np.full(len(y_validation), float(y_fit.median()))
        baseline_metrics = calculate_metrics(y_validation.to_numpy(), baseline_prediction)
        fold_results.append(
            {
                "Fold": fold["name"],
                "Model": "Median Baseline",
                "Configuration": "Training-fold median",
                "Train_Years": f"2005–{fold['train_end']}",
                "Validation_Years": (
                    f"{fold['validation_start']}–{fold['validation_end']}"
                ),
                "Train_Observations": int(training_mask.sum()),
                "Validation_Observations": int(validation_mask.sum()),
                **baseline_metrics,
            }
        )

        for configuration in CONFIGURATIONS:
            pipeline = build_pipeline(configuration)
            pipeline.fit(X_fit, y_fit)
            prediction = pipeline.predict(X_validation)
            if len(prediction) != len(y_validation) or not np.isfinite(prediction).all():
                raise AssertionError(
                    f"{configuration['name']} produced invalid predictions in {fold['name']}"
                )
            metrics = calculate_metrics(y_validation.to_numpy(), prediction)
            fold_results.append(
                {
                    "Fold": fold["name"],
                    "Model": "Random Forest",
                    "Configuration": configuration["name"],
                    "Train_Years": f"2005–{fold['train_end']}",
                    "Validation_Years": (
                        f"{fold['validation_start']}–{fold['validation_end']}"
                    ),
                    "Train_Observations": int(training_mask.sum()),
                    "Validation_Observations": int(validation_mask.sum()),
                    **metrics,
                }
            )

    fold_frame = pd.DataFrame(fold_results)
    aggregate_rows = []
    model_specs = [("Median Baseline", "Training-fold median")] + [
        ("Random Forest", config["name"]) for config in CONFIGURATIONS
    ]
    fold_names = [fold["name"] for fold in FOLDS]
    for model_name, configuration_name in model_specs:
        selected = fold_frame.loc[
            (fold_frame["Model"] == model_name)
            & (fold_frame["Configuration"] == configuration_name)
        ]
        aggregate = {
            "Fold": "Aggregate",
            "Model": model_name,
            "Configuration": configuration_name,
            "Train_Years": "",
            "Validation_Years": "",
            "Train_Observations": "",
            "Validation_Observations": "",
            "MAE": float(selected["MAE"].mean()),
            "RMSE": float(selected["RMSE"].mean()),
            "Bias": float(selected["Bias"].mean()),
        }
        for fold_name in fold_names:
            fold_mae = selected.loc[selected["Fold"] == fold_name, "MAE"].iloc[0]
            aggregate[f"{fold_name.replace(' ', '_')}_MAE"] = float(fold_mae)
        baseline = fold_frame.loc[
            (fold_frame["Model"] == "Median Baseline")
            & (fold_frame["Fold"].isin(fold_names)),
            ["Fold", "MAE"],
        ].set_index("Fold")["MAE"]
        model_maes = selected.set_index("Fold")["MAE"]
        improvements = baseline - model_maes
        aggregate["Folds_Better_Than_Baseline"] = int((improvements > 0).sum())
        aggregate["Mean_MAE_Improvement_vs_Baseline"] = float(improvements.mean())
        aggregate_rows.append(aggregate)

    output = pd.concat(
        [fold_frame, pd.DataFrame(aggregate_rows)],
        ignore_index=True,
        sort=False,
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    output.to_csv(REPORT_DIR / "time_aware_validation_summary_v1.csv", index=False)

    aggregate_frame = output.loc[output["Fold"] == "Aggregate"].copy()
    baseline_row = aggregate_frame.loc[
        aggregate_frame["Model"] == "Median Baseline"
    ].iloc[0]
    rf_aggregates = aggregate_frame.loc[
        aggregate_frame["Model"] == "Random Forest"
    ].sort_values("MAE")
    best_rf = rf_aggregates.iloc[0]
    best_rf_folds = fold_frame.loc[
        (fold_frame["Model"] == "Random Forest")
        & (fold_frame["Configuration"] == best_rf["Configuration"])
    ].set_index("Fold")["MAE"]
    baseline_folds = fold_frame.loc[
        (fold_frame["Model"] == "Median Baseline")
    ].set_index("Fold")["MAE"]
    best_rf_wins = int((baseline_folds - best_rf_folds > 0).sum())
    rf_promising = (
        float(best_rf["MAE"]) < float(baseline_row["MAE"])
        and best_rf_wins == len(FOLDS)
    )

    fold_lines = [
        "| Fold | Training years (n) | Validation years (n) |",
        "|---|---:|---:|",
    ]
    for fold in fold_specs:
        fold_lines.append(
            f"| {fold['name']} | 2005–{fold['train_end']} "
            f"({fold['training_count']}) | {fold['validation_start']}–"
            f"{fold['validation_end']} ({fold['validation_count']}) |"
        )

    aggregate_lines = [
        "| Model/configuration | Mean MAE | Mean RMSE | Mean bias | "
        + " | ".join(f"{fold} MAE" for fold in fold_names)
        + " | Folds better than baseline | Mean MAE improvement vs baseline |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for _, row in aggregate_frame.iterrows():
        fold_values = " | ".join(
            f"{row[f'{fold.replace(' ', '_')}_MAE']:.4f}" for fold in fold_names
        )
        aggregate_lines.append(
            f"| {row['Model']} — {row['Configuration']} | {row['MAE']:.4f} | "
            f"{row['RMSE']:.4f} | {row['Bias']:.4f} | {fold_values} | "
            f"{int(row['Folds_Better_Than_Baseline'])} | "
            f"{float(row['Mean_MAE_Improvement_vs_Baseline']):.4f} |"
        )

    configuration_lines = [
        "| Configuration | n_estimators | max_depth | min_samples_leaf |",
        "|---|---:|---:|---:|",
    ]
    for config in CONFIGURATIONS:
        configuration_lines.append(
            f"| {config['name']} | {config['n_estimators']} | "
            f"{config['max_depth'] if config['max_depth'] is not None else 'None'} | "
            f"{config['min_samples_leaf']} |"
        )

    report = f"""# ReefGuard-ML — Time-Aware Model Validation

## Method

Only the existing 2,201 training observations from 2005–2015 were used. Rows were sorted by calendar year; years were kept intact within each fold. Each fold uses an expanding training period followed by later validation years. All candidate models use the same validation rows in each fold. The validation-fold median and each imputer were fitted using that fold's training observations only.

The script does not read the 2016 test dataset. The 2016 results were inspected in earlier analyses and therefore should not be described as a completely untouched holdout.

## Folds and observation counts

{chr(10).join(fold_lines)}

## Candidate configurations

{chr(10).join(configuration_lines)}

All Random Forests use `random_state=42`, `n_jobs=-1`, and the same `SimpleImputer(strategy="median")` → `RandomForestRegressor` pipeline. MAE is the primary selection metric.

## Aggregate comparison

Metrics below are arithmetic means of the three fold-level metrics; fold MAEs are shown individually. Positive MAE improvement means lower MAE than the baseline.

{chr(10).join(aggregate_lines)}

## Model selection

The best Random Forest by mean validation MAE was **{best_rf['Configuration']}** ({best_rf['MAE']:.4f}), compared with the fold-median baseline at {baseline_row['MAE']:.4f}.

{"It beat the baseline in every fold, so it is a candidate for further validation, not proof of reliable future performance." if rf_promising else f"It improved mean MAE by {float(baseline_row['MAE']) - float(best_rf['MAE']):.4f} ({(float(baseline_row['MAE']) - float(best_rf['MAE'])) / float(baseline_row['MAE']) * 100:.1f}%), but beat the baseline in only {best_rf_wins} of {len(FOLDS)} folds. Its mean advantage comes from Fold 3; its MAE was {best_rf_folds['Fold 1'] - baseline_folds['Fold 1']:.4f} worse in Fold 1 and {best_rf_folds['Fold 2'] - baseline_folds['Fold 2']:.4f} worse in Fold 2. Treat {best_rf['Configuration']} as a candidate for independent validation, not as the selected model. Retain the median baseline as the current reference."}

## Limitations and next step

- These are only three expanding-window folds within 2005–2015; the periods and sample sizes differ.
- This validation is useful for model comparison but does not prove future forecasting ability.
- The candidate set is deliberately small; results can vary with the particular historical periods.
- The existing 2016 results have already been examined and must not be treated as a pristine, untouched final test.

{"If the Random Forest candidate appears promising, evaluate the fixed candidate in a future, independently collected or otherwise genuinely held-out period before making deployment claims." if rf_promising else "Keep the median baseline as the reference and gather an additional independent time period. If that is not available, revisit data quality and validation design before further model changes; do not treat the already inspected 2016 scores as an independent confirmation."}
"""

    (REPORT_DIR / "time_aware_validation_v1.md").write_text(report, encoding="utf-8")

    print("Time-aware validation completed.")
    print(f"Training observations used: {len(train)}")
    print(f"Rows from 2016 used: 0")
    print(aggregate_frame[
        ["Model", "Configuration", "MAE", "RMSE", "Bias",
         "Fold_1_MAE", "Fold_2_MAE", "Fold_3_MAE",
         "Folds_Better_Than_Baseline", "Mean_MAE_Improvement_vs_Baseline"]
    ].to_string(index=False))
    print(
        "Random Forest candidate promising across all folds:",
        "yes" if rf_promising else "no",
    )


if __name__ == "__main__":
    main()
