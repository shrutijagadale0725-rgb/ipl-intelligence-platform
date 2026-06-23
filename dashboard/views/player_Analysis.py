import streamlit as st
import pandas as pd
import plotly.express as px
import os

from views.shared_styles import inject_base_css, section_label, PLOTLY_LAYOUT

# ═════════════════════════════════════════════════════════════
# PAGE-SPECIFIC HTML HELPERS
# ═════════════════════════════════════════════════════════════
def _role_badge(role, color):
    """Pill badge showing the player's classified role."""
    return (
        f'<span style="display:inline-block;background:{color}20;border:1px solid {color}44;'
        f'border-radius:99px;padding:3px 12px;font-family:\'DM Sans\',sans-serif;font-size:11px;'
        f'font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:{color};">{role}</span>'
    )

def _stat_row(label, value, icon=" "):
    """Single stat row used inside player cards."""
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:13px;color:rgba(240,244,255,0.55);">{icon} {label}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:15px;font-weight:600;color:#F0F4FF;">{value}</span>'
        f'</div>'
    )

def _phase_block(phase, sr, avg, color):
    """One column in the 3-phase breakdown strip."""
    return (
        f'<div style="flex:1;background:{color}0C;border:1px solid {color}22;border-radius:16px;padding:18px 16px;text-align:center;">'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:{color};margin-bottom:12px;">{phase}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:26px;font-weight:600;color:#F0F4FF;line-height:1;">{sr}</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.35);margin:4px 0 10px;">Strike Rate</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:18px;font-weight:600;color:rgba(240,244,255,0.7);">{avg}</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.35);margin-top:4px;">Average</div>'
        f'</div>'
    )

def _consistency_bar(score, color):
    """Visual consistency bar 0-100."""
    pct = int(score * 100)
    if score >= 0.70:
        label, desc = "CONSISTENT", "Low variance — reliable scorer every innings."
    elif score >= 0.45:
        label, desc = "VARIABLE", "Mixed output — performs well in patches."
    else:
        label, desc = "BOOM OR BUST", "High variance — either dominates or fails cheaply."
    return (
        f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:22px 24px;">'
        f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:12px;">'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:22px;letter-spacing:0.05em;color:{color};">{label}</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:20px;font-weight:600;color:#F0F4FF;">{pct}<span style="font-size:12px;color:rgba(240,244,255,0.4);">/100</span></div>'
        f'</div>'
        f'<div style="width:100%;height:8px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;margin-bottom:10px;">'
        f'<div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{color}88,{color});border-radius:99px;"></div>'
        f'</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.45);">{desc}</div>'
        f'</div>'
    )

def _venue_mini_table(title, rows_data, color):
    """Best/worst venues mini table."""
    rows_html = " ".join(
        f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.6);">{v}</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:12px;font-weight:600;color:{color};">{avg:.1f}</span>'
        f'</div>'
        for v, avg in rows_data
    )
    return (
        f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 20px;">'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
        f'text-transform:uppercase;color:rgba(240,244,255,0.35);margin-bottom:12px;">{title}</div>'
        f'{rows_html}'
        f'</div>'
    )

def _comparison_winner(label, v1, v2, p1, p2, higher_is_better=True):
    if higher_is_better:
        winner = p1 if v1 > v2 else (p2 if v2 > v1 else None)
    else:
        winner = p1 if v1 < v2 else (p2 if v2 < v1 else None)
    if winner is None:
        badge = '<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(240,244,255,0.35);">Tied</span>'
    else:
        badge = (
            f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:600;'
            f'color:#00E676;">▲ {winner}</span>'
        )
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;'
        f'padding:9px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.5);">{label}</span>'
        f'<div style="display:flex;align-items:center;gap:16px;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:#00B0FF;">{v1}</span>'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.2);">vs</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:12px;color:#FF3D71;">{v2}</span>'
        f'{badge}'
        f'</div></div>'
    )

# ═════════════════════════════════════════════════════════════
# ROLE CLASSIFIER & STATS ENGINES
# ═════════════════════════════════════════════════════════════
ROLE_CONFIG = {
    "Explosive Opener":  {"color": "#FF3D71", "icon": "💥", "desc": "High-impact in Powerplay. Attacks from ball one."},
    "Classic Anchor":    {"color": "#00B0FF", "icon": "⚓", "desc": "Builds innings steadily. Low risk, high average."},
    "Finisher":          {"color": "#FFD740", "icon": "🎯", "desc": "Peaks in death overs. Elevates SR when it matters most."},
    "Middle Order Batter":{"color": "#00E676", "icon": "🏏", "desc": "Consistent presence in overs 7-15. Balances attack and defence."},
    "Lower Order Hitter": {"color": "#A78BFA", "icon": "⚡", "desc": "Quick runs late. High SR but limited average."},
}

def _estimate_innings(player_data: pd.DataFrame) -> int:
    if 'match_id' in player_data.columns:
        return player_data['match_id'].nunique()
    return max(1, len(player_data) // 20)

def classify_player_role(player_data: pd.DataFrame) -> tuple[str, dict]:
    if player_data.empty or len(player_data) < 20:
        return "Middle Order Batter", ROLE_CONFIG["Middle Order Batter"]

    total_balls = len(player_data)
    total_runs  = player_data['batsman_runs'].sum()
    overall_sr  = (total_runs / total_balls * 100) if total_balls > 0 else 0

    pp   = player_data[player_data['over'].between(1, 6)]
    death= player_data[player_data['over'].between(16, 20)]

    pp_balls    = len(pp)
    death_balls = len(death)

    pp_sr    = (pp['batsman_runs'].sum() / pp_balls * 100) if pp_balls > 5 else 0
    death_sr = (death['batsman_runs'].sum() / death_balls * 100) if death_balls > 5 else 0

    boundaries = player_data[player_data['batsman_runs'].isin([4, 6])]
    boundary_pct = len(boundaries) / total_balls * 100 if total_balls > 0 else 0

    avg = total_runs / max(1, _estimate_innings(player_data))

    if pp_balls > 0.35 * total_balls and pp_sr > 145 and boundary_pct > 18:
        return "Explosive Opener", ROLE_CONFIG["Explosive Opener"]
    if death_balls > 0.30 * total_balls and death_sr > 150:
        return "Finisher", ROLE_CONFIG["Finisher"]
    if total_balls > 100 and overall_sr < 130 and avg > 30:
        return "Classic Anchor", ROLE_CONFIG["Classic Anchor"]
    if overall_sr > 145 and avg < 18:
        return "Lower Order Hitter", ROLE_CONFIG["Lower Order Hitter"]

    return "Middle Order Batter", ROLE_CONFIG["Middle Order Batter"]

def get_phase_stats(player_data: pd.DataFrame) -> dict:
    phases = {
        "Powerplay\n(1-6)": player_data[player_data['over'].between(1, 6)],
        "Middle\n(7-15)":   player_data[player_data['over'].between(7, 15)],
        "Death\n(16-20)":   player_data[player_data['over'].between(16, 20)],
    }
    result = {}
    for name, df in phases.items():
        balls = len(df)
        runs  = df['batsman_runs'].sum() if balls > 0 else 0
        inns  = _estimate_innings(df) if balls > 0 else 1
        sr    = round(runs / balls * 100, 1) if balls > 5 else "—"
        avg   = round(runs / inns, 1) if balls > 5 else "—"
        result[name] = {"sr": sr, "avg": avg, "balls": balls}
    return result

def get_consistency_score(player_data: pd.DataFrame) -> float:
    if 'match_id' not in player_data.columns or len(player_data) < 30:
        return 0.5
    innings_scores = player_data.groupby('match_id')['batsman_runs'].sum()
    if len(innings_scores) < 5:
        return 0.5
    mean, std = innings_scores.mean(), innings_scores.std()
    if mean == 0: return 0.0
    return float(max(0.0, min(1.0, 1 - (std / mean))))

def get_venue_performance(player, deliveries, matches):
    if 'venue' not in deliveries.columns:
        venue_map = matches.set_index('id')['venue'].to_dict() if 'id' in matches.columns else {}
        deliveries = deliveries.copy()
        deliveries['venue'] = deliveries['match_id'].map(venue_map)

    p_data = deliveries[deliveries['batter'] == player].copy()
    if p_data.empty or 'venue' not in p_data.columns:
        return [], []

    venue_stats = (
        p_data.groupby('venue')
        .agg(runs=('batsman_runs', 'sum'), innings=('match_id', 'nunique'))
        .reset_index()
    )
    venue_stats = venue_stats[venue_stats['innings'] >= 2]
    venue_stats['avg'] = venue_stats['runs'] / venue_stats['innings']
    venue_stats = venue_stats.sort_values('avg', ascending=False)

    best  = [(r['venue'], r['avg']) for _, r in venue_stats.head(3).iterrows()]
    worst = [(r['venue'], r['avg']) for _, r in venue_stats.tail(3).iterrows()]
    return best, worst

def get_player_stats(player, deliveries):
    player_data = deliveries[deliveries['batter'] == player]
    runs   = int(player_data['batsman_runs'].sum())
    balls  = len(player_data)
    fours   = int((player_data['batsman_runs'] == 4).sum())
    sixes  = int((player_data['batsman_runs'] == 6).sum())
    innings = _estimate_innings(player_data)
    sr     = round((runs / balls) * 100, 2) if balls > 0 else 0
    avg    = round(runs / innings, 2) if innings > 0 else 0
    return {
        "Runs": runs, "Balls": balls, "4s": fours, "6s": sixes,
        "Strike Rate": sr, "Average": avg, "Innings": innings,
        "_data": player_data,
    }

# ═════════════════════════════════════════════════════════════
# DATA LOADER (now cached — was missing before)
# ═════════════════════════════════════════════════════════════
@st.cache_data
def load_player_data():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    deliveries = pd.read_csv(os.path.join(BASE_DIR, "data", "cleaned", "deliveries_clean.csv"))
    matches    = pd.read_csv(os.path.join(BASE_DIR, "data", "cleaned", "matches_clean.csv"))
    return matches, deliveries

# ═════════════════════════════════════════════════════════════
# MAIN PAGE RENDERER
# ═════════════════════════════════════════════════════════════
def show_player_analysis():
    inject_base_css()

    st.markdown(
        '<div style="text-align:center;padding:20px 0 36px;">'
        '<div style="display:inline-block;background:linear-gradient(135deg,rgba(0,230,118,0.12),rgba(0,176,255,0.12));'
        'border:1px solid rgba(0,230,118,0.2);border-radius:99px;padding:6px 18px;margin-bottom:20px;">'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#00E676;">🏏 Batting Intelligence</span>'
        '</div>'
        '<h1 style="font-family:\'Bebas Neue\',sans-serif;font-size:clamp(44px,7vw,72px);letter-spacing:0.06em;'
        'color:#F0F4FF;margin:0 0 12px;line-height:1;">PLAYER ANALYSIS</h1>'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:16px;color:rgba(240,244,255,0.45);margin:0;'
        'font-weight:300;">Role classification, phase intelligence & scouting insights</p>'
        '</div>', unsafe_allow_html=True
    )

    matches, deliveries = load_player_data()

    st.markdown(section_label("🔭 Player Scouting"), unsafe_allow_html=True)
    st.markdown(
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:13px;color:rgba(240,244,255,0.4);margin:-10px 0 18px;">'
        'Select any player to see their role classification, phase breakdown, consistency score, and venue intelligence.</p>',
        unsafe_allow_html=True
    )

    players = sorted(deliveries['batter'].dropna().unique())
    scout_player = st.selectbox("Select Player", players,
                                index=players.index('V Kohli') if 'V Kohli' in players else 0,
                                key="scout_select")

    p_data  = deliveries[deliveries['batter'] == scout_player]
    p_stats = get_player_stats(scout_player, deliveries)

    role, role_cfg = classify_player_role(p_data)
    role_color = role_cfg['color']
    role_desc  = role_cfg['desc']

    c_score = get_consistency_score(p_data)
    c_pct   = int(c_score * 100)
    c_color = "#00E676" if c_score >= 0.70 else ("#FFD740" if c_score >= 0.45 else "#FF3D71")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,{role_color}12,{role_color}06);'
        f'border:1px solid {role_color}28;border-radius:24px;padding:28px 28px 20px;margin-bottom:16px;">'
        f'<div style="display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px;margin-bottom:20px;">'
        f'<div>'
        f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:36px;letter-spacing:0.04em;color:#F0F4FF;line-height:1;margin-bottom:8px;">{scout_player}</div>'
        + _role_badge(f"{role_cfg['icon']} {role}", role_cfg['color'])
        + f'<div style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.45);margin-top:8px;">{role_desc}</div>'
        f'</div>'
        f'<div style="text-align:center;">'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin-bottom:6px;">Consistency</div>'
        f'<div style="font-family:\'JetBrains Mono\',monospace;font-size:40px;font-weight:600;color:{c_color};line-height:1;">{c_pct}</div>'
        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.35);">/ 100</div>'
        f'</div>'
        f'</div>'
        + _stat_row("Total Runs", f'{p_stats["Runs"]:,}', "🏏")
        + _stat_row("Strike Rate", p_stats["Strike Rate"], "⚡")
        + _stat_row("Average", p_stats["Average"], "📊")
        + _stat_row("Innings", p_stats["Innings"], "🎯")
        + _stat_row("Fours / Sixes", f'{p_stats["4s"]} / {p_stats["6s"]}', "🔥")
        + '</div>', unsafe_allow_html=True
    )

    st.markdown(section_label("⏱️ Phase-by-Phase Breakdown"), unsafe_allow_html=True)
    phase_stats = get_phase_stats(p_data)
    phase_colors = ["#00B0FF", "#00E676", "#FF3D71"]
    phase_html = '<div style="display:flex;gap:12px;margin-bottom:20px;">'
    for (phase_name, pdata), color in zip(phase_stats.items(), phase_colors):
        phase_html += _phase_block(phase_name, pdata["sr"], pdata["avg"], color)
    phase_html += '</div>'
    st.markdown(phase_html, unsafe_allow_html=True)

    st.markdown(section_label("📈 Consistency Profile"), unsafe_allow_html=True)
    st.markdown(_consistency_bar(c_score, c_color), unsafe_allow_html=True)

    best_venues, worst_venues = get_venue_performance(scout_player, deliveries, matches)
    if best_venues or worst_venues:
        st.markdown(section_label("🏟️ Venue Intelligence"), unsafe_allow_html=True)
        vc1, vc2 = st.columns(2)
        with vc1:
            if best_venues: st.markdown(_venue_mini_table("✅ Strongest Venues (avg)", best_venues, "#00E676"), unsafe_allow_html=True)
        with vc2:
            if worst_venues: st.markdown(_venue_mini_table("⚠️ Weakest Venues (avg)", worst_venues, "#FF3D71"), unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:28px 0 4px;"></div>', unsafe_allow_html=True)

    st.markdown(section_label("⚔️ Player Comparison"), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1: player1 = st.selectbox("Select Player 1", players, index=0, key="cmp1")
    with col2: player2 = st.selectbox("Select Player 2", players, index=1, key="cmp2")

    stats1 = get_player_stats(player1, deliveries)
    stats2 = get_player_stats(player2, deliveries)

    role1, rc1 = classify_player_role(stats1["_data"])
    role2, rc2 = classify_player_role(stats2["_data"])

    cc1, cc2 = st.columns(2)
    badge1 = _role_badge(f"{rc1['icon']}  {role1}", rc1['color'])
    badge2 = _role_badge(f"{rc2['icon']}  {role2}", rc2['color'])

    with cc1:
        st.markdown(
            '<div style="background:linear-gradient(135deg,#00B0FF14,#00B0FF08);border:1px solid #00B0FF33;border-radius:22px;padding:26px 24px;">'
            '<div style="margin-bottom:10px;">' + badge1 + '</div>'
            + f'<h2 style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;letter-spacing:0.04em;color:#F0F4FF;margin:0 0 18px;line-height:1.1;">{player1}</h2>'
            + _stat_row("Runs", f'{stats1["Runs"]:,}', "🏏") + _stat_row("Strike Rate", stats1["Strike Rate"], "⚡")
            + _stat_row("Average", stats1["Average"], "📊") + _stat_row("4s / 6s", f'{stats1["4s"]} / {stats1["6s"]}', "🔥") + '</div>', unsafe_allow_html=True)
    with cc2:
        st.markdown(
            '<div style="background:linear-gradient(135deg,#FF3D7114,#FF3D7108);border:1px solid #FF3D7133;border-radius:22px;padding:26px 24px;">'
            '<div style="margin-bottom:10px;">' + badge2 + '</div>'
            + f'<h2 style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;letter-spacing:0.04em;color:#F0F4FF;margin:0 0 18px;line-height:1.1;">{player2}</h2>'
            + _stat_row("Runs", f'{stats2["Runs"]:,}', "🏏") + _stat_row("Strike Rate", stats2["Strike Rate"], "⚡")
            + _stat_row("Average", stats2["Average"], "📊") + _stat_row("4s / 6s", f'{stats2["4s"]} / {stats2["6s"]}', "🔥") + '</div>', unsafe_allow_html=True)

    st.markdown(section_label("📋 Head-to-Head Summary"), unsafe_allow_html=True)
    summary_html = (
        '<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:18px 22px;margin-bottom:20px;">'
        + _comparison_winner("Runs", f'{stats1["Runs"]:,}', f'{stats2["Runs"]:,}', player1, player2)
        + _comparison_winner("Strike Rate", stats1["Strike Rate"], stats2["Strike Rate"], player1, player2)
        + _comparison_winner("Average", stats1["Average"], stats2["Average"], player1, player2)
        + _comparison_winner("Fours", stats1["4s"], stats2["4s"], player1, player2)
        + _comparison_winner("Sixes", stats1["6s"], stats2["6s"], player1, player2) + '</div>'
    )
    st.markdown(summary_html, unsafe_allow_html=True)

    st.markdown(section_label("📊 Head-to-Head Chart"), unsafe_allow_html=True)
    comparison_df = pd.DataFrame({
        "Metric": ["Runs", "Strike Rate", "4s", "6s"],
        player1: [stats1["Runs"], stats1["Strike Rate"], stats1["4s"], stats1["6s"]],
        player2: [stats2["Runs"], stats2["Strike Rate"], stats2["4s"], stats2["6s"]],
    })
    fig2 = px.bar(comparison_df, x="Metric", y=[player1, player2], barmode="group",
                  color_discrete_map={player1: "#00B0FF", player2: "#FF3D71"})
    fig2.update_traces(marker_line_width=0)
    fig2.update_layout(**PLOTLY_LAYOUT, title=f"{player1} vs {player2}",
                       legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#F0F4FF")))
    st.plotly_chart(fig2, use_container_width=True)