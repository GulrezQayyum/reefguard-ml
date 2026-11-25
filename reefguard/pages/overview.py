from __future__ import annotations

import streamlit as st

from reefguard.charts import annual_bleaching, bleaching_distribution, yearly_observation_counts
from reefguard.config import TARGET
from reefguard.data import load_pilot_data


def render() -> None:
    data = load_pilot_data()
    st.markdown('<div class="page-kicker">Scientific dashboard</div>', unsafe_allow_html=True)
    st.markdown('<h1 class="page-title">Overview</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="page-subtitle">A grounded snapshot of the FRRP pilot dataset and the model evidence. '
        'These are historical observations, not live monitoring or forecasts.</p>',
        unsafe_allow_html=True,
    )

    metrics = st.columns(3)
    with metrics[0]:
        st.metric("Historical observations", f"{len(data):,}")
    with metrics[1]:
        st.metric("Study period", f"{int(data['Date_Year'].min())}–{int(data['Date_Year'].max())}")
    with metrics[2]:
        st.metric("Historical median bleaching", f"{data[TARGET].median():.2f}%")

    left, right = st.columns(2, gap="large")
    with left:
        st.subheader("Observed bleaching")
        st.plotly_chart(bleaching_distribution(data), width="stretch")
    with right:
        st.subheader("Yearly median")
        st.plotly_chart(annual_bleaching(data), width="stretch")

    st.subheader("Observations by year")
    st.plotly_chart(yearly_observation_counts(data), width="stretch")

    st.markdown(
        '<div class="callout">The pilot has 2,394 records across 2005–2016. The overall median of '
        '10.26% is a descriptive historical baseline, not a prediction for any individual reef.</div>',
        unsafe_allow_html=True,
    )
