"""
Benchmark simulation scenarios corresponding to Section V of the research paper.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ScenarioDefinition:
    id: str
    name: str
    description: str
    parameter_name: str
    parameter_values: List[Any]
    paper_figure_reference: str


BENCHMARK_SCENARIOS: Dict[str, ScenarioDefinition] = {
    "uav_scaling": ScenarioDefinition(
        id="uav_scaling",
        name="1. Service Time & Energy vs Number of UAVs",
        description="Scales UAV count from 10 to 100 UAVs to evaluate network resource utilization, queuing, and power scaling.",
        parameter_name="num_uavs",
        parameter_values=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        paper_figure_reference="Figures 3 & 7"
    ),
    "data_size_variation": ScenarioDefinition(
        id="data_size_variation",
        name="2. Service Time & Energy vs Input Data Size",
        description="Varies input data size from 5 MB to 30 MB to evaluate transmission and propagation impact.",
        parameter_name="input_data_size_mb",
        parameter_values=[5, 10, 15, 20, 25, 30],
        paper_figure_reference="Figures 4 & 8"
    ),
    "fog_capability": ScenarioDefinition(
        id="fog_capability",
        name="3. Service Time vs Fog Node Capabilities",
        description="Evaluates execution time as fog node processing capability scales from 10 GHz to 50 GHz (1200 to 6000 MIPS).",
        parameter_name="fog_mips",
        parameter_values=[1200, 2400, 3600, 4800, 6000],
        paper_figure_reference="Figure 5"
    ),
    "application_classes": ScenarioDefinition(
        id="application_classes",
        name="4. Service Time by Application Class",
        description="Compares Class A (500 MIPS), Class B (2000 MIPS), and Class C (6000 MIPS) performance across all strategies.",
        parameter_name="task_class",
        parameter_values=["A", "B", "C"],
        paper_figure_reference="Figure 6"
    ),
    "fog_node_scaling": ScenarioDefinition(
        id="fog_node_scaling",
        name="5. Energy Consumption vs Number of Fog Nodes",
        description="Varies the number of active fog nodes from 2 to 10 to evaluate distributed edge processing efficiency.",
        parameter_name="num_fog_nodes",
        parameter_values=[2, 4, 6, 8, 10],
        paper_figure_reference="Figure 9"
    ),
    "heuristic_validation": ScenarioDefinition(
        id="heuristic_validation",
        name="6. MILP vs Heuristic (Algorithm 1) Validation",
        description="Compares the exact MILP optimal power against the fast polynomial-time heuristic Algorithm 1.",
        parameter_name="algorithm_comparison",
        parameter_values=["MILP", "Heuristic"],
        paper_figure_reference="Figure 10"
    ),
}
