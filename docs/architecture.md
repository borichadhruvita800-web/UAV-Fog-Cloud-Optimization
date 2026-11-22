# SOFTWARE SYSTEM ARCHITECTURE

## 1. Modular Architecture Overview

```
UAV-Fog-Cloud-Optimization/
├── app.py                      # Streamlit Mission Control (8 Pages)
├── requirements.txt            # Dependency specification
├── config/
│   ├── settings.py             # Euro-28 cities, links, colors, paths
│   └── parameters.py           # Dataclasses for Table 2, 3, 4 parameters
├── models/
│   ├── uav.py                  # UAV entity with onboard compute & gateway pairing
│   ├── fog_node.py             # Fog node entity (3600 MIPS, PUE 1.9)
│   ├── cloud_server.py         # Cloud entity (18000 MIPS, PUE 1.1)
│   ├── network.py              # TelecommunicationNetwork (PON, MAN, WAN, Dijkstra)
│   └── task.py                 # UAVTask data model with Class A/B/C definitions
├── optimization/
│   ├── solver.py               # SolverManager for HiGHS and CBC solvers
│   ├── objective.py            # MILP objective builder (Eq. 4)
│   ├── constraints.py          # MILP constraints builder (C1 - C12)
│   ├── milp_model.py           # MILPOptimizer executive
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
│   └── comparison.py           # Paper reproduction curves (Figs 3, 4, 5, 7, 8, 9, 10)
├── data/
│   ├── parameters.json         # Exported baseline research parameters
│   ├── scenarios/              # Scenario configurations
│   └── results/                # Exported CSV result datasets
├── tests/
│   ├── test_models.py          # Domain model unit tests
│   ├── test_milp.py            # MILP engine unit tests
│   ├── test_simulation.py      # Simulation & strategy unit tests
│   └── test_metrics.py         # Metrics calculation unit tests
└── docs/                       # Research and technical documentation
```

---

## 2. Component Design & Information Flow

1. **Parameter Layer:**
   - `ResearchSystemParameters` encapsulates all physical constants, device power draws, bitrates, and PUE factors.
   - Serializes to and from JSON for reproducibility and user experimentation.

2. **Domain Models Layer:**
   - Independent classes representing UAVs, Fog nodes, Cloud servers, and Tasks.
   - `TelecommunicationNetwork` maintains the Euro-28 graph topology and calculates multi-tier routing (Dijkstra) and transmission latencies.

3. **Optimization Engine:**
   - Formulates the exact MILP model in PuLP using binary variables $\theta_{i,d}$ and integer equipment dimensioning variables.
   - Solves via HiGHS or CBC in milliseconds.

4. **Simulation Engine:**
   - Coordinates Monte Carlo parameter sweeps reproducing research paper experiments.
   - Produces structured pandas DataFrames exported to `data/results/`.

5. **Presentation Layer:**
   - Interactive Streamlit dashboard with custom dark aerospace mission control styling.
   - 8 specialized views connected to live simulation data and Plotly charts.
