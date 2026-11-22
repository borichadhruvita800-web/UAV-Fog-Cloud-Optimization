"""
Result data models for MILP optimization output.
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import pandas as pd


@dataclass
class TaskOffloadingDecision:
    """Individual task placement decision determined by the optimization engine."""
    task_id: str
    uav_id: str
    source_city: str
    task_class: str
    mips_required: float
    input_data_size_mb: float
    assigned_tier: str  # 'uav', 'fog', or 'cloud'
    assigned_node_id: str
    service_latency_ms: float = 0.0
    energy_joules: float = 0.0
    power_watts: float = 0.0


@dataclass
class OptimizationResult:
    """Complete results from solving the UAV-Fog-Cloud offloading problem."""
    status: str = "Not Solved"
    is_optimal: bool = False
    solver_name: str = ""
    solve_time_seconds: float = 0.0
    total_power_watts: float = 0.0
    total_energy_joules: float = 0.0
    
    # Power breakdowns by layer (Eqs 1, 2, 3)
    power_uav_access_watts: float = 0.0
    power_fog_metro_watts: float = 0.0
    power_cloud_core_watts: float = 0.0
    
    # Latency metrics
    average_service_latency_ms: float = 0.0
    max_service_latency_ms: float = 0.0
    
    # Allocation counts
    uav_count: int = 0
    fog_count: int = 0
    cloud_count: int = 0
    
    task_decisions: List[TaskOffloadingDecision] = field(default_factory=list)
    equipment_metrics: Dict[str, Any] = field(default_factory=dict)
    detailed_metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for JSON serialization."""
        d = asdict(self)
        d["task_decisions"] = [asdict(t) for t in self.task_decisions]
        return d

    def decisions_dataframe(self) -> pd.DataFrame:
        """Converts task decisions to a pandas DataFrame."""
        if not self.task_decisions:
            return pd.DataFrame()
        return pd.DataFrame([asdict(t) for t in self.task_decisions])

    def summary_dataframe(self) -> pd.DataFrame:
        """Returns a high-level summary DataFrame."""
        return pd.DataFrame([{
            "Status": self.status,
            "Solver": self.solver_name,
            "Solve Time (s)": round(self.solve_time_seconds, 4),
            "Total Power (W)": round(self.total_power_watts, 2),
            "Total Energy (J)": round(self.total_energy_joules, 2),
            "Avg Latency (ms)": round(self.average_service_latency_ms, 2),
            "UAV Tasks": self.uav_count,
            "Fog Tasks": self.fog_count,
            "Cloud Tasks": self.cloud_count,
        }])
