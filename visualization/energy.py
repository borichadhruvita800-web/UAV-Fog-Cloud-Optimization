"""
Energy and power analysis visualizations.
Based on Mohammad Aldossary, IEEE Access, 2024 (Equations 1, 2, 3, 4).
"""

from typing import Dict, Any, List
import plotly.graph_objects as go
from config.settings import THEME_CONFIG


def plot_layer_power_breakdown(
    pwr_uav_access: float,
    pwr_fog_metro: float,
    pwr_cloud_core: float
) -> go.Figure:
    """Renders a horizontal bar chart of power consumption across the 3 layers (Eqs 1, 2, 3)."""
    categories = [
        "Cloud + Core (WAN/WDM) [Eq. 3]",
        "Fog + Metro (MAN) [Eq. 2]",
        "UAV + Access (PON) [Eq. 1]"
    ]
    values = [pwr_cloud_core, pwr_fog_metro, pwr_uav_access]
    colors = [
        THEME_CONFIG["accent_red"],
        THEME_CONFIG["accent_orange"],
        THEME_CONFIG["accent_gold"]
    ]

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation="h",
        marker=dict(color=colors, line=dict(color="#161b22", width=1.5)),
        text=[f"{v:.1f} W" for v in values],
        textposition="outside",
        textfont=dict(color="#f0f6fc")
    ))

    fig.update_layout(
        title_text="Subsystem Power Consumption Breakdown",
        xaxis=dict(title="Power (Watts)", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        yaxis=dict(color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16, 22, 38, 0.65)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=300,
        margin=dict(l=200, r=40, t=40, b=30)
    )
    return fig


def plot_strategy_energy_comparison(summaries: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Renders a comparative bar chart of total energy consumption across strategies."""
    strategies = list(summaries.keys())
    energies = [summaries[s]["total_energy_joules"] for s in strategies]
    
    colors = []
    for s in strategies:
        if "Proposed" in s:
            colors.append(THEME_CONFIG["accent_orange"])
        elif "Heuristic" in s:
            colors.append(THEME_CONFIG["accent_gold"])
        elif "UAV" in s:
            colors.append(THEME_CONFIG["accent_amber"])
        elif "Fog" in s:
            colors.append("#38bdf8")
        else:
            colors.append("#f87171")

    fig = go.Figure(go.Bar(
        x=strategies,
        y=energies,
        marker=dict(color=colors, line=dict(color="rgba(255, 167, 38, 0.3)", width=1)),
        text=[f"{e:.1f} J" for e in energies],
        textposition="outside",
        textfont=dict(color="#f8fafc")
    ))

    fig.update_layout(
        title_text="Total System Energy Consumption (Joules)",
        xaxis=dict(title="Strategy", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        yaxis=dict(title="Energy (Joules)", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16, 22, 38, 0.65)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=340,
        margin=dict(l=50, r=30, t=40, b=40)
    )
    return fig
