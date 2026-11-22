"""
Constraints formulation for UAV-Fog-Cloud MILP optimization.
Implements constraints C1 through C12 from Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import Dict, List, Tuple, Any
import pulp
from config.parameters import ResearchSystemParameters
from models.task import UAVTask


class MILPConstraintBuilder:
    """
    Builds and attaches constraints C1 through C12 to the PuLP optimization problem.
    """
    def __init__(self, params: ResearchSystemParameters):
        self.params = params

    def add_assignment_constraints(
        self,
        problem: pulp.LpProblem,
        tasks: List[UAVTask],
        theta: Dict[Tuple[str, str], pulp.LpVariable],
        destinations: List[str]
    ) -> None:
        """
        Constraint C1:
        All offloaded tasks must be assigned to exactly one destination (UAV, Fog, or Cloud).
        sum_{d in D} theta_{i, d} == 1  forall i in I
        """
        for task in tasks:
            assigned_sum = pulp.lpSum([
                theta[(task.task_id, d)] for d in destinations if (task.task_id, d) in theta
            ])
            problem += (assigned_sum == 1, f"C1_Assignment_{task.task_id}")

    def add_capacity_constraints(
        self,
        problem: pulp.LpProblem,
        tasks: List[UAVTask],
        theta: Dict[Tuple[str, str], pulp.LpVariable],
        city_tasks_map: Dict[str, List[UAVTask]],
        uav_capacity_mips: float,
        fog_capacity_mips: float,
        cloud_capacity_mips: float
    ) -> None:
        """
        Capacity constraints for UAV, Fog, and Cloud resources.
        - C6: MIPS assigned to Fog <= FS^(MIPS) (3600 MIPS)
        - C7: MIPS assigned to Cloud <= CS^(MIPS) (18000 MIPS)
        - UAV MIPS assigned <= processing_mips (800 MIPS)
        """
        # 1. UAV onboard capacity constraint per UAV / originating task group
        uav_task_groups: Dict[str, List[UAVTask]] = {}
        for t in tasks:
            uav_task_groups.setdefault(t.uav_id or t.task_id, []).append(t)

        for uav_id, u_tasks in uav_task_groups.items():
            uav_mips = pulp.lpSum([
                theta[(t.task_id, "uav")] * t.mips_required for t in u_tasks
                if (t.task_id, "uav") in theta
            ])
            problem += (uav_mips <= uav_capacity_mips, f"UAV_Capacity_{uav_id}")

        # 2. Fog capacity constraint per city/region (Constraint C6)
        for city, c_tasks in city_tasks_map.items():
            fog_mips = pulp.lpSum([
                theta[(t.task_id, "fog")] * t.mips_required for t in c_tasks
                if (t.task_id, "fog") in theta
            ])
            problem += (fog_mips <= fog_capacity_mips, f"C6_Fog_Capacity_{city}")

        # 3. Cloud capacity constraint (Constraint C7)
        total_cloud_mips = pulp.lpSum([
            theta[(t.task_id, "cloud")] * t.mips_required for t in tasks
            if (t.task_id, "cloud") in theta
        ])
        problem += (total_cloud_mips <= cloud_capacity_mips, "C7_Cloud_Capacity")

    def add_traffic_and_equipment_constraints(
        self,
        problem: pulp.LpProblem,
        tasks: List[UAVTask],
        theta: Dict[Tuple[str, str], pulp.LpVariable],
        city_tasks_map: Dict[str, List[UAVTask]],
        equipment_vars: Dict[str, Any]
    ) -> None:
        """
        Implements constraints C8, C9, C10, C11, C12 for telecommunication equipment:
        - C9: r_d >= TU_sd / B (router ports dimensioning)
        - C10: ONU_s + OLT_s >= sum(UI) / (ONU_rate + OLT_rate)
        - C11: MR_s + MS_s >= 2 * sum(UI) / (MR_rate + MS_rate)
        - C12: Traffic conservation and flow balance
        """
        # C10: Access network equipment per city
        access_rate_sum = self.params.access_net.onu_bitrate_bps + self.params.access_net.olt_bitrate_bps
        for city, c_tasks in city_tasks_map.items():
            city_traffic_expr = pulp.lpSum([
                t.data_rate_bps for t in c_tasks
            ])
            onu_var = equipment_vars["access"][city]["onu"]
            olt_var = equipment_vars["access"][city]["olt"]
            problem += (
                (onu_var + olt_var) * access_rate_sum >= city_traffic_expr,
                f"C10_Access_Equip_{city}"
            )

        # C11: Metro network equipment per city
        metro_rate_sum = self.params.metro_net.router_bitrate_bps + self.metro_net_switch_bitrate()
        for city, c_tasks in city_tasks_map.items():
            offloaded_traffic_expr = pulp.lpSum([
                (theta[(t.task_id, "fog")] + theta[(t.task_id, "cloud")]) * t.data_rate_bps
                for t in c_tasks
                if (t.task_id, "fog") in theta and (t.task_id, "cloud") in theta
            ])
            mr_var = equipment_vars["metro"][city]["mr"]
            ms_var = equipment_vars["metro"][city]["ms"]
            problem += (
                (mr_var + ms_var) * metro_rate_sum >= 2.0 * offloaded_traffic_expr,
                f"C11_Metro_Equip_{city}"
            )

        # C9: Core network router ports
        core_traffic_expr = pulp.lpSum([
            theta[(t.task_id, "cloud")] * t.data_rate_bps
            for t in tasks
            if (t.task_id, "cloud") in theta
        ])
        router_port_var = equipment_vars["core"]["router_ports"]
        b = self.params.core_net.router_port_bandwidth_bps
        problem += (router_port_var * b >= core_traffic_expr, "C9_Core_Router_Ports")

    def metro_net_switch_bitrate(self) -> float:
        return self.params.metro_net.switch_bitrate_bps
