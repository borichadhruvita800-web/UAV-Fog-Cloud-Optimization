"""
UAV Execution Strategy (Standalone UAV baseline).
Based on Mohammad Aldossary, IEEE Access, 2024 (Section V-B).
Tasks are processed locally within UAV resources or offloaded to peer UAVs.
"""

from typing import List, Dict, Any, Optional
import copy
from models.task import UAVTask
from config.parameters import ResearchSystemParameters
from simulation.environment import SimulationEnvironment


class UAVOnlyStrategy:
    """
    Executes tasks strictly within the UAV layer.
    If local UAV capacity is exceeded, offloads to peer UAVs within the local gateway cluster.
    """
    def __init__(self, params: Optional[ResearchSystemParameters] = None):
        self.params = params or ResearchSystemParameters()

    def execute(self, tasks: List[UAVTask], env: Optional[SimulationEnvironment] = None) -> List[UAVTask]:
        """
        Executes all tasks on UAV layer resources.
        Returns the updated task list with latency and energy metrics.
        """
        resolved_tasks = copy.deepcopy(tasks)
        uav_capacity_mips = self.params.uav.processing_mips  # 800 MIPS
        uav_power_w = self.params.uav.power_watts  # 63 W

        # Group tasks by originating UAV
        uav_loads: Dict[str, float] = {}

        for task in resolved_tasks:
            orig_uav = task.uav_id or f"UAV_{task.source_city}_01"
            current_load = uav_loads.get(orig_uav, 0.0)

            if current_load + task.mips_required <= uav_capacity_mips:
                # 1. Processed locally on originating UAV
                uav_loads[orig_uav] = current_load + task.mips_required
                task.assigned_destination = "uav"
                task.target_node_id = orig_uav
                
                # Compute latency: T_comp = (task MIPS / 800) * 1000 ms
                comp_lat_ms = (task.mips_required / uav_capacity_mips) * 1000.0
                task.execution_latency_ms = comp_lat_ms
                task.total_energy_joules = uav_power_w * (comp_lat_ms / 1000.0)

            else:
                # 2. Local UAV is overloaded -> offload to peer UAV in same area
                peer_uav = f"{orig_uav}_peer"
                peer_load = uav_loads.get(peer_uav, 0.0)
                uav_loads[peer_uav] = peer_load + task.mips_required

                task.assigned_destination = "uav"
                task.target_node_id = peer_uav

                # Wireless peer-to-peer transmission latency (54 Mbps nominal)
                t_comm_ms = (task.input_data_size_bits / self.params.uav.wireless_bandwidth_bps) * 1000.0
                comp_lat_ms = (task.mips_required / uav_capacity_mips) * 1000.0
                
                # Overload queuing delay proportional to queue load
                queue_factor = max(1.0, (peer_load + task.mips_required) / uav_capacity_mips)
                total_lat_ms = t_comm_ms + (comp_lat_ms * queue_factor)

                task.execution_latency_ms = total_lat_ms
                # Energy consumed by transmitting UAV + executing peer UAV
                comm_energy = self.params.uav.power_watts * (t_comm_ms / 1000.0)
                comp_energy = uav_power_w * ((comp_lat_ms * queue_factor) / 1000.0)
                task.total_energy_joules = comm_energy + comp_energy

        return resolved_tasks
