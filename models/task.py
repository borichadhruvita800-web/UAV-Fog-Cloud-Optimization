"""
Task model for UAV computational tasks.
Based on Mohammad Aldossary, IEEE Access, 2024 (Table 4 and Section IV).
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import uuid


@dataclass
class UAVTask:
    """
    Represents an offloadable computing task originating from a UAV.
    
    Attributes:
        task_id: Unique identifier for the task.
        uav_id: ID of the originating UAV.
        source_city: City / region s where the UAV is located.
        task_class: Application intensity class ('A', 'B', or 'C').
        mips_required: Computational complexity in MIPS (500, 2000, 6000).
        input_data_size_mb: Size of input data in Megabytes.
        data_rate_bps: Uplink data rate in bits/second (default 100 Kbps from Table 2).
        assigned_destination: Offloading destination: 'uav', 'fog', or 'cloud'.
        target_node_id: Specific destination node ID (e.g. 'fog_Paris', 'cloud_Frankfurt').
        execution_latency_ms: Total latency experienced by the task in milliseconds.
        total_energy_joules: Total energy consumption consumed across processing and networking.
        metrics_breakdown: Detailed latency and power component breakdowns.
    """
    task_id: str = field(default_factory=lambda: f"TASK-{uuid.uuid4().hex[:8].upper()}")
    uav_id: str = ""
    source_city: str = "Frankfurt"
    task_class: str = "A"
    mips_required: float = 500.0
    input_data_size_mb: float = 15.0
    data_rate_bps: float = 100_000.0
    assigned_destination: Optional[str] = None
    target_node_id: Optional[str] = None
    execution_latency_ms: float = 0.0
    total_energy_joules: float = 0.0
    metrics_breakdown: Dict[str, Any] = field(default_factory=dict)

    @property
    def input_data_size_bits(self) -> float:
        """Returns input data size in bits."""
        return self.input_data_size_mb * 8.0 * 1024.0 * 1024.0

    @property
    def input_data_size_bytes(self) -> float:
        """Returns input data size in bytes."""
        return self.input_data_size_mb * 1024.0 * 1024.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation."""
        return {
            "task_id": self.task_id,
            "uav_id": self.uav_id,
            "source_city": self.source_city,
            "task_class": self.task_class,
            "mips_required": self.mips_required,
            "input_data_size_mb": self.input_data_size_mb,
            "data_rate_bps": self.data_rate_bps,
            "assigned_destination": self.assigned_destination,
            "target_node_id": self.target_node_id,
            "execution_latency_ms": round(self.execution_latency_ms, 3),
            "total_energy_joules": round(self.total_energy_joules, 4),
            "metrics_breakdown": self.metrics_breakdown
        }
