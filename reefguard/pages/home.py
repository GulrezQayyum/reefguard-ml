from __future__ import annotations

from collections.abc import Callable

import streamlit as st


def render(explore_dashboard: Callable[[], None]) -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="hero-copy">
            <div class="eyebrow">A data-led coral conservation prototype</div>
            <h1>Our reefs are changing. Let's understand why.</h1>
            <p>Explore a carefully documented coral bleaching pilot dataset, examine environmental patterns, and see what an experimental model can — and cannot — tell us.</p>
          </div>
          <div class="hero-note">ReefGuard-ML · historical observations, 2005–2016</div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    _, action, _ = st.columns([1, 2, 1])
    with action:
        if st.button(
            "Explore the scientific dashboard  →",
            type="primary",
            width="stretch",
            key="hero_dashboard_cta",
        ):
            explore_dashboard()

    st.markdown(
        """
        <section class="home-intro" id="why-reefs">
          <div class="eyebrow">Why reefs matter</div>
          <div class="section-heading">
            <h2>Bleaching is a signal worth understanding.</h2>
            <p>When corals experience stress, they can lose the microscopic algae that give them much of their colour and energy. A bleached coral is under stress, but bleaching does not always mean the coral has died. ReefGuard-ML helps explore historical observations without turning association into a claim of cause.</p>
          </div>
          <a href="https://oceanservice.noaa.gov/facts/coral_bleach.html" target="_blank" rel="noopener">Learn about coral bleaching from NOAA Ocean Service ↗</a>
        </section>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="section-heading">
          <div class="eyebrow">Explore the application</div>
          <h2>Three ways to look closer</h2>
          <p>Move from historical records to model evidence, with limitations visible at every step.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    columns = st.columns(3, gap="large")
    features = [
        ("01", "Bleaching assessment", "Try the saved experimental Random Forest with environmental values inside the pilot's observed ranges."),
        ("02", "Historical data exploration", "Filter recorded observations by year and bleaching percentage, then explore how selected variables relate to the target."),
        ("03", "Environmental insights", "Compare environmental distributions and model feature importance. Associations are descriptive, not causal."),
    ]
    for column, (index, title, copy) in zip(columns, features):
        with column:
            st.markdown(
                f'<article class="feature-card"><div class="feature-index">{index} / REEFGUARD</div>'
                f"<h3>{title}</h3><p>{copy}</p></article>",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:3.6rem'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-heading">
          <div class="eyebrow">The pilot, at a glance</div>
          <h2>A small, transparent starting point.</h2>
          <p>The FRRP pilot contains 2,394 observations from 2005–2016. The modelling target is <code>Percent_Bleached</code>. Eight environmental fields are used as model inputs; the dataset is observational and its environmental units and temporal windows are not fully documented.</p>
        </div>
        <div class="callout">The assessment model is experimental. Temporal validation found its performance was inconsistent across folds, and the saved pipeline is not the RF-2 configuration described in the validation report.</div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <footer class="footer">
          <strong>ReefGuard-ML</strong> · A research and learning prototype, not an alert or forecasting service.<br>
          Dataset origin: Florida Reef Resilience Program (FRRP) observations extracted from the Global Coral Bleaching Database, as documented in the project README.
          <a href="https://github.com/GulrezQayyum/reefguard-ml/blob/main/README.md" target="_blank" rel="noopener">Project methodology and source notes ↗</a>
        </footer>
        """,
        unsafe_allow_html=True,
    )
