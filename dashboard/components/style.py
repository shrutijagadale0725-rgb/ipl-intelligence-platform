import streamlit as st
def hide_radio_circle():
    st.markdown("""
    <style>

    div[role="radiogroup"] > label {
        background: rgba(255,255,255,0.05);
        padding: 12px 16px;
        border-radius: 14px;
        margin-bottom: 10px;
        border: 1px solid rgba(255,255,255,0.08);
        transition: 0.3s;
        cursor: pointer;
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(255,255,255,0.10);
        transform: translateX(4px);
    }

    /* HIDE RADIO CIRCLE */
    div[role="radiogroup"] input[type="radio"] {
        display: none;
    }

    </style>
    """, unsafe_allow_html=True)
def inject_glass_theme():
    """
    Injects the full IPL Insights glassmorphism dark theme into Streamlit.
    Call this at the TOP of every page file, right after st.set_page_config().
    """
    st.html("""
    <link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap" rel="stylesheet"/>

    <style>
    /* ═══════════════════════════════════════════
       ROOT VARIABLES
    ═══════════════════════════════════════════ */
    :root {
        --gold:        #f5a623;
        --blue:        #1a8fff;
        --pink:        #ff4d8d;
        --green:       #3ecf8e;
        --glass-bg:    rgba(255,255,255,0.045);
        --glass-bd:    rgba(255,255,255,0.10);
        --glass-hover: rgba(255,255,255,0.075);
        --text:        #f0f0f0;
        --muted:       rgba(255,255,255,0.45);
        --radius:      16px;
    }

    /* ═══════════════════════════════════════════
       GLOBAL RESET & BACKGROUND
    ═══════════════════════════════════════════ */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background: #060810 !important;
        color: var(--text) !important;
        font-family: 'DM Sans', sans-serif !important;
    }

    /* Animated gradient orbs behind everything */
    [data-testid="stAppViewContainer"]::before {
        content: '';
        position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background:
            radial-gradient(ellipse 70% 50% at 15%  10%, rgba(26,143,255,0.16)  0%, transparent 60%),
            radial-gradient(ellipse 55% 45% at 85%  85%, rgba(245,166,35,0.12)  0%, transparent 55%),
            radial-gradient(ellipse 45% 40% at 60%  20%, rgba(255,77,141,0.09)  0%, transparent 50%),
            #060810;
        animation: bgPulse 10s ease-in-out infinite alternate;
    }
    @keyframes bgPulse {
        from { opacity: 1; }
        to   { opacity: 0.85; }
    }

    /* Grain texture overlay */
    [data-testid="stAppViewContainer"]::after {
        content: '';
        position: fixed; inset: 0; z-index: 0; pointer-events: none;
        background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
        opacity: 0.35;
    }

    /* ═══════════════════════════════════════════
       HIDE STREAMLIT CHROME
    ═══════════════════════════════════════════ */
    #MainMenu, footer, header,
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="collapsedControl"] { display: none !important; }

    /* ═══════════════════════════════════════════
       SIDEBAR — GLASS PANEL
    ═══════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: rgba(6,8,16,0.85) !important;
        border-right: 1px solid var(--glass-bd) !important;
        backdrop-filter: blur(24px) !important;
        -webkit-backdrop-filter: blur(24px) !important;
    }
    [data-testid="stSidebar"] * { color: var(--text) !important; }

    /* Sidebar nav links */
    [data-testid="stSidebarNav"] a {
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin: 2px 0 !important;
        transition: background 0.2s ease !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 14px !important;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: var(--glass-hover) !important;
    }
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: rgba(26,143,255,0.15) !important;
        border-left: 3px solid var(--blue) !important;
    }

    /* ═══════════════════════════════════════════
       MAIN CONTENT AREA
    ═══════════════════════════════════════════ */
    .main .block-container {
        padding: 2rem 2.5rem !important;
        max-width: 1200px !important;
        position: relative; z-index: 2;
    }

    /* ═══════════════════════════════════════════
       HEADINGS
    ═══════════════════════════════════════════ */
    h1, h2, h3, h4 {
        font-family: 'Syne', sans-serif !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        color: #fff !important;
    }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.4rem !important; }

    /* ═══════════════════════════════════════════
       GLASS CARD UTILITY CLASS
       Usage in Python: st.markdown('<div class="glass-card">...</div>', unsafe_allow_html=True)
    ═══════════════════════════════════════════ */
    .glass-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-bd);
        border-radius: var(--radius);
        padding: 24px;
        backdrop-filter: blur(28px) saturate(160%);
        -webkit-backdrop-filter: blur(28px) saturate(160%);
        box-shadow:
            0 0 0 1px rgba(255,255,255,0.035) inset,
            0 24px 60px rgba(0,0,0,0.5);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
        animation: cardFadeUp 0.5s cubic-bezier(.22,1,.36,1) both;
    }
    .glass-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 0 0 1px rgba(255,255,255,0.06) inset,
                    0 32px 70px rgba(0,0,0,0.6),
                    0 0 40px rgba(26,143,255,0.07);
    }

    /* KPI variant */
    .glass-kpi {
        background: var(--glass-bg);
        border: 1px solid var(--glass-bd);
        border-radius: var(--radius);
        padding: 20px 24px;
        backdrop-filter: blur(28px) saturate(160%);
        -webkit-backdrop-filter: blur(28px) saturate(160%);
        text-align: center;
        box-shadow: 0 16px 40px rgba(0,0,0,0.4);
        transition: transform 0.2s ease;
        animation: cardFadeUp 0.5s cubic-bezier(.22,1,.36,1) both;
    }
    .glass-kpi:hover { transform: translateY(-4px); }

    .kpi-label {
        font-size: 11px; font-weight: 600; letter-spacing: 1px;
        text-transform: uppercase; color: var(--muted); margin-bottom: 8px;
    }
    .kpi-value {
        font-family: 'Syne', sans-serif; font-size: 2rem;
        font-weight: 800; color: #fff; line-height: 1;
    }
    .kpi-sub {
        font-size: 12px; color: var(--muted); margin-top: 6px;
    }
    .kpi-accent-gold  { border-top: 3px solid var(--gold) !important; }
    .kpi-accent-blue  { border-top: 3px solid var(--blue) !important; }
    .kpi-accent-pink  { border-top: 3px solid var(--pink) !important; }
    .kpi-accent-green { border-top: 3px solid var(--green) !important; }

    /* Badge */
    .badge {
        display: inline-flex; align-items: center; gap: 6px;
        background: rgba(245,166,35,0.12);
        border: 1px solid rgba(245,166,35,0.25);
        border-radius: 20px; padding: 4px 12px;
        font-size: 11px; color: var(--gold);
        font-weight: 600; letter-spacing: 0.5px;
    }
    .badge-dot {
        width: 6px; height: 6px; border-radius: 50%;
        background: var(--gold); display: inline-block;
        animation: pulse 1.8s ease-in-out infinite;
    }
    @keyframes pulse {
        0%,100% { opacity: 1; transform: scale(1); }
        50%      { opacity: 0.5; transform: scale(0.8); }
    }

    /* Section divider */
    .glass-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--glass-bd), transparent);
        margin: 28px 0;
    }

    /* Page title block */
    .page-header { margin-bottom: 28px; }
    .page-header h1 { margin-bottom: 6px !important; }
    .page-header p  { color: var(--muted); font-size: 14px; margin: 0; }

    /* ═══════════════════════════════════════════
       STREAMLIT WIDGETS — GLASS OVERRIDE
    ═══════════════════════════════════════════ */
    /* Selectbox, text input, number input */
    [data-testid="stSelectbox"] > div,
    [data-testid="stTextInput"] > div > div,
    [data-testid="stNumberInput"] > div > div {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid var(--glass-bd) !important;
        border-radius: 10px !important;
        color: #fff !important;
    }
    [data-testid="stSelectbox"] > div:focus-within,
    [data-testid="stTextInput"] > div > div:focus-within {
        border-color: rgba(26,143,255,0.5) !important;
        box-shadow: 0 0 0 3px rgba(26,143,255,0.12) !important;
    }

    /* Slider */
    [data-testid="stSlider"] [role="slider"] {
        background: var(--blue) !important;
    }

    /* Primary button */
    [data-testid="stButton"] button[kind="primary"],
    .stButton > button {
        background: linear-gradient(135deg, var(--blue), #0f62d4) !important;
        border: none !important;
        border-radius: 11px !important;
        color: #fff !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 0.2px !important;
        padding: 10px 24px !important;
        box-shadow: 0 4px 20px rgba(26,143,255,0.3) !important;
        transition: transform 0.15s ease, box-shadow 0.15s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 28px rgba(26,143,255,0.45) !important;
    }

    /* Metric */
    [data-testid="stMetric"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-bd) !important;
        border-radius: var(--radius) !important;
        padding: 16px 20px !important;
        backdrop-filter: blur(20px) !important;
    }
    [data-testid="stMetricLabel"] { color: var(--muted) !important; }
    [data-testid="stMetricValue"] { color: #fff !important; font-family: 'Syne', sans-serif !important; }

    /* Dataframe */
    [data-testid="stDataFrame"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-bd) !important;
        border-radius: var(--radius) !important;
        overflow: hidden !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tablist"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--glass-bd) !important;
        border-radius: 12px !important;
        padding: 4px !important;
        gap: 4px !important;
    }
    [data-testid="stTabs"] [role="tab"] {
        border-radius: 9px !important;
        color: var(--muted) !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: rgba(255,255,255,0.09) !important;
        color: #fff !important;
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        color: #fff !important;
    }

    /* Alert / info boxes */
    [data-testid="stAlert"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-bd) !important;
        border-radius: var(--radius) !important;
        backdrop-filter: blur(20px) !important;
    }

    /* ═══════════════════════════════════════════
       PLOTLY CHART GLASS BACKGROUND
    ═══════════════════════════════════════════ */
    .js-plotly-plot .plotly {
        border-radius: var(--radius) !important;
    }

    /* ═══════════════════════════════════════════
       ANIMATIONS
    ═══════════════════════════════════════════ */
    @keyframes cardFadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* Stagger delays for multiple cards */
    .glass-card:nth-child(1), .glass-kpi:nth-child(1) { animation-delay: 0.05s; }
    .glass-card:nth-child(2), .glass-kpi:nth-child(2) { animation-delay: 0.10s; }
    .glass-card:nth-child(3), .glass-kpi:nth-child(3) { animation-delay: 0.15s; }
    .glass-card:nth-child(4), .glass-kpi:nth-child(4) { animation-delay: 0.20s; }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(255,255,255,0.12);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.22); }

    </style>
    """)


def glass_card(content_html: str, extra_class: str = ""):
    """Wraps HTML content in a glass card."""
    st.markdown(f'<div class="glass-card {extra_class}">{content_html}</div>', unsafe_allow_html=True)


def glass_kpi(label: str, value: str, sub: str = "", accent: str = "blue"):
    """
    Renders a glassmorphism KPI card.
    accent: 'gold' | 'blue' | 'pink' | 'green'
    """
    st.markdown(f"""
    <div class="glass-kpi kpi-accent-{accent}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {"<div class='kpi-sub'>" + sub + "</div>" if sub else ""}
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", badge: str = ""):
    """Renders a styled page header with optional live badge."""
    badge_html = f'<div class="badge"><div class="badge-dot"></div> {badge}</div><br/>' if badge else ""
    st.markdown(f"""
    <div class="page-header">
        {badge_html}
        <h1>{title}</h1>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def divider():
    """Renders a glass-style horizontal divider."""
    st.markdown('<div class="glass-divider"></div>', unsafe_allow_html=True)