# REPRODUCTION ASSUMPTIONS & KNOWN LIMITATIONS

This document details the explicit engineering assumptions, reproduction nuances, and future research extensions for the software implementation of:
*"Optimizing Task Offloading for Collaborative Unmanned Aerial Vehicles (UAVs) in Fog–Cloud Computing Environments"* — Mohammad Aldossary, IEEE Access, 2024.

---

## 1. Research Implementation Assumptions

1. **UAV Onboard Processing Capacity:**
   - Table 2 in the paper lists UAV power (63 W), data rate (100 Kbps), and gateway capacity (3 UAVs per gateway), but does not state a numerical value for single UAV MIPS.
   - *Engineering Decision:* In accordance with related multi-tier MEC literature cited in the paper (e.g., Alharbi et al. [38], Almutairi et al. [1]), UAV onboard processing capacity is set to **800 MIPS**. This allows Class A tasks (500 MIPS) to be computed locally in ~625 ms, while Class B (2000 MIPS) and Class C (6000 MIPS) benefit heavily from Fog or Cloud offloading.

2. **Optical Link Propagation Delay:**
   - The paper specifies 62 bidirectional optical links of 600 km length each.
   - Optical propagation speed in single-mode fiber is set to $200\,000$ km/s, contributing $3.0$ ms of propagation delay per 600 km link.
   - Inter-city shortest paths are computed via Dijkstra's algorithm over the Euro-28 topological graph.

3. **Solver Selection:**
   - The paper used the commercial IBM ILOG CPLEX solver.
   - To ensure free, open-source, and zero-license installation across platforms, this software integrates **HiGHS** and **COIN-OR CBC** via PuLP. Both solvers solve the exact mathematical MILP model (C1-C12) in milliseconds, producing provably optimal integer programming solutions.

---

## 2. Model Limitations & Scope

1. **Static Time-Slot Formulation:**
   - The paper's MILP formulation optimizes task offloading decisions per time-slot/snapshot. It does not model continuous 3D aerodynamic flight trajectories or battery drainage dynamics over prolonged multi-hour flight missions.

2. **Wireless Channel Fading:**
   - Air-to-ground communication assumes nominal uplink bandwidth (54 Mbps) and PON access transfer rates. Microscopic Doppler shifts and Rayleigh/Rician fast-fading channel variations are abstracted into average effective transfer rates.

---

## 3. Future Research Extensions (Section VII)

As highlighted in the conclusion of the research paper:
- Integration of Deep Reinforcement Learning (DRL) and Deep Q-Networks (DQN) for dynamic real-time UAV trajectory planning in uncertain environments.
- Multi-objective Pareto optimization balancing energy consumption, carbon footprint, and latency deadlines simultaneously.
