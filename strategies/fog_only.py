"""
Fog Execution Strategy (Standalone Fog baseline).
Based on Mohammad Aldossary, IEEE Access, 2024 (Section V-B).
Tasks are offloaded from UAVs to appropriately connected fog nodes.
"""

from typing import List, Dict, Optional
import copy
from models.task import UAVTask
from config.parameters import ResearchSystemParameters
from simulation.environment import SimulationEnvironment


class FogOnlyStrategy:
    """
    Executes tasks strictly within the Fog layer.
    Tasks are offloaded from UAV to the local city fog node, or forwarded to nearby fog nodes
    if the local node is saturated.
    """
    def __init__(self, params: Optional[ResearchSystemParameters] = None):
        self.params = params or ResearchSystemParameters()

    def execute(self, tasks: List[UAVTask], env: Optional[SimulationEnvironment] = None) -> List[UAVTask]:
        """Executes all tasks on Fog nodes."""
        resolved_tasks = copy.deepcopy(tasks)
        environment = env or SimulationEnvironment(params=self.params)
        fog_capacity_mips = self.params.fog.capacity_mips  # 3600 MIPS
        pue_fog = self.params.fog.pue_fog  # 1.9
        pcmips_fog = self.params.fog.pcmips_watts_per_mips  # 0.035 W/MIPS
        np_fog_bps = self.params.fog.np_fog_watts_per_gbps / 1.0e9  # W/bps

        fog_loads: Dict[str, float] = {city: 0.0 for city in environment.fog_nodes.keys()}

        for task in resolved_tasks:
            src_city = task.source_city
            current_load = fog_loads.get(src_city, 0.0)

            # Check if local fog node has capacity
            if current_load + task.mips_required <= fog_capacity_mips:
                target_city = src_city
                fog_loads[src_city] = current_load + task.mips_required
            else:
                # Find the nearest available fog node
                candidates = sorted(
                    fog_loads.keys(),
                    key=lambda c: fog_loads[c]
                )
                target_city = candidates[0] if candidates else src_city
                fog_loads[target_city] += task.mips_required

            task.assigned_destination = "fog"
            task.target_node_id = f"fog_{target_city}"

            # 1. Network Latency: Access + Metro (+ Core if inter-city)
            comm_info = environment.network.compute_transmission_latency(
                data_size_bits=task.input_data_size_bits,
                source_city=src_city,
                destination_city=target_city,
                target_layer="fog"
            )
            comm_lat_ms = comm_info["total_comm_latency_ms"]

            # 2. Computation Latency on Fog node
            comp_lat_ms = (task.mips_required / fog_capacity_mips) * 1000.0
            
            # Queue congestion factor if node is heavily loaded
            load_ratio = fog_loads[target_city] / fog_capacity_mips
            congestion_penalty_ms = max(0.0, (load_ratio - 1.0) * 50.0)
            
            total_lat_ms = comm_lat_ms + comp_lat_ms + congestion_penalty_ms
            task.execution_latency_ms = total_lat_ms

            # 3. Energy Consumption
            # Compute power + Internal Fog network power
            proc_power_w = pue_fog * (task.mips_required * pcmips_fog)
            int_net_power_w = pue_fog * (np_fog_bps * task.input_data_size_bits)
            total_pwr_w = proc_power_w + int_net_power_w
            
            # Energy in Joules = Power * Execution duration
            task.total_energy_joules = total_pwr_w * (total_lat_ms / 1000.0)

        return resolved_tasks
