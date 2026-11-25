from __future__ import annotations

import streamlit as st

from reefguard.config import NAV_ITEMS
from reefguard.pages import (
    assessment,
    data_explorer,
    home,
    insights,
    methodology,
    model_evaluation,
    overview,
)
from reefguard.styles import apply_styles


PAGE_RENDERERS = {
    "overview": overview.render,
    "data": data_explorer.render,
    "assessment": assessment.render,
    "insights": insights.render,
    "evaluation": model_evaluation.render,
    "methodology": methodology.render,
}


def navigate_to(page: str) -> None:
    st.query_params["page"] = page
    st.rerun()


def render_home_navigation() -> None:
    brand, mission, explore = st.columns([4.2, 1.3, 2.0], vertical_alignment="center")
    with brand:
        st.markdown(
            '<div class="brand"><span class="brand-mark">R</span>'
            '<span>ReefGuard<span class="brand-light">-ML</span></span></div>',
            unsafe_allow_html=True,
        )
    with mission:
        st.markdown('<a class="nav-anchor" href="#why-reefs">Why reefs</a>', unsafe_allow_html=True)
    with explore:
        if st.button("Explore dashboard", type="primary", width="stretch", key="home_nav_explore"):
            navigate_to("overview")


def render_dashboard_navigation(current_page: str) -> None:
    brand, home_col = st.columns([5, 1.3], vertical_alignment="center")
    with brand:
        st.markdown(
            '<div class="brand"><span class="brand-mark">R</span>'
            '<span>ReefGuard<span class="brand-light">-ML</span></span></div>',
            unsafe_allow_html=True,
        )
    with home_col:
        if st.button("Home", width="stretch", key="dashboard_nav_home"):
            navigate_to("home")

    for offset in range(0, len(NAV_ITEMS), 3):
        columns = st.columns(3, gap="small")
        for column, (page_id, label) in zip(columns, NAV_ITEMS[offset : offset + 3]):
            with column:
                if st.button(
                    label,
                    type="primary" if current_page == page_id else "secondary",
                    width="stretch",
                    key=f"dashboard_nav_{page_id}",
                ):
                    navigate_to(page_id)
    st.markdown('<div class="nav-rule"></div>', unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="ReefGuard-ML | Coral bleaching research",
        page_icon="🪸",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    apply_styles()

    page_id = st.query_params.get("page", "home")
    if page_id == "home":
        render_home_navigation()
        home.render(lambda: navigate_to("overview"))
        return

    if page_id not in PAGE_RENDERERS:
        st.warning("That page is not available. Returning to the project home.")
        page_id = "home"
        render_home_navigation()
        home.render(lambda: navigate_to("overview"))
        return

    render_dashboard_navigation(page_id)
    PAGE_RENDERERS[page_id]()


if __name__ == "__main__":
    main()
