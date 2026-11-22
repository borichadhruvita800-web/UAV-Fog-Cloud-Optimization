"""
Collaborative UAV-Fog-Cloud Execution Strategy (Proposed Strategy).
Based on Mohammad Aldossary, IEEE Access, 2024.
Employs Mixed-Integer Linear Programming (MILP) to find the optimal multi-tier placement.
"""

from typing import List, Optional
import copy
from models.task import UAVTask
from config.parameters import ResearchSystemParameters
from config.settings import DEFAULT_CLOUD_CITY
from optimization.milp_model import MILPOptimizer
from optimization.results import OptimizationResult
from simulation.environment import SimulationEnvironment


class CollaborativeStrategy:
    """
    Proposed collaborative UAV-Fog-Cloud offloading strategy.
    Optimizes task placement across UAV, Fog, and Cloud resources using MILP
    to minimize total system energy while reducing service latency.
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        solver_preference: str = "HiGHS",
        cloud_city: str = DEFAULT_CLOUD_CITY
    ):
        self.params = params or ResearchSystemParameters()
        self.solver_preference = solver_preference
        self.cloud_city = cloud_city
        self.last_optimization_result: Optional[OptimizationResult] = None

    def execute(
        self,
        tasks: List[UAVTask],
        env: Optional[SimulationEnvironment] = None,
        time_limit_sec: int = 30
    ) -> List[UAVTask]:
        """
        Executes the MILP optimization to allocate tasks collaboratively across tiers.
        """
        resolved_tasks = copy.deepcopy(tasks)
        environment = env or SimulationEnvironment(params=self.params, cloud_city=self.cloud_city)

        optimizer = MILPOptimizer(
            params=self.params,
            network=environment.network,
            solver_preference=self.solver_preference
        )

        opt_result = optimizer.optimize(
            tasks=resolved_tasks,
            fog_nodes_count=len(environment.fog_nodes),
            cloud_city=self.cloud_city,
            time_limit_sec=time_limit_sec
        )
        self.last_optimization_result = opt_result

        return resolved_tasks
