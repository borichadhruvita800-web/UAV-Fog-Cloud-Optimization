"""
Unit tests for MILP optimization engine and constraints.
"""

import pytest
from optimization.solver import SolverManager
from optimization.milp_model import MILPOptimizer
from models.task import UAVTask
from config.parameters import ResearchSystemParameters


def test_solver_manager():
    solvers = SolverManager.list_available_solvers()
    assert len(solvers) > 0
    solver = SolverManager.get_solver("HiGHS")
    assert solver is not None


def test_milp_optimizer_small_scenario():
    optimizer = MILPOptimizer()
    
    tasks = [
        UAVTask(task_id="T1", uav_id="U1", source_city="London", task_class="A", mips_required=500.0, input_data_size_mb=10.0),
        UAVTask(task_id="T2", uav_id="U2", source_city="London", task_class="B", mips_required=2000.0, input_data_size_mb=15.0),
        UAVTask(task_id="T3", uav_id="U3", source_city="Paris", task_class="A", mips_required=500.0, input_data_size_mb=10.0),
        UAVTask(task_id="T4", uav_id="U4", source_city="Frankfurt", task_class="C", mips_required=6000.0, input_data_size_mb=25.0),
        UAVTask(task_id="T5", uav_id="U5", source_city="Berlin", task_class="B", mips_required=2000.0, input_data_size_mb=15.0),
    ]

    result = optimizer.optimize(tasks, time_limit_sec=10)
    
    assert result.is_optimal is True
    assert result.status == "Optimal"
    assert len(result.task_decisions) == 5
    assert (result.uav_count + result.fog_count + result.cloud_count) == 5
    assert result.total_power_watts > 0.0
    assert result.average_service_latency_ms > 0.0
    assert result.solve_time_seconds < 5.0

    # Test DataFrame extraction
    df = result.decisions_dataframe()
    assert len(df) == 5
    assert "assigned_tier" in df.columns


def test_empty_tasks():
    optimizer = MILPOptimizer()
    result = optimizer.optimize([])
    assert result.status == "No Tasks Provided"
