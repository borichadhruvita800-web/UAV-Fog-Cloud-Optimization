"""
Task generation engine for UAV computational workloads.
Based on Table 4 in Mohammad Aldossary, IEEE Access, 2024.
"""

import random
from typing import List, Optional, Dict
from config.parameters import ResearchSystemParameters, DEFAULT_TASK_CLASSES
from config.settings import EURO_28_CITIES
from models.task import UAVTask


class TaskGenerator:
    """
    Generates synthetic UAV computational tasks according to research paper distributions:
    - Class A (Low: 500 MIPS): 60% frequency
    - Class B (Med: 2000 MIPS): 30% frequency
    - Class C (High: 6000 MIPS): 10% frequency
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        seed: Optional[int] = 42
    ):
        self.params = params or ResearchSystemParameters()
        self.seed = seed
        if self.seed is not None:
            random.seed(self.seed)

    def generate_tasks(
        self,
        num_tasks: int,
        fixed_data_size_mb: Optional[float] = None,
        data_size_range_mb: Optional[tuple] = None,
        specific_class: Optional[str] = None,
        cities: Optional[List[str]] = None,
        seed: Optional[int] = None
    ) -> List[UAVTask]:
        """
        Generates a batch of UAV tasks distributed across European cities.
        """
        if seed is not None:
            random.seed(seed)

        available_cities = cities or list(EURO_28_CITIES.keys())
        tasks: List[UAVTask] = []

        class_weights = [
            ("A", 0.60, 500.0, 10.0),
            ("B", 0.30, 2000.0, 15.0),
            ("C", 0.10, 6000.0, 25.0),
        ]

        for i in range(num_tasks):
            city = random.choice(available_cities)
            uav_id = f"UAV_{city[:3].upper()}_{i + 1:04d}"

            if specific_class in ["A", "B", "C"]:
                c_name = specific_class
                for c_t, _, mips, typical_size in class_weights:
                    if c_t == specific_class:
                        task_mips = mips
                        default_size = typical_size
                        break
            else:
                # Weighted distribution matching paper Table 4
                rnd = random.random()
                if rnd < 0.60:
                    c_name, task_mips, default_size = "A", 500.0, 10.0
                elif rnd < 0.90:
                    c_name, task_mips, default_size = "B", 2000.0, 15.0
                else:
                    c_name, task_mips, default_size = "C", 6000.0, 25.0

            # Determine input data size
            if fixed_data_size_mb is not None:
                data_size = fixed_data_size_mb
            elif data_size_range_mb is not None:
                data_size = random.uniform(data_size_range_mb[0], data_size_range_mb[1])
            else:
                # Slight variation around typical size
                data_size = round(random.uniform(default_size * 0.8, default_size * 1.2), 2)

            task = UAVTask(
                task_id=f"TSK_{i + 1:05d}",
                uav_id=uav_id,
                source_city=city,
                task_class=c_name,
                mips_required=task_mips,
                input_data_size_mb=data_size,
                data_rate_bps=self.params.uav.data_rate_bps
            )
            tasks.append(task)

        return tasks
