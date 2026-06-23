import streamlit as st
import pandas as pd
import plotly.express as px
import os

from views.shared_styles import inject_base_css, section_label, takeaway

# ═════════════════════════════════════════════════════════════
# PAGE-SPECIFIC HTML HELPERS
# ═════════════════════════════════════════════════════════════
def _index_badge(score, label, color):
    return (
        f'<span style="display:inline-flex;align-items:center;gap:8px;background:{color}15;border:1px solid {color}33;'
        f'border-radius:99px;padding:6px 14px;font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:700;color:{color};">'
        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;">{score:.1f}</span> {label}</span>'
    )

def _venue_row(venue, score, label, color):
    return (
        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.6);">{venue}</span>'
        f'{_index_badge(score, label, color)}'
        f'</div>'
    )

# ═════════════════════════════════════════════════════════════
# DATA LOADER (Cached & Robust)
# ═════════════════════════════════════════════════════════════
@st.cache_data
def load_venue_data():
    base = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    m_path = os.path.join(base, "data", "cleaned", "matches_clean.csv")
    d_path = os.path.join(base, "data", "cleaned", "deliveries_clean.csv")

    matches = pd.read_csv(m_path)
    deliveries = pd.read_csv(d_path)

    if 'total_runs' in deliveries.columns and 'batsman_runs' not in deliveries.columns:
        deliveries.rename(columns={'total_runs': 'batsman_runs'}, inplace=True)
    if 'venue' not in deliveries.columns and 'venue' in matches.columns:
        venue_map = matches.set_index('id')['venue'].to_dict()
        deliveries['venue'] = deliveries['match_id'].map(venue_map)
    if 'season' not in deliveries.columns and 'season' in matches.columns:
        season_map = matches.set_index('id')['season'].to_dict()
        deliveries['season'] = deliveries['match_id'].map(season_map)

    return matches, deliveries

# ═════════════════════════════════════════════════════════════
# ANALYTICS ENGINES
# ═════════════════════════════════════════════════════════════
@st.cache_data
def compute_season_trends(matches, deliveries):
    """Computes match-level 1st innings totals, then averages by season."""
    if 'inning' not in deliveries.columns or 'batsman_runs' not in deliveries.columns:
        return pd.DataFrame()

    innings = deliveries.groupby(['match_id', 'inning'])['batsman_runs'].sum().reset_index(name='innings_runs')
    first_inn = innings[innings['inning'] == 1].copy()

    if 'season' in matches.columns:
        season_map = matches.set_index('id')['season'].to_dict()
        first_inn['season'] = first_inn['match_id'].map(season_map)
    else:
        first_inn['season'] = matches.iloc[0].get('season', 2024)

    trends = first_inn.groupby('season')['innings_runs'].mean().reset_index()
    trends.columns = ['season', 'avg_1st_innings']
    trends = trends.sort_values('season')
    return trends

@st.cache_data
def compute_venue_intelligence(matches, deliveries):
    """Computes Difficulty Index, Defendable Score, and Chase Win % per venue."""
    if 'venue' not in deliveries.columns: return pd.DataFrame()

    inn_runs = deliveries.groupby(['match_id', 'inning'])['batsman_runs'].sum().reset_index(name='runs')
    inn_1 = inn_runs[inn_runs['inning']==1][['match_id', 'runs']]
    inn_1 = inn_1.merge(matches[['id', 'venue', 'winner']], left_on='match_id', right_on='id')

    wicket_mask = deliveries.get('is_wicket') == 1 if 'is_wicket' in deliveries.columns else deliveries['player_dismissed'].notna()
    wkts = deliveries[wicket_mask].groupby('match_id').size().reset_index(name='wickets')
    wkts = wkts.merge(matches[['id', 'venue']], left_on='match_id', right_on='id')

    venue_stats = inn_1.groupby('venue').agg(
        avg_score=('runs', 'mean'),
        matches=('id', 'count'),
        defendable_median=('runs', 'median')
    ).reset_index()

    wkt_stats = wkts.groupby('venue')['wickets'].mean().reset_index(name='avg_wickets')
    venue_stats = venue_stats.merge(wkt_stats, on='venue', how='left')

    matches_temp = matches.copy()
    matches_temp['is_chase_win'] = matches_temp['winner'] != matches_temp['toss_winner']
    chase_pct = matches_temp.groupby('venue')['is_chase_win'].mean() * 100
    venue_stats = venue_stats.merge(chase_pct.rename('chase_win_pct'), on='venue')

    venue_stats = venue_stats[venue_stats['matches'] >= 5].copy()

    def normalize(col, invert=False):
        mn, mx = col.min(), col.max()
        if mn == mx: return 5.0
        norm = (col - mn) / (mx - mn) * 10
        return (10 - norm) if invert else norm

    venue_stats['difficulty'] = (
        normalize(venue_stats['avg_score']) * 0.5 +
        normalize(venue_stats['avg_wickets'], invert=True) * 0.3 +
        normalize(venue_stats['chase_win_pct']) * 0.2
    )

    def label_idx(score):
        if score >= 7.0: return "Batting Paradise", "#00E676"
        if score <= 3.5: return "Bowler's Haven", "#FF3D71"
        return "Balanced", "#FFD740"

    venue_stats['label'] = venue_stats['difficulty'].apply(lambda x: label_idx(x)[0])
    venue_stats['color']  = venue_stats['difficulty'].apply(lambda x: label_idx(x)[1])

    return venue_stats.sort_values('difficulty', ascending=False)

# ═════════════════════════════════════════════════════════════
# MAIN PAGE
# ═════════════════════════════════════════════════════════════
def show_venue_season():
    inject_base_css()

    st.markdown(
        '<div style="text-align:center;padding:20px 0 36px;">'
        '<div style="display:inline-block;background:linear-gradient(135deg,rgba(255,215,64,0.12),rgba(255,61,113,0.12));'
        'border:1px solid rgba(255,215,64,0.2);border-radius:99px;padding:6px 18px;margin-bottom:20px;">'
        '<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;font-weight:600;letter-spacing:0.12em;'
        'text-transform:uppercase;color:#FFD740;">🏟️ Ground & Season Intelligence</span>'
        '</div>'
        '<h1 style="font-family:\'Bebas Neue\',sans-serif;font-size:clamp(44px,7vw,72px);letter-spacing:0.06em;'
        'color:#F0F4FF;margin:0 0 12px;line-height:1;">VENUE & SEASON</h1>'
        '<p style="font-family:\'DM Sans\',sans-serif;font-size:16px;color:rgba(240,244,255,0.45);margin:0;'
        'font-weight:300;">Difficulty indices, defendable thresholds & chasing analysis</p>'
        '</div>', unsafe_allow_html=True
    )

    matches, deliveries = load_venue_data()
    if matches.empty or deliveries.empty:
        st.error("📂 Dataset not found. Verify `data/cleaned/` paths.")
        return

    # ── SECTION 1: VENUE DIFFICULTY INDEX ─────────────────
    st.markdown(section_label("📊 Venue Difficulty Index", "Composite score (0-10) combining avg 1st innings score, wicket frequency, and chase win rate."), unsafe_allow_html=True)
    v_intel = compute_venue_intelligence(matches, deliveries)

    if not v_intel.empty:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px;">'
                        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;text-transform:uppercase;color:rgba(240,244,255,0.35);margin-bottom:10px;">🔝 Highest Scoring</div>'
                        + _venue_row(v_intel.iloc[0]['venue'], v_intel.iloc[0]['difficulty'], v_intel.iloc[0]['label'], v_intel.iloc[0]['color'])
                        + '</div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px;">'
                        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;text-transform:uppercase;color:rgba(240,244,255,0.35);margin-bottom:10px;">📉 Lowest Scoring</div>'
                        + _venue_row(v_intel.iloc[-1]['venue'], v_intel.iloc[-1]['difficulty'], v_intel.iloc[-1]['label'], v_intel.iloc[-1]['color'])
                        + '</div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px;">'
                        f'<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;text-transform:uppercase;color:rgba(240,244,255,0.35);margin-bottom:10px;">⚖️ Most Balanced</div>'
                        + _venue_row(v_intel.iloc[len(v_intel)//2]['venue'], v_intel.iloc[len(v_intel)//2]['difficulty'], v_intel.iloc[len(v_intel)//2]['label'], v_intel.iloc[len(v_intel)//2]['color'])
                        + '</div>', unsafe_allow_html=True)

        st.markdown(takeaway("Index weights: 50% avg score, 30% wicket frequency (inverse), 20% chase win %."), unsafe_allow_html=True)

    # ── SECTION 2: DEFENDABLE SCORE CALCULATOR ───────────
    st.markdown(section_label("🎯 Defendable Score Thresholds", "Median 1st innings total in matches where the defending team actually won."), unsafe_allow_html=True)
    if not v_intel.empty:
        def_df = v_intel[['venue', 'defendable_median', 'avg_score']].sort_values('defendable_median', ascending=False).head(6)
        def_html = ''.join(
            f'<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
            f'<span style="font-family:\'DM Sans\',sans-serif;font-size:12px;color:rgba(240,244,255,0.6);">{r.venue}</span>'
            f'<div style="display:flex;align-items:center;gap:12px;">'
            f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:14px;font-weight:600;color:#00E676;">{r.defendable_median:.0f}</span>'
            f'<span style="font-family:\'DM Sans\',sans-serif;font-size:10px;color:rgba(240,244,255,0.3);">(avg: {r.avg_score:.1f})</span>'
            f'</div></div>'
            for r in def_df.itertuples()
        )
        st.markdown(f'<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px 20px;">{def_html}</div>', unsafe_allow_html=True)
        st.markdown(takeaway(f"At {def_df.iloc[0]['venue']}, {def_df.iloc[0]['defendable_median']:.0f} is statistically safe enough to defend half the time."), unsafe_allow_html=True)

    # ── SECTION 3: SEASON SCORING TRENDS ────────
    st.markdown(section_label("📈 Season Scoring Trends", "Average first-innings totals per IPL season (match-level aggregation)."), unsafe_allow_html=True)
    trends = compute_season_trends(matches, deliveries)

    if not trends.empty:
        fig = px.line(trends, x='season', y='avg_1st_innings', markers=True,
                      color_discrete_sequence=['#00B0FF'])
        fig.update_traces(line=dict(width=3), marker=dict(size=8))
        fig.update_layout(
            template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans", color="#F0F4FF"), margin=dict(l=20,r=20,t=30,b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.05)"), yaxis=dict(gridcolor="rgba(255,255,255,0.05)", title="Avg 1st Innings Score")
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(takeaway(f"Scores trend upward over time. Peak average: {trends['avg_1st_innings'].max():.1f} in {trends.loc[trends['avg_1st_innings'].idxmax(), 'season']}."), unsafe_allow_html=True)

    # ── SECTION 4: CHASING & TOSS STRATEGY ──────────────
    st.markdown(section_label("🔄 Chasing Advantage vs Batting First", "Historical win rates for teams batting first vs second per venue."), unsafe_allow_html=True)

    chase_stats = matches.copy()
    chase_stats['is_chase'] = chase_stats['winner'] != chase_stats['toss_winner']
    chase_venue = chase_stats.groupby('venue').agg(
        total=('id', 'count'),
        chase_wins=('is_chase', 'sum')
    ).reset_index()
    chase_venue['chase_pct'] = (chase_venue['chase_wins'] / chase_venue['total']) * 100
    chase_venue = chase_venue[chase_venue['total'] >= 10].sort_values('chase_pct', ascending=False)

    if not chase_venue.empty:
        best_chase = chase_venue.head(5)
        worst_chase = chase_venue.tail(5).iloc[::-1]

        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown(
                '<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px 20px;">'
                '<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;text-transform:uppercase;color:#00E676;margin-bottom:10px;">✅ Best Chasing Venues</div>' +
                ''.join(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(240,244,255,0.6);">{r.venue}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#00E676;font-weight:600;">{r.chase_pct:.1f}%</span></div>'
                        for r in best_chase.itertuples()) + '</div>', unsafe_allow_html=True)
        with cc2:
            st.markdown(
                '<div style="background:#0E1420;border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:16px 20px;">'
                '<div style="font-family:\'DM Sans\',sans-serif;font-size:10px;text-transform:uppercase;color:#FF3D71;margin-bottom:10px;">⚠️ Defend-Friendly Venues</div>' +
                ''.join(f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);">'
                        f'<span style="font-family:\'DM Sans\',sans-serif;font-size:11px;color:rgba(240,244,255,0.6);">{r.venue}</span>'
                        f'<span style="font-family:\'JetBrains Mono\',monospace;font-size:11px;color:#FF3D71;font-weight:600;">{r.chase_pct:.1f}%</span></div>'
                        for r in worst_chase.itertuples()) + '</div>', unsafe_allow_html=True)
        st.markdown(takeaway(f"Teams win {chase_venue['chase_pct'].mean():.1f}% of chases on average. At {best_chase.iloc[0]['venue']}, chasing wins {best_chase.iloc[0]['chase_pct']:.0f}% of the time."), unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.06);margin:32px 0;"></div>', unsafe_allow_html=True)