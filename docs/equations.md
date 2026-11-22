# MATHEMATICAL EQUATIONS & RESEARCH FORMULATION

**Based on:**  
*"Optimizing Task Offloading for Collaborative Unmanned Aerial Vehicles (UAVs) in Fog–Cloud Computing Environments"*  
— Mohammad Aldossary, IEEE Access, Vol. 12, pp. 74698–74710, 2024.

---

## 1. System Power Consumption Equations

The total power consumption of the UAV-Fog-Cloud architecture is divided into three subsystem layers:

### 1.1 UAV and Access Network Layer (Function 1)
$$\begin{aligned}
P_{UAV+Access} = &\sum_{s \in N} UAV^{(number)}_s \cdot UAV^{(power)} \\
&+ \sum_{s \in N} GW^{(number)}_s \cdot GW^{(power)} \\
&+ PUE^{(network)} \cdot \left( \sum_{s \in N} ONU^{(number)}_s \cdot ONU^{(power)} + \sum_{s \in N} OLT^{(number)}_s \cdot OLT^{(power)} \right)
\end{aligned}$$

Where:
- $UAV^{(power)} = 63.0$ W (Single UAV power consumption)
- $GW^{(power)} = 30.0$ W (Gateway power consumption, serving up to 3 UAVs)
- $ONU^{(power)} = 5.0$ W (Optical Network Unit power)
- $OLT^{(power)} = 1842.0$ W (1.842 kW Optical Line Terminal power)
- $PUE^{(network)} = 1.5$ (Network Power Usage Effectiveness)

---

### 1.2 Fog Computing and Metro Area Network Layer (Function 2)
$$\begin{aligned}
P_{Fog+Metro} = &PUE^{(fog)} \cdot \left( \sum_{s \in N} MIPS^{(fog)}_{i,s} \cdot PCMIPS^{(fog)} + \sum_{s \in N} NP^{(fog)} \cdot TU_{s,d} \right) \\
&+ PUE^{(network)} \cdot \left( \sum_{s \in N} MR^{(number)}_s \cdot MR^{(power)} + \sum_{s \in N} MS^{(number)}_s \cdot MS^{(power)} \right)
\end{aligned}$$

Where:
- $FS^{(MIPS)} = 3600.0$ MIPS (Processing capacity per fog node)
- $PFS^{(power)} = 126.0$ W (Fog node power consumption)
- $PCMIPS^{(fog)} = \frac{PFS^{(power)}}{FS^{(MIPS)}} = \frac{126}{3600} = 0.035$ W/MIPS
- $PUE^{(fog)} = 1.9$ (PUE of fog layer)
- $NP^{(fog)} = 2.57$ W/Gbps (Internal fog networking power per bit)
- $MR^{(power)} = 30.0$ W (Metro router power, 40 Gbps bitrate)
- $MS^{(power)} = 470.0$ W (Metro switch power, 0.5 Tbps bitrate)

---

### 1.3 Cloud Computing and Core Network Layer (Function 3)
$$\begin{aligned}
P_{Cloud+Core} = &PUE^{(cloud)} \cdot \left( \sum_{s \in N} MIPS^{(cloud)}_{i,s} \cdot PCMIPS^{(cloud)} + \sum_{s \in N} NP^{(cloud)} \cdot TU_{s,d} \right) \\
&+ PUE^{(network)} \cdot \left( \sum_{d \in N} r^{(power)} \cdot r_d + \sum_{m \in N} \sum_{n \in N_m: n \neq m} \sum_{s \in N} \sum_{d \in N: s \neq d} l^{s,d}_{m,n} \cdot t^{(power)} \right. \\
&\left. + \sum_{m \in N} \sum_{n \in N_m: n \neq m} E^{(power)} \cdot F_{m,n} \cdot A_{m,n} + \sum_{d \in N} S^{(power)}_d \right)
\end{aligned}$$

Where:
- $CS^{(MIPS)} = 18000.0$ MIPS (Cloud server capacity)
- $PCS^{(power)} = 630.0$ W (Cloud server power)
- $PCMIPS^{(cloud)} = \frac{PCS^{(power)}}{CS^{(MIPS)}} = \frac{630}{18000} = 0.035$ W/MIPS
- $PUE^{(cloud)} = 1.1$ (PUE of cloud layer)
- $NP^{(cloud)} = 2.48$ W/Gbps (Internal cloud networking power per bit)
- $r^{(power)} = 37.1$ W (Router port power in core network, 40 Gbps bandwidth $\mathbb{B}$)
- $t^{(power)} = 129.0$ W (Transponder power)
- $E^{(power)} = 11.0$ W (Optical amplifier power)
- $S_d^{(power)} = 85.0$ W (Optical switch power)
- $A_{m,n} = \lceil \frac{D_{m,n}}{S} - 1 \rceil = \lceil \frac{600}{80} - 1 \rceil = 7$ amplifiers per 600 km link ($S = 80$ km).

---

## 2. MILP Objective Function (Function 4)

$$\min_{Power} \quad \left( P_{UAV+Access} \right) + \left( P_{Fog+Metro} \right) + \left( P_{Cloud+Core} \right)$$

Subject to constraints **C1 through C12**:

### Constraints:
- **C1 (Task Assignment):**
  $$\sum_{s,d \in N} UI_{i,s,d} = \sum_{s,d \in N} T^{UAV}_{i,s,d} \quad \forall i \in I$$
  All offloaded tasks must be handled either locally by UAV or remotely by fog or cloud: $\sum_{d} \theta_{i,d} = 1$.

- **C2 & C3 (Binary Assignment & Big-M Bounds):**
  $$\sum_{s \in N} T^{UAV}_{i,s,d} \ge \theta_{i,d}, \quad \sum_{s \in N} T^{UAV}_{i,s,d} \le \omega \cdot \theta_{i,d} \quad \forall d \in N, i \in I$$

- **C4 & C5 (Flow Conservation on Links):**
  $$l^{s,d}_{m,n} \ge 0, \quad l^{s,d}_{m,n} \le 1 \quad \forall s, d, m, n \in c, f$$

- **C6 (Fog Node Processing Allocation):**
  $$MIPS^{(fog)}_{i,s} = \theta_{i,d} \cdot MIPS^{(fog)}_{i,s} \quad \forall d \in N, i \in I$$

- **C7 (Cloud Processing Allocation):**
  $$MIPS^{(cloud)}_{i,s} = \sum_{i \in I} MIPS^{(cloud)}_{i,s} \quad \forall d \in N$$

- **C8 (Total Offloaded Traffic):**
  $$TU_{s,d} = \sum_{i \in I} T^{UAV}_{i,s,d} \quad \forall s, d \in c, f$$

- **C9 (Core Router Ports Dimensioning):**
  $$r_d \ge \frac{\sum_{s \in N} TU_{s,d}}{\mathbb{B}} \quad \forall d \in c, f$$

- **C10 (Access Network Equipment Dimensioning):**
  $$ONU^{(number)}_s + OLT^{(number)}_s \ge \frac{\sum_{i \in I} \sum_{d \in N} UI_{i,s,d}}{ONU^{(bitrate)} + OLT^{(bitrate)}} \quad \forall s \in N$$

- **C11 (Metro Network Equipment Dimensioning):**
  $$MR^{(number)}_s + MS^{(number)}_s \ge 2 \cdot \frac{\sum_{i \in I} \sum_{d \in (c \cap f)} UI_{i,s,d}}{MR^{(bitrate)} + MS^{(bitrate)}} \quad \forall s \in N$$

- **C12 (Total Data Traffic Conservation):**
  $$T_s = \sum_{i \in I} \sum_{d \in N} UI_{i,s,d} \quad \forall d \in N$$
