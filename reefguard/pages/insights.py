from __future__ import annotations

import streamlit as st

from reefguard.charts import feature_distribution, feature_importance_chart, selected_feature_scatter
from reefguard.config import FEATURES, FEATURE_LABELS
from reefguard.data import load_csv, load_pilot_data
from reefguard.config import FEATURE_IMPORTANCE_PATH, TEMPORAL_VALIDATION_PATH


def render() -> None:
    data = load_pilot_data()
    importance = load_csv(str(FEATURE_IMPORTANCE_PATH))
    temporal = load_csv(str(TEMPORAL_VALIDATION_PATH))
    st.markdown('<div class="page-kicker">Descriptive patterns</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Environmental Insights</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Inspect environmental distributions, their observed relationship '
        'with bleaching, and the features used by the initial saved Random Forest.</p>',
        unsafe_allow_html=True,
    )

    feature = st.selectbox(
        "Choose an environmental variable",
        FEATURES,
        format_func=lambda value: FEATURE_LABELS.get(value, value),
        key="insights_feature",
    )
    left, right = st.columns(2, gap="large")
    with left:
        st.subheader(f"Distribution · {FEATURE_LABELS.get(feature, feature)}")
        st.plotly_chart(feature_distribution(data, feature), width="stretch")
    with right:
        st.subheader("Observed values versus bleaching")
        st.plotly_chart(selected_feature_scatter(data, feature), width="stretch")

    st.subheader("Saved Random Forest feature importance")
    st.plotly_chart(feature_importance_chart(importance), width="stretch")
    st.caption(
        "Impurity-based importance describes how the initial saved Random Forest used its inputs. "
        "It is model-specific, may be affected by correlated inputs, and does not establish causation "
        "or scientific importance."
    )

    rf2 = temporal.loc[
        (temporal["Fold"] == "Aggregate")
        & (temporal["Model"] == "Random Forest")
        & (temporal["Configuration"] == "RF-2")
    ]
    baseline = temporal.loc[
        (temporal["Fold"] == "Aggregate")
        & (temporal["Model"] == "Median Baseline")
    ]
    if not rf2.empty and not baseline.empty:
        rf2_row = rf2.iloc[0]
        baseline_row = baseline.iloc[0]
        st.markdown(
            f'<div class="callout warning-callout"><strong>RF-2 temporal validation:</strong> '
            f'mean fold MAE {float(rf2_row["MAE"]):.2f} versus {float(baseline_row["MAE"]):.2f} '
            f'for the fold-median baseline, but RF-2 beat the baseline in only '
            f'{int(rf2_row["Folds_Better_Than_Baseline"])} of 3 folds. Its performance was '
            'inconsistent across periods. This is separate from the saved model used in assessment.</div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<p class="muted-copy">These plots show descriptive associations in an observational pilot. '
        'They do not support causal conclusions or claims about future reef conditions.</p>',
        unsafe_allow_html=True,
    )
