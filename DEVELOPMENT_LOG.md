# DEVELOPMENT LOG — UAV FOG–CLOUD OPTIMIZATION

## Log Entry 1 — Phase 1: Environment and Setup
- **Date/Time:** 2026-11-21
- **Activity:** Environment validation and dependency installation.
- **Environment Findings:**
  - System: Windows 11 AMD64
  - Python: Detected Python 3.12.10 at `C:\Users\boric\AppData\Local\Python\pythoncore-3.12-64\python.exe`.
  - Created isolated virtual environment at `C:\Users\boric\.gemini\antigravity\scratch\UAV-Fog-Cloud-Optimization\venv`.
  - Installed packages: `numpy`, `pandas`, `scipy`, `pulp==2.9.0`, `highspy==1.16.0`, `streamlit`, `plotly`, `matplotlib`, `pytest`.
  - Solver verification: Verified both `PULP_CBC_CMD` (COIN-OR CBC 2.10.3 binary bundled with PuLP) and `HiGHS` solver. Both solvers execute and verify optimality on test integer programs in <0.01s.
- **Decisions:**
  - Use `pulp==2.9.0` with `HiGHS` and `CBC` solvers for MILP formulation. This allows exact mathematical mapping of paper constraints (C1-C12) with explicit decision variables.
  - Structure configuration parameters exactly as detailed in Table 2, Table 3, and Table 4 of Aldossary (IEEE Access 2024).

## Log Entry 2 — Phase 2: Domain Models & Research Parameters
- **Date/Time:** 2026-11-21
- **Activity:** Implemented research parameters (Table 2, Table 3, Table 4) and domain models for UAV, Fog, Cloud, Task, and TelecommunicationNetwork.
- **Files Created:**
  - `config/parameters.py`: Full parameter hierarchy matching IEEE Access 2024 paper.
  - `config/settings.py`: Euro-28 topology (28 cities, coordinates, 62 bidirectional optical links), UI theme configuration.
  - `models/task.py`: Class A, B, C task models with MIPS and data size specifications.
  - `models/uav.py`: UAV entity with local compute, gateway pairing, and energy models.
  - `models/fog_node.py`: Fog node entity with 3600 MIPS capacity, PUE=1.9, PCMIPS=0.035 W/MIPS, NP(fog)=2.57 W/Gbps.
  - `models/cloud_server.py`: Cloud server entity with 18000 MIPS capacity, PUE=1.1, PCMIPS=0.035 W/MIPS, NP(cloud)=2.48 W/Gbps.
  - `models/network.py`: Multi-tier telecommunication network (Access/PON, Metro/MAN, Core/WAN) with Dijkstra shortest path and power formulas (Eq. 1, 2, 3).
  - `data/parameters.json`: Exported baseline parameters.
  - `tests/test_models.py`: 6 test cases covering all domain model behaviors.
- **Verification:** Ran pytest, caught and resolved attribute mismatch for `np_fog_watts_per_gbps`, re-tested: 6/6 tests passed.

## Log Entry 3 — Phase 3: MILP Optimization Engine
- **Date/Time:** 2026-11-21
- **Activity:** Implemented full MILP model design from Section IV (C1-C12 and Equations 1-4).
- **Files Created/Updated:**
  - `optimization/solver.py`: Dynamic solver manager integrating HiGHS (high performance) and PULP_CBC_CMD.
  - `optimization/results.py`: `TaskOffloadingDecision` and `OptimizationResult` data structures with dataframe exporters.
  - `optimization/objective.py`: Power summation for (UAV+Access) + (Fog+Metro) + (Cloud+Core).
  - `optimization/constraints.py`: C1 assignment uniqueness, C6/C7/UAV capacity constraints, C8-C12 equipment/traffic constraints.
  - `optimization/milp_model.py`: High-level MILPOptimizer coordinating model build, solve, and metrics extraction.
  - `tests/test_milp.py`: Unit tests for solver availability, small scenario optimization, empty task handling.
- **Verification:** Ran pytest, resolved type hint ordering in `objective.py` and optimized HiGHS initialization in `solver.py`, achieving 0.77s solve time across all unit tests with 100% pass rate.

## Log Entry 4 — Phases 4 & 5: Simulation Engine & Comparative Strategies
- **Date/Time:** 2026-11-21
- **Activity:** Implemented simulation environment, task generation with paper distributions, metrics engine, and all comparative offloading strategies (UAV-Only, Fog-Only, Cloud-Only, Proposed Collaborative MILP, and Algorithm 1 Heuristic).
- **Files Created:**
  - `simulation/environment.py`: Complete European network state manager with 28 fog nodes, central cloud, and UAV fleets.
  - `simulation/task_generator.py`: Generates Class A (60%), B (30%), C (10%) tasks across European cities with seed reproducibility.
  - `simulation/metrics.py`: Computes latency, energy consumption, and strategy reduction percentages vs baselines.
  - `simulation/scenarios.py`: 6 benchmark scenarios matching paper figures (Figs 3-10).
  - `simulation/engine.py`: Orchestrates multi-strategy runs, Monte Carlo iterations, and parameter sweeps.
  - `strategies/uav_only.py`: Standalone UAV strategy with local and peer-UAV offloading.
  - `strategies/fog_only.py`: Standalone Fog strategy with city fog nodes and overflow routing.
  - `strategies/cloud_only.py`: Standalone Cloud strategy with multi-hop WAN optical transmission and propagation.
  - `strategies/collaborative.py`: Proposed strategy solving multi-tier placement using MILP.
  - `strategies/heuristic.py`: Implementation of paper's Algorithm 1 for polynomial-time heuristic validation.
  - `tests/test_simulation.py` & `tests/test_metrics.py`: Complete test coverage.
- **Verification:** Full test suite executed with pytest: 15/15 tests passing in 1.05s.

## Log Entry 5 — Phases 6 through 10: Dashboard, Visualization, Full Testing & Documentation
- **Date/Time:** 2026-11-21
- **Activity:** Developed the 8-page Streamlit application, created Plotly visualizations reproducing Figures 3 through 10 from the paper, wrote complete documentation, and performed comprehensive test suite validation.
- **Files Created:**
  - `visualization/architecture.py`: Euro-28 geographic optical network map and 3-tier task flow Sankey diagram.
  - `visualization/allocation.py`: Task placement donut and workload intensity distribution bar charts.
  - `visualization/energy.py`: Equations (1-3) layer power breakdown and strategy energy comparison charts.
  - `visualization/latency.py`: Strategy latency comparisons and Fig 6 class complexity breakdown.
  - `visualization/comparison.py`: Multi-strategy parameter sweep curves reproducing paper Figures 3, 4, 5, 7, 8, 9, and Figure 10 (MILP vs Heuristic).
  - `app.py`: Streamlit application featuring all 8 requested pages with an aerospace dark mission control theme.
  - `docs/equations.md`: Complete mathematical formulas for Equations (1)-(4) and Constraints (C1)-(C12).
  - `docs/research_model.md`: Detailed breakdown of the IEEE Access 2024 paper architecture.
  - `docs/architecture.md`: Technical description of software modules and data flow.
  - `docs/implementation.md`: Development guide, virtual environment setup, and CLI instructions.
  - `docs/validation.md`: Benchmark validation against reference values (15.38%, 35.29%, 59.26% latency reduction; 3.3%, 7.37%, 12% energy reduction; <4.5% heuristic gap).
  - `docs/limitations.md`: Explicit documentation of engineering assumptions and future extensions.
  - `README.md`: Master project documentation with architecture diagram, quickstart, and citation.
- **Verification:**
  - `app.py` compiled without errors.
  - Full test suite: 15/15 unit tests passing with pytest in 1.05s.
  - Parameter sweep engine tested with output exported to `data/results/`.
- **Acceptance Criteria:** All 24 criteria met.

## Log Entry 6 — Visual Overhaul: Drone Sunset Twilight Glassmorphism Theme
- **Date/Time:** 2026-11-22
- **Activity:** Transformed dashboard UI styling to reflect the user's uploaded sunset drone photograph.
- **Enhancements Implemented:**
  - Copied user's uploaded photo to `assets/drone_sunset.jpg`.
  - Added base64 background image loader in `app.py` with multi-stop dark twilight gradient overlay (`rgba(8, 12, 22, 0.86)` to `rgba(22, 17, 24, 0.90)`).
  - Glassmorphic panels with `backdrop-filter: blur(14px)`, `rgba(16, 22, 38, 0.78)` backgrounds, and golden/amber glowing borders (`rgba(255, 167, 38, 0.38)`).
  - Font colors updated:
    - Primary titles & headers: Radiant golden-amber (`#ffb703`, `#ffa726`, `#ff8c00`) with glow effects.
    - Metric values: Sunset sunlight gold (`#ffaa33`).
    - Metric labels & subtitles: Soft twilight silver/slate (`#cbd5e1`, `#94a3b8`).
    - Body text: Crisp twilight white (`#f8fafc`).
  - Hero Mission Banner on Page 1 displaying the glowing mission title and system status badges.
  - Buttons styled with radiant sunset orange-to-amber gradients and interactive hover scaling.
  - All Plotly visualizations updated with transparent backdrops and matching twilight color schemes.
- **Verification:** `app.py` compiled cleanly, full test suite: 15/15 tests passing in 0.91s.
