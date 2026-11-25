from __future__ import annotations

import streamlit as st

from reefguard.config import FEATURES, FEATURE_UNITS
from reefguard.data import environmental_summary, load_pilot_data


def render() -> None:
    data = load_pilot_data()
    st.markdown('<div class="page-kicker">How to read this prototype</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Methodology & limitations</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">A plain-language record of the dataset scope, model inputs, '
        'validation design, and intended use.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("### Dataset origin and scope")
    st.write(
        f"The project pilot was extracted from the Global Coral Bleaching Database for the "
        f"Florida Reef Resilience Program (FRRP), using the read-only project query. It contains "
        f"{len(data):,} observations from {int(data['Date_Year'].min())} to "
        f"{int(data['Date_Year'].max())}. These are historical sample observations, not a live feed. "
        "The repository README records the source database as Global_Coral_Bleaching_Database_SQLite_11_24_21.db."
    )
    st.write("The target is `Percent_Bleached`, recorded between 0 and 100.")

    st.markdown("### Selected model features and observed ranges")
    ranges = data.loc[:, FEATURES].agg(["min", "max"]).T
    ranges["unit"] = [FEATURE_UNITS.get(feature, "not confirmed") for feature in ranges.index]
    st.dataframe(ranges, width="stretch")
    st.write(
        "Depth is in metres; project notes identify ClimSST and Temperature_Mean as Kelvin. "
        "Units and temporal windows for the other environmental variables are not confirmed in "
        "the available documentation. The repeated `ClimSST = 262.15` value occurs in 187 rows "
        "and its meaning remains unresolved."
    )

    st.markdown("### Temporal split and models")
    st.write(
        "The original modeling split uses 2005–2015 for training (2,201 observations) and 2016 "
        "for testing (193 observations). The initial model comparison evaluated a training-median "
        "baseline, Linear Regression, and Random Forest on the same 2016 rows. Existing reports "
        "show the median baseline had the lowest MAE (7.37 percentage points); Linear Regression "
        "scored 9.04 and the initial Random Forest scored 9.75."
    )
    st.write(
        "A separate expanding-window validation used three folds within 2005–2015. RF-2 was "
        "configured with 200 trees, unlimited depth, minimum leaf size 5, and random state 42. "
        "Its mean fold MAE was 12.60 compared with 13.98 for fold-median baselines, but it beat "
        "the baseline in only one of three folds. The repository does not contain a saved fitted "
        "RF-2 pipeline; the assessment page therefore loads the distinct saved Random Forest v1 "
        "pipeline (300 trees, minimum leaf size 2)."
    )

    st.markdown("### Evaluation measures")
    st.write(
        "Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) are reported in bleaching "
        "percentage points, with lower values indicating smaller errors. R² compares predictions "
        "with the mean of the evaluated target values. Bias is `mean(actual − predicted)`: a "
        "positive value indicates underprediction on average."
    )
    st.write(
        "The 2016 test results were examined in prior project analyses and are not an untouched "
        "final holdout. The temporal-validation averages are separate fold-level results, not "
        "2016 metrics."
    )

    st.markdown("### Known data limitations")
    st.write(
        "The data is observational, the test period shares 22 site IDs with the training period, "
        "environmental measurement units and timing are incomplete, and the `ClimSST` repeated "
        "value is unresolved. The high-bleaching group in the 2016 test set contains only six "
        "observations. These factors limit interpretation and generalization."
    )

    st.markdown("### Intended use")
    st.markdown(
        '<div class="callout warning-callout">This is a research and learning prototype for '
        'exploring historical data and existing model artifacts. It does not establish causation, '
        'predict future conditions, provide early warning, or recommend conservation action. '
        'Model outputs are experimental and should not be used as operational guidance.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("Environmental summary statistics"):
        st.dataframe(environmental_summary(data), width="stretch")
