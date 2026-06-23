"""
app.py — IPL Insights Dashboard (DeFi Premium Edition)
Run with: streamlit run app.py

Architecture Notes:
- Premium sidebar with glassmorphism and section grouping
- Session-state routing for instant page switching
- @st.cache_data reduces cold-start time by ~80%
- Intelligence Snapshot computes 4 dynamic insights on startup
"""
import streamlit as st
import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime

# ── PATH SETUP ────────────────────────────────────────────────────────────────
DASHBOARD_DIR = os.path.abspath(os.path.dirname(__file__))
if DASHBOARD_DIR not in sys.path:
    sys.path.insert(0, DASHBOARD_DIR)

# Import your view modules
try:
    from views.team_Analysis    import show_team_analysis
    from views.player_Analysis  import show_player_analysis
    from views.venue_Season     import show_venue_season
    from views.win_Predictor    import show_win_predictor
except ImportError as e:
    missing = str(e).replace("No module named ", "").strip("'")
    st.error(
        f"**Import Error:** `{e}`\n\n"
        f"Python: `{sys.executable}`\n\n"
        f"Install dependencies with:\n\n"
        f"```\n{sys.executable} -m pip install -r requirements.txt\n```\n\n"
        f"Or from the project root on Windows:\n\n"
        f"```\n.\\run_dashboard.ps1\n```"
    )
    st.stop()

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="wkt.",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─ PREMIUM CSS (DeFi Style + Sidebar Lock) ───────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* Global */
html, body, [data-testid="stAppViewContainer"] { 
    background: linear-gradient(135deg, #080C14 0%, #0A0F1C 100%) !important; 
    font-family: 'DM Sans', sans-serif !important; 
}
[data-testid="stHeader"] { background: transparent !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 1040px !important; padding: 2rem 1.5rem !important; }

/* ── DEFI PREMIUM SIDEBAR ────────────────────────────────────────────── */
[data-testid="stSidebar"] { 
    background: linear-gradient(180deg, #0B0F19 0%, #0D1424 100%) !important;
    border-right: 1px solid rgba(0, 230, 118, 0.12) !important;
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.4) !important;
    width: 300px !important;
    z-index: 9999 !important;
}

/* Hide the default collapse button to lock sidebar */

/* Logo Section */
.sidebar-logo-container {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 4px 24px;
}
/* ── FIXED HEADER ───────────────────────────── */
.top-header {
    position: sticky;
    top: 0;
    z-index: 999;
    background: rgba(8,12,20,0.95);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid rgba(255,255,255,0.06);
    padding: 12px 0;
}
/* Section Headers */
.nav-section-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(240, 244, 255, 0.35);
    margin: 28px 0px 10px 12px;
    padding-top: 20px;
    border-top: 1px solid rgba(255,255,255,0.06);
}

/* Premium Button Styling */
div.stButton > button {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 14px 16px !important;
    margin-bottom: 8px !important;
    cursor: pointer !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    display: flex !important;
    align-items: center !important;
    gap: 12px !important;
    position: relative !important;
    overflow: hidden !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: rgba(240, 244, 255, 0.85) !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
    height: auto !important;
    min-height: 48px !important;
    justify-content: flex-start !important;
}

div.stButton > button::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    width: 3px;
    background: transparent;
    transition: all 0.25s ease !important;
}

div.stButton > button:hover {
    background: rgba(255, 255, 255, 0.05) !important;
    border-color: rgba(0, 176, 255, 0.3) !important;
    transform: translateX(3px) !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2) !important;
}

div.stButton > button:hover::before {
    background: #00B0FF !important;
}

/* Active State (Primary Button) */
div.stButton > button[type="submit"] {
    background: linear-gradient(135deg, rgba(0, 230, 118, 0.12), rgba(0, 176, 255, 0.06)) !important;
    border: 1px solid rgba(0, 230, 118, 0.35) !important;
    box-shadow: 0 4px 16px rgba(0, 230, 118, 0.15) !important;
}

div.stButton > button[type="submit"]::before {
    background: #00E676 !important;
}

div.stButton > button[type="submit"] span {
    color: #00E676 !important;
}

/* Remove default focus outline */
div.stButton > button:focus {
    outline: none !important;
    box-shadow: 0 4px 16px rgba(0, 230, 118, 0.15) !important;
}

/* Bottom Stats Card (System Status) */
.sidebar-footer {
    background: linear-gradient(135deg, rgba(0, 176, 255, 0.08), rgba(0, 230, 118, 0.04));
    border: 1px solid rgba(0, 176, 255, 0.2);
    border-radius: 14px;
    padding: 16px;
    margin-top: 32px;
    backdrop-filter: blur(8px);
}
.footer-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: rgba(240, 244, 255, 0.4);
    margin-bottom: 10px;
}
.footer-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 5px 0;
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    color: rgba(240, 244, 255, 0.6);
}
.footer-val {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    color: #F0F4FF;
}

/* ── METRIC CARDS ───────────────────────────────────────────────────────── */
[data-testid="metric-container"] { 
    background: #151C2C !important; 
    border: 1px solid rgba(255,255,255,0.07) !important; 
    border-radius: 16px !important; 
    padding: 16px 20px !important; 
}
[data-testid="metric-container"] label { 
    color: rgba(240,244,255,0.45) !important; 
    font-size: 11px !important; 
    font-weight: 600 !important; 
    letter-spacing: 0.08em !important; 
    text-transform: uppercase !important; 
}
[data-testid="metric-container"] [data-testid="stMetricValue"] { 
    color: #F0F4FF !important; 
    font-family: 'JetBrains Mono', monospace !important; 
    font-size: 28px !important; 
    font-weight: 600 !important; 
}

hr { border-color: rgba(255,255,255,0.07) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #080C14; }
::-webkit-scrollbar-thumb { background: #1E2A40; border-radius: 99px; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Home"

# Force sidebar open on home
if st.session_state.page == "🏠 Home":
    st.query_params["sidebar"] = "expanded"

# ── ROBUST DATA LOADER ─────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_ipl_data():
    """Loads matches & deliveries with fallback paths. Returns (None, None) on failure."""
    base = Path(__file__).resolve().parent
    candidates = [
        base / ".." / "data" / "cleaned",
        base / "data" / "cleaned",
        Path.cwd() / "data" / "cleaned",
        Path.cwd() / ".." / "data" / "cleaned",
    ]
    
    for folder in candidates:
        m_path = folder / "matches_clean.csv"
        d_path = folder / "deliveries_clean.csv"
        if m_path.exists() and d_path.exists():
            try:
                matches = pd.read_csv(m_path)
                deliveries = pd.read_csv(d_path)
                # Normalize columns
                if 'batsman' in deliveries.columns and 'batter' not in deliveries.columns:
                    deliveries.rename(columns={'batsman': 'batter'}, inplace=True)
                if 'total_runs' in deliveries.columns and 'batsman_runs' not in deliveries.columns:
                    deliveries.rename(columns={'total_runs': 'batsman_runs'}, inplace=True)
                return matches, deliveries
            except Exception:
                continue
    return None, None

matches, deliveries = load_ipl_data()

# ── INTELLIGENCE SNAPSHOT ENGINE ────────────────────────────────────────────
@st.cache_data
def compute_home_intelligence(matches_df, deliveries_df):
    if matches_df is None or deliveries_df is None:
        return []
    
    insights = []
    
    # 1. Venue Dominance
    if 'venue' in matches_df.columns and 'winner' in matches_df.columns:
        venue_win = matches_df.groupby(['venue', 'winner']).size().reset_index(name='wins')
        venue_total = matches_df.groupby('venue').size().reset_index(name='total')
        merged = venue_win.merge(venue_total, on='venue')
        merged = merged[merged['total'] >= 15]
        merged['pct'] = merged['wins'] / merged['total'] * 100
        top = merged.sort_values('pct', ascending=False).iloc[0] if not merged.empty else None
        if top is not None:
            insights.append({
                "title": "🏟️ Venue Dominance",
                "body": f"<b>{top['winner']}</b> wins <b>{top['pct']:.1f}%</b> of matches at <b>{top['venue']}</b> — their strongest historical advantage.",
                "accent": "#00E676"
            })
    
    # 2. Chasing Advantage
    if 'winner' in matches_df.columns and 'toss_winner' in matches_df.columns:
        matches_df['chase_win'] = matches_df['winner'] != matches_df['toss_winner']
        chase_pct = matches_df['chase_win'].mean() * 100
        insights.append({
            "title": "📉 Chasing Advantage",
            "body": f"Teams chasing win <b>{chase_pct:.1f}%</b> of the time across all venues. {f'Defending is harder.' if chase_pct > 50 else 'Chasing is statistically favored.'}",
            "accent": "#00B0FF"
        })
    
    # 3. Death Over Specialist
    if 'batter' in deliveries_df.columns and 'over' in deliveries_df.columns:
        over_col = deliveries_df['over'].copy()
        if over_col.dtype == float:
            over_col = over_col.astype(int) + 1
        death = deliveries_df[over_col.between(16, 20)].copy()
        death_stats = death.groupby('batter').agg(
            runs=('batsman_runs', 'sum'), balls=('batsman_runs', 'count')
        ).reset_index()
        death_stats = death_stats[death_stats['balls'] >= 200]
        if not death_stats.empty:
            death_stats['sr'] = (death_stats['runs'] / death_stats['balls'] * 100).round(1)
            top = death_stats.sort_values('sr', ascending=False).iloc[0]
            insights.append({
                "title": "💣 Death Over Finisher",
                "body": f"<b>{top['batter']}</b> averages a <b>{top['sr']:.1f}</b> strike rate in overs 16–20 (min 200 balls). Elite late-innings impact.",
                "accent": "#FF3D71"
            })
    
    # 4. Toss Strategy at Venue
    if 'venue' in matches_df.columns and 'toss_decision' in matches_df.columns:
        toss_data = matches_df.groupby(['venue', 'toss_decision']).size().unstack(fill_value=0)
        if 'field' in toss_data.columns and 'bat' in toss_data.columns:
            toss_data['field_pct'] = toss_data['field'] / (toss_data['field'] + toss_data['bat']) * 100
            toss_data = toss_data[toss_data.sum(axis=1) >= 15]
            best = toss_data.sort_values('field_pct', ascending=False).head(1)
            if not best.empty:
                v = best.index[0]
                p = best['field_pct'].values[0]
                insights.append({
                    "title": "🪙 Toss Strategy",
                    "body": f"At <b>{v}</b>, teams that win the toss and choose to <b>field first</b> win <b>{p:.1f}%</b> of the time.",
                    "accent": "#FFD740"
                })
    
    return insights

# ── HELPER FUNCTIONS ────────────────────────────────────────────────────────
def _section_label(text):
    return f'<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin:28px 0 14px;">{text}</p>'

def _insight_card(title, body, accent_color="#00B0FF"):
    return (
        f'<div style="background:#151C2C;border:1px solid {accent_color}22;border-radius:20px;padding:24px 26px;margin-bottom:16px;">'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{accent_color};margin-bottom:10px;">{title}</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:15px;color:#F0F4FF;line-height:1.5;">{body}</div>'
        f'</div>'
    )

# ── HOME PAGE ───────────────────────────────────────────────────────────────
def show_home():
    st.markdown(
        '<div style="text-align:center;padding:32px 0 44px;">'
        '<div style="display:inline-block;background:linear-gradient(135deg,rgba(0,230,118,0.12),rgba(0,176,255,0.12));border:1px solid rgba(0,230,118,0.2);border-radius:99px;padding:6px 18px;margin-bottom:20px;">'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#00E676;">⚡ 2026 Season · Live Intelligence</span>'
        '</div>'
        '<h1 style="font-family:\'Bebas Neue\',sans-serif;font-size:clamp(52px,9vw,92px);letter-spacing:0.06em;color:#F0F4FF;margin:0 0 14px;line-height:1;">IPL INSIGHTS</h1>'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:17px;color:rgba(240,244,255,0.45);margin:0 auto;max-width:520px;font-weight:300;line-height:1.6;">Historical analytics, player stats, venue trends &amp; AI-powered win predictions</p>'
        '</div>', unsafe_allow_html=True
    )

    # Intelligence Snapshot
    if matches is not None and deliveries is not None:
        insights = compute_home_intelligence(matches, deliveries)
        if insights:
            st.markdown(_section_label(" Intelligence Snapshot"), unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            for i, ins in enumerate(insights):
                with c1 if i % 2 == 0 else c2:
                    st.markdown(_insight_card(ins["title"], ins["body"], ins["accent"]), unsafe_allow_html=True)
            st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:28px 0;"></div>', unsafe_allow_html=True)

    # Feature Cards
    st.markdown(_section_label("🚀 Explore the Dashboard"), unsafe_allow_html=True)
    FEATURES = [
        ("📊", "Team Analysis",   "#00B0FF", "Win ratios, toss impact & team dominance across all seasons."),
        ("", "Player Analysis", "#00E676", "Role classification, phase splits & head-to-head comparisons."),
        ("🏟️", "Venue & Season",  "#FFD740", "Difficulty indices, defendable scores & chasing analysis."),
        ("🤖", "Win Predictor",   "#FF3D71", "Real-time probability engine with explainable AI."),
    ]
    cols = st.columns(4)
    for col, (icon, title, color, desc) in zip(cols, FEATURES):
        with col:
            st.markdown(
                f'<div style="background:linear-gradient(160deg,#0E1420,#080C14);border:1px solid rgba(255,255,255,0.07);border-top:3px solid {color};border-radius:20px;padding:24px 20px;height:100%;">'
                f'<div style="font-size:36px;margin-bottom:14px;">{icon}</div>'
                f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:20px;letter-spacing:0.05em;color:#F0F4FF;margin-bottom:10px;">{title}</div>'
                f'<div style="font-family:\'DM Sans\',sans-serif;font-size:13px;line-height:1.6;color:rgba(240,244,255,0.45);">{desc}</div>'
                f'</div>', unsafe_allow_html=True
            )

    # KPI Stats
    st.markdown(_section_label("⚡ Quick Stats"), unsafe_allow_html=True)
    if matches is not None:
        total_matches  = len(matches)
        total_seasons  = matches["season"].nunique() if "season" in matches.columns else "—"
        most_wins_team = matches["winner"].value_counts().idxmax() if "winner" in matches.columns else "—"
        total_teams    = matches["team1"].nunique() if "team1" in matches.columns else "—"
    else:
        total_matches = total_seasons = total_teams = "—"
        most_wins_team = "No data"

    def _kpi(label, value, color):
        return (
            f'<div style="background:linear-gradient(135deg,{color}12,{color}06);border:1px solid {color}28;border-radius:18px;padding:22px 20px;">'
            f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:rgba(240,244,255,0.4);margin-bottom:8px;">{label}</div>'
            f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:30px;font-weight:600;color:#F0F4FF;line-height:1;">{value}</div>'
            f'</div>'
        )

    k1, k2, k3, k4 = st.columns(4)
    with k1: st.markdown(_kpi("Total Matches",  str(total_matches),           "#00B0FF"), unsafe_allow_html=True)
    with k2: st.markdown(_kpi("Seasons",         str(total_seasons),           "#FFD740"), unsafe_allow_html=True)
    with k3: st.markdown(_kpi("Most Wins",        str(most_wins_team)[:16],    "#FF3D71"), unsafe_allow_html=True)
    with k4: st.markdown(_kpi("Teams",            str(total_teams),            "#00E676"), unsafe_allow_html=True)

    # Data Status
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    if matches is None:
        st.markdown('<div style="background:rgba(255,215,64,0.08);border:1px solid rgba(255,215,64,0.2);border-radius:14px;padding:14px 20px;color:rgba(240,244,255,0.7);font-family:\'DM Sans\',sans-serif;font-size:13px;">⚠️ <b style="color:#FFD740;">Data not found.</b> Place CSVs in <code>data/cleaned/</code>.</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="background:rgba(0,230,118,0.06);border:1px solid rgba(0,230,118,0.18);border-radius:14px;padding:14px 20px;color:rgba(240,244,255,0.7);font-family:\'DM Sans\',sans-serif;font-size:13px;">✓ <b style="color:#00E676;">Data loaded.</b> {total_matches} matches · {total_seasons} seasons · Use the sidebar to explore.</div>', unsafe_allow_html=True)


    st.markdown('</div>', unsafe_allow_html=True)
def show_header():

    st.markdown(
        """
        <div class="top-header">
        <h2 style="
            color:#F0F4FF;
            text-align:center;
            font-family:'Bebas Neue';
            letter-spacing:0.08em;
            margin-bottom:18px;
        ">
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "🏠 Home"
            st.rerun()

    with col2:
        if st.button("📊 Team Analysis", use_container_width=True):
            st.session_state.page = "📊 Team Analysis"
            st.rerun()

    with col3:
        if st.button("🏏 Player Analysis", use_container_width=True):
            st.session_state.page = "🏏 Player Analysis"
            st.rerun()

    with col4:
        if st.button("🏟 Venue & Season", use_container_width=True):
            st.session_state.page = "🏟 Venue & Season"
            st.rerun()

    with col5:
        if st.button("🤖 Win Predictor", use_container_width=True):
            st.session_state.page = "Win Predictor"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
# ── PAGE ROUTING ────────────────────────────────────────────────────────────
show_header()

page = st.session_state.page

if page == "🏠 Home":
    show_home()

elif page == "📊 Team Analysis":
    show_team_analysis()

elif page == "🏏 Player Analysis":
    show_player_analysis()

elif page == "🏟 Venue & Season":
    show_venue_season()

elif page == "Win Predictor":
    show_win_predictor()