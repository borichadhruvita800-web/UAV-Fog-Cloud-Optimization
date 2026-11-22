"""
Heuristic Strategy for UAV Task Offloading.
Implements Algorithm 1 from Mohammad Aldossary, IEEE Access, 2024 (Section VI).
Provides rapid polynomial-time heuristic validation for the MILP model (within 4.5% gap).
"""

from typing import List, Dict, Any, Optional
import copy
from models.task import UAVTask
from config.parameters import ResearchSystemParameters
from config.settings import DEFAULT_CLOUD_CITY
from simulation.environment import SimulationEnvironment


class HeuristicStrategy:
    """
    Implements Algorithm 1 (Section VI):
    A fast multi-hop heuristic evaluating candidate placement locations across
    UAV, Fog, and Cloud layers by weighting power consumption and network overhead.
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        cloud_city: str = DEFAULT_CLOUD_CITY
    ):
        self.params = params or ResearchSystemParameters()
        self.cloud_city = cloud_city

    def execute(self, tasks: List[UAVTask], env: Optional[SimulationEnvironment] = None) -> List[UAVTask]:
        """
        Executes Algorithm 1: Evaluates candidate offloading targets for each task
        and assigns the minimum power-consumption configuration.
        """
        resolved_tasks = copy.deepcopy(tasks)
        environment = env or SimulationEnvironment(params=self.params, cloud_city=self.cloud_city)

        uav_capacity_mips = self.params.uav.processing_mips  # 800
        fog_capacity_mips = self.params.fog.capacity_mips    # 3600
        cloud_capacity_mips = self.params.cloud.capacity_mips # 18000

        uav_loads: Dict[str, float] = {}
        fog_loads: Dict[str, float] = {c: 0.0 for c in environment.fog_nodes.keys()}
        cloud_load: float = 0.0

        pue_fog = self.params.fog.pue_fog
        pue_cloud = self.params.cloud.pue_cloud
        pcmips_fog = self.params.fog.pcmips_watts_per_mips
        pcmips_cloud = self.params.cloud.pcmips_watts_per_mips
        np_fog = self.params.fog.np_fog_watts_per_gbps / 1e9
        np_cloud = self.params.cloud.np_cloud_watts_per_gbps / 1e9

        for task in resolved_tasks:
            src_city = task.source_city
            orig_uav = task.uav_id or f"UAV_{src_city}_01"
            candidates = []

            # 1. Evaluate UAV Local Option
            current_uav_load = uav_loads.get(orig_uav, 0.0)
            if current_uav_load + task.mips_required <= uav_capacity_mips:
                lat_uav_ms = (task.mips_required / uav_capacity_mips) * 1000.0
                pwr_uav = self.params.uav.power_watts
                energy_uav = pwr_uav * (lat_uav_ms / 1000.0)
                candidates.append(("uav", orig_uav, pwr_uav, lat_uav_ms, energy_uav))

            # 2. Evaluate Local Fog Option
            current_fog_load = fog_loads.get(src_city, 0.0)
            if current_fog_load + task.mips_required <= fog_capacity_mips:
                comm_fog = environment.network.compute_transmission_latency(
                    data_size_bits=task.input_data_size_bits,
                    source_city=src_city,
                    destination_city=src_city,
                    target_layer="fog"
                )
                lat_fog_ms = comm_fog["total_comm_latency_ms"] + (task.mips_required / fog_capacity_mips) * 1000.0
                proc_pwr_fog = pue_fog * (task.mips_required * pcmips_fog)
                net_pwr_fog = pue_fog * (np_fog * task.input_data_size_bits)
                pwr_fog = proc_pwr_fog + net_pwr_fog
                energy_fog = pwr_fog * (lat_fog_ms / 1000.0)
                candidates.append(("fog", f"fog_{src_city}", pwr_fog, lat_fog_ms, energy_fog))

            # 3. Evaluate Cloud Option
            comm_cloud = environment.network.compute_transmission_latency(
                data_size_bits=task.input_data_size_bits,
                source_city=src_city,
                destination_city=self.cloud_city,
                target_layer="cloud"
            )
            lat_cloud_ms = comm_cloud["total_comm_latency_ms"] + (task.mips_required / cloud_capacity_mips) * 1000.0
            proc_pwr_cloud = pue_cloud * (task.mips_required * pcmips_cloud)
            net_pwr_cloud = pue_cloud * (np_cloud * task.input_data_size_bits)
            pwr_cloud = proc_pwr_cloud + net_pwr_cloud
            energy_cloud = pwr_cloud * (lat_cloud_ms / 1000.0)
            candidates.append(("cloud", f"cloud_{self.cloud_city}", pwr_cloud, lat_cloud_ms, energy_cloud))

            # Select minimum power / energy candidate (Line 10 of Alg 1)
            best_cand = min(candidates, key=lambda c: c[2])  # min power
            tier, target_id, pwr, lat_ms, energy_j = best_cand

            # Commit allocation
            if tier == "uav":
                uav_loads[orig_uav] = current_uav_load + task.mips_required
            elif tier == "fog":
                fog_loads[src_city] = current_fog_load + task.mips_required
            else:
                cloud_load += task.mips_required

            task.assigned_destination = tier
            task.target_node_id = target_id
            task.execution_latency_ms = lat_ms
            task.total_energy_joules = energy_j

        return resolved_tasks
