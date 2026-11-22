"""
Latency analysis visualizations.
Based on Mohammad Aldossary, IEEE Access, 2024 (Section V & Figure 6).
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
from config.settings import THEME_CONFIG


def plot_strategy_latency_comparison(summaries: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Renders a comparative bar chart of average service latency across strategies."""
    strategies = list(summaries.keys())
    latencies = [summaries[s]["avg_latency_ms"] for s in strategies]
    
    colors = []
    for s in strategies:
        if "Proposed" in s:
            colors.append(THEME_CONFIG["accent_orange"])
        elif "Heuristic" in s:
            colors.append(THEME_CONFIG["accent_amber"])
        elif "UAV" in s:
            colors.append(THEME_CONFIG["accent_gold"])
        elif "Fog" in s:
            colors.append("#58a6ff")
        else:
            colors.append("#f85149")

    fig = go.Figure(go.Bar(
        x=strategies,
        y=latencies,
        marker=dict(color=colors, line=dict(color="#30363d", width=1)),
        text=[f"{l:.1f} ms" for l in latencies],
        textposition="outside",
        textfont=dict(color="#f0f6fc")
    ))

    fig.update_layout(
        title_text="Average Service Latency (ms)",
        xaxis=dict(title="Strategy", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        yaxis=dict(title="Latency (ms)", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16, 22, 38, 0.65)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=340,
        margin=dict(l=50, r=30, t=40, b=40)
    )
    return fig


def plot_class_latency_benchmark(summaries: Dict[str, Dict[str, Any]]) -> go.Figure:
    """
    Renders grouped bar chart of service latency across application classes A, B, C,
    directly reproducing Figure 6 from the research paper.
    """
    classes = ["A (500 MIPS)", "B (2000 MIPS)", "C (6000 MIPS)"]
    fig = go.Figure()

    strategy_styles = {
        "UAV Execution": {"color": THEME_CONFIG["accent_gold"]},
        "Fog Execution": {"color": "#ef4444"},
        "Cloud Execution": {"color": "#10b981"},
        "Proposed (Collaborative)": {"color": THEME_CONFIG["accent_orange"]},
        "Heuristic (Algorithm 1)": {"color": THEME_CONFIG["accent_sun"]}
    }

    for strat_name, style in strategy_styles.items():
        if strat_name in summaries:
            s_data = summaries[strat_name]
            y_vals = [
                s_data.get("class_A_latency_ms", 0.0),
                s_data.get("class_B_latency_ms", 0.0),
                s_data.get("class_C_latency_ms", 0.0)
            ]
            fig.add_trace(go.Bar(
                name=strat_name,
                x=classes,
                y=y_vals,
                marker_color=style["color"]
            ))

    fig.update_layout(
        barmode="group",
        title_text="Figure 6 Reproduction — Service Time by Application Intensity",
        xaxis=dict(title="Application Class Complexity", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        yaxis=dict(title="Service Time (ms)", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16, 22, 38, 0.65)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=360,
        margin=dict(l=50, r=20, t=50, b=30),
        legend=dict(orientation="h", y=-0.2, font=dict(color="#f0f6fc"))
    )
    return fig
