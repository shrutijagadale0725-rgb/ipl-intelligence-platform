"""
model_explain.py — Logistic-regression feature attributions for Win Predictor.

Uses coefficient × feature value on the transformed pipeline input (linear SHAP
equivalent for LogisticRegression). No extra dependencies beyond scikit-learn.
"""
import pandas as pd
import plotly.graph_objects as go

from views.shared_styles import PLOTLY_LAYOUT

NUMERIC_LABELS = {
    "runs_left": "Runs Left",
    "balls_left": "Balls Left",
    "wickets_left": "Wickets in Hand",
    "total_runs_x": "Target Score",
    "crr": "Current Run Rate",
    "rrr": "Required Run Rate",
}

TEAM_ABBR = {
    "Mumbai Indians": "MI",
    "Chennai Super Kings": "CSK",
    "Royal Challengers Bengaluru": "RCB",
    "Kolkata Knight Riders": "KKR",
    "Sunrisers Hyderabad": "SRH",
    "Rajasthan Royals": "RR",
    "Delhi Capitals": "DC",
    "Punjab Kings": "PBKS",
    "Lucknow Super Giants": "LSG",
    "Gujarat Titans": "GT",
}


def _human_label(feat_name: str, input_df: pd.DataFrame) -> str:
    for key, label in NUMERIC_LABELS.items():
        if key in feat_name:
            return label
    if "batting_team_" in feat_name:
        team = input_df["batting_team"].iloc[0]
        abbr = TEAM_ABBR.get(team, team[:3].upper())
        return f"Batting Team ({abbr})"
    if "bowling_team_" in feat_name:
        team = input_df["bowling_team"].iloc[0]
        abbr = TEAM_ABBR.get(team, team[:3].upper())
        return f"Bowling Team ({abbr})"
    if "city_" in feat_name:
        city = input_df["city"].iloc[0]
        return f"City ({city})"
    return feat_name.split("__")[-1].replace("_", " ").title()


def compute_top_contributions(pipe, input_df: pd.DataFrame, top_n: int = 6) -> pd.DataFrame:
    """
    Return top features by |contribution| to log-odds of a batting-team win.
    Positive values push toward win; negative toward loss.
    """
    preprocessor = pipe.named_steps["step1"]
    classifier = pipe.named_steps["step2"]

    X_trans = preprocessor.transform(input_df)
    if hasattr(X_trans, "toarray"):
        X_trans = X_trans.toarray()
    X_trans = X_trans[0]

    feature_names = preprocessor.get_feature_names_out()
    coefs = classifier.coef_[0]

    rows = []
    for name, val, coef in zip(feature_names, X_trans, coefs):
        contribution = float(coef * val)
        if abs(contribution) < 1e-12:
            continue
        rows.append(
            {
                "feature": _human_label(name, input_df),
                "contribution": round(contribution, 4),
            }
        )

    if not rows:
        return pd.DataFrame(columns=["feature", "contribution"])

    df = pd.DataFrame(rows)
    df = df.reindex(df["contribution"].abs().sort_values(ascending=False).index)
    return df.head(top_n).reset_index(drop=True)


def build_contribution_chart(contributions: pd.DataFrame, batting_abbr: str) -> go.Figure:
    """Horizontal bar chart of feature contributions, dark-theme styled."""
    if contributions.empty:
        fig = go.Figure()
        fig.update_layout(**PLOTLY_LAYOUT, title="No feature contributions available")
        return fig

    colors = [
        "#00E676" if c >= 0 else "#FF3D71"
        for c in contributions["contribution"]
    ]
    hover = [
        f"{'Toward win' if c >= 0 else 'Toward loss'} · {abs(c):.3f} log-odds"
        for c in contributions["contribution"]
    ]

    fig = go.Figure(
        go.Bar(
            x=contributions["contribution"],
            y=contributions["feature"],
            orientation="h",
            marker=dict(color=colors, line=dict(width=0)),
            hovertext=hover,
            hoverinfo="text+y",
        )
    )

    layout = {**PLOTLY_LAYOUT}
    layout["title"] = dict(
        text=f"Top Drivers · {batting_abbr} Win Probability",
        x=0,
        xanchor="left",
    )
    layout["height"] = max(280, 56 * len(contributions) + 80)
    layout["showlegend"] = False
    layout["xaxis"] = {
        **PLOTLY_LAYOUT.get("xaxis", {}),
        "title": "Contribution to log-odds (→ win)",
        "zeroline": True,
        "zerolinecolor": "rgba(255,255,255,0.25)",
        "zerolinewidth": 1,
    }
    layout["yaxis"] = {
        **PLOTLY_LAYOUT.get("yaxis", {}),
        "autorange": "reversed",
        "categoryorder": "array",
        "categoryarray": list(reversed(contributions["feature"].tolist())),
    }
    fig.update_layout(**layout)
    return fig


def explanation_summary(contributions: pd.DataFrame, batting_team: str, win_pct: int) -> str:
    """One-line plain-English summary of the top driver."""
    if contributions.empty:
        return "Not enough signal to explain this prediction."

    top = contributions.iloc[0]
    direction = "increases" if top["contribution"] > 0 else "reduces"
    return (
        f"The strongest factor is **{top['feature']}**, which {direction} "
        f"{batting_team}'s estimated **{win_pct}%** win chance."
    )
