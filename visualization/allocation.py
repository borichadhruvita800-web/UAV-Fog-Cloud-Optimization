"""
Task allocation visualizations.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import List, Dict, Any
import plotly.graph_objects as go
import pandas as pd
from config.settings import THEME_CONFIG
from models.task import UAVTask


def plot_tier_distribution_donut(uav_count: int, fog_count: int, cloud_count: int) -> go.Figure:
    """Renders a donut chart of task allocation across tiers."""
    labels = ["UAV Tier", "Fog Tier", "Cloud Tier"]
    values = [uav_count, fog_count, cloud_count]
    colors = [
        THEME_CONFIG["accent_gold"],
        THEME_CONFIG["accent_orange"],
        THEME_CONFIG["accent_red"]
    ]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color="#161b22", width=2)),
        textinfo="label+percent+value",
        hoverinfo="label+value+percent",
        textfont=dict(color="#f0f6fc", size=13)
    )])

    fig.update_layout(
        title_text="Offloading Tier Allocation Ratio",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=320,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=-0.1, font=dict(color="#f8fafc"))
    )
    return fig


def plot_class_allocation_breakdown(tasks: List[UAVTask]) -> go.Figure:
    """Renders a stacked bar chart of Application Classes A, B, C allocated to UAV, Fog, Cloud."""
    data = {"uav": {"A": 0, "B": 0, "C": 0},
            "fog": {"A": 0, "B": 0, "C": 0},
            "cloud": {"A": 0, "B": 0, "C": 0}}

    for t in tasks:
        tier = t.assigned_destination or "fog"
        c = t.task_class
        if tier in data and c in data[tier]:
            data[tier][c] += 1

    tiers = ["UAV", "Fog", "Cloud"]
    fig = go.Figure()

    class_colors = {
        "A": "#38bdf8",
        "B": THEME_CONFIG["accent_gold"],
        "C": THEME_CONFIG["accent_orange"]
    }
    class_labels = {
        "A": "Class A (500 MIPS - Low)",
        "B": "Class B (2000 MIPS - Med)",
        "C": "Class C (6000 MIPS - High)"
    }

    for c in ["A", "B", "C"]:
        counts = [data["uav"][c], data["fog"][c], data["cloud"][c]]
        fig.add_trace(go.Bar(
            name=class_labels[c],
            x=tiers,
            y=counts,
            marker_color=class_colors[c]
        ))

    fig.update_layout(
        barmode="stack",
        title_text="Workload Intensity Placement by Layer",
        xaxis=dict(title="Execution Tier", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        yaxis=dict(title="Task Count", color="#f8fafc", gridcolor="rgba(255, 255, 255, 0.08)"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(16, 22, 38, 0.65)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=320,
        margin=dict(l=40, r=20, t=40, b=20),
        legend=dict(orientation="h", y=-0.2, font=dict(color="#f8fafc"))
    )
    return fig
