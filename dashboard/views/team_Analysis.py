import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path

# ═════════════════════════════════════════════════════════════
# CSS & UI HELPERS (Matches your existing design system)
# ═════════════════════════════════════════════════════════════
def inject_team_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background: #080C14 !important; font-family: 'DM Sans', sans-serif !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    [data-testid="stSidebar"] { display: none; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { max-width: 960px !important; padding: 2rem 1.5rem !important; }
    [data-testid="stSelectbox"] > div > div { background: #151C2C !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 12px !important; color: #F0F4FF !important; font-family: 'DM Sans', sans-serif !important; font-size: 15px !important; }
    [data-testid="stSelectbox"] label { color: rgba(240,244,255,0.45) !important; font-size: 12px !important; font-weight: 600 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
    ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #080C14; } ::-webkit-scrollbar-thumb { background: #1E2A40; border-radius: 99px; }
    </style>
    """, unsafe_allow_html=True)

def _section_label(text, subtext=""):
    html = f'<p style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:rgba(240,244,255,0.35);margin:28px 0 8px;">{text}</p>'
    if subtext:
        html += f'<p style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.35);margin:0 0 14px;">{subtext}</p>'
    return html

def _takeaway(text, color="#00B0FF"):
    """Renders a one-line analytical takeaway below charts."""
    return (
        f'<div style="background:{color}0A;border:1px solid {color}1A;border-radius:10px;padding:10px 14px;margin:-8px 0 20px;display:flex;align-items:center;gap:8px;">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:500;color:{color};">💡 {text}</span>'
        f'</div>'
    )

def _form_badge(win_rate, matches_played):
    """Returns a colored badge: HOT / WARM / COLD based on last 5 win rate."""
    if matches_played < 2: return '<span style="color:rgba(240,244,255,0.3);">Insufficient Data</span>'
    if win_rate >= 0.7: color, label = "#00E676", "🔥 HOT"
    elif win_rate >= 0.4: color, label = "#FFD740", "⚖️ WARM"
    else: color, label = "#FF3D71", "❄️ COLD"
    return (
        f'<span style="display:inline-block;background:{color}15;border:1px solid {color}33;border-radius:99px;'
        f'padding:3px 10px;font-family:\'DM Sans\',sans-serif;font-size:10px;font-weight:700;'
        f'letter-spacing:0.1em;color:{color};">{label} ({int(win_rate*100)}%)</span>'
    )

def _sparkline_5(results):
    """Visual sparkline for last 5 matches. W=Win, L=Loss."""
    dots = []
    for r in results:
        color = "#00E676" if r == 1 else "#FF3D71"
        dots.append(f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{color};margin:0 2px;"></span>')
    return f'<div style="display:inline-flex;align-items:center;margin-left:8px;">{" ".join(dots)}</div>'

def _venue_heatmap_row(venue, win_pct, matches, color):
    """Row for venue strength table."""
    bar_w = int(win_pct * 100)
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(240,244,255,0.6);width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{venue}</span>'
        f'<div style="flex:1;margin:0 12px;height:4px;background:rgba(255,255,255,0.06);border-radius:99px;overflow:hidden;">'
        f'<div style="width:{bar_w}%;height:100%;background:{color};border-radius:99px;"></div>'
        f'</div>'
        f'<div style="display:flex;align-items:center;gap:6px;min-width:80px;justify-content:flex-end;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:{color};font-weight:600;">{win_pct*100:.0f}%</span>'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:9px;color:rgba(240,244,255,0.3);">({matches}m)</span>'
        f'</div></div>'
    )

def _toss_insight_row(venue, bat_win, field_win, matches):
    """Row for toss decision intelligence table."""
    delta = field_win - bat_win
    if delta > 10: rec, color = "Field First", "#00E676"
    elif delta < -10: rec, color = "Bat First", "#00B0FF"
    else: rec, color = "Neutral", "rgba(240,244,255,0.4)"
    
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(240,244,255,0.6);width:160px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">{venue}</span>'
        f'<div style="display:flex;gap:12px;align-items:center;">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#00B0FF;">Bat: {bat_win:.0f}%</span>'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:10px;color:#FF3D71;">Field: {field_win:.0f}%</span>'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;background:{color}22;color:{color};">{rec}</span>'
        f'</div></div>'
    )

# ═════════════════════════════════════════════════════════════
# ANALYTICS ENGINES
# ═════════════════════════════════════════════════════════════
def compute_rolling_form(team, matches_df, season=None):
    """Computes last 5 match results (W/L) for a team."""
    mdf = matches_df.copy()
    if season and season != "All Seasons":
        mdf = mdf[mdf['season'] == season]
    
    # Sort by date to ensure chronological order
    mdf = mdf.sort_values('date', ascending=True)
    
    # Filter matches involving the team
    team_matches = mdf[(mdf['team1'] == team) | (mdf['team2'] == team)]
    if len(team_matches) == 0:
        return 0.0, [], 0
    
    # Determine win/loss
    results = []
    for _, row in team_matches.tail(5).iterrows():
        if row['winner'] == team:
            results.append(1)
        else:
            results.append(0)
            
    win_rate = sum(results) / len(results) if results else 0.0
    return win_rate, results, len(results)

def compute_venue_strength(team, matches_df):
    """Returns sorted list of (venue, win_pct, matches_played)."""
    mdf = matches_df[matches_df['team1'].eq(team) | matches_df['team2'].eq(team)]
    if mdf.empty: return []
    
    venue_stats = mdf.groupby('venue').agg(
        matches=('id', 'count'),
        wins=('winner', lambda x: (x == team).sum())
    ).reset_index()
    
    venue_stats['win_pct'] = venue_stats['wins'] / venue_stats['matches']
    venue_stats = venue_stats[venue_stats['matches'] >= 5] # Filter noise
    venue_stats = venue_stats.sort_values('win_pct', ascending=False)
    return venue_stats[['venue', 'win_pct', 'matches']].values.tolist()

def compute_toss_intelligence(matches_df):
    """Returns venues ranked by toss decision impact."""
    mdf = matches_df.copy()
    
    # Batting first wins
    bat_data = mdf[mdf['toss_decision'] == 'bat']
    bat_wins = bat_data.groupby('venue').agg(
        total=('id', 'count'),
        wins=('winner', lambda x: (x == bat_data.loc[x.index, 'toss_winner']).sum())
    ).reset_index()
    bat_wins['bat_win_pct'] = (bat_wins['wins'] / bat_wins['total']) * 100
    
    # Bowling first wins (fielding)
    field_data = mdf[mdf['toss_decision'] == 'field']
    field_wins = field_data.groupby('venue').agg(
        total=('id', 'count'),
        wins=('winner', lambda x: (x == field_data.loc[x.index, 'toss_winner']).sum())
    ).reset_index()
    field_wins['field_win_pct'] = (field_wins['wins'] / field_wins['total']) * 100
    
    # Merge
    toss_intel = bat_wins[['venue', 'bat_win_pct']].merge(field_wins[['venue', 'field_win_pct']], on='venue')
    toss_intel = toss_intel[(bat_wins['total'] + field_wins['total']) >= 10] # Min sample size
    toss_intel['impact'] = (toss_intel['field_win_pct'] - toss_intel['bat_win_pct']).abs()
    toss_intel = toss_intel.sort_values('impact', ascending=False)
    return toss_intel[['venue', 'bat_win_pct', 'field_win_pct', 'impact']].values.tolist()

# ═════════════════════════════════════════════════════════════
# MAIN PAGE
# ═════════════════════════════════════════════════════════════
def show_team_analysis():
    inject_team_css()
    
    # ── HERO ───────────────────────────────────────────────
    st.markdown(
        '<div style="text-align:center;padding:20px 0 36px;">'
        '<div style="display:inline-block;background:linear-gradient(135deg,rgba(0,176,255,0.12),rgba(0,230,118,0.12));'
        'border:1px solid rgba(0,176,255,0.2);border-radius:99px;padding:6px 18px;margin-bottom:20px;">'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#00B0FF;">👥 Team Intelligence</span>'
        '</div>'
        '<h1 style="font-family:\'Bebas Neue\',sans-serif;font-size:clamp(44px,7vw,72px);letter-spacing:0.06em;'
        'color:#F0F4FF;margin:0 0 12px;line-height:1;">TEAM ANALYSIS</h1>'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:16px;color:rgba(240,244,255,0.45);margin:0;'
        'font-weight:300;">Form tracking, venue dominance & toss strategy</p>'
        '</div>', unsafe_allow_html=True
    )

    # ── LOAD DATA ──────────────────────────────────────────
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    try:
        matches = pd.read_csv(os.path.join(BASE_DIR, "data", "cleaned", "matches_clean.csv"))
    except FileNotFoundError:
        st.error("📂 `matches_clean.csv` not found. Check your data path.")
        return

    # Normalize date if needed
    if 'date' in matches.columns and not pd.api.types.is_datetime64_any_dtype(matches['date']):
        matches['date'] = pd.to_datetime(matches['date'], errors='coerce')

    teams = sorted(matches['team1'].unique())
    seasons = ["All Seasons"] + sorted(matches['season'].dropna().unique(), reverse=True)
    
    # Session state persistence
    default_team = 'Chennai Super Kings' if 'Chennai Super Kings' in teams else teams[0]
    sel_team = st.selectbox("Select Team", teams, index=teams.index(default_team), key="team_select")
    sel_season = st.selectbox("Select Season", seasons, index=0, key="season_select")

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:24px 0;"></div>', unsafe_allow_html=True)

    # ── SECTION 1: FORM & DOMINANCE ────────────────────────
    st.markdown(_section_label("📊 Current Form & Overall Performance", "How the team has performed recently vs historically."), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Win Rate Card
        team_matches = matches[(matches['team1'] == sel_team) | (matches['team2'] == sel_team)]
        if sel_season != "All Seasons":
            team_matches = team_matches[team_matches['season'] == sel_season]
        
        total_matches = len(team_matches)
        wins = len(team_matches[team_matches['winner'] == sel_team])
        win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
        
        # Color gradient for card
        card_color = "#00E676" if win_rate > 55 else ("#FFD740" if win_rate > 45 else "#FF3D71")
        
        st.markdown(
            f'<div style="background:{card_color}0C;border:1px solid {card_color}22;border-radius:18px;padding:22px 24px;">'
            f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:rgba(240,244,255,0.4);margin-bottom:8px;">Win Rate (All Time)</div>'
            f'<div style="display:flex;align-items:baseline;gap:12px;">'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:42px;font-weight:700;color:{card_color};line-height:1;">{win_rate:.1f}%</span>'
            f'<span style="font-family:\'DM Sans\',sans-serif;font-size:13px;color:rgba(240,244,255,0.5);">{wins}W / {total_matches}M</span>'
            f'</div></div>', unsafe_allow_html=True)
        st.markdown(_takeaway(f"{sel_team} has a {win_rate:.0f}% historical win rate across {total_matches} matches."), unsafe_allow_html=True)

    with col2:
        # Rolling Form
        win_pct, form_results, m_played = compute_rolling_form(sel_team, matches, sel_season)
        st.markdown(
            '<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:22px 24px;">'
            '<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
            'text-transform:uppercase;color:rgba(240,244,255,0.4);margin-bottom:8px;">Last 5 Matches</div>'
            '<div style="display:flex;align-items:center;gap:10px;">'
            + _sparkline_5(form_results) + _form_badge(win_pct, m_played) +
            '</div></div>', unsafe_allow_html=True)
        st.markdown(_takeaway(f"Recent form: {win_pct*100:.0f}% win rate in last {m_played} games.") if m_played > 0 else "", unsafe_allow_html=True)

    with col3:
        # Quick Context Chip
        st.markdown(
            '<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:18px;padding:22px 24px;text-align:center;">'
            '<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
            'text-transform:uppercase;color:rgba(240,244,255,0.4);margin-bottom:8px;">Seasons Played</div>'
            f'<div style="font-family:\'Bebas Neue\',sans-serif;font-size:42px;color:#F0F4FF;line-height:1;">'
            f'{matches[matches["team1"].eq(sel_team) | matches["team2"].eq(sel_team)]["season"].nunique()}</div>'
            '</div>', unsafe_allow_html=True)

    # ── SECTION 2: VENUE STRENGTH MATRIX ──────────────────
    st.markdown(_section_label("🏟️ Venue Strength Matrix", "Win percentage at each ground (min. 5 matches)."), unsafe_allow_html=True)
    venue_data = compute_venue_strength(sel_team, matches)
    if venue_data:
        # Sort by win rate for display
        best_venues = [v for v in venue_data if v[1] > 0.5]
        worst_venues = [v for v in venue_data if v[1] < 0.45]
        
        vc1, vc2 = st.columns(2)
        with vc1:
            if best_venues:
                st.markdown(
                    f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px 20px;">'
                    f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
                    f'text-transform:uppercase;color:#00E676;margin-bottom:12px;">✅ Strong Venues</div>'
                    + "".join(_venue_heatmap_row(v[0], v[1], v[2], "#00E676") for v in best_venues) + '</div>', unsafe_allow_html=True)
                st.markdown(_takeaway(f"Dominates at venues like {best_venues[0][0]} with {best_venues[0][1]*100:.0f}% win rate."), unsafe_allow_html=True)
        with vc2:
            if worst_venues:
                st.markdown(
                    f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px 20px;">'
                    f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
                    f'text-transform:uppercase;color:#FF3D71;margin-bottom:12px;">⚠️ Challenging Venues</div>'
                    + "".join(_venue_heatmap_row(v[0], v[1], v[2], "#FF3D71") for v in worst_venues) + '</div>', unsafe_allow_html=True)
                st.markdown(_takeaway(f"Struggles at {worst_venues[0][0]} (win rate drops to {worst_venues[0][1]*100:.0f}%)."), unsafe_allow_html=True)
    else:
        st.info("Insufficient venue data to generate matrix.")

    # ── SECTION 3: TOSS DECISION INTELLIGENCE ─────────────
    st.markdown(_section_label("🪙 Toss Decision Intelligence", "Where does winning the toss actually matter?"), unsafe_allow_html=True)
    toss_data = compute_toss_intelligence(matches)
    if toss_data:
        # Show top 5 most impactful venues
        st.markdown(
            f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px 20px;margin-bottom:12px;">'
            f'<div style="font-family:\'DM Sans\',sans-serif;font-size:11px;font-weight:700;letter-spacing:0.1em;'
            f'text-transform:uppercase;color:rgba(240,244,255,0.35);margin-bottom:12px;">Top Venues by Toss Impact</div>'
            + "".join(_toss_insight_row(v[0], v[1], v[2], v[3]) for v in toss_data[:5]) + '</div>', unsafe_allow_html=True)
        st.markdown(_takeaway("At these venues, the toss winner's decision to bat or field first shifts win probability by >15%."), unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:28px 0 4px;"></div>', unsafe_allow_html=True)

    # ── SECTION 4: ENHANCED H2H ──────────────────────────
    st.markdown(_section_label("⚔️ Head-to-Head Comparison", "Select opponent to see matchup history."), unsafe_allow_html=True)
    opp_col1, opp_col2 = st.columns(2)
    with opp_col1: opponent = st.selectbox("vs Opponent", [t for t in teams if t != sel_team], index=0, key="opp_select")
    with opp_col2: h2h_season = st.selectbox("Filter by Season", seasons, index=0, key="h2h_season")

    h2h_data = matches[(matches['team1'].isin([sel_team, opponent])) & (matches['team2'].isin([sel_team, opponent]))]
    if h2h_season != "All Seasons":
        h2h_data = h2h_data[h2h_data['season'] == h2h_season]

    if len(h2h_data) > 0:
        s_wins = len(h2h_data[h2h_data['winner'] == sel_team])
        o_wins = len(h2h_data[h2h_data['winner'] == opponent])
        total = len(h2h_data)
        
        # Pie Chart
        h2h_df = pd.DataFrame({"Team": [sel_team, opponent], "Wins": [s_wins, o_wins]})
        fig = px.pie(h2h_df, values='Wins', names='Team', hole=0.65,
                     color_discrete_map={sel_team: '#00B0FF', opponent: '#FF3D71'})
        fig.update_traces(textposition='outside', textinfo='percent+label', marker_line_width=0)
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font=dict(family="DM Sans", color="#F0F4FF"), margin=dict(l=0,r=0,t=30,b=0))
        
        st.plotly_chart(fig, use_container_width=True)
        
        # H2H Takeaway
        dominance = sel_team if s_wins > o_wins else opponent
        diff = abs(s_wins - o_wins)
        if diff > 2:
            st.markdown(_takeaway(f"{dominance} dominates this rivalry, winning {diff} more matches."), unsafe_allow_html=True)
        else:
            st.markdown(_takeaway("Highly competitive rivalry with a narrow historical margin."), unsafe_allow_html=True)
    else:
        st.info("No matches played between these teams in the selected timeframe.")
