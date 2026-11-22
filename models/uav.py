"""
UAV model for collaborative task offloading.
Based on Mohammad Aldossary, IEEE Access, 2024 (Table 2 & Section III-A).
"""

from typing import List, Optional, Dict, Any
from models.task import UAVTask
from config.parameters import UAVParameters


class UAV:
    """
    Represents an autonomous Unmanned Aerial Vehicle (UAV).
    Acts as a flying sensor/computing node capable of local computation
    or offloading to peer UAVs, fog nodes, or cloud servers.
    """
    def __init__(
        self,
        uav_id: str,
        city: str,
        params: Optional[UAVParameters] = None,
        gateway_id: Optional[str] = None
    ):
        self.uav_id = uav_id
        self.city = city
        self.params = params or UAVParameters()
        self.gateway_id = gateway_id or f"GW_{city}_{uav_id.split('_')[-1]}"
        
        self.total_mips: float = self.params.processing_mips
        self.available_mips: float = self.params.processing_mips
        self.power_watts: float = self.params.power_watts  # 63.0 W
        self.data_rate_bps: float = self.params.data_rate_bps  # 100 Kbps
        
        self.assigned_tasks: List[UAVTask] = []

    def can_process_locally(self, task: UAVTask) -> bool:
        """Checks if UAV has sufficient MIPS capacity to process task."""
        return self.available_mips >= task.mips_required

    def assign_task(self, task: UAVTask) -> bool:
        """Allocates MIPS capacity to execute task locally on this UAV."""
        if self.can_process_locally(task):
            self.available_mips -= task.mips_required
            self.assigned_tasks.append(task)
            task.assigned_destination = "uav"
            task.target_node_id = self.uav_id
            return True
        return False

    def compute_local_latency(self, task: UAVTask) -> float:
        """
        Calculate local processing latency on UAV in milliseconds.
        T_comp = (task MIPS / allocated UAV MIPS) * 1000 ms.
        """
        # UAV processing execution time
        return (task.mips_required / self.total_mips) * 1000.0

    def compute_local_energy(self, task: UAVTask, duration_seconds: Optional[float] = None) -> float:
        """
        Calculate energy consumed by UAV processing locally (in Joules).
        Energy = Power (63W) * execution time.
        """
        exec_time_s = (task.mips_required / self.total_mips) if duration_seconds is None else duration_seconds
        return self.power_watts * exec_time_s

    def reset(self) -> None:
        """Reset allocated capacity and assigned tasks."""
        self.available_mips = self.total_mips
        self.assigned_tasks.clear()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "uav_id": self.uav_id,
            "city": self.city,
            "gateway_id": self.gateway_id,
            "total_mips": self.total_mips,
            "available_mips": round(self.available_mips, 2),
            "assigned_tasks_count": len(self.assigned_tasks),
            "power_watts": self.power_watts,
            "data_rate_bps": self.data_rate_bps
        }
