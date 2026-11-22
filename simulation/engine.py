"""
Simulation Engine orchestrating multi-strategy execution and Monte Carlo parameter sweeps.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import List, Dict, Any, Optional, Callable
import time
import pandas as pd
from pathlib import Path

from config.parameters import ResearchSystemParameters
from config.settings import RESULTS_DIR
from simulation.environment import SimulationEnvironment
from simulation.task_generator import TaskGenerator
from simulation.metrics import MetricsCalculator
from strategies.uav_only import UAVOnlyStrategy
from strategies.fog_only import FogOnlyStrategy
from strategies.cloud_only import CloudOnlyStrategy
from strategies.collaborative import CollaborativeStrategy
from strategies.heuristic import HeuristicStrategy


class SimulationEngine:
    """
    Main simulation executive responsible for executing scenarios,
    running comparative offloading strategies, and collecting research metrics.
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        solver_preference: str = "HiGHS"
    ):
        self.params = params or ResearchSystemParameters()
        self.solver_preference = solver_preference
        
        self.env = SimulationEnvironment(params=self.params)
        self.generator = TaskGenerator(params=self.params)
        
        # Strategies
        self.strategies = {
            "UAV Execution": UAVOnlyStrategy(self.params),
            "Fog Execution": FogOnlyStrategy(self.params),
            "Cloud Execution": CloudOnlyStrategy(self.params),
            "Proposed (Collaborative)": CollaborativeStrategy(self.params, solver_preference=self.solver_preference),
            "Heuristic (Algorithm 1)": HeuristicStrategy(self.params),
        }

    def run_single_comparison(
        self,
        num_tasks: int = 20,
        fixed_data_size_mb: Optional[float] = None,
        specific_class: Optional[str] = None,
        seed: Optional[int] = 42
    ) -> Dict[str, Any]:
        """
        Executes a comparative run across all 4 strategies (plus heuristic) for a single batch of tasks.
        Returns detailed summary and comparison DataFrame.
        """
        tasks = self.generator.generate_tasks(
            num_tasks=num_tasks,
            fixed_data_size_mb=fixed_data_size_mb,
            specific_class=specific_class,
            seed=seed
        )

        summaries: Dict[str, Dict[str, Any]] = {}
        executed_tasks_by_strategy: Dict[str, list] = {}

        for strat_name, strat in self.strategies.items():
            self.env.reset()
            exec_tasks = strat.execute(tasks, env=self.env)
            executed_tasks_by_strategy[strat_name] = exec_tasks
            summary = MetricsCalculator.calculate_strategy_summary(strat_name, exec_tasks)
            summaries[strat_name] = summary

        comparison_df = MetricsCalculator.compare_strategies(
            summaries,
            baseline_name="Proposed (Collaborative)"
        )

        return {
            "tasks_input": tasks,
            "summaries": summaries,
            "comparison_df": comparison_df,
            "executed_tasks": executed_tasks_by_strategy,
            "collab_opt_result": getattr(self.strategies["Proposed (Collaborative)"], "last_optimization_result", None)
        }

    def run_parameter_sweep(
        self,
        scenario_key: str,
        iterations_per_point: int = 5,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> pd.DataFrame:
        """
        Executes a complete parameter sweep (e.g. UAV scaling from 10 to 100, or Data size 5 to 30 MB)
        averaging results over multiple runs to reproduce paper curves.
        """
        from simulation.scenarios import BENCHMARK_SCENARIOS
        scenario = BENCHMARK_SCENARIOS[scenario_key]
        results_rows = []
        total_steps = len(scenario.parameter_values)

        for step_idx, param_val in enumerate(scenario.parameter_values):
            if progress_callback:
                progress_callback(
                    step_idx / total_steps,
                    f"Evaluating {scenario.name}: {scenario.parameter_name} = {param_val}"
                )

            # Accumulator across Monte Carlo runs
            strat_metrics: Dict[str, Dict[str, float]] = {
                name: {"latency": 0.0, "energy": 0.0} for name in self.strategies.keys()
            }

            for run in range(iterations_per_point):
                seed = 100 * (step_idx + 1) + run
                
                # Configure run according to parameter
                if scenario_key == "uav_scaling":
                    num_tasks = int(param_val)
                    run_res = self.run_single_comparison(num_tasks=num_tasks, seed=seed)
                elif scenario_key == "data_size_variation":
                    run_res = self.run_single_comparison(
                        num_tasks=25,
                        fixed_data_size_mb=float(param_val),
                        seed=seed
                    )
                elif scenario_key == "application_classes":
                    run_res = self.run_single_comparison(
                        num_tasks=25,
                        specific_class=str(param_val),
                        seed=seed
                    )
                elif scenario_key == "fog_capability":
                    # Temporarily adjust fog node capacity
                    orig_mips = self.params.fog.capacity_mips
                    self.params.fog.capacity_mips = float(param_val)
                    run_res = self.run_single_comparison(num_tasks=30, seed=seed)
                    self.params.fog.capacity_mips = orig_mips
                elif scenario_key == "fog_node_scaling":
                    # Temporarily adjust fog nodes count
                    orig_nodes = len(self.env.fog_nodes)
                    self.env = SimulationEnvironment(params=self.params, num_fog_nodes=int(param_val))
                    run_res = self.run_single_comparison(num_tasks=30, seed=seed)
                    self.env = SimulationEnvironment(params=self.params, num_fog_nodes=orig_nodes)
                else:
                    run_res = self.run_single_comparison(num_tasks=20, seed=seed)

                for name, summary in run_res["summaries"].items():
                    strat_metrics[name]["latency"] += summary["avg_latency_ms"]
                    strat_metrics[name]["energy"] += summary["total_energy_joules"]

            # Compute averages
            for name, vals in strat_metrics.items():
                results_rows.append({
                    "Scenario": scenario.name,
                    "Parameter": scenario.parameter_name,
                    "Parameter_Value": param_val,
                    "Strategy": name,
                    "Avg_Latency_ms": round(vals["latency"] / iterations_per_point, 3),
                    "Total_Energy_J": round(vals["energy"] / iterations_per_point, 4)
                })

        df = pd.DataFrame(results_rows)
        # Auto-export result to data/results/
        out_csv = RESULTS_DIR / f"{scenario_key}_results.csv"
        df.to_csv(out_csv, index=False)
        return df
