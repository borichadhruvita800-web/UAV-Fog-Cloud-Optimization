"""
Cloud Server model for collaborative UAV task offloading.
Based on Mohammad Aldossary, IEEE Access, 2024 (Table 2 & Section III-B).
"""

from typing import List, Optional, Dict, Any
from models.task import UAVTask
from config.parameters import CloudServerParameters


class CloudServer:
    """
    Represents a Centralized Cloud Computing Data Center.
    High computational capability (18000 MIPS) and high energy efficiency (PUE = 1.1),
    but subject to WAN transmission and propagation delays.
    """
    def __init__(
        self,
        server_id: str = "cloud_central",
        city: str = "Frankfurt",
        params: Optional[CloudServerParameters] = None
    ):
        self.server_id = server_id
        self.city = city
        self.params = params or CloudServerParameters()
        
        self.total_mips: float = self.params.capacity_mips  # 18000 MIPS
        self.available_mips: float = self.params.capacity_mips
        self.power_watts: float = self.params.power_watts  # 630 W
        self.pue: float = self.params.pue_cloud  # 1.1
        self.pcmips: float = self.params.pcmips_watts_per_mips  # 0.035 W/MIPS
        self.np_cloud_w_gbps: float = self.params.np_cloud_watts_per_gbps  # 2.48 W/Gbps
        
        self.assigned_tasks: List[UAVTask] = []

    def can_process(self, task: UAVTask) -> bool:
        """Checks if cloud has capacity for task."""
        return self.available_mips >= task.mips_required

    def assign_task(self, task: UAVTask) -> bool:
        """Assign task to execute on cloud server."""
        if self.can_process(task):
            self.available_mips -= task.mips_required
            self.assigned_tasks.append(task)
            task.assigned_destination = "cloud"
            task.target_node_id = self.server_id
            return True
        return False

    def compute_processing_latency(self, task: UAVTask) -> float:
        """
        Compute processing execution latency on cloud in milliseconds.
        T_proc = (task MIPS / Cloud MIPS) * 1000 ms.
        """
        return (task.mips_required / self.total_mips) * 1000.0

    def compute_compute_power(self, allocated_mips: Optional[float] = None) -> float:
        """
        Compute power consumption for computing according to Eq. (3):
        PUE(cloud) * sum(MIPS_i * PCMIPS(cloud))
        """
        mips = allocated_mips if allocated_mips is not None else (self.total_mips - self.available_mips)
        return self.pue * (mips * self.pcmips)

    def compute_internal_network_power(self, traffic_bps: float) -> float:
        """
        Compute internal networking power consumption according to Eq. (3):
        PUE(cloud) * NP(cloud) * TU_s,d
        NP(cloud) is 2.48 Watts/Gbps
        """
        traffic_gbps = traffic_bps / 1.0e9
        return self.pue * (self.np_cloud_w_gbps * traffic_gbps)

    def reset(self) -> None:
        """Reset server allocations."""
        self.available_mips = self.total_mips
        self.assigned_tasks.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "server_id": self.server_id,
            "city": self.city,
            "total_mips": self.total_mips,
            "available_mips": round(self.available_mips, 2),
            "assigned_tasks_count": len(self.assigned_tasks),
            "power_watts": self.power_watts,
            "pue": self.pue,
            "pcmips": self.pcmips
        }
