"""
UAV COLLABORATIVE COMPUTING — MISSION OPTIMIZATION
Interactive Simulation Platform for UAV Task Offloading in Fog-Cloud Computing.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import time
import base64
from pathlib import Path

# Set Streamlit page configuration as first command
st.set_page_config(
    page_title="UAV Collaborative Computing — Mission Optimization",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config.parameters import ResearchSystemParameters
from config.settings import (
    EURO_28_CITIES,
    DEFAULT_CLOUD_CITY,
    RESULTS_DIR,
    BACKGROUND_IMAGE_PATH,
    THEME_CONFIG
)
from simulation.environment import SimulationEnvironment
from simulation.task_generator import TaskGenerator
from simulation.engine import SimulationEngine
from simulation.scenarios import BENCHMARK_SCENARIOS
from visualization.architecture import plot_euro28_network_map, plot_system_layers_sankey
from visualization.allocation import plot_tier_distribution_donut, plot_class_allocation_breakdown
from visualization.energy import plot_layer_power_breakdown, plot_strategy_energy_comparison
from visualization.latency import plot_strategy_latency_comparison, plot_class_latency_benchmark
from visualization.comparison import plot_paper_curve, plot_figure_10_heuristic_validation


@st.cache_data
def get_base64_image(image_path: Path | str) -> str:
    """Reads and encodes local background image as base64 data URI."""
    try:
        p = Path(image_path)
        if p.exists():
            with open(p, "rb") as f:
                return base64.b64encode(f.read()).decode()
    except Exception:
        pass
    return ""


# Load background image
bg_b64 = get_base64_image(BACKGROUND_IMAGE_PATH)
bg_css_rule = (
    f"""
    background: linear-gradient(180deg, rgba(8, 12, 22, 0.86) 0%, rgba(13, 17, 30, 0.82) 40%, rgba(22, 17, 24, 0.90) 100%),
                url("data:image/jpeg;base64,{bg_b64}") no-repeat center center fixed;
    background-size: cover;
    """
    if bg_b64
    else "background: linear-gradient(180deg, #0a0e1a 0%, #101626 50%, #16101c 100%);"
)

# Custom Mission Control Styling matching Sunset Drone Aesthetics
st.markdown(f"""
<style>
    /* Full Page Background with Drone Sunset Backdrop */
    .stApp {{
        {bg_css_rule}
        color: #f8fafc;
        font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    }}

    /* Global Headings with Sunset Radiance */
    h1, h2, h3, h4 {{
        color: #ffb703 !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
        text-shadow: 0 0 20px rgba(255, 183, 3, 0.35);
    }}

    /* Hero Banner Header */
    .hero-banner {{
        background: linear-gradient(135deg, rgba(16, 22, 38, 0.82) 0%, rgba(30, 20, 26, 0.78) 100%);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 167, 38, 0.38);
        border-radius: 12px;
        padding: 22px 28px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 183, 77, 0.25);
    }}
    .hero-title {{
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ffe082 0%, #ffb703 40%, #ff8c00 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }}
    .hero-subtitle {{
        color: #cbd5e1;
        font-size: 1.0rem;
    }}

    /* Glassmorphic Metric Cards */
    .metric-card {{
        background: rgba(16, 22, 38, 0.78);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 167, 38, 0.3);
        border-radius: 10px;
        padding: 16px 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(255, 183, 77, 0.15);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }}
    .metric-card:hover {{
        transform: translateY(-2px);
        border-color: rgba(255, 183, 77, 0.6);
        box-shadow: 0 12px 28px rgba(255, 123, 0, 0.25);
    }}
    .metric-label {{
        color: #cbd5e1;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }}
    .metric-value {{
        color: #ffaa33;
        font-size: 1.85rem;
        font-weight: 800;
        margin-top: 4px;
        text-shadow: 0 0 14px rgba(255, 170, 51, 0.4);
    }}

    /* Status Badges */
    .status-badge {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: rgba(16, 185, 129, 0.2);
        color: #34d399;
        border: 1px solid #10b981;
    }}
    .status-badge-amber {{
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        background-color: rgba(245, 158, 11, 0.2);
        color: #fbbf24;
        border: 1px solid #f59e0b;
    }}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {{
        background: rgba(10, 14, 25, 0.94) !important;
        border-right: 1px solid rgba(255, 167, 38, 0.25);
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: #ffb703 !important;
    }}

    /* Primary and Secondary Buttons */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #ff7b00 0%, #d97706 100%) !important;
        color: #ffffff !important;
        border: 1px solid #ffb703 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 16px rgba(255, 123, 0, 0.45) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button[kind="primary"]:hover {{
        background: linear-gradient(135deg, #ff9100 0%, #f59e0b 100%) !important;
        box-shadow: 0 6px 22px rgba(255, 145, 0, 0.6) !important;
        transform: scale(1.02);
    }}
    .stButton > button:not([kind="primary"]) {{
        background: rgba(20, 26, 42, 0.8) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 167, 38, 0.3) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }}
    .stButton > button:not([kind="primary"]):hover {{
        border-color: #ffb703 !important;
        color: #ffb703 !important;
    }}

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: rgba(16, 22, 38, 0.85);
        padding: 8px;
        border-radius: 10px;
        border: 1px solid rgba(255, 167, 38, 0.28);
    }}
    .stTabs [data-baseweb="tab"] {{
        color: #cbd5e1;
        border-radius: 6px;
        padding: 8px 18px;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(90deg, #ff7b00 0%, #d97706 100%) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 10px rgba(255, 123, 0, 0.35);
    }}

    /* Glass Container Panels */
    div[data-testid="stExpander"] {{
        background: rgba(16, 22, 38, 0.7);
        border: 1px solid rgba(255, 167, 38, 0.25);
        border-radius: 10px;
    }}
    div[data-testid="stAlert"] {{
        background-color: rgba(16, 22, 38, 0.88);
        border: 1px solid rgba(255, 167, 38, 0.4);
        color: #f8fafc;
    }}
    
    /* Tables and DataFrames */
    [data-testid="stDataFrame"] {{
        background: rgba(16, 22, 38, 0.75);
        border: 1px solid rgba(255, 167, 38, 0.25);
        border-radius: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if "params" not in st.session_state:
    st.session_state.params = ResearchSystemParameters()
if "engine" not in st.session_state:
    st.session_state.engine = SimulationEngine(params=st.session_state.params)
if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None
if "sweep_results" not in st.session_state:
    st.session_state.sweep_results = None

# Sidebar Navigation
with st.sidebar:
    st.markdown("### 🛰️ MISSION CONTROL")
    st.markdown("<b style='color:#ffb703;'>UAV FOG–CLOUD OPTIMIZATION</b>", unsafe_allow_html=True)
    st.caption("IEEE Access 2024 Research Implementation")
    
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [
            "1. System Overview",
            "2. UAV–Fog–Cloud Architecture",
            "3. Simulation Configuration",
            "4. Task Offloading",
            "5. Energy Analysis",
            "6. Latency Analysis",
            "7. Strategy Comparison",
            "8. Results & Export"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("<h4 style='color:#ffd166; font-size:1.05rem;'>⚡ Quick Mission Actions</h4>", unsafe_allow_html=True)
    quick_uavs = st.slider("Quick UAV Batch Count", 10, 100, 30, step=10)
    if st.button("🚀 Execute Optimization Run", type="primary", use_container_width=True):
        with st.spinner("Formulating MILP and solving multi-tier offloading..."):
            res = st.session_state.engine.run_single_comparison(num_tasks=quick_uavs)
            st.session_state.simulation_results = res
            st.success("Optimization Solved Successfully!")

    st.markdown("---")
    st.markdown("<div style='font-size:0.85rem; color:#cbd5e1;'>Status: <span style='color:#34d399; font-weight:700;'>SYSTEM ONLINE</span></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.82rem; color:#94a3b8;'>Solvers: HiGHS (Active) / CBC (Standby)</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PAGE 1 — SYSTEM OVERVIEW
# -----------------------------------------------------------------------------
if page == "1. System Overview":
    st.markdown("""
    <div class="hero-banner">
        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 16px;">
            <div>
                <div class="hero-title">🛰️ UAV COLLABORATIVE COMPUTING — MISSION OPTIMIZATION</div>
                <div class="hero-subtitle">Real-time simulation platform for collaborative UAV task offloading in hierarchical Fog–Cloud computing environments</div>
            </div>
            <div style="display: flex; gap: 10px; align-items: center;">
                <span class="status-badge">🛰️ 28 FOG NODES</span>
                <span class="status-badge-amber">⚡ MILP HIGHS READY</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Top Mission Status Banner
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Active UAV Fleet</div>
            <div class="metric-value">100 / City</div>
            <span class="status-badge">800 MIPS Nominal</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Fog Edge Nodes</div>
            <div class="metric-value">{len(EURO_28_CITIES)} Cities</div>
            <span class="status-badge">3600 MIPS / Node</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Central Cloud Data Center</div>
            <div class="metric-value">{DEFAULT_CLOUD_CITY}</div>
            <span class="status-badge">18000 MIPS</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">MILP Optimization Engine</div>
            <div class="metric-value">HiGHS (0.003s)</div>
            <span class="status-badge">Optimal C1-C12</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.subheader("🌐 Euro-28 Telecommunication Network Overview")
        st.plotly_chart(plot_euro28_network_map(cloud_city=DEFAULT_CLOUD_CITY), use_container_width=True)

    with col_right:
        st.subheader("📋 Research Framework Summary")
        st.markdown("""
        <div class="metric-card" style="font-size:0.95rem; line-height:1.6; color:#f8fafc;">
            <p><b style="color:#ffb703;">• Primary Research Source:</b> Mohammad Aldossary, <i>IEEE Access</i>, 2024.</p>
            <p><b style="color:#ffb703;">• Core Innovation:</b> Autonomous collaborative task offloading balancing computation and networking across UAV, edge Fog, and central Cloud.</p>
            <p><b style="color:#ffb703;">• Mathematical Objective (Eq. 4):</b></p>
            <p style="text-align:center; color:#ffd166; font-weight:600;">min Power = (UAV + Access) + (Fog + Metro) + (Cloud + Core)</p>
            <p><b style="color:#ffb703;">• Network Infrastructure:</b></p>
            <ul style="color:#cbd5e1; margin-top:-6px;">
                <li><b>Access PON:</b> ONUs (2.4 Gbps, 5 W), OLTs (1.28 Tbps, 1842 W)</li>
                <li><b>Metro MAN:</b> Metro Routers (40 Gbps, 30 W), Switches (500 Gbps, 470 W)</li>
                <li><b>Core WAN:</b> WDM router ports (40 Gbps), transponders (129 W), 600 km links with amplifiers every 80 km</li>
            </ul>
            <p><b style="color:#ffb703;">• Documented Gains:</b> Up to <span style="color:#34d399; font-weight:700;">59.26%</span> latency reduction and <span style="color:#34d399; font-weight:700;">12.0%</span> energy savings vs standalone baselines.</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# PAGE 2 — UAV–FOG–CLOUD ARCHITECTURE
# -----------------------------------------------------------------------------
elif page == "2. UAV–Fog–Cloud Architecture":
    st.markdown("## 🏛️ Multi-Tier Collaborative Architecture")
    st.markdown("<p style='color:#cbd5e1;'>Interactive visualization of the three computing layers and telecommunication transport pipelines across Europe.</p>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🗺️ Geographic Topology (Euro-28)", "🔀 Task Flow & Layer Traverse"])
    
    with tab1:
        st.plotly_chart(plot_euro28_network_map(cloud_city=DEFAULT_CLOUD_CITY), use_container_width=True)
        st.info("The Euro-28 reference topology models 28 municipal fog nodes covering European cities, 1 central cloud server in Frankfurt, and 62 bidirectional optical fiber links (600 km length each, with optical amplification every 80 km).")

    with tab2:
        if st.session_state.simulation_results:
            summ = st.session_state.simulation_results["summaries"]["Proposed (Collaborative)"]
            u_c, f_c, c_c = summ["uav_tasks"], summ["fog_tasks"], summ["cloud_tasks"]
        else:
            u_c, f_c, c_c = 8, 16, 6
        st.plotly_chart(plot_system_layers_sankey(u_c, f_c, c_c), use_container_width=True)
        st.caption("Flow represents task dispatch from originating UAV through Access PON, Metro MAN, and Core WAN to optimal execution targets.")

# -----------------------------------------------------------------------------
# PAGE 3 — SIMULATION CONFIGURATION
# -----------------------------------------------------------------------------
elif page == "3. Simulation Configuration":
    st.markdown("## ⚙️ Simulation Configuration & Research Parameters")
    st.markdown("<p style='color:#cbd5e1;'>Adjust experimental parameters from Table 2, Table 3, and Table 4 of the research paper.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🛸 UAV & Access Layer Configuration")
        uav_power = st.number_input("UAV Power Consumption (Watts)", value=float(st.session_state.params.uav.power_watts), step=1.0)
        uav_mips = st.number_input("UAV Onboard Processing (MIPS)", value=float(st.session_state.params.uav.processing_mips), step=50.0)
        gw_power = st.number_input("Gateway Power (Watts)", value=float(st.session_state.params.uav.gateway_power_watts), step=1.0)
        onu_power = st.number_input("ONU Power (Watts)", value=float(st.session_state.params.access_net.onu_power_watts), step=0.5)
        olt_power = st.number_input("OLT Power (Watts)", value=float(st.session_state.params.access_net.olt_power_watts), step=10.0)
        pue_net = st.number_input("Network PUE", value=float(st.session_state.params.access_net.pue_network), step=0.1)

    with col2:
        st.subheader("☁️ Fog & Cloud Layer Configuration")
        fog_mips = st.number_input("Fog Node Capacity (MIPS)", value=float(st.session_state.params.fog.capacity_mips), step=100.0)
        fog_power = st.number_input("Fog Node Power (Watts)", value=float(st.session_state.params.fog.power_watts), step=5.0)
        pue_fog = st.number_input("Fog PUE", value=float(st.session_state.params.fog.pue_fog), step=0.05)
        cloud_mips = st.number_input("Cloud Server Capacity (MIPS)", value=float(st.session_state.params.cloud.capacity_mips), step=500.0)
        cloud_power = st.number_input("Cloud Server Power (Watts)", value=float(st.session_state.params.cloud.power_watts), step=10.0)
        pue_cloud = st.number_input("Cloud PUE", value=float(st.session_state.params.cloud.pue_cloud), step=0.05)

    st.markdown("---")
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        if st.button("💾 Apply & Update Parameters", type="primary", use_container_width=True):
            st.session_state.params.uav.power_watts = uav_power
            st.session_state.params.uav.processing_mips = uav_mips
            st.session_state.params.uav.gateway_power_watts = gw_power
            st.session_state.params.access_net.onu_power_watts = onu_power
            st.session_state.params.access_net.olt_power_watts = olt_power
            st.session_state.params.access_net.pue_network = pue_net
            st.session_state.params.fog.capacity_mips = fog_mips
            st.session_state.params.fog.power_watts = fog_power
            st.session_state.params.fog.pue_fog = pue_fog
            st.session_state.params.cloud.capacity_mips = cloud_mips
            st.session_state.params.cloud.power_watts = cloud_power
            st.session_state.params.cloud.pue_cloud = pue_cloud
            st.session_state.engine = SimulationEngine(params=st.session_state.params)
            st.success("Parameters updated in active simulation engine.")

    with c_btn2:
        if st.button("🔄 Reset to Original Research Paper Values", use_container_width=True):
            st.session_state.params = ResearchSystemParameters()
            st.session_state.engine = SimulationEngine(params=st.session_state.params)
            st.info("Reset to Table 2 & Table 4 research paper defaults.")
            st.rerun()

# -----------------------------------------------------------------------------
# PAGE 4 — TASK OFFLOADING
# -----------------------------------------------------------------------------
elif page == "4. Task Offloading":
    st.markdown("## 🎯 Task Offloading & Multi-Tier Placement")
    st.markdown("<p style='color:#cbd5e1;'>Real results returned by the Mixed-Integer Linear Programming (MILP) optimization engine.</p>", unsafe_allow_html=True)

    if st.session_state.simulation_results is None:
        st.info("No active simulation results. Click 'Execute Optimization Run' in the sidebar or run below.")
        if st.button("🚀 Run Live Task Offloading Simulation", type="primary"):
            st.session_state.simulation_results = st.session_state.engine.run_single_comparison(num_tasks=30)
            st.rerun()
    else:
        res = st.session_state.simulation_results
        collab_opt = res.get("collab_opt_result")
        executed_tasks = res["executed_tasks"]["Proposed (Collaborative)"]
        df_tasks = pd.DataFrame([t.to_dict() for t in executed_tasks])

        # Summary KPIs
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Total Tasks</div>
                <div class="metric-value">{len(df_tasks)}</div>
            </div>
            """, unsafe_allow_html=True)
        with k2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">UAV Tier Tasks</div>
                <div class="metric-value">{sum(df_tasks["assigned_destination"] == "uav")}</div>
            </div>
            """, unsafe_allow_html=True)
        with k3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Fog Tier Tasks</div>
                <div class="metric-value">{sum(df_tasks["assigned_destination"] == "fog")}</div>
            </div>
            """, unsafe_allow_html=True)
        with k4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cloud Tier Tasks</div>
                <div class="metric-value">{sum(df_tasks["assigned_destination"] == "cloud")}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            u_count = sum(df_tasks["assigned_destination"] == "uav")
            f_count = sum(df_tasks["assigned_destination"] == "fog")
            c_count = sum(df_tasks["assigned_destination"] == "cloud")
            st.plotly_chart(plot_tier_distribution_donut(u_count, f_count, c_count), use_container_width=True)
        with col_c2:
            st.plotly_chart(plot_class_allocation_breakdown(executed_tasks), use_container_width=True)

        st.subheader("📋 Optimization Decision Matrix")
        st.dataframe(
            df_tasks[[
                "task_id", "uav_id", "source_city", "task_class",
                "mips_required", "input_data_size_mb", "assigned_destination",
                "target_node_id", "execution_latency_ms", "total_energy_joules"
            ]],
            use_container_width=True,
            height=360
        )

# -----------------------------------------------------------------------------
# PAGE 5 — ENERGY ANALYSIS
# -----------------------------------------------------------------------------
elif page == "5. Energy Analysis":
    st.markdown("## ⚡ Energy & Power Consumption Analysis")
    st.markdown("<p style='color:#cbd5e1;'>Evaluation of equations (1), (2), (3), and (4) across UAV, Fog, Cloud, Access, Metro, and Core networks.</p>", unsafe_allow_html=True)

    if st.session_state.simulation_results is None:
        st.info("Please run an optimization first from the sidebar.")
    else:
        res = st.session_state.simulation_results
        collab_opt = res.get("collab_opt_result")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">UAV + Access Power (Eq 1)</div>
                <div class="metric-value">{collab_opt.power_uav_access_watts:.1f} W</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Fog + Metro Power (Eq 2)</div>
                <div class="metric-value">{collab_opt.power_fog_metro_watts:.1f} W</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Cloud + Core Power (Eq 3)</div>
                <div class="metric-value">{collab_opt.power_cloud_core_watts:.1f} W</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.plotly_chart(
                plot_layer_power_breakdown(
                    collab_opt.power_uav_access_watts,
                    collab_opt.power_fog_metro_watts,
                    collab_opt.power_cloud_core_watts
                ),
                use_container_width=True
            )
        with col_p2:
            st.plotly_chart(
                plot_strategy_energy_comparison(res["summaries"]),
                use_container_width=True
            )

        st.info("The proposed collaborative approach reduces overall energy by offloading computationally intensive tasks to power-efficient tiers while processing low-latency tasks locally to avoid transmission energy overhead.")

# -----------------------------------------------------------------------------
# PAGE 6 — LATENCY ANALYSIS
# -----------------------------------------------------------------------------
elif page == "6. Latency Analysis":
    st.markdown("## ⏱️ Service Latency Analysis")
    st.markdown("<p style='color:#cbd5e1;'>Service latency evaluation across UAV, Fog, Cloud, and Collaborative offloading.</p>", unsafe_allow_html=True)

    if st.session_state.simulation_results is None:
        st.info("Please run an optimization first from the sidebar.")
    else:
        res = st.session_state.simulation_results
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.plotly_chart(
                plot_strategy_latency_comparison(res["summaries"]),
                use_container_width=True
            )
        with col_l2:
            st.plotly_chart(
                plot_class_latency_benchmark(res["summaries"]),
                use_container_width=True
            )

        st.subheader("📊 Class-Level Latency Comparison (Paper Fig 6 Reproduction)")
        st.caption("Class A (500 MIPS - License plate/agriculture), Class B (2000 MIPS - Video surveillance), Class C (6000 MIPS - AR/VR)")
        class_rows = []
        for strat_name, s in res["summaries"].items():
            class_rows.append({
                "Strategy": strat_name,
                "Class A (ms)": s.get("class_A_latency_ms", 0.0),
                "Class B (ms)": s.get("class_B_latency_ms", 0.0),
                "Class C (ms)": s.get("class_C_latency_ms", 0.0),
                "Average Latency (ms)": s.get("avg_latency_ms", 0.0)
            })
        st.dataframe(pd.DataFrame(class_rows), use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 7 — STRATEGY COMPARISON
# -----------------------------------------------------------------------------
elif page == "7. Strategy Comparison":
    st.markdown("## 📊 Offloading Strategy Comparison & Benchmark Scenarios")
    st.markdown("<p style='color:#cbd5e1;'>Comparison across UAV-Only, Fog-Only, Cloud-Only, Proposed Collaborative (MILP), and Heuristic (Algorithm 1).</p>", unsafe_allow_html=True)

    if st.session_state.simulation_results:
        st.subheader("🏆 Current Run Comparison Matrix")
        st.dataframe(st.session_state.simulation_results["comparison_df"], use_container_width=True)

    st.markdown("---")
    st.subheader("🔬 Benchmark Scenario Parameter Sweeps (Reproduce Paper Figures)")
    
    scenario_choice = st.selectbox(
        "Select Research Benchmark Scenario",
        list(BENCHMARK_SCENARIOS.keys()),
        format_func=lambda k: f"{BENCHMARK_SCENARIOS[k].name} ({BENCHMARK_SCENARIOS[k].paper_figure_reference})"
    )
    
    selected_scenario = BENCHMARK_SCENARIOS[scenario_choice]
    st.caption(selected_scenario.description)

    if st.button(f"▶️ Run Parameter Sweep for {selected_scenario.name}", type="primary"):
        prog_bar = st.progress(0.0)
        status_txt = st.empty()

        def update_progress(p, text):
            prog_bar.progress(p)
            status_txt.text(text)

        with st.spinner("Executing parameter sweep with Monte Carlo iterations..."):
            df_sweep = st.session_state.engine.run_parameter_sweep(
                scenario_key=scenario_choice,
                iterations_per_point=3,
                progress_callback=update_progress
            )
            st.session_state.sweep_results = (scenario_choice, df_sweep)
            prog_bar.progress(1.0)
            status_txt.text("Parameter sweep finished successfully!")

    if st.session_state.sweep_results and st.session_state.sweep_results[0] == scenario_choice:
        _, df_sweep = st.session_state.sweep_results
        
        c_plot1, c_plot2 = st.columns(2)
        with c_plot1:
            st.plotly_chart(
                plot_paper_curve(
                    df_sweep,
                    x_col="Parameter_Value",
                    y_col="Avg_Latency_ms",
                    title=f"Service Time vs {selected_scenario.parameter_name}",
                    x_label=selected_scenario.parameter_name,
                    y_label="Service Time (ms)"
                ),
                use_container_width=True
            )
        with c_plot2:
            st.plotly_chart(
                plot_paper_curve(
                    df_sweep,
                    x_col="Parameter_Value",
                    y_col="Total_Energy_J",
                    title=f"Energy Consumption vs {selected_scenario.parameter_name}",
                    x_label=selected_scenario.parameter_name,
                    y_label="Energy Consumption (J)"
                ),
                use_container_width=True
            )

        # If Heuristic Validation scenario, show Fig 10
        if scenario_choice == "heuristic_validation":
            st.subheader("Figure 10 Reproduction: MILP vs Heuristic Difference")
            milp_en = df_sweep[df_sweep["Strategy"] == "Proposed (Collaborative)"]["Total_Energy_J"].mean()
            heur_en = df_sweep[df_sweep["Strategy"] == "Heuristic (Algorithm 1)"]["Total_Energy_J"].mean()
            st.plotly_chart(plot_figure_10_heuristic_validation(milp_en, heur_en), use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 8 — RESULTS AND EXPORT
# -----------------------------------------------------------------------------
elif page == "8. Results & Export":
    st.markdown("## 💾 Results Export & Research Data Repository")
    st.markdown("<p style='color:#cbd5e1;'>Download simulation results, optimization logs, and experiment configurations.</p>", unsafe_allow_html=True)

    if st.session_state.simulation_results is not None:
        res = st.session_state.simulation_results
        executed_tasks = res["executed_tasks"]["Proposed (Collaborative)"]
        df_tasks = pd.DataFrame([t.to_dict() for t in executed_tasks])

        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            st.subheader("📥 Export Task Decisions (CSV)")
            csv_data = df_tasks.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Task Decisions CSV",
                data=csv_data,
                file_name="uav_task_offloading_decisions.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

        with c_exp2:
            st.subheader("📥 Export Strategy Comparison (CSV)")
            comp_csv = res["comparison_df"].to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Strategy Comparison CSV",
                data=comp_csv,
                file_name="strategy_comparison_metrics.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown("---")
        st.subheader("⚙️ Active Research Parameters JSON")
        params_json = json.dumps(st.session_state.params.to_dict(), indent=2)
        st.download_button(
            label="Download Parameters JSON",
            data=params_json.encode("utf-8"),
            file_name="research_parameters.json",
            mime="application/json"
        )
        st.json(st.session_state.params.to_dict())
    else:
        st.info("Execute an optimization run or parameter sweep to generate exportable datasets.")
