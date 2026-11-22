# UAV FOG–CLOUD OPTIMIZATION
## UAV COLLABORATIVE COMPUTING — MISSION OPTIMIZATION

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![MILP Solver](https://img.shields.io/badge/solver-HiGHS%20%7C%20CBC-orange.svg)](https://highs.dev/)
[![Streamlit](https://img.shields.io/badge/dashboard-Streamlit-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive, aerospace mission-control simulation platform implementing the research paper:

> **"Optimizing Task Offloading for Collaborative Unmanned Aerial Vehicles (UAVs) in Fog–Cloud Computing Environments"**  
> **Author:** Mohammad Aldossary  
> **Journal:** *IEEE Access*, Vol. 12, pp. 74698–74710, 2024.  
> **DOI:** [10.1109/ACCESS.2024.3405566](https://doi.org/10.1109/ACCESS.2024.3405566)

---

## 🚀 Key Features

- **Exact Mathematical MILP Formulation:** Minimizes total system power $(P_{UAV+Access}) + (P_{Fog+Metro}) + (P_{Cloud+Core})$ subject to constraints **C1 through C12**.
- **Real MILP Optimization Engine:** Solves the combinatorial multi-tier task offloading problem using **HiGHS** and **COIN-OR CBC** via PuLP in milliseconds.
- **Hierarchical 3-Tier Computing:** Autonomous UAV swarms (800 MIPS), municipal Fog edge nodes (3600 MIPS each across 28 European cities), and a central Cloud data center (18000 MIPS in Frankfurt).
- **Multi-Tier Telecommunication Transport:** Access Network (PON with ONUs and OLTs), Metro Area Network (MAN with Metro Routers and Metro Switches), and Core Network (WAN IP-over-WDM with optical amplifiers every 80 km).
- **Multi-Strategy Comparison:** Evaluates:
  1. *UAV Execution* (Standalone UAV layer with peer-to-peer offloading)
  2. *Fog Execution* (Standalone edge municipal fog nodes with overflow routing)
  3. *Cloud Execution* (Standalone central remote cloud via multi-hop WAN)
  4. *Proposed Collaborative Strategy* (MILP-optimized multi-tier placement)
  5. *Heuristic Validation* (Polynomial-time Algorithm 1 from paper Section VI)
- **Paper Figure Reproductions:** Faithfully reproduces Figures 3, 4, 5, 6, 7, 8, 9, and 10 from the original research paper.
- **Aerospace Mission Control Dashboard:** Built with Streamlit and Plotly, styled with dark charcoal, deep graphite, and aerospace amber/orange accents.
- **Export & Persistence:** Download task offloading matrices, parameter configurations, and benchmark datasets in CSV and JSON formats.

---

## 📁 Project Architecture

```
UAV-Fog-Cloud-Optimization/
├── app.py                      # Streamlit Mission Control (8 Pages)
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview & documentation
├── .gitignore                  # Git ignore rules
├── PROJECT_PROGRESS.md         # Development tracker
├── DEVELOPMENT_LOG.md          # Implementation decisions & logs
├── config/
│   ├── settings.py             # Euro-28 cities, links, colors, paths
│   └── parameters.py           # Dataclasses for Tables 2, 3, 4
├── models/
│   ├── uav.py                  # UAV entity with local compute & gateway
│   ├── fog_node.py             # Fog node entity (3600 MIPS, PUE 1.9)
│   ├── cloud_server.py         # Cloud server entity (18000 MIPS, PUE 1.1)
│   ├── network.py              # TelecommunicationNetwork (PON, MAN, WAN, Dijkstra)
│   └── task.py                 # UAVTask data model with Class A/B/C definitions
├── optimization/
│   ├── solver.py               # SolverManager for HiGHS and CBC solvers
│   ├── objective.py            # MILP objective builder (Eq. 4)
│   ├── constraints.py          # MILP constraints builder (C1 - C12)
│   ├── milp_model.py           # High-level MILPOptimizer
│   └── results.py              # OptimizationResult and TaskOffloadingDecision
├── simulation/
│   ├── environment.py          # Euro-28 multi-tier simulation environment
│   ├── task_generator.py       # Task generator with Table 4 frequencies
│   ├── scenarios.py            # Benchmark scenarios (Figs 3-10)
│   ├── metrics.py              # Latency, energy, percentage savings calculator
│   └── engine.py               # SimulationEngine for runs & parameter sweeps
├── strategies/
│   ├── uav_only.py             # Standalone UAV strategy
│   ├── fog_only.py             # Standalone Fog strategy
│   ├── cloud_only.py           # Standalone Cloud strategy
│   ├── collaborative.py        # Proposed Collaborative MILP strategy
│   └── heuristic.py            # Algorithm 1 Heuristic validation strategy
├── visualization/
│   ├── architecture.py         # Euro-28 geographic map & Sankey flow
│   ├── allocation.py           # Donut & stacked bar workload distributions
│   ├── energy.py               # Layer power (Eqs 1-3) & total energy charts
│   ├── latency.py              # Latency benchmarks & Fig 6 class breakdown
│   └── comparison.py           # Paper reproduction curves (Figs 3-10)
├── data/
│   ├── parameters.json         # Exported baseline research parameters
│   ├── scenarios/              # Scenario definitions
│   └── results/                # Exported CSV result datasets
├── tests/
│   ├── test_models.py          # Domain model unit tests
│   ├── test_milp.py            # MILP engine unit tests
│   ├── test_simulation.py      # Simulation & strategy unit tests
│   └── test_metrics.py         # Metrics calculation unit tests
└── docs/
    ├── research_model.md       # IEEE Access 2024 model overview
    ├── architecture.md         # Technical architecture documentation
    ├── equations.md            # Exact mathematical formulas (Eqs 1-4, C1-C12)
    ├── implementation.md       # Implementation guide & runbook
    ├── validation.md           # Benchmark validation against paper values
    └── limitations.md          # Assumptions & research extensions
```

---

## ⚡ Quickstart Guide

### 1. Environment Setup (Windows PowerShell)

```powershell
# Navigate to the project root directory
Set-Location "C:\Users\boric\.gemini\antigravity\scratch\UAV-Fog-Cloud-Optimization"

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install requirements (if configuring a new machine)
pip install -r requirements.txt
```

### 2. Run All Tests

```powershell
pytest
```
*Expected: 15 passed in ~1.0 second.*

### 3. Launch the Mission Control Dashboard

```powershell
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 📊 Dashboard Pages Overview

1. **Page 1 — System Overview:** Fleet readiness, Euro-28 network status, active solver engine, architecture overview.
2. **Page 2 — UAV–Fog–Cloud Architecture:** Interactive European topology map with optical links and 3-tier Sankey data flow.
3. **Page 3 — Simulation Configuration:** Configure UAVs, MIPS capacities, bitrates, PUE factors, or reset to paper defaults.
4. **Page 4 — Task Offloading:** Live MILP optimization execution, decision table, tier ratio donut, and workload class distribution.
5. **Page 5 — Energy Analysis:** Layer power consumption (Eq 1: UAV+Access, Eq 2: Fog+Metro, Eq 3: Cloud+Core), total energy in Joules.
6. **Page 6 — Latency Analysis:** Service latency comparison, communication vs computation delay, Figure 6 reproduction.
7. **Page 7 — Strategy Comparison:** Side-by-side benchmark of 5 offloading strategies and automated parameter sweeps (Figs 3-10).
8. **Page 8 — Results & Export:** Download decision matrices (CSV), strategy benchmarks (CSV), and parameters (JSON).

---

## 🔬 Research Findings Reproduction

The simulation platform validates the paper's core findings:

- **Service Latency Reduction:**
  - **15.38%** reduction vs UAV Execution.
  - **35.29%** reduction vs Fog Execution.
  - **59.26%** reduction vs Cloud Execution.
- **Overall Energy Consumption Reduction:**
  - **3.3%** reduction vs UAV Execution.
  - **7.37%** reduction vs Fog Execution.
  - **12.0%** reduction vs Cloud Execution.
- **Heuristic Validation (Algorithm 1):**
  - Evaluates within sub-second timeframe.
  - Maximum difference in power consumption is **$\le 4.5\%$** relative to the exact MILP solution.

---

## 📜 Citation

```bibtex
@article{aldossary2024optimizing,
  title={Optimizing Task Offloading for Collaborative Unmanned Aerial Vehicles (UAVs) in Fog--Cloud Computing Environments},
  author={Aldossary, Mohammad},
  journal={IEEE Access},
  volume={12},
  pages={74698--74710},
  year={2024},
  publisher={IEEE},
  doi={10.1109/ACCESS.2024.3405566}
}
```
