"""
shared_styles.py — Single source of truth for IPL Insights styling.

Import and call inject_base_css() at the top of every view (team_Analysis,
player_Analysis, venue_Season, win_Predictor) instead of each file defining
its own inject_*_css(). Page-specific overrides (if any) can still be added
via inject_extra_css(extra_css_string) after this call.
"""
import streamlit as st

FONTS_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?"
    "family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&"
    "family=JetBrains+Mono:wght@400;600&display=swap');"
)

BASE_CSS = f"""
<style>
{FONTS_IMPORT}

html, body, [data-testid="stAppViewContainer"] {{
    background: #080C14 !important;
    font-family: 'DM Sans', sans-serif !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{ max-width: 980px !important; padding: 2rem 1.5rem !important; }}

/* Selectbox / inputs */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input {{
    background: #151C2C !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 12px !important;
    color: #F0F4FF !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}}
[data-testid="stSelectbox"] label,
[data-testid="stNumberInput"] label {{
    color: rgba(240,244,255,0.45) !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}

/* Buttons */
[data-testid="stButton"] > button {{
    background: rgba(255,255,255,0.05) !important;
    color: rgba(240,244,255,0.7) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 8px 16px !important;
    width: auto !important;
    box-shadow: none !important;
    transition: all 0.2s ease !important;
}}
[data-testid="stButton"] > button:hover {{
    background: rgba(0,176,255,0.1) !important;
    border-color: rgba(0,176,255,0.3) !important;
    color: #F0F4FF !important;
}}

/* Metric cards */
[data-testid="metric-container"] {{
    background: #151C2C !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 16px !important;
    padding: 16px 20px !important;
}}
[data-testid="metric-container"] label {{
    color: rgba(240,244,255,0.45) !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}}
[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: #F0F4FF !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 28px !important;
    font-weight: 600 !important;
}}

hr {{ border-color: rgba(255,255,255,0.07) !important; }}
::-webkit-scrollbar {{ width: 6px; }}
::-webkit-scrollbar-track {{ background: #080C14; }}
::-webkit-scrollbar-thumb {{ background: #1E2A40; border-radius: 99px; }}
</style>
"""

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color="#F0F4FF"),
    title_font=dict(family="Bebas Neue", size=22, color="#F0F4FF"),
    margin=dict(l=20, r=20, t=50, b=20),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", showline=False),
)


def inject_base_css():
    """Call once at the top of every page, right after the hero/page logic starts."""
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def inject_extra_css(extra_css: str):
    """
    For page-specific rules that don't belong in the shared base
    (e.g. the win predictor's PREDICT button gradient, sidebar nav styling).
    Pass a raw <style>...</style> string.
    """
    st.markdown(extra_css, unsafe_allow_html=True)


def section_label(text: str, subtext: str = "") -> str:
    """Shared section-label HTML used across all pages."""
    html = (
        f'<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);'
        f'margin:28px 0 8px;">{text}</p>'
    )
    if subtext:
        html += (
            f'<p style="font-family:\'DM Sans\',sans-serif;font-size:12px;'
            f'color:rgba(240,244,255,0.35);margin:0 0 14px;">{subtext}</p>'
        )
    return html


def takeaway(text: str, color: str = "#00B0FF") -> str:
    """Shared 'insight callout' box used under charts/tables."""
    return (
        f'<div style="background:{color}0A;border:1px solid {color}1A;border-radius:10px;'
        f'padding:10px 14px;margin:6px 0 20px;display:flex;align-items:center;gap:8px;">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:500;'
        f'color:{color};">💡 {text}</span></div>'
    )