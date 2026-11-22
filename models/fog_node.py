"""
Fog Node model for collaborative UAV task offloading.
Based on Mohammad Aldossary, IEEE Access, 2024 (Table 2 & Section III-B).
"""

from typing import List, Optional, Dict, Any
from models.task import UAVTask
from config.parameters import FogNodeParameters


class FogNode:
    """
    Represents a Fog Computing Node situated at the edge/metro network layer.
    Provides lower latency than cloud and higher processing capability than UAVs.
    """
    def __init__(
        self,
        node_id: str,
        city: str,
        params: Optional[FogNodeParameters] = None
    ):
        self.node_id = node_id
        self.city = city
        self.params = params or FogNodeParameters()
        
        self.total_mips: float = self.params.capacity_mips  # 3600 MIPS
        self.available_mips: float = self.params.capacity_mips
        self.power_watts: float = self.params.power_watts  # 126 W
        self.pue: float = self.params.pue_fog  # 1.9
        self.pcmips: float = self.params.pcmips_watts_per_mips  # 0.035 W/MIPS
        self.np_fog_w_gbps: float = self.params.np_fog_watts_per_gbps  # 2.57 W/Gbps
        
        self.assigned_tasks: List[UAVTask] = []

    def can_process(self, task: UAVTask) -> bool:
        """Checks if fog node has sufficient capacity for task."""
        return self.available_mips >= task.mips_required

    def assign_task(self, task: UAVTask) -> bool:
        """Assign task to execute on this fog node."""
        if self.can_process(task):
            self.available_mips -= task.mips_required
            self.assigned_tasks.append(task)
            task.assigned_destination = "fog"
            task.target_node_id = self.node_id
            return True
        return False

    def compute_processing_latency(self, task: UAVTask) -> float:
        """
        Compute processing execution latency on fog node in milliseconds.
        T_proc = (task MIPS / Fog MIPS) * 1000 ms.
        """
        return (task.mips_required / self.total_mips) * 1000.0

    def compute_compute_power(self, allocated_mips: Optional[float] = None) -> float:
        """
        Compute power consumption for computing according to Eq. (2):
        PUE(fog) * sum(MIPS_i * PCMIPS(fog))
        """
        mips = allocated_mips if allocated_mips is not None else (self.total_mips - self.available_mips)
        return self.pue * (mips * self.pcmips)

    def compute_internal_network_power(self, traffic_bps: float) -> float:
        """
        Compute internal networking power consumption according to Eq. (2):
        PUE(fog) * NP(fog) * TU_s,d
        NP(fog) is 2.57 Watts/Gbps
        """
        traffic_gbps = traffic_bps / 1.0e9
        return self.pue * (self.np_fog_w_gbps * traffic_gbps)

    def reset(self) -> None:
        """Reset node allocations."""
        self.available_mips = self.total_mips
        self.assigned_tasks.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "city": self.city,
            "total_mips": self.total_mips,
            "available_mips": round(self.available_mips, 2),
            "assigned_tasks_count": len(self.assigned_tasks),
            "power_watts": self.power_watts,
            "pue": self.pue,
            "pcmips": self.pcmips
        }
