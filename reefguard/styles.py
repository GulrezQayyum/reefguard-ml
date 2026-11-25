from __future__ import annotations

import base64
import mimetypes

import streamlit as st

from reefguard.config import HERO_IMAGE_PATH


def _hero_image_url() -> str:
    if HERO_IMAGE_PATH.is_file():
        try:
            content_type = mimetypes.guess_type(HERO_IMAGE_PATH.name)[0] or "image/jpeg"
            encoded = base64.b64encode(HERO_IMAGE_PATH.read_bytes()).decode("ascii")
            return f"data:{content_type};base64,{encoded}"
        except OSError:
            pass
    return (
        "https://images.unsplash.com/photo-1546026423-cc4642628d2b"
        "?auto=format&fit=crop&w=2200&q=85"
    )


def apply_styles() -> None:
    hero_image = _hero_image_url()
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
        :root {{
            --ocean: #082B36;
            --teal: #103F46;
            --turquoise: #42C9BA;
            --seafoam: #EAF5F1;
            --coral: #FF806F;
            --offwhite: #F7FAF8;
            --muted: #627A7B;
        }}
        html, body, [class*="css"] {{
            font-family: 'DM Sans', sans-serif;
        }}
        .stApp, [data-testid="stAppViewContainer"] {{
            background: var(--offwhite);
            color: var(--ocean);
        }}
        [data-testid="stHeader"] {{
            display: none;
            height: 0 !important;
            pointer-events: none;
        }}
        [data-testid="stToolbar"], footer, #MainMenu {{
            visibility: hidden;
        }}
        .block-container {{
            max-width: 1280px;
            padding-top: 3rem;
            padding-bottom: 4rem;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            color: var(--ocean);
            font-family: 'Manrope', sans-serif;
            font-weight: 800;
            font-size: 1.2rem;
            letter-spacing: -0.035em;
        }}
        .brand-mark {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 0.7rem 0.7rem 0.7rem 0.2rem;
            background: var(--turquoise);
            color: var(--ocean);
            font-weight: 800;
        }}
        .brand-light {{ font-weight: 500; }}
        #stMain .nav-anchor {{
            color: var(--teal);
            text-decoration: none !important;
            font-size: .9rem;
            font-weight: 600;
        }}
        .block-container {{
            position: relative;
            z-index: 1;
        }}
        .nav-anchor {{
            display: inline-flex;
            align-items: center;
            border: 1px solid #d5e5de;
            border-radius: 999px;
            background: white;
            color: var(--teal);
            text-decoration: none;
            font-size: .9rem;
            font-weight: 600;
            padding: .62rem .9rem;
        }}
        .nav-rule {{
            height: 1px;
            margin: 0.65rem 0 1.4rem;
            background: #dce8e3;
        }}
        div.stButton > button {{
            border-radius: 999px;
            border: 1px solid #d5e5de;
            color: var(--ocean);
            background: white;
            font-weight: 600;
            padding: 0.62rem 1rem;
            transition: background-color 120ms ease, border-color 120ms ease;
        }}
        #stMain button[data-testid="stBaseButton-secondary"] {{
            background-color: #FFFFFF !important;
            background-image: none !important;
            border-color: #d5e5de !important;
            color: var(--ocean) !important;
        }}
        div.stButton > button[kind="primary"] {{
            background: var(--ocean) !important;
            border-color: var(--ocean) !important;
            color: white !important;
        }}
        div.stButton > button:hover {{
            border-color: var(--turquoise);
            color: var(--ocean);
        }}
        .hero {{
            position: relative;
            min-height: 490px;
            display: flex;
            align-items: flex-end;
            overflow: hidden;
            margin: 1rem 0 3.8rem;
            padding: clamp(2rem, 6vw, 5rem);
            border-radius: 1.7rem;
            color: white;
            background-color: #0a3b46;
            background-image: linear-gradient(90deg, rgba(4, 29, 39, .87) 0%, rgba(4, 29, 39, .52) 48%, rgba(4, 29, 39, .08) 100%), url("{hero_image}");
            background-position: center;
            background-size: cover;
        }}
        .hero-copy {{ max-width: 720px; }}
        .eyebrow {{
            color: #15776f;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.13em;
            text-transform: uppercase;
        }}
        .hero .eyebrow {{ color: #9af0df; }}
        .hero h1 {{
            max-width: 680px;
            margin: 0.8rem 0 1rem;
            color: white;
            font-family: 'Manrope', sans-serif;
            font-size: clamp(2.6rem, 6vw, 5rem);
            line-height: 1.04;
            letter-spacing: -0.06em;
        }}
        .hero p {{
            max-width: 570px;
            color: rgba(255,255,255,.88);
            font-size: 1.05rem;
            line-height: 1.65;
        }}
        .hero-note {{
            position: absolute;
            right: 1.3rem;
            bottom: 1.2rem;
            color: rgba(255,255,255,.8);
            font-size: 0.75rem;
        }}
        .section-heading {{
            max-width: 760px;
            margin: 0 0 1.5rem;
        }}
        .section-heading h2, .page-title {{
            margin: 0.35rem 0 0.55rem;
            color: var(--ocean);
            font-family: 'Manrope', sans-serif;
            font-size: clamp(1.7rem, 3vw, 2.45rem);
            line-height: 1.15;
            letter-spacing: -0.045em;
        }}
        .section-heading p, .muted-copy {{
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.65;
        }}
        .home-intro {{
            margin: 0 0 3.8rem;
            padding: clamp(1.5rem, 4vw, 3rem);
            border-radius: 1.4rem;
            background: var(--seafoam);
        }}
        .feature-card, .info-card, .stat-card {{
            height: 100%;
            padding: 1.4rem;
            border: 1px solid #e4eee9;
            border-radius: 1.1rem;
            background: white;
            box-shadow: 0 10px 28px rgba(8, 43, 54, .045);
        }}
        .feature-card h3, .info-card h3 {{
            margin: 0.25rem 0 0.5rem;
            color: var(--ocean);
            font-family: 'Manrope', sans-serif;
            font-size: 1.15rem;
        }}
        .feature-card p, .info-card p {{
            margin: 0;
            color: var(--muted);
            line-height: 1.6;
        }}
        .feature-index {{
            color: #178f83;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: .12em;
        }}
        .stat-card {{ min-height: 118px; }}
        .stat-label {{ color: var(--muted); font-size: .83rem; }}
        .stat-value {{
            margin-top: .35rem;
            color: var(--ocean);
            font-family: 'Manrope', sans-serif;
            font-size: 1.8rem;
            font-weight: 800;
            letter-spacing: -.05em;
        }}
        .callout {{
            padding: 1rem 1.15rem;
            border-left: 4px solid var(--turquoise);
            border-radius: 0 .8rem .8rem 0;
            background: var(--seafoam);
            color: var(--teal);
            line-height: 1.55;
        }}
        .warning-callout {{
            border-left-color: var(--coral);
            background: #fff0ed;
            color: #553b38;
        }}
        .page-kicker {{
            margin: 0 0 .35rem;
            color: #15776f;
            font-size: .75rem;
            font-weight: 700;
            letter-spacing: .12em;
            text-transform: uppercase;
        }}
        .page-subtitle {{
            max-width: 820px;
            margin: 0 0 1.6rem;
            color: var(--muted);
            line-height: 1.65;
        }}
        .footer {{
            margin-top: 4rem;
            padding: 1.7rem 0 0;
            border-top: 1px solid #dce8e3;
            color: var(--muted);
            font-size: .85rem;
            line-height: 1.65;
        }}
        .footer a {{ color: #15776f; }}
        [data-testid="stMetric"] {{
            padding: .8rem 1rem;
            border: 1px solid #e4eee9;
            border-radius: 1rem;
            background: white;
        }}
        [data-testid="stMetricLabel"] {{ color: var(--muted) !important; }}
        [data-testid="stMetricValue"] {{
            color: var(--ocean) !important;
            font-size: clamp(1rem, 2vw, 1.25rem) !important;
        }}
        @media (max-width: 850px) {{
            .block-container {{ padding-top: 3rem; }}
            .hero {{ min-height: 420px; border-radius: 1.1rem; }}
            .hero-note {{ display: none; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
