"""
Evaluation metrics calculation for UAV-Fog-Cloud collaborative offloading.
Computes latency, energy consumption, and strategy comparison metrics.
Based on Mohammad Aldossary, IEEE Access, 2024 (Section V).
"""

from typing import Dict, List, Any
import pandas as pd
from models.task import UAVTask


class MetricsCalculator:
    """
    Computes performance and energy metrics across offloading strategies.
    """
    @staticmethod
    def calculate_strategy_summary(strategy_name: str, tasks: List[UAVTask]) -> Dict[str, Any]:
        """
        Calculates aggregate latency, energy, and tier distribution for a set of executed tasks.
        """
        if not tasks:
            return {
                "strategy": strategy_name,
                "task_count": 0,
                "avg_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "total_energy_joules": 0.0,
                "uav_tier_pct": 0.0,
                "fog_tier_pct": 0.0,
                "cloud_tier_pct": 0.0,
            }

        latencies = [t.execution_latency_ms for t in tasks]
        energies = [t.total_energy_joules for t in tasks]
        
        uav_count = sum(1 for t in tasks if t.assigned_destination == "uav")
        fog_count = sum(1 for t in tasks if t.assigned_destination == "fog")
        cloud_count = sum(1 for t in tasks if t.assigned_destination == "cloud")
        total_tasks = len(tasks)

        avg_lat = sum(latencies) / total_tasks
        max_lat = max(latencies) if latencies else 0.0
        tot_energy = sum(energies)

        # By-class latency breakdown
        by_class_lat: Dict[str, float] = {}
        for c in ["A", "B", "C"]:
            c_tasks = [t.execution_latency_ms for t in tasks if t.task_class == c]
            by_class_lat[f"class_{c}_latency_ms"] = (sum(c_tasks) / len(c_tasks)) if c_tasks else 0.0

        return {
            "strategy": strategy_name,
            "task_count": total_tasks,
            "avg_latency_ms": round(avg_lat, 3),
            "max_latency_ms": round(max_lat, 3),
            "total_energy_joules": round(tot_energy, 4),
            "uav_tasks": uav_count,
            "fog_tasks": fog_count,
            "cloud_tasks": cloud_count,
            "uav_tier_pct": round((uav_count / total_tasks) * 100.0, 1),
            "fog_tier_pct": round((fog_count / total_tasks) * 100.0, 1),
            "cloud_tier_pct": round((cloud_count / total_tasks) * 100.0, 1),
            **by_class_lat
        }

    @staticmethod
    def compare_strategies(
        summaries: Dict[str, Dict[str, Any]],
        baseline_name: str = "Proposed (Collaborative)"
    ) -> pd.DataFrame:
        """
        Calculates percentage latency and energy savings achieved by the proposed strategy
        relative to UAV-only, Fog-only, and Cloud-only baselines.
        """
        rows = []
        collab = summaries.get(baseline_name)

        for name, summary in summaries.items():
            row = {
                "Strategy": name,
                "Avg Latency (ms)": summary["avg_latency_ms"],
                "Total Energy (J)": summary["total_energy_joules"],
                "UAV (%)": summary.get("uav_tier_pct", 0.0),
                "Fog (%)": summary.get("fog_tier_pct", 0.0),
                "Cloud (%)": summary.get("cloud_tier_pct", 0.0),
            }

            if collab and name != baseline_name:
                # Latency Reduction = (Base - Collab) / Base * 100%
                base_lat = summary["avg_latency_ms"]
                if base_lat > 0:
                    lat_red = ((base_lat - collab["avg_latency_ms"]) / base_lat) * 100.0
                    row["Latency Reduction vs Base (%)"] = round(lat_red, 2)
                else:
                    row["Latency Reduction vs Base (%)"] = 0.0

                # Energy Reduction = (Base - Collab) / Base * 100%
                base_ene = summary["total_energy_joules"]
                if base_ene > 0:
                    ene_red = ((base_ene - collab["total_energy_joules"]) / base_ene) * 100.0
                    row["Energy Reduction vs Base (%)"] = round(ene_red, 2)
                else:
                    row["Energy Reduction vs Base (%)"] = 0.0
            else:
                row["Latency Reduction vs Base (%)"] = "-"
                row["Energy Reduction vs Base (%)"] = "-"

            rows.append(row)

        return pd.DataFrame(rows)
