import plotly.graph_objects as go

SENTIMENT_COLORS = {
    "positive": "#22c55e",
    "neutral":  "#f59e0b",
    "negative": "#ef4444",
}


def sentiment_bar_chart(categories: list[dict]) -> go.Figure:
    cat_names = [c["category"]              for c in categories]
    pct_pos   = [float(c["pct_positive"])   for c in categories]
    pct_neu   = [float(c["pct_neutral"])    for c in categories]
    pct_neg   = [float(c["pct_negative"])   for c in categories]

    fig = go.Figure()
    for label, values, color in [
        ("Positive", pct_pos, SENTIMENT_COLORS["positive"]),
        ("Neutral",  pct_neu, SENTIMENT_COLORS["neutral"]),
        ("Negative", pct_neg, SENTIMENT_COLORS["negative"]),
    ]:
        fig.add_trace(go.Bar(
            name         = label,
            y            = cat_names,
            x            = values,
            orientation  = "h",
            marker_color = color,
            text         = [f"{v:.1f}%" for v in values],
            textposition = "inside",
        ))

    fig.update_layout(
        barmode     = "stack",
        xaxis_title = "Percentage (%)",
        xaxis       = dict(range=[0, 100]),
        legend      = dict(orientation="h", yanchor="bottom", y=1.02),
        margin      = dict(l=20, r=20, t=40, b=20),
        height      = max(300, len(categories) * 55),
    )
    return fig


def overall_donut_chart(summary: dict) -> go.Figure:
    labels = ["Positive", "Neutral", "Negative"]
    values = [
        summary["overall_positive"],
        summary["overall_neutral"],
        summary["overall_negative"],
    ]
    colors = [
        SENTIMENT_COLORS["positive"],
        SENTIMENT_COLORS["neutral"],
        SENTIMENT_COLORS["negative"],
    ]
    fig = go.Figure(go.Pie(
        labels   = labels,
        values   = values,
        hole     = 0.55,
        marker   = dict(colors=colors),
        textinfo = "label+percent",
    ))
    fig.update_layout(
        showlegend = False,
        margin     = dict(l=10, r=10, t=10, b=10),
        height     = 260,
    )
    return fig
