"""
Complete MILP Optimization Engine for collaborative UAV-Fog-Cloud task offloading.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

import time
from typing import List, Dict, Tuple, Optional, Any
import pulp

from config.parameters import ResearchSystemParameters
from config.settings import DEFAULT_CLOUD_CITY
from models.task import UAVTask
from models.network import TelecommunicationNetwork
from optimization.solver import SolverManager
from optimization.objective import MILPObjectiveBuilder
from optimization.constraints import MILPConstraintBuilder
from optimization.results import OptimizationResult, TaskOffloadingDecision


class MILPOptimizer:
    """
    Formulates and solves the Mixed-Integer Linear Programming (MILP) model
    for optimizing task offloading across UAV, Fog, and Cloud environments.
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        network: Optional[TelecommunicationNetwork] = None,
        solver_preference: str = "HiGHS"
    ):
        self.params = params or ResearchSystemParameters()
        self.network = network or TelecommunicationNetwork()
        self.solver_preference = solver_preference
        
        self.obj_builder = MILPObjectiveBuilder(self.params)
        self.constraint_builder = MILPConstraintBuilder(self.params)

    def optimize(
        self,
        tasks: List[UAVTask],
        fog_nodes_count: int = 28,
        cloud_city: str = DEFAULT_CLOUD_CITY,
        time_limit_sec: int = 30
    ) -> OptimizationResult:
        """
        Executes the MILP optimization model.
        Returns OptimizationResult with decisions, power, latency, and solver metrics.
        """
        start_time = time.perf_counter()

        if not tasks:
            return OptimizationResult(status="No Tasks Provided")

        # Create PuLP Minimization Problem
        prob = pulp.LpProblem("UAV_Fog_Cloud_Offloading_Optimization", pulp.LpMinimize)

        # Candidate destinations for each task
        destinations = ["uav", "fog", "cloud"]

        # Decision Variables: theta_(i, d) in {0, 1}
        # theta[(task_id, target)] == 1 if task i is assigned to target d
        theta: Dict[Tuple[str, str], pulp.LpVariable] = {}
        for task in tasks:
            for d in destinations:
                var_name = f"theta_{task.task_id}_{d}"
                theta[(task.task_id, d)] = pulp.LpVariable(var_name, cat=pulp.LpBinary)

        # Map tasks by originating city
        city_tasks_map: Dict[str, List[UAVTask]] = {}
        for t in tasks:
            city_tasks_map.setdefault(t.source_city, []).append(t)

        # Telecommunication Equipment Variables (Integers)
        equipment_vars: Dict[str, Any] = {
            "access": {},
            "metro": {},
            "core": {}
        }

        for city in city_tasks_map.keys():
            equipment_vars["access"][city] = {
                "onu": pulp.LpVariable(f"onu_{city}", lowBound=1, cat=pulp.LpInteger),
                "olt": pulp.LpVariable(f"olt_{city}", lowBound=1, cat=pulp.LpInteger)
            }
            equipment_vars["metro"][city] = {
                "mr": pulp.LpVariable(f"mr_{city}", lowBound=1, cat=pulp.LpInteger),
                "ms": pulp.LpVariable(f"ms_{city}", lowBound=1, cat=pulp.LpInteger)
            }

        equipment_vars["core"] = {
            "router_ports": pulp.LpVariable("core_router_ports", lowBound=1, cat=pulp.LpInteger),
            "transponders": pulp.LpVariable("core_transponders", lowBound=1, cat=pulp.LpInteger),
            "amplifiers": pulp.LpVariable("core_amplifiers", lowBound=1, cat=pulp.LpInteger),
            "optical_switches": pulp.LpVariable("core_optical_switches", lowBound=1, cat=pulp.LpInteger)
        }

        # 1. Attach Objective Function (Equation 4)
        prob.objective = self.obj_builder.build_objective(
            tasks=tasks,
            theta=theta,
            equipment_vars=equipment_vars,
            base_num_uavs=len(tasks),
            num_cities=len(city_tasks_map)
        )

        # 2. Attach Constraints (C1 - C12)
        # Assignment Uniqueness C1
        self.constraint_builder.add_assignment_constraints(prob, tasks, theta, destinations)

        # Capacity Constraints C6, C7, UAV
        self.constraint_builder.add_capacity_constraints(
            problem=prob,
            tasks=tasks,
            theta=theta,
            city_tasks_map=city_tasks_map,
            uav_capacity_mips=self.params.uav.processing_mips,
            fog_capacity_mips=self.params.fog.capacity_mips,
            cloud_capacity_mips=self.params.cloud.capacity_mips
        )

        # Equipment and Dimensioning Constraints C9, C10, C11
        self.constraint_builder.add_traffic_and_equipment_constraints(
            problem=prob,
            tasks=tasks,
            theta=theta,
            city_tasks_map=city_tasks_map,
            equipment_vars=equipment_vars
        )

        # 3. Solve with configured solver
        solver = SolverManager.get_solver(
            preferred=self.solver_preference,
            time_limit_sec=time_limit_sec,
            msg=False
        )
        prob.solve(solver)

        solve_duration = time.perf_counter() - start_time
        solver_status_str = pulp.LpStatus.get(prob.status, "Unknown")
        is_optimal = (prob.status == pulp.LpStatusOptimal)

        # 4. Extract Solution & Metrics
        return self._extract_results(
            prob=prob,
            tasks=tasks,
            theta=theta,
            equipment_vars=equipment_vars,
            cloud_city=cloud_city,
            solver_status=solver_status_str,
            is_optimal=is_optimal,
            solve_time=solve_duration
        )

    def _extract_results(
        self,
        prob: pulp.LpProblem,
        tasks: List[UAVTask],
        theta: Dict[Tuple[str, str], pulp.LpVariable],
        equipment_vars: Dict[str, Any],
        cloud_city: str,
        solver_status: str,
        is_optimal: bool,
        solve_time: float
    ) -> OptimizationResult:
        """Extracts task placement decisions, power breakdowns, and latency metrics."""
        task_decisions: List[TaskOffloadingDecision] = []
        uav_count = 0
        fog_count = 0
        cloud_count = 0
        total_latency_ms = 0.0
        max_latency_ms = 0.0

        for task in tasks:
            chosen_tier = "fog"  # fallback
            for d in ["uav", "fog", "cloud"]:
                var = theta.get((task.task_id, d))
                if var is not None and pulp.value(var) is not None and pulp.value(var) > 0.5:
                    chosen_tier = d
                    break

            if chosen_tier == "uav":
                uav_count += 1
                assigned_node = task.uav_id or f"UAV_{task.task_id}"
                # UAV compute latency
                comp_lat_ms = (task.mips_required / self.params.uav.processing_mips) * 1000.0
                comm_lat_ms = 0.0
                task_lat_ms = comp_lat_ms + comm_lat_ms
                task_pwr_w = self.params.uav.power_watts
                task_energy_j = task_pwr_w * (task_lat_ms / 1000.0)

            elif chosen_tier == "fog":
                fog_count += 1
                assigned_node = f"fog_{task.source_city}"
                comp_lat_ms = (task.mips_required / self.params.fog.capacity_mips) * 1000.0
                comm_info = self.network.compute_transmission_latency(
                    data_size_bits=task.input_data_size_bits,
                    source_city=task.source_city,
                    destination_city=task.source_city,
                    target_layer="fog"
                )
                comm_lat_ms = comm_info["total_comm_latency_ms"]
                task_lat_ms = comp_lat_ms + comm_lat_ms
                
                # Fog power
                pue_fog = self.params.fog.pue_fog
                proc_pwr = pue_fog * (task.mips_required * self.params.fog.pcmips_watts_per_mips)
                net_pwr = pue_fog * ((self.params.fog.np_fog_watts_per_gbps / 1e9) * task.input_data_size_bits)
                task_pwr_w = proc_pwr + net_pwr
                task_energy_j = task_pwr_w * (task_lat_ms / 1000.0)

            else:  # cloud
                cloud_count += 1
                assigned_node = f"cloud_{cloud_city}"
                comp_lat_ms = (task.mips_required / self.params.cloud.capacity_mips) * 1000.0
                comm_info = self.network.compute_transmission_latency(
                    data_size_bits=task.input_data_size_bits,
                    source_city=task.source_city,
                    destination_city=cloud_city,
                    target_layer="cloud"
                )
                comm_lat_ms = comm_info["total_comm_latency_ms"]
                task_lat_ms = comp_lat_ms + comm_lat_ms
                
                # Cloud power
                pue_cloud = self.params.cloud.pue_cloud
                proc_pwr = pue_cloud * (task.mips_required * self.params.cloud.pcmips_watts_per_mips)
                net_pwr = pue_cloud * ((self.params.cloud.np_cloud_watts_per_gbps / 1e9) * task.input_data_size_bits)
                task_pwr_w = proc_pwr + net_pwr
                task_energy_j = task_pwr_w * (task_lat_ms / 1000.0)

            task.assigned_destination = chosen_tier
            task.target_node_id = assigned_node
            task.execution_latency_ms = task_lat_ms
            task.total_energy_joules = task_energy_j

            decision = TaskOffloadingDecision(
                task_id=task.task_id,
                uav_id=task.uav_id,
                source_city=task.source_city,
                task_class=task.task_class,
                mips_required=task.mips_required,
                input_data_size_mb=task.input_data_size_mb,
                assigned_tier=chosen_tier,
                assigned_node_id=assigned_node,
                service_latency_ms=task_lat_ms,
                energy_joules=task_energy_j,
                power_watts=task_pwr_w
            )
            task_decisions.append(decision)
            total_latency_ms += task_lat_ms
            if task_lat_ms > max_latency_ms:
                max_latency_ms = task_lat_ms

        avg_latency = total_latency_ms / len(tasks) if tasks else 0.0

        # Calculate Layer Power sums
        total_pwr = pulp.value(prob.objective) if prob.objective is not None else 0.0
        
        # Power breakdowns (Eqs 1, 2, 3)
        uav_access_pwr = len(tasks) * self.params.uav.power_watts + (len(tasks) // 3) * self.params.uav.gateway_power_watts
        fog_metro_pwr = sum(d.power_watts for d in task_decisions if d.assigned_tier == "fog")
        cloud_core_pwr = sum(d.power_watts for d in task_decisions if d.assigned_tier == "cloud")
        total_energy = sum(d.energy_joules for d in task_decisions)

        return OptimizationResult(
            status=solver_status,
            is_optimal=is_optimal,
            solver_name=str(prob.solver),
            solve_time_seconds=solve_time,
            total_power_watts=total_pwr,
            total_energy_joules=total_energy,
            power_uav_access_watts=uav_access_pwr,
            power_fog_metro_watts=fog_metro_pwr,
            power_cloud_core_watts=cloud_core_pwr,
            average_service_latency_ms=avg_latency,
            max_service_latency_ms=max_latency_ms,
            uav_count=uav_count,
            fog_count=fog_count,
            cloud_count=cloud_count,
            task_decisions=task_decisions
        )
