# 🏏 IPL Insights Dashboard

A Streamlit-powered analytics platform for IPL cricket data — combining historical team/player statistics, venue intelligence, and a machine-learning win predictor with model transparency, all wrapped in a dark glassmorphism "DeFi Premium" UI.

> Run locally with: `streamlit run app.py`
> 🔗 **Live demo:** [overlly.streamlit.app](https://overlly.streamlit.app/)

---

## ✨ Features

### 🏠 Home
- **Intelligence Snapshot** — auto-computed insight cards generated on startup:
  - Venue Dominance (team with highest win % at a given ground, min. 15 matches)
  - Chasing Advantage (league-wide win rate when chasing)
  - Death Over Finisher (highest strike rate in overs 16–20, min. 200 balls)
  - Toss Strategy (best venue for fielding-first decisions)
- Quick KPIs: total matches, seasons, most-winning team, total teams
- Feature cards linking to each section of the dashboard

### 📊 Team Analysis
- Win rate (all-time) with color-coded performance card
- Rolling form — last 5 matches as a win/loss sparkline + HOT/WARM/COLD badge
- **Venue Strength Matrix** — win % per venue (min. 5 matches), split into strongest/weakest grounds
- **Toss Decision Intelligence** — which venues favor batting vs. fielding first
- Head-to-head comparison vs. any opponent, filterable by season, visualized as a donut chart

### 🏏 Player Analysis
- **Role Classifier** — automatically tags a batter as Explosive Opener, Finisher, Classic Anchor, Middle Order Batter, or Lower Order Hitter based on phase-wise strike rate, boundary %, and average
- **Phase-by-Phase Breakdown** — strike rate & average across Powerplay (1–6), Middle (7–15), and Death (16–20) overs
- **Consistency Score** — variance-based rating (0–100) of innings-to-innings reliability
- **Venue Intelligence** — a player's best/worst grounds by average
- **Head-to-Head Player Comparison** — side-by-side stats, role badges, and a comparison chart for any two players

### 🏟️ Venue & Season
- **Venue Difficulty Index** — composite 0–10 score (50% avg 1st-innings score, 30% wicket frequency inverse, 20% chase win %), labeled Batting Paradise / Balanced / Bowler's Haven
- **Defendable Score Thresholds** — median 1st-innings total in matches the defending team actually won
- **Season Scoring Trends** — average 1st-innings totals across IPL seasons (line chart)
- **Chasing Advantage vs. Batting First** — best/worst venues for chasing teams

### 🤖 Win Predictor
- Real-time win probability via a trained scikit-learn pipeline (`pipe.pkl`)
- Inputs: batting/bowling team, city, target, current score, overs, wickets
- Auto-calculated: runs left, balls left, wickets in hand, current run rate (CRR), required run rate (RRR)
- Animated scoreboard with team-branded colors and a momentum bar
- **Pressure Meter** — derived from RRR − CRR, labeled Low/Moderate/High Pressure
- **AI Commentary** — plain-language read of the match situation based on win probability
- **Model Transparency** — top 6 feature contributions to the prediction (coefficient × feature value, the linear-model equivalent of SHAP), shown as a horizontal bar chart with a one-line explanation

---

## 🧱 Tech Stack

| Layer | Tools |
|---|---|
| App framework | Streamlit |
| Data processing | pandas |
| Visualization | Plotly (`plotly.express`, `plotly.graph_objects`) |
| ML model | scikit-learn `Pipeline` (preprocessing + `LogisticRegression`), serialized with `pickle` |
| Styling | Custom CSS injection (no external UI framework) |
| Fonts | Bebas Neue (headers), DM Sans (body), JetBrains Mono (stats/numbers) |

---

## 📁 Project Structure

```
IPL-Data-Insights/
├── app.py                      # Entry point — routing, sidebar/header nav, Home page
├── views/
│   ├── shared_styles.py        # Single source of truth for CSS, Plotly theme, section_label(), takeaway()
│   ├── team_Analysis.py        # show_team_analysis()
│   ├── player_Analysis.py      # show_player_analysis()
│   ├── venue_Season.py         # show_venue_season()
│   ├── win_Predictor.py        # show_win_predictor()
│   └── model_explain.py        # Feature-contribution logic for the Win Predictor
├── models/
│   └── pipe.pkl                # Trained sklearn pipeline (preprocessor + LogisticRegression)
├── data/
│   └── cleaned/
│       ├── matches_clean.csv
│       └── deliveries_clean.csv
└── requirements.txt
```

> Views are imported in `app.py` as `views.team_Analysis`, `views.player_Analysis`, `views.venue_Season`, `views.win_Predictor` — keep this package structure intact when adding new pages.

---

## ⚙️ Setup

```bash
# 1. Clone / open the project
cd IPL-Data-Insights

# 2. Install dependencies
pip install -r requirements.txt
# or, matching the in-app error message format:
python -m pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

On Windows, a `run_dashboard.ps1` script is referenced as a shortcut for launching the app from the project root.

---

## 🚀 Deployment

Hosted live on **Streamlit Community Cloud**: **[overlly.streamlit.app](https://overlly.streamlit.app/)**

This matches the `page_title="overlly"` set in `app.py`'s `st.set_page_config()` — the app is in the process of being rebranded (working names: **wkt.** / **Stump**), so the deployed name, favicon (`cute_ovr.png`), and in-app hero copy ("IPL INSIGHTS") are currently out of sync and will be unified in a future pass.

To redeploy after changes:
1. Push to the connected GitHub repo
2. Streamlit Community Cloud auto-redeploys on push to the tracked branch
3. Confirm `requirements.txt` is up to date — the free tier rebuilds the environment from scratch on each deploy

---

## 📦 Data Requirements

Place two CSVs in `data/cleaned/`:

| File | Required columns (used across views) |
|---|---|
| `matches_clean.csv` | `id`, `season`, `date`, `team1`, `team2`, `venue`, `city`, `winner`, `toss_winner`, `toss_decision` |
| `deliveries_clean.csv` | `match_id`, `inning`, `over`, `batter` (or `batsman`), `batsman_runs` (or `total_runs`), `is_wicket`/`player_dismissed` |

`app.py`'s `load_ipl_data()` checks several relative paths (`../data/cleaned`, `data/cleaned`, and CWD-relative variants) so the app can run whether launched from the project root or the `views/` directory. Column auto-renaming (`batsman`→`batter`, `total_runs`→`batsman_runs`) is handled automatically for both the Home page and Venue & Season loaders.

If data isn't found, the Home page shows a warning instead of crashing; Team Analysis and Venue & Season show explicit errors pointing at the expected path.

---

## 🧠 Model Notes (Win Predictor)

- `pipe.pkl` is a two-step `Pipeline`: `step1` (ColumnTransformer/preprocessor) → `step2` (`LogisticRegression`)
- Input features: `batting_team`, `bowling_team`, `city`, `runs_left`, `balls_left`, `wickets_left`, `total_runs_x` (target), `crr`, `rrr`
- `model_explain.py` computes per-feature log-odds contributions (`coefficient × transformed feature value`) — this is exact for a linear model, not an approximation, and requires no extra dependency like `shap`
- Output: win probability for the **batting team** (`pipe.predict_proba(input_df)[0][1]`)

---

## 🎨 Design System

Defined once in `views/shared_styles.py` and imported by every view via `inject_base_css()`:

- **Background:** `#080C14` (near-black navy)
- **Card surface:** `#0E1420` / `#151C2C`
- **Accents:** `#00E676` (green/positive), `#00B0FF` (blue/neutral), `#FF3D71` (red/negative), `#FFD740` (yellow/caution)
- **Typography:** Bebas Neue for display headers, DM Sans for UI text, JetBrains Mono for all numeric/stat values
- Shared helpers: `section_label()` for uppercase section dividers, `takeaway()` for the inline insight callout boxes under charts/tables
- Page-specific CSS (e.g. the Win Predictor's gradient "PREDICT" button) is layered on top via `inject_extra_css()` rather than duplicated per file

---

## 🗺️ Roadmap / Ideas

- [ ] PDF export of player/team/venue reports (via `reportlab`)
- [ ] Mobile-responsive layout pass
- [ ] Additional ML layer for the Venue & Season difficulty index
- [ ] Rebrand pass (working names: **wkt.** / **Stump**) — update `page_title`/favicon and hero copy across all views

---

## 📄 License

Personal portfolio project — built on public IPL datasets (2008–2025, Kaggle).