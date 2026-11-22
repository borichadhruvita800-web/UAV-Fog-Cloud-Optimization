"""
Unit tests for Simulation Engine, Scenarios, and Comparative Strategies.
"""

import pytest
import pandas as pd
from simulation.task_generator import TaskGenerator
from simulation.environment import SimulationEnvironment
from simulation.engine import SimulationEngine
from simulation.scenarios import BENCHMARK_SCENARIOS
from strategies.uav_only import UAVOnlyStrategy
from strategies.fog_only import FogOnlyStrategy
from strategies.cloud_only import CloudOnlyStrategy
from strategies.collaborative import CollaborativeStrategy
from strategies.heuristic import HeuristicStrategy


def test_task_generator_distribution():
    gen = TaskGenerator(seed=42)
    tasks = gen.generate_tasks(num_tasks=200)
    assert len(tasks) == 200
    
    classes = [t.task_class for t in tasks]
    count_a = classes.count("A")
    count_b = classes.count("B")
    count_c = classes.count("C")

    # In 200 tasks, Class A should be dominant ~60% (e.g. >50%)
    assert count_a > count_b
    assert count_b > count_c
    assert (count_a + count_b + count_c) == 200


def test_simulation_environment():
    env = SimulationEnvironment(num_fog_nodes=28)
    assert len(env.fog_nodes) == 28
    assert env.cloud_server.city == "Frankfurt"
    uav = env.get_or_create_uav("UAV_TEST_01", "Paris")
    assert uav.city == "Paris"
    env.reset()
    assert env.cloud_server.available_mips == 18000.0


def test_comparative_strategies():
    gen = TaskGenerator(seed=123)
    tasks = gen.generate_tasks(num_tasks=10)
    env = SimulationEnvironment()

    # 1. UAV only
    uav_strat = UAVOnlyStrategy()
    uav_res = uav_strat.execute(tasks, env=env)
    assert len(uav_res) == 10
    assert all(t.assigned_destination == "uav" for t in uav_res)
    assert all(t.execution_latency_ms > 0 for t in uav_res)

    # 2. Fog only
    fog_strat = FogOnlyStrategy()
    fog_res = fog_strat.execute(tasks, env=env)
    assert len(fog_res) == 10
    assert all(t.assigned_destination == "fog" for t in fog_res)
    assert all(t.execution_latency_ms > 0 for t in fog_res)

    # 3. Cloud only
    cloud_strat = CloudOnlyStrategy()
    cloud_res = cloud_strat.execute(tasks, env=env)
    assert len(cloud_res) == 10
    assert all(t.assigned_destination == "cloud" for t in cloud_res)
    assert all(t.execution_latency_ms > 0 for t in cloud_res)

    # 4. Collaborative (MILP)
    collab_strat = CollaborativeStrategy()
    collab_res = collab_strat.execute(tasks, env=env)
    assert len(collab_res) == 10
    assert all(t.assigned_destination in ["uav", "fog", "cloud"] for t in collab_res)

    # 5. Heuristic (Algorithm 1)
    heur_strat = HeuristicStrategy()
    heur_res = heur_strat.execute(tasks, env=env)
    assert len(heur_res) == 10
    assert all(t.assigned_destination in ["uav", "fog", "cloud"] for t in heur_res)


def test_simulation_engine_single_run():
    engine = SimulationEngine()
    run_output = engine.run_single_comparison(num_tasks=15, seed=42)
    assert "summaries" in run_output
    assert "comparison_df" in run_output
    assert len(run_output["summaries"]) == 5
    
    comp_df = run_output["comparison_df"]
    assert isinstance(comp_df, pd.DataFrame)
    assert len(comp_df) == 5
    assert "Avg Latency (ms)" in comp_df.columns
    assert "Total Energy (J)" in comp_df.columns
