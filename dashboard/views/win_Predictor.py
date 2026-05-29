import streamlit as st
import pandas as pd
import pickle
import os

# ── LOAD MODEL ─────────────────────────────────────────────
model_path = os.path.join(os.path.dirname(__file__), "..", "..", "models", "pipe.pkl")
pipe = pickle.load(open(model_path, "rb"))

# ── LOAD DATA ──────────────────────────────────────────────
matches_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "cleaned", "matches_clean.csv")
matches = pd.read_csv(matches_path)

teams = [
    'Mumbai Indians', 'Chennai Super Kings', 'Royal Challengers Bengaluru',
    'Kolkata Knight Riders', 'Sunrisers Hyderabad', 'Rajasthan Royals',
    'Delhi Capitals', 'Punjab Kings', 'Lucknow Super Giants', 'Gujarat Titans'
]

cities = sorted(matches['city'].dropna().unique())

TEAM_COLORS = {
    'Mumbai Indians':              ('#004BA0', '#00BFFF'),
    'Chennai Super Kings':         ('#F9CD05', '#FF8C00'),
    'Royal Challengers Bengaluru': ('#CC0000', '#FFD700'),
    'Kolkata Knight Riders':       ('#3A225D', '#B3A123'),
    'Sunrisers Hyderabad':         ('#F7A721', '#E8461B'),
    'Rajasthan Royals':            ('#EA1A85', '#254AA5'),
    'Delhi Capitals':              ('#0078BC', '#EF1C25'),
    'Punjab Kings':                ('#ED1B24', '#A7A9AC'),
    'Lucknow Super Giants':        ('#A72056', '#FFCC00'),
    'Gujarat Titans':              ('#1C2B5E', '#00D4FF'),
}

TEAM_ABBR = {
    'Mumbai Indians': 'MI', 'Chennai Super Kings': 'CSK',
    'Royal Challengers Bengaluru': 'RCB', 'Kolkata Knight Riders': 'KKR',
    'Sunrisers Hyderabad': 'SRH', 'Rajasthan Royals': 'RR',
    'Delhi Capitals': 'DC', 'Punjab Kings': 'PBKS',
    'Lucknow Super Giants': 'LSG', 'Gujarat Titans': 'GT',
}


# ── CSS ────────────────────────────────────────────────────
def inject_css():
    css = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [data-testid="stAppViewContainer"] { background: #080C14 !important; font-family: 'DM Sans', sans-serif !important; }
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stSidebar"] { display: none; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { max-width: 900px !important; padding: 2rem 1.5rem !important; }
[data-testid="stSelectbox"] > div > div, [data-testid="stNumberInput"] input { background: #151C2C !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; color: #F0F4FF !important; font-family: 'DM Sans', sans-serif !important; font-size: 15px !important; }
[data-testid="stSelectbox"] label, [data-testid="stNumberInput"] label { color: rgba(240,244,255,0.45) !important; font-size: 12px !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
[data-testid="stButton"] > button { background: rgba(255,255,255,0.05) !important; color: rgba(240,244,255,0.7) !important; font-family: 'DM Sans', sans-serif !important; font-size: 13px !important; font-weight: 600 !important; border: 1px solid rgba(255,255,255,0.1) !important; border-radius: 10px !important; padding: 8px 16px !important; width: auto !important; box-shadow: none !important; transition: all 0.2s ease !important; }
[data-testid="stButton"] > button:hover { background: rgba(0,176,255,0.1) !important; border-color: rgba(0,176,255,0.3) !important; color: #F0F4FF !important; }
button[data-testid="baseButton-secondary"]:has-text("PREDICT"), [data-testid="stButton"]:nth-of-type(2) > button { width: 100% !important; background: linear-gradient(135deg, #00E676, #00B0FF) !important; color: #080C14 !important; font-family: 'Bebas Neue', sans-serif !important; font-size: 22px !important; letter-spacing: 0.12em !important; border: none !important; border-radius: 16px !important; padding: 18px 0 !important; margin-top: 8px !important; box-shadow: 0 4px 24px rgba(0,230,118,0.25) !important; }
[data-testid="metric-container"] { background: #151C2C !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 16px !important; padding: 16px 20px !important; }
[data-testid="metric-container"] label { color: rgba(240,244,255,0.45) !important; font-size: 11px !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #F0F4FF !important; font-family: 'JetBrains Mono', monospace !important; font-size: 28px !important; font-weight: 600 !important; }
hr { border-color: rgba(255,255,255,0.07) !important; }
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #080C14; }
::-webkit-scrollbar-thumb { background: #1E2A40; border-radius: 99px; }
</style>"""
    st.markdown(css, unsafe_allow_html=True)


# ── HTML HELPERS  (single-line, no indented nesting) ───────
def _card_wrap(label, content):
    """Wraps content in a dark card with a small section label."""
    return (
        '<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:24px;padding:28px 28px 20px;margin-bottom:16px;">'
        f'<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin:0 0 20px;">{label}</p>'
        f'{content}'
        '</div>'
    )


def _section_label(text):
    return (
        f'<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;'
        f'letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin:24px 0 12px;">{text}</p>'
    )


def _team_card(team, abbr, role, pct, c1, c2):
    return (
        f'<div style="flex:1;background:linear-gradient(135deg,{c1}18,{c2}10);border:1px solid {c1}44;border-radius:20px;padding:28px 20px;text-align:center;">'
        f'<div style="display:inline-block;background:{c1}33;border:1px solid {c1}55;border-radius:10px;padding:4px 12px;margin-bottom:14px;">'
        f'<span style="font-family:\'Bebas Neue\',sans-serif;font-size:14px;letter-spacing:0.1em;color:{c2};">{role} · {abbr}</span>'
        '</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:13px;font-weight:500;color:rgba(240,244,255,0.55);margin-bottom:6px;">{team}</div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:76px;line-height:1;color:#F0F4FF;margin:8px 0;">'
        f'{pct}<span style="font-size:32px;color:rgba(240,244,255,0.4);">%</span>'
        '</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:{c2};opacity:0.85;">Win Probability</div>'
        '</div>'
    )


def _vs_divider():
    return (
        '<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;gap:8px;padding:0 4px;">'
        '<div style="flex:1;width:1px;background:rgba(255,255,255,0.07);"></div>'
        '<span style="font-family:\'Bebas Neue\',sans-serif;font-size:18px;letter-spacing:0.1em;color:rgba(240,244,255,0.2);">VS</span>'
        '<div style="flex:1;width:1px;background:rgba(255,255,255,0.07);"></div>'
        '</div>'
    )


def _momentum_bar(bat_abbr, bowl_abbr, win_pct, loss_pct, bat_c1, bat_c2, bowl_c2):
    return (
        '<div style="margin-top:24px;">'
        '<div style="display:flex;justify-content:space-between;margin-bottom:8px;">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:{bat_c2};">{bat_abbr} {win_pct}%</span>'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:{bowl_c2};">{bowl_abbr} {loss_pct}%</span>'
        '</div>'
        '<div style="width:100%;height:8px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
        f'<div style="width:{win_pct}%;height:100%;background:linear-gradient(90deg,{bat_c1},{bat_c2});border-radius:99px;"></div>'
        '</div>'
        '</div>'
    )


def _pressure_card(p_label, p_color, p_width, pressure):
    return (
        '<div style="flex:1;background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:24px;">'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin:0 0 18px;">🔥 Pressure Meter</p>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:36px;line-height:1;color:{p_color};margin-bottom:4px;">{p_label}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:13px;color:rgba(240,244,255,0.4);margin-bottom:20px;">Index: {pressure}</div>'
        '<div style="width:100%;height:10px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
        f'<div style="width:{p_width};height:100%;background:linear-gradient(90deg,{p_color}88,{p_color});border-radius:99px;box-shadow:0 0 12px {p_color}55;"></div>'
        '</div>'
        '<div style="display:flex;justify-content:space-between;margin-top:8px;">'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.2);">Comfortable</span>'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.2);">Critical</span>'
        '</div>'
        '</div>'
    )


def _commentary_card(ins_color, ins_emoji, ins_title, ins_line1, ins_line2):
    return (
        f'<div style="flex:1.2;background:#0E1420;border:1px solid {ins_color}2a;border-left:4px solid {ins_color};border-radius:20px;padding:24px;">'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin:0 0 14px;">🧠 AI Commentary</p>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:26px;letter-spacing:0.06em;color:{ins_color};margin-bottom:12px;">{ins_emoji} {ins_title}</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:14px;line-height:1.75;color:rgba(240,244,255,0.75);font-weight:400;">{ins_line1}<br><br>{ins_line2}</div>'
        '</div>'
    )


# ── MAIN ───────────────────────────────────────────────────
def show_win_predictor():

    inject_css()

    # HERO
    st.markdown(
        '<div style="text-align:center;padding:20px 0 36px;">'
        '<div style="display:inline-block;background:linear-gradient(135deg,rgba(0,230,118,0.12),rgba(0,176,255,0.12));border:1px solid rgba(0,230,118,0.2);border-radius:99px;padding:6px 18px;margin-bottom:20px;">'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;color:#00E676;">⚡ Live Match Intelligence</span>'
        '</div>'
        '<h1 style="font-family:\'Bebas Neue\',sans-serif;font-size:clamp(48px,8vw,80px);letter-spacing:0.06em;color:#F0F4FF;margin:0 0 12px;line-height:1;">IPL WIN PREDICTOR</h1>'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:16px;color:rgba(240,244,255,0.45);margin:0;font-weight:300;">Real-time probability engine powered by machine learning</p>'
        '</div>',
        unsafe_allow_html=True
    )

    # MATCH SETUP CARD (label only — inputs rendered by Streamlit widgets below)
    st.markdown(_card_wrap("🏏 Match Setup", ""), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        batting_team = st.selectbox("Batting Team", sorted(teams))
    with col2:
        bowling_team = st.selectbox("Bowling Team", sorted(teams))
    city = st.selectbox("Match City", cities)

    # MATCH SITUATION CARD
    st.markdown(_card_wrap("📊 Match Situation", ""), unsafe_allow_html=True)
    target = st.number_input("Target Score", min_value=1)
    col3, col4, col5 = st.columns(3)
    with col3:
        score = st.number_input("Current Score", min_value=0)
    with col4:
        overs = st.number_input("Overs Completed", min_value=0.1, max_value=20.0, step=0.1)
    with col5:
        wickets = st.number_input("Wickets Out", min_value=0, max_value=10)

    predict = st.button("⚡  PREDICT OUTCOME")

    if not predict:
        return

    # ── VALIDATION ─────────────────────────────────────────
    if batting_team == bowling_team:
        st.markdown(
            '<div style="background:rgba(255,61,113,0.1);border:1px solid rgba(255,61,113,0.3);border-radius:14px;padding:16px 20px;color:#FF3D71;font-family:\'DM Sans\',sans-serif;font-weight:600;margin-top:12px;">⚠️ Batting and bowling teams cannot be the same.</div>',
            unsafe_allow_html=True
        )
        return

    # ── CALCULATIONS ───────────────────────────────────────
    runs_left    = target - score
    balls_left   = 120 - int(overs * 6)
    wickets_left = 10 - wickets
    crr          = score / overs if overs > 0 else 0
    rrr          = (runs_left * 6) / balls_left if balls_left > 0 else 0

    input_df = pd.DataFrame({
        'batting_team':  [batting_team], 'bowling_team':  [bowling_team],
        'city':          [city],         'runs_left':     [runs_left],
        'balls_left':    [balls_left],   'wickets_left':  [wickets_left],
        'total_runs_x':  [target],       'crr':           [crr],
        'rrr':           [rrr],
    })

    result   = pipe.predict_proba(input_df)
    loss     = result[0][0]
    win      = result[0][1]
    win_pct  = round(win  * 100)
    loss_pct = round(loss * 100)

    bat_c1,  bat_c2  = TEAM_COLORS.get(batting_team,  ('#00E676', '#00B0FF'))
    bowl_c1, bowl_c2 = TEAM_COLORS.get(bowling_team, ('#FF3D71', '#FFD740'))
    bat_abbr         = TEAM_ABBR.get(batting_team,  batting_team[:3].upper())
    bowl_abbr        = TEAM_ABBR.get(bowling_team, bowling_team[:3].upper())

    # ── PREDICTION SCOREBOARD ──────────────────────────────
    glow_left  = f'<div style="position:absolute;top:-60px;left:-60px;width:220px;height:220px;background:radial-gradient(circle,{bat_c1}22 0%,transparent 70%);border-radius:50%;pointer-events:none;"></div>'
    glow_right = f'<div style="position:absolute;bottom:-60px;right:-60px;width:220px;height:220px;background:radial-gradient(circle,{bowl_c1}22 0%,transparent 70%);border-radius:50%;pointer-events:none;"></div>'
    cards_row  = (
        '<div style="display:flex;gap:16px;position:relative;">'
        + _team_card(batting_team,  bat_abbr,  "BATTING",  win_pct,  bat_c1,  bat_c2)
        + _vs_divider()
        + _team_card(bowling_team, bowl_abbr, "BOWLING", loss_pct, bowl_c1, bowl_c2)
        + '</div>'
    )
    scoreboard = (
        '<div style="position:relative;background:linear-gradient(160deg,#0E1420 0%,#080C14 100%);border:1px solid rgba(255,255,255,0.08);border-radius:28px;padding:36px 32px 32px;margin:28px 0 20px;overflow:hidden;">'
        + glow_left + glow_right
        + _section_label("🧠 AI Prediction Result")
        + cards_row
        + _momentum_bar(bat_abbr, bowl_abbr, win_pct, loss_pct, bat_c1, bat_c2, bowl_c2)
        + '</div>'
    )
    st.markdown(scoreboard, unsafe_allow_html=True)

    # ── MATCH STATS ────────────────────────────────────────
    st.markdown(_section_label("📊 Match Situation"), unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:  st.metric("Runs Left",   runs_left)
    with c2:  st.metric("Balls Left",  balls_left)
    with c3:  st.metric("Current RR",  round(crr, 2))
    with c4:  st.metric("Required RR", round(rrr, 2))

    # ── PRESSURE ───────────────────────────────────────────
    pressure     = round(rrr - crr, 2)
    pressure_abs = abs(pressure)

    if pressure < 0 or pressure_abs <= 1:
        p_label, p_color, p_width = "LOW PRESSURE",      "#00E676", "22%"
    elif pressure_abs <= 3:
        p_label, p_color, p_width = "MODERATE PRESSURE", "#FFD740", "60%"
    else:
        p_label, p_color, p_width = "HIGH PRESSURE",     "#FF3D71", "95%"

    # ── COMMENTARY ─────────────────────────────────────────
    if win > 0.75:
        ins_color, ins_emoji, ins_title = "#00E676", "🔥", "Dominant Chase"
        ins_line1 = f"{batting_team} is completely controlling the chase."
        ins_line2 = "Current momentum strongly favors them — a very high probability of winning."
    elif win > 0.55:
        ins_color, ins_emoji, ins_title = "#00B0FF", "📈", "Upper Hand"
        ins_line1 = f"{batting_team} currently holds the advantage."
        ins_line2 = "Their scoring pace and wickets in hand are keeping them ahead."
    elif win > 0.45:
        ins_color, ins_emoji, ins_title = "#FFD740", "⚖️", "Neck & Neck"
        ins_line1 = "This match could go either way."
        ins_line2 = "A single over can swing the result completely."
    else:
        ins_color, ins_emoji, ins_title = "#FF3D71", "🚨", "Under Pressure"
        ins_line1 = f"{bowling_team} is firmly in control right now."
        ins_line2 = f"Pressure is mounting heavily on {batting_team}."

    bottom_row = (
        '<div style="display:flex;gap:16px;margin-top:20px;margin-bottom:32px;">'
        + _pressure_card(p_label, p_color, p_width, pressure)
        + _commentary_card(ins_color, ins_emoji, ins_title, ins_line1, ins_line2)
        + '</div>'
    )
    st.markdown(bottom_row, unsafe_allow_html=True)