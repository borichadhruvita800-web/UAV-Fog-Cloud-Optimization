# RESEARCH MODEL DOCUMENTATION

**Paper Title:** Optimizing Task Offloading for Collaborative Unmanned Aerial Vehicles (UAVs) in Fog–Cloud Computing Environments  
**Author:** Mohammad Aldossary  
**Journal:** IEEE Access, Volume 12, May 2024 (Digital Object Identifier: 10.1109/ACCESS.2024.3405566)

---

## 1. System Architecture Overview

The system models a multi-tier collaborative computing environment with three primary computing layers interconnected by three telecommunication network tiers:

```
[ Central Cloud Server (Frankfurt - 18000 MIPS) ]
                       ▲
                       │ (Core WAN / IP over WDM / 600 km spans)
                       ▼
[ Metro Area Fog Nodes (28 European Cities - 3600 MIPS each) ]
                       ▲
                       │ (Metro MAN / Ethernet / 40 Gbps - 0.5 Tbps)
                       ▼
[ Access Gateways (PON: ONU 2.4 Gbps, OLT 1.280 Tbps) ]
                       ▲
                       │ (Wireless Air-to-Ground / Peer-to-Peer 54 Mbps)
                       ▼
[ Collaborative UAV Swarm (100 UAVs per City - 800 MIPS, 63 W) ]
```

---

## 2. Telecommunication Network Tiers

1. **Access Network (LAN):**
   - Implemented via Passive Optical Networks (PONs).
   - End-user terminals connect via Optical Network Units (ONUs, 2.4 Gbps, 5 Watts) and Optical Line Terminals (OLTs, 1.280 Tbps, 1842 Watts).
   - Gateways bundle up to 3 UAVs (30 Watts each).
   - Network Power Usage Effectiveness ($PUE^{(network)} = 1.5$).

2. **Metro Area Network (MAN):**
   - Operates with Metro Ethernet technology interconnecting local UAV clusters and municipal Fog nodes.
   - Metro Routers (MR, 40 Gbps, 30 Watts) and Metro Switches (MS, 0.5 Tbps, 470 Watts).
   - Internal Fog networking overhead ($NP^{(fog)} = 2.57$ Watts/Gbps).

3. **Core Network (WAN):**
   - High-capacity backbone utilizing Internet Protocol (IP) over Wavelength Division Multiplexing (WDM).
   - 62 bidirectional optical links spanning 600 km each in the Euro-28 reference topology.
   - Optical amplification with max span of 80 km ($A_{m,n} = \lceil 600 / 80 - 1 \rceil = 7$ amplifiers per link, 11 Watts each, 2 fibers).
   - Transponders ($129$ Watts), Core Router ports ($40$ Gbps, $37.1$ Watts), and Optical Switches ($85$ Watts).

---

## 3. Workload Classification (Table 4)

| Application Name | Class | Intensity (MIPS) | Frequency | Real-world Context |
|---|---|---|---|---|
| Number Plate / Health / Sustainable Agriculture | **A** | 500 MIPS | 60% | Low processing, real-time sensing |
| Fire Detection / Video Surveillance | **B** | 2000 MIPS | 30% | Medium processing, computer vision |
| Augmented Reality / Virtual Reality (AR/VR) | **C** | 6000 MIPS | 10% | High processing, immersive rendering |

---

## 4. Offloading Execution Strategies

1. **UAV Execution:**
   - Tasks execute locally within UAV capacity. If overloaded, offloaded to peer UAVs within the same cluster.
2. **Fog Execution:**
   - Tasks offload to connected city fog nodes via Access + Metro. If overloaded, forwarded to adjacent cities.
3. **Cloud Execution:**
   - Tasks traverse Access, Metro, and Core WAN to the central cloud data center in Frankfurt.
4. **Proposed Collaborative Strategy:**
   - Solves the MILP formulation to dynamically place each task across UAV, Fog, or Cloud to achieve optimal system energy and minimize latency.
5. **Heuristic Strategy (Algorithm 1):**
   - Polynomial-time validation approach assessing node weights and multi-hop network power, matching MILP within 4.5% gap in under 7 seconds.
