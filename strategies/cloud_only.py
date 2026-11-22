"""
Cloud Execution Strategy (Standalone Cloud baseline).
Based on Mohammad Aldossary, IEEE Access, 2024 (Section V-B).
All tasks are offloaded to a central remote cloud server.
"""

from typing import List, Optional
import copy
from models.task import UAVTask
from config.parameters import ResearchSystemParameters
from config.settings import DEFAULT_CLOUD_CITY
from simulation.environment import SimulationEnvironment


class CloudOnlyStrategy:
    """
    Executes all tasks remotely in the Cloud data center.
    Benefits from massive processing capability (18000 MIPS) and low PUE (1.1),
    but incurs significant WAN core transmission and propagation delays.
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        cloud_city: str = DEFAULT_CLOUD_CITY
    ):
        self.params = params or ResearchSystemParameters()
        self.cloud_city = cloud_city

    def execute(self, tasks: List[UAVTask], env: Optional[SimulationEnvironment] = None) -> List[UAVTask]:
        """Executes all tasks on the Cloud server."""
        resolved_tasks = copy.deepcopy(tasks)
        environment = env or SimulationEnvironment(params=self.params, cloud_city=self.cloud_city)
        cloud_capacity_mips = self.params.cloud.capacity_mips  # 18000 MIPS
        pue_cloud = self.params.cloud.pue_cloud  # 1.1
        pcmips_cloud = self.params.cloud.pcmips_watts_per_mips  # 0.035 W/MIPS
        np_cloud_bps = self.params.cloud.np_cloud_watts_per_gbps / 1.0e9  # W/bps

        for task in resolved_tasks:
            src_city = task.source_city
            task.assigned_destination = "cloud"
            task.target_node_id = f"cloud_{self.cloud_city}"

            # 1. Network Latency: Access + Metro + Core WAN (multi-hop Dijkstra + fiber propagation)
            comm_info = environment.network.compute_transmission_latency(
                data_size_bits=task.input_data_size_bits,
                source_city=src_city,
                destination_city=self.cloud_city,
                target_layer="cloud"
            )
            comm_lat_ms = comm_info["total_comm_latency_ms"]

            # 2. Computation Latency on Cloud server
            comp_lat_ms = (task.mips_required / cloud_capacity_mips) * 1000.0
            total_lat_ms = comm_lat_ms + comp_lat_ms
            task.execution_latency_ms = total_lat_ms

            # 3. Energy Consumption:
            # Cloud computing power + Internal Cloud network power
            proc_power_w = pue_cloud * (task.mips_required * pcmips_cloud)
            int_net_power_w = pue_cloud * (np_cloud_bps * task.input_data_size_bits)
            total_pwr_w = proc_power_w + int_net_power_w
            
            task.total_energy_joules = total_pwr_w * (total_lat_ms / 1000.0)

        return resolved_tasks
