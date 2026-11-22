"""
Unit tests for MetricsCalculator and savings percentages.
"""

import pytest
from models.task import UAVTask
from simulation.metrics import MetricsCalculator


def test_metrics_calculator_summary():
    t1 = UAVTask(mips_required=500.0, input_data_size_mb=10.0)
    t1.assigned_destination = "uav"
    t1.execution_latency_ms = 625.0
    t1.total_energy_joules = 39.375

    t2 = UAVTask(mips_required=2000.0, input_data_size_mb=15.0)
    t2.assigned_destination = "fog"
    t2.execution_latency_ms = 560.0
    t2.total_energy_joules = 75.0

    summary = MetricsCalculator.calculate_strategy_summary("TestStrategy", [t1, t2])
    assert summary["task_count"] == 2
    assert summary["avg_latency_ms"] == (625.0 + 560.0) / 2
    assert summary["total_energy_joules"] == 39.375 + 75.0
    assert summary["uav_tasks"] == 1
    assert summary["fog_tasks"] == 1
    assert summary["cloud_tasks"] == 0


def test_metrics_calculator_comparison():
    summaries = {
        "UAV Execution": {"avg_latency_ms": 1000.0, "total_energy_joules": 200.0},
        "Fog Execution": {"avg_latency_ms": 800.0, "total_energy_joules": 180.0},
        "Cloud Execution": {"avg_latency_ms": 1200.0, "total_energy_joules": 190.0},
        "Proposed (Collaborative)": {"avg_latency_ms": 500.0, "total_energy_joules": 150.0},
    }

    df = MetricsCalculator.compare_strategies(summaries, baseline_name="Proposed (Collaborative)")
    assert len(df) == 4
    
    # Check reduction for UAV
    uav_row = df[df["Strategy"] == "UAV Execution"].iloc[0]
    # (1000 - 500)/1000 * 100 = 50%
    assert uav_row["Latency Reduction vs Base (%)"] == 50.0
    # (200 - 150)/200 * 100 = 25%
    assert uav_row["Energy Reduction vs Base (%)"] == 25.0
