from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "modeling"
REPORT_DIR = PROJECT_ROOT / "reports"
FIGURE_DIR = REPORT_DIR / "figures"

MODEL_ORDER = ["Median Baseline", "Linear Regression", "Random Forest"]
PREDICTION_COLUMNS = {
    "Median Baseline": "Median baseline prediction",
    "Linear Regression": "Linear Regression prediction",
    "Random Forest": "Random Forest prediction",
}
MODEL_COLORS = {
    "Median Baseline": "#6c757d",
    "Linear Regression": "#2474a6",
    "Random Forest": "#e07a2d",
}
FOLD_ORDER = ["Fold 1", "Fold 2", "Fold 3"]
VALIDATION_SERIES = [
    ("Median Baseline", "Training-fold median", "Median Baseline"),
    ("Random Forest", "RF-1", "RF-1"),
    ("Random Forest", "RF-2", "RF-2"),
    ("Random Forest", "RF-3", "RF-3"),
    ("Random Forest", "RF-4", "RF-4"),
]


def require_columns(frame: pd.DataFrame, source: str, columns: list[str]) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{source} is missing required columns: {', '.join(missing)}")


def load_inputs() -> dict[str, pd.DataFrame]:
    comparison = pd.read_csv(REPORT_DIR / "model_comparison_v1.csv")
    predictions = pd.read_csv(DATA_DIR / "model_predictions_v1.csv")
    test = pd.read_csv(DATA_DIR / "test_v1.csv")
    metadata = pd.read_csv(DATA_DIR / "split_metadata_v1.csv")
    importance = pd.read_csv(REPORT_DIR / "random_forest_feature_importance_v1.csv")
    validation = pd.read_csv(REPORT_DIR / "time_aware_validation_summary_v1.csv")

    require_columns(comparison, "model_comparison_v1.csv", ["Model", "MAE", "RMSE", "R2"])
    require_columns(
        predictions,
        "model_predictions_v1.csv",
        ["Actual Percent_Bleached", *PREDICTION_COLUMNS.values()],
    )
    require_columns(test, "test_v1.csv", ["Percent_Bleached"])
    require_columns(metadata, "split_metadata_v1.csv", ["Date_Year", "split"])
    require_columns(
        importance,
        "random_forest_feature_importance_v1.csv",
        ["Feature", "Importance"],
    )
    require_columns(
        validation,
        "time_aware_validation_summary_v1.csv",
        ["Fold", "Model", "Configuration", "Validation_Years", "MAE"],
    )

    if len(predictions) != len(test):
        raise ValueError(
            "Prediction and test row counts differ "
            f"({len(predictions)} versus {len(test)})"
        )
    predicted_actual = predictions["Actual Percent_Bleached"].to_numpy(dtype=float)
    test_actual = test["Percent_Bleached"].to_numpy(dtype=float)
    if not np.allclose(predicted_actual, test_actual, equal_nan=True):
        raise ValueError("Prediction actual values do not align with test_v1.csv row-for-row")

    test_metadata = metadata.loc[metadata["split"].eq("test")]
    if len(test_metadata) != len(test):
        raise ValueError(
            "Test metadata and test data row counts differ "
            f"({len(test_metadata)} versus {len(test)})"
        )
    test_years = set(test_metadata["Date_Year"].dropna().astype(int))
    if test_years != {2016}:
        raise ValueError(f"Expected 2016 test observations; found years {sorted(test_years)}")

    actual_and_predictions = predictions[
        ["Actual Percent_Bleached", *PREDICTION_COLUMNS.values()]
    ]
    if not np.isfinite(actual_and_predictions.to_numpy(dtype=float)).all():
        raise ValueError("Prediction data contains non-finite values")

    comparison_models = comparison["Model"].tolist()
    if len(comparison_models) != len(MODEL_ORDER) or set(comparison_models) != set(MODEL_ORDER):
        raise ValueError(f"Expected one comparison row for each of {MODEL_ORDER}")
    if comparison["Model"].duplicated().any():
        raise ValueError("Model comparison contains duplicate model rows")

    if importance.empty or not np.isfinite(importance["Importance"].to_numpy(dtype=float)).all():
        raise ValueError("Feature importance data is empty or contains non-finite values")
    if (importance["Importance"] < 0).any():
        raise ValueError("Feature importance values must not be negative")

    fold_rows = validation.loc[validation["Fold"].isin(FOLD_ORDER)]
    expected_validation_pairs = {
        (fold, model, configuration)
        for fold in FOLD_ORDER
        for model, configuration, _ in VALIDATION_SERIES
    }
    observed_validation_pairs = set(
        fold_rows[["Fold", "Model", "Configuration"]].itertuples(index=False, name=None)
    )
    if observed_validation_pairs != expected_validation_pairs:
        raise ValueError("Temporal validation summary does not contain the expected fold results")
    if fold_rows.duplicated(["Fold", "Model", "Configuration"]).any():
        raise ValueError("Temporal validation summary contains duplicate fold results")
    if fold_rows["MAE"].isna().any() or not np.isfinite(fold_rows["MAE"].to_numpy(dtype=float)).all():
        raise ValueError("Temporal validation MAE contains missing or non-finite values")

    return {
        "comparison": comparison,
        "predictions": predictions,
        "importance": importance,
        "validation": validation,
    }


def plot_model_comparison(comparison: pd.DataFrame) -> None:
    metrics = [("MAE", "MAE (percentage points)"), ("RMSE", "RMSE (percentage points)"), ("R2", "R²")]
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.3))
    fig.suptitle("2016 Test-Set Model Performance", fontsize=16, fontweight="bold")
    fig.text(
        0.5,
        0.92,
        "Same 193 observations for all models; each metric has its own scale",
        ha="center",
        fontsize=10,
    )

    indexed = comparison.set_index("Model")
    for ax, (metric, label) in zip(axes, metrics):
        values = indexed.loc[MODEL_ORDER, metric].astype(float)
        bars = ax.bar(
            MODEL_ORDER,
            values,
            color=[MODEL_COLORS[model] for model in MODEL_ORDER],
            width=0.68,
        )
        ax.set_title(label)
        ax.set_ylabel(label)
        ax.tick_params(axis="x", labelrotation=20)
        ax.grid(axis="y", alpha=0.25)
        ax.set_axisbelow(True)
        for bar, value in zip(bars, values):
            vertical_offset = 4 if value >= 0 else -14
            ax.annotate(
                f"{value:.6f}",
                (bar.get_x() + bar.get_width() / 2, value),
                xytext=(0, vertical_offset),
                textcoords="offset points",
                ha="center",
                va="bottom" if value >= 0 else "top",
                fontsize=8,
            )
        lower = min(0.0, float(values.min()) * 1.15)
        upper = max(0.0, float(values.max()) * 1.20)
        if lower == upper:
            upper = 1.0
        ax.set_ylim(lower, upper)

    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURE_DIR / "model_performance_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_actual_vs_predicted(predictions: pd.DataFrame) -> None:
    actual = predictions["Actual Percent_Bleached"].to_numpy(dtype=float)
    prediction_values = [
        predictions[PREDICTION_COLUMNS[model]].to_numpy(dtype=float) for model in MODEL_ORDER
    ]
    minimum = min(float(actual.min()), *(float(values.min()) for values in prediction_values))
    maximum = max(float(actual.max()), *(float(values.max()) for values in prediction_values))
    padding = max((maximum - minimum) * 0.05, 1.0)
    limits = (minimum - padding, maximum + padding)

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), sharex=True, sharey=True)
    fig.suptitle("Actual vs. Predicted Bleaching — 2016 Test Set", fontsize=16, fontweight="bold")
    fig.text(0.5, 0.92, f"n = {len(actual)} for each model", ha="center", fontsize=10)
    for ax, model, predicted in zip(axes, MODEL_ORDER, prediction_values):
        ax.scatter(
            actual,
            predicted,
            s=24,
            alpha=0.7,
            color=MODEL_COLORS[model],
            edgecolors="white",
            linewidths=0.35,
            label=model,
        )
        ax.plot(limits, limits, color="#222222", linestyle="--", linewidth=1.2, label="y = x")
        ax.set_title(model)
        ax.set_xlabel("Actual bleaching (percentage points)")
        ax.set_ylabel("Predicted bleaching (percentage points)")
        ax.set_xlim(limits)
        ax.set_ylim(limits)
        ax.grid(alpha=0.22)
        ax.legend(loc="upper left", fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURE_DIR / "actual_vs_predicted.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_prediction_error_distribution(predictions: pd.DataFrame) -> None:
    actual = predictions["Actual Percent_Bleached"].to_numpy(dtype=float)
    residuals = {
        model: actual - predictions[PREDICTION_COLUMNS[model]].to_numpy(dtype=float)
        for model in MODEL_ORDER
    }
    low = min(float(values.min()) for values in residuals.values())
    high = max(float(values.max()) for values in residuals.values())
    bins = np.linspace(low, high, 31)

    fig, ax = plt.subplots(figsize=(11.5, 6.2))
    for model in MODEL_ORDER:
        ax.hist(
            residuals[model],
            bins=bins,
            color=MODEL_COLORS[model],
            alpha=0.32,
            edgecolor=MODEL_COLORS[model],
            linewidth=1,
            label=model,
        )
    ax.axvline(0, color="#222222", linestyle="--", linewidth=1.5, label="Zero error")
    ax.axvspan(low, 0, color="#2474a6", alpha=0.06)
    ax.axvspan(0, high, color="#e07a2d", alpha=0.06)
    ax.text(0.02, 0.95, "Overprediction\n(actual − predicted < 0)", transform=ax.transAxes,
            ha="left", va="top", color="#2474a6", fontsize=9)
    ax.text(0.98, 0.95, "Underprediction\n(actual − predicted > 0)", transform=ax.transAxes,
            ha="right", va="top", color="#b45c1f", fontsize=9)
    ax.set_title("Prediction Error Distributions — 2016 Test Set", fontsize=15, fontweight="bold")
    ax.set_xlabel("Residual: actual − predicted (percentage points)")
    ax.set_ylabel("Observation count")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 0.84), ncol=4, fontsize=9)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "prediction_error_distribution.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_random_forest_feature_importance(importance: pd.DataFrame) -> None:
    ordered = importance.sort_values("Importance", ascending=True)
    fig_height = max(5.5, 0.48 * len(ordered) + 2.0)
    fig, ax = plt.subplots(figsize=(10.5, fig_height))
    bars = ax.barh(ordered["Feature"], ordered["Importance"], color="#2474a6")
    ax.set_title("Random Forest Feature Importance", fontsize=15, fontweight="bold")
    ax.set_xlabel("Impurity-based importance")
    ax.set_ylabel("Feature")
    ax.grid(axis="x", alpha=0.22)
    ax.set_axisbelow(True)
    for bar, value in zip(bars, ordered["Importance"]):
        ax.annotate(
            f"{value:.6f}",
            (bar.get_width(), bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
        )
    ax.text(
        0,
        -0.17,
        "Importance is specific to this fitted model and does not establish causation.",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(
        FIGURE_DIR / "random_forest_feature_importance.png",
        dpi=180,
        bbox_inches="tight",
    )
    plt.close(fig)


def plot_temporal_validation_comparison(validation: pd.DataFrame) -> None:
    fold_rows = validation.loc[validation["Fold"].isin(FOLD_ORDER)]
    aggregate_rows = validation.loc[validation["Fold"].eq("Aggregate")]
    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    x_values = np.arange(len(FOLD_ORDER))
    labels = []

    for fold in FOLD_ORDER:
        fold_periods = fold_rows.loc[fold_rows["Fold"].eq(fold), "Validation_Years"].unique()
        if len(fold_periods) != 1:
            raise ValueError(f"{fold} must have exactly one validation period")
        labels.append(f"{fold}\n{fold_periods[0]}")

    colors = {
        "Median Baseline": MODEL_COLORS["Median Baseline"],
        "RF-1": "#537fa5",
        "RF-2": "#b23a48",
        "RF-3": "#60a17e",
        "RF-4": "#9773aa",
    }
    markers = {
        "Median Baseline": "o",
        "RF-1": "^",
        "RF-2": "D",
        "RF-3": "s",
        "RF-4": "v",
    }
    line_styles = {
        "Median Baseline": "-",
        "RF-1": "--",
        "RF-2": "-",
        "RF-3": "-.",
        "RF-4": ":",
    }
    label_offsets = {
        "Median Baseline": (0, -17),
        "RF-1": (0, 16),
        "RF-2": (0, -31),
        "RF-3": (0, 31),
        "RF-4": (0, 46),
    }
    for model, configuration, label in VALIDATION_SERIES:
        selected = fold_rows.loc[
            (fold_rows["Model"] == model) & (fold_rows["Configuration"] == configuration)
        ].set_index("Fold")
        values = selected.loc[FOLD_ORDER, "MAE"].astype(float).to_numpy()
        is_rf2 = label == "RF-2"
        aggregate = aggregate_rows.loc[
            (aggregate_rows["Model"] == model)
            & (aggregate_rows["Configuration"] == configuration),
            "MAE",
        ]
        if len(aggregate) != 1 or not np.isclose(float(values.mean()), float(aggregate.iloc[0])):
            raise ValueError(f"{label} fold MAEs do not match its saved aggregate mean")
        ax.plot(
            x_values,
            values,
            marker=markers[label],
            linestyle=line_styles[label],
            linewidth=2.8 if is_rf2 else 1.7,
            markersize=8,
            markerfacecolor=colors[label] if is_rf2 else "white",
            markeredgewidth=1.5,
            color=colors[label],
            label=label,
            zorder=5 if is_rf2 else 2,
        )
        vertical_offset = label_offsets[label]
        for x_value, value in zip(x_values, values):
            ax.annotate(
                f"{value:.2f}",
                (x_value, value),
                xytext=vertical_offset,
                textcoords="offset points",
                ha="center",
                va="bottom" if vertical_offset[1] > 0 else "top",
                color=colors[label],
                fontsize=7,
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.8, "pad": 0.5},
                zorder=6,
            )

    rf2_mean = float(
        aggregate_rows.loc[
            (aggregate_rows["Model"] == "Random Forest")
            & (aggregate_rows["Configuration"] == "RF-2"),
            "MAE",
        ].iloc[0]
    )
    rf_means = aggregate_rows.loc[aggregate_rows["Model"].eq("Random Forest"), "MAE"]
    if rf2_mean != float(rf_means.min()):
        raise ValueError("RF-2 is not the lowest-mean Random Forest configuration in the report")

    fig.suptitle("Expanding-Window Temporal Validation MAE", fontsize=15, fontweight="bold")
    fig.text(
        0.5,
        0.92,
        f"RF-2 mean: {rf2_mean:.4f} - lowest among RF configurations; "
        "median baseline lower in Folds 1 and 2.",
        ha="center",
        fontsize=9,
    )
    ax.set_ylabel("Validation MAE (percentage points)")
    ax.set_xticks(x_values, labels)
    ax.set_xlabel("Validation period")
    ax.set_ylim(bottom=0)
    ax.grid(axis="y", alpha=0.22)
    ax.set_axisbelow(True)
    ax.legend(title="Model/configuration", loc="upper left", ncol=2, fontsize=9)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURE_DIR / "temporal_validation_comparison.png", dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    inputs = load_inputs()
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    plot_model_comparison(inputs["comparison"])
    plot_actual_vs_predicted(inputs["predictions"])
    plot_prediction_error_distribution(inputs["predictions"])
    plot_random_forest_feature_importance(inputs["importance"])
    plot_temporal_validation_comparison(inputs["validation"])
    print(f"Saved five evaluation figures to {FIGURE_DIR}")


if __name__ == "__main__":
    main()
