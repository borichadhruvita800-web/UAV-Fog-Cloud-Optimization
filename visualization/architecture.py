"""
Architecture and Euro-28 topology visualizations.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import Dict, List, Tuple, Optional
import plotly.graph_objects as go
from config.settings import EURO_28_CITIES, EURO_28_LINKS, DEFAULT_CLOUD_CITY, THEME_CONFIG


def plot_euro28_network_map(
    cloud_city: str = DEFAULT_CLOUD_CITY,
    highlight_links: Optional[List[Tuple[str, str]]] = None,
    task_counts_per_city: Optional[Dict[str, int]] = None
) -> go.Figure:
    """
    Plots the Euro-28 optical network topology overlaid on a geographic map.
    Displays Fog Nodes (cities), Central Cloud Server, and bidirectional WDM links (600 km).
    """
    fig = go.Figure()

    # 1. Draw WDM Optical Links (62 links)
    for u, v in EURO_28_LINKS:
        if u in EURO_28_CITIES and v in EURO_28_CITIES:
            c1 = EURO_28_CITIES[u]
            c2 = EURO_28_CITIES[v]
            
            is_highlight = highlight_links and ((u, v) in highlight_links or (v, u) in highlight_links)
            line_color = THEME_CONFIG["accent_orange"] if is_highlight else "#3a4454"
            line_width = 3.5 if is_highlight else 1.5

            fig.add_trace(go.Scattergeo(
                lon=[c1["lon"], c2["lon"]],
                lat=[c1["lat"], c2["lat"]],
                mode="lines",
                line=dict(width=line_width, color=line_color),
                hoverinfo="none",
                showlegend=False
            ))

    # 2. Draw Fog Nodes (28 European Cities)
    fog_lats, fog_lons, fog_texts, fog_sizes = [], [], [], []
    for city, data in EURO_28_CITIES.items():
        if city != cloud_city:
            fog_lats.append(data["lat"])
            fog_lons.append(data["lon"])
            t_count = task_counts_per_city.get(city, 0) if task_counts_per_city else 0
            fog_texts.append(f"<b>Fog Node: {city}</b><br>Country: {data['country']}<br>Tasks: {t_count}<br>Capacity: 3600 MIPS")
            fog_sizes.append(10 + min(15, t_count * 2))

    fig.add_trace(go.Scattergeo(
        lon=fog_lons,
        lat=fog_lats,
        text=fog_texts,
        hoverinfo="text",
        mode="markers+text",
        textposition="top center",
        marker=dict(
            size=fog_sizes,
            color=THEME_CONFIG["accent_amber"],
            symbol="circle",
            line=dict(width=1.5, color="#ffffff")
        ),
        name="Fog Nodes (28 Cities)"
    ))

    # 3. Draw Central Cloud Server (Frankfurt)
    if cloud_city in EURO_28_CITIES:
        cloud_data = EURO_28_CITIES[cloud_city]
        fig.add_trace(go.Scattergeo(
            lon=[cloud_data["lon"]],
            lat=[cloud_data["lat"]],
            text=[f"<b>Central Cloud Server: {cloud_city}</b><br>Capacity: 18000 MIPS<br>Core WDM Backbone Hub"],
            hoverinfo="text",
            mode="markers+text",
            textposition="bottom center",
            marker=dict(
                size=18,
                color=THEME_CONFIG["accent_orange"],
                symbol="star",
                line=dict(width=2, color="#ffffff")
            ),
            name="Cloud Server (Frankfurt)"
        ))

    # Layout styling matching aerospace dark mission control with sunset palette
    fig.update_layout(
        geo=dict(
            scope="europe",
            projection_type="natural earth",
            showland=True,
            landcolor="#121826",
            showocean=True,
            oceancolor="#080c16",
            showcoastlines=True,
            coastlinecolor="rgba(255, 167, 38, 0.45)",
            showcountries=True,
            countrycolor="#1c2438",
            bgcolor="rgba(0,0,0,0)",
            resolution=50
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=30, b=0),
        legend=dict(
            x=0.02, y=0.98,
            bgcolor="rgba(16, 22, 38, 0.85)",
            bordercolor="rgba(255, 167, 38, 0.3)",
            borderwidth=1,
            font=dict(color="#f8fafc")
        ),
        height=520
    )
    return fig


def plot_system_layers_sankey(
    uav_count: int,
    fog_count: int,
    cloud_count: int
) -> go.Figure:
    """
    Renders a Sankey diagram showing task flow from UAV generation
    through Access, Metro, and Core network layers into processing destinations.
    """
    total = max(1, uav_count + fog_count + cloud_count)
    labels = [
        "UAV Tasks Generated",
        "Access Network (PON)",
        "Metro Network (MAN)",
        "Core Network (WAN/WDM)",
        "UAV Local Execution",
        "Fog Computing Tier",
        "Cloud Computing Tier"
    ]
    # Indices:
    # 0: UAV Tasks
    # 1: Access PON
    # 2: Metro MAN
    # 3: Core WAN
    # 4: UAV Local
    # 5: Fog
    # 6: Cloud

    sources = [0, 0, 1, 2, 2, 3]
    targets = [4, 1, 2, 5, 3, 6]
    values = [
        uav_count,                      # 0 -> 4: local UAV
        fog_count + cloud_count,        # 0 -> 1: into Access PON
        fog_count + cloud_count,        # 1 -> 2: into Metro MAN
        fog_count,                      # 2 -> 5: to Fog node
        cloud_count,                    # 2 -> 3: to Core WAN
        cloud_count                     # 3 -> 6: to Cloud Server
    ]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="rgba(255, 167, 38, 0.4)", width=1),
            label=labels,
            color=[
                THEME_CONFIG["accent_gold"],
                "#38bdf8",
                "#a78bfa",
                "#34d399",
                THEME_CONFIG["accent_amber"],
                THEME_CONFIG["accent_orange"],
                "#f87171"
            ]
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color="rgba(255, 123, 0, 0.35)"
        )
    )])

    fig.update_layout(
        title_text="Multi-Tier Task Offloading Flow & Network Traverse",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family=THEME_CONFIG["font_family"]),
        height=380,
        margin=dict(l=10, r=10, t=40, b=10)
    )
    return fig
