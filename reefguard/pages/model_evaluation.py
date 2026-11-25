from __future__ import annotations

import streamlit as st

from reefguard.charts import (
    actual_vs_predicted_chart,
    feature_importance_chart,
    model_comparison_chart,
    residual_distribution,
    temporal_validation_chart,
)
from reefguard.data import load_evaluation_artifacts


def render() -> None:
    st.markdown('<div class="page-kicker">Existing evaluation artifacts</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Model Evaluation</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">The 2016 test comparison and 2005–2015 expanding-window '
        'validation answer different questions. They are presented separately and were not regenerated here.</p>',
        unsafe_allow_html=True,
    )
    try:
        artifacts = load_evaluation_artifacts()
    except (FileNotFoundError, OSError, ValueError) as error:
        st.error(f"An evaluation artifact could not be loaded: {error}")
        return

    comparison = artifacts["comparison"]
    predictions = artifacts["predictions"]
    test = artifacts["test"]
    if len(predictions) != len(test):
        st.error(
            "Saved prediction and test row counts differ "
            f"({len(predictions)} versus {len(test)}); actual-versus-predicted charts are unavailable."
        )
        return
    if "Actual Percent_Bleached" not in predictions or "Percent_Bleached" not in test:
        st.error("Required target columns are missing from saved prediction or test artifacts.")
        return
    if not predictions["Actual Percent_Bleached"].equals(test["Percent_Bleached"]):
        st.error("Saved prediction actuals do not align row-for-row with the 2016 test dataset.")
        return

    st.markdown("### Initial comparison · 2016 test set")
    st.caption(
        f"{len(test):,} observations from 2016. These results belong to the initial saved "
        "model comparison and are not RF-2 results."
    )
    st.dataframe(comparison, hide_index=True, width="stretch")
    st.plotly_chart(model_comparison_chart(comparison), width="stretch")
    st.caption("MAE and RMSE are measured in percentage points; lower values are better.")

    st.subheader("Actual versus predicted")
    st.plotly_chart(actual_vs_predicted_chart(predictions), width="stretch")
    st.caption(
        "The dashed diagonal represents exact agreement. Predictions are plotted as saved and "
        "are not clipped to 0–100."
    )

    st.subheader("Residual distributions")
    st.plotly_chart(residual_distribution(predictions), width="stretch")
    st.caption("Residual = actual − predicted. Negative values indicate overprediction.")

    st.subheader("Initial Random Forest feature importance")
    st.plotly_chart(feature_importance_chart(artifacts["importance"]), width="stretch")
    st.caption("Model-specific importance is not evidence of causation.")

    st.markdown("### Expanding-window validation · 2005–2015")
    st.markdown(
        "These three folds use earlier years for training and later years for validation. "
        "The 2016 test set is not part of this chart."
    )
    st.plotly_chart(temporal_validation_chart(artifacts["temporal"]), width="stretch")
    aggregate = artifacts["temporal"].loc[artifacts["temporal"]["Fold"] == "Aggregate"]
    display_columns = [
        "Model",
        "Configuration",
        "MAE",
        "RMSE",
        "Fold_1_MAE",
        "Fold_2_MAE",
        "Fold_3_MAE",
        "Folds_Better_Than_Baseline",
    ]
    st.dataframe(aggregate[display_columns], hide_index=True, width="stretch")
    st.markdown(
        '<div class="callout warning-callout">RF-2 has the lowest mean MAE among the four '
        'Random Forest candidates, but beat the fold-median baseline in only one of three folds. '
        'The available saved assessment pipeline is a different Random Forest configuration. '
        'The previously examined 2016 results should not be treated as an untouched final holdout.</div>',
        unsafe_allow_html=True,
    )
