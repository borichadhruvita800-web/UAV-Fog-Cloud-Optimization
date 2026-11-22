"""
Unit tests for domain models and research parameters.
"""

import pytest
from config.parameters import ResearchSystemParameters, DEFAULT_TASK_CLASSES
from models.task import UAVTask
from models.uav import UAV
from models.fog_node import FogNode
from models.cloud_server import CloudServer
from models.network import TelecommunicationNetwork


def test_research_parameters_defaults():
    params = ResearchSystemParameters()
    assert params.uav.power_watts == 63.0
    assert params.uav.data_rate_bps == 100_000.0
    assert params.access_net.olt_power_watts == 1842.0
    assert params.metro_net.router_power_watts == 30.0
    assert params.metro_net.switch_power_watts == 470.0
    assert params.core_net.router_port_power_watts == 37.1
    assert params.fog.capacity_mips == 3600.0
    assert params.fog.power_watts == 126.0
    assert params.cloud.capacity_mips == 18000.0
    assert params.cloud.power_watts == 630.0
    assert params.cloud.pue_cloud == 1.1
    assert params.fog.pue_fog == 1.9


def test_task_model():
    task = UAVTask(
        task_id="TASK-001",
        uav_id="UAV_01",
        source_city="Frankfurt",
        task_class="A",
        mips_required=500.0,
        input_data_size_mb=15.0
    )
    assert task.input_data_size_mb == 15.0
    assert task.input_data_size_bytes == 15.0 * 1024 * 1024
    assert task.input_data_size_bits == 15.0 * 8 * 1024 * 1024
    d = task.to_dict()
    assert d["task_id"] == "TASK-001"
    assert d["mips_required"] == 500.0


def test_uav_model():
    uav = UAV(uav_id="UAV_01", city="London")
    assert uav.total_mips == 800.0
    assert uav.power_watts == 63.0

    task_low = UAVTask(mips_required=500.0)
    assert uav.can_process_locally(task_low)
    success = uav.assign_task(task_low)
    assert success is True
    assert uav.available_mips == 300.0
    assert task_low.assigned_destination == "uav"

    lat = uav.compute_local_latency(task_low)
    assert lat == (500.0 / 800.0) * 1000.0  # 625 ms


def test_fog_model():
    fog = FogNode(node_id="fog_Paris", city="Paris")
    assert fog.total_mips == 3600.0
    assert fog.pue == 1.9
    assert fog.pcmips == 0.035

    task = UAVTask(mips_required=2000.0)
    assert fog.can_process(task)
    success = fog.assign_task(task)
    assert success is True
    assert fog.available_mips == 1600.0
    assert task.assigned_destination == "fog"

    lat = fog.compute_processing_latency(task)
    assert pytest.approx(lat, 0.01) == (2000.0 / 3600.0) * 1000.0

    # Eq 2 computing power: PUE * MIPS * PCMIPS = 1.9 * 2000 * 0.035
    pwr = fog.compute_compute_power(2000.0)
    assert pytest.approx(pwr, 0.01) == 1.9 * 2000.0 * 0.035


def test_cloud_model():
    cloud = CloudServer(server_id="cloud_Frankfurt", city="Frankfurt")
    assert cloud.total_mips == 18000.0
    assert cloud.pue == 1.1
    assert cloud.pcmips == 0.035

    task = UAVTask(mips_required=6000.0)
    assert cloud.can_process(task)
    success = cloud.assign_task(task)
    assert success is True
    assert cloud.available_mips == 12000.0

    lat = cloud.compute_processing_latency(task)
    assert pytest.approx(lat, 0.01) == (6000.0 / 18000.0) * 1000.0


def test_network_routing_and_power():
    net = TelecommunicationNetwork()
    path, dist = net.get_shortest_path("London", "Frankfurt")
    assert len(path) >= 2
    assert path[0] == "London"
    assert path[-1] == "Frankfurt"
    assert dist > 0.0

    # Test access network power
    acc_pwr = net.calculate_access_network_power(num_uavs=100, total_traffic_bps=10_000_000.0)
    assert acc_pwr["total_access_power"] > 0.0
    assert acc_pwr["gw_count"] == 34  # ceil(100/3)

    # Test metro network power
    metro_pwr = net.calculate_metro_network_power(metro_traffic_bps=1_000_000_000.0)
    assert metro_pwr["total_metro_power"] > 0.0

    # Test transmission latency
    lat_info = net.compute_transmission_latency(
        data_size_bits=15.0 * 8 * 1024 * 1024,
        source_city="London",
        destination_city="Frankfurt",
        target_layer="cloud"
    )
    assert lat_info["total_comm_latency_ms"] > 0.0
    assert lat_info["t_core_ms"] > 0.0
