from __future__ import annotations

import streamlit as st

from reefguard.charts import annual_bleaching, selected_feature_scatter
from reefguard.config import FEATURES, FEATURE_LABELS, TARGET
from reefguard.data import filter_historical_data, load_pilot_data


def render() -> None:
    data = load_pilot_data()
    st.markdown('<div class="page-kicker">Historical observations</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Data Explorer</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">Filter the recorded FRRP pilot observations and inspect '
        'historical bleaching alongside one environmental variable. All charts use observed records only.</p>',
        unsafe_allow_html=True,
    )

    years = sorted(data["Date_Year"].astype(int).unique())
    filters = st.columns([1.2, 1.7, 1.3], gap="large")
    with filters[0]:
        year_range = st.slider(
            "Observation years",
            min_value=years[0],
            max_value=years[-1],
            value=(years[0], years[-1]),
            step=1,
        )
    with filters[1]:
        bleaching_range = st.slider(
            "Observed bleaching (%)",
            min_value=0.0,
            max_value=100.0,
            value=(0.0, 100.0),
            step=1.0,
        )
    with filters[2]:
        feature = st.selectbox(
            "Environmental variable",
            FEATURES,
            format_func=lambda value: FEATURE_LABELS.get(value, value),
        )

    filtered = filter_historical_data(
        data,
        year_range[0],
        year_range[1],
        bleaching_range[0],
        bleaching_range[1],
    )
    st.caption(f"{len(filtered):,} of {len(data):,} historical records match these filters.")

    if filtered.empty:
        st.info("No records match the selected filters. Widen the year or bleaching range.")
        return

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Bleaching trend within the selected years")
        st.plotly_chart(annual_bleaching(filtered), width="stretch")
    with right:
        st.subheader(f"{FEATURE_LABELS.get(feature, feature)} and bleaching")
        st.plotly_chart(selected_feature_scatter(filtered, feature), width="stretch")

    with st.expander("View filtered historical records"):
        columns = ["Date_Year", *FEATURES, TARGET]
        st.dataframe(
            filtered[columns].sort_values("Date_Year", ascending=False),
            width="stretch",
            hide_index=True,
        )

    st.markdown(
        '<div class="callout">A pattern in historical observations is an association in this dataset. '
        'It does not establish that an environmental variable caused a bleaching outcome.</div>',
        unsafe_allow_html=True,
    )
