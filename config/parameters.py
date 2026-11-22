"""
Research parameters for UAV-Fog-Cloud collaborative task offloading.
Source: Mohammad Aldossary, 'Optimizing Task Offloading for Collaborative
Unmanned Aerial Vehicles (UAVs) in Fog-Cloud Computing Environments', IEEE Access, 2024.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any
import json
from pathlib import Path


@dataclass
class UAVParameters:
    """Parameters for UAV layer from Table 2."""
    power_watts: float = 63.0  # Power consumption of a single UAV (Watts)
    data_rate_bps: float = 100_000.0  # Data rate of each UAV (100 Kbps)
    processing_mips: float = 800.0  # UAV onboard CPU capacity in MIPS
    gateway_power_watts: float = 30.0  # Power consumption of gateway (Watts)
    gateway_uav_capacity: int = 3  # Maximum connected UAVs per gateway
    wireless_bandwidth_bps: float = 54_000_000.0  # Local wireless air-to-ground / UAV link (54 Mbps)


@dataclass
class AccessNetworkParameters:
    """Parameters for Access network (LAN / PON) from Table 2."""
    onu_power_watts: float = 5.0  # Optical Network Unit power (Watts)
    onu_bitrate_bps: float = 2.4e9  # 2.4 Gbps
    olt_power_watts: float = 1842.0  # Optical Line Terminal power (1.842 kW)
    olt_bitrate_bps: float = 1.28e12  # 1.280 Tbps
    pue_network: float = 1.5  # Power Usage Effectiveness of network


@dataclass
class MetroNetworkParameters:
    """Parameters for Metro Area Network (MAN) from Table 2."""
    router_power_watts: float = 30.0  # Metro router power (Watts)
    router_bitrate_bps: float = 40.0e9  # 40 Gbps
    switch_power_watts: float = 470.0  # Metro switch power (Watts)
    switch_bitrate_bps: float = 0.5e12  # 0.5 Tbps (500 Gbps)
    np_fog_watts_per_gbps: float = 2.57  # Internal fog network power per Gbps


@dataclass
class CoreNetworkParameters:
    """Parameters for Core network (WAN / WDM) from Table 2."""
    router_port_power_watts: float = 37.1  # r^(power): router port in core (Watts)
    router_port_bandwidth_bps: float = 40.0e9  # B: Router port bandwidth (40 Gbps)
    transponder_power_watts: float = 129.0  # t^(power): transponder power (Watts)
    amplifier_power_watts: float = 11.0  # E^(power): amplifier power (Watts)
    optical_switch_power_watts: float = 85.0  # S_d^(power): optical switch power (Watts)
    amplifier_max_span_km: float = 80.0  # S: Max distance an amplifier can span (km)
    default_link_distance_km: float = 600.0  # Default link length in Euro 28 (km)
    fibers_per_link: int = 2  # F_m,n: Number of fibers per link
    speed_of_light_fiber_km_s: float = 200_000.0  # Propagation speed in fiber (~200 km/ms)


@dataclass
class FogNodeParameters:
    """Parameters for Fog nodes from Table 2."""
    power_watts: float = 126.0  # PFS^(power): Fog node power consumption (Watts)
    capacity_mips: float = 3600.0  # FS^(MIPS): Number of MIPS per fog node
    pue_fog: float = 1.9  # PUE^(fog): Power Usage Effectiveness of fog layer
    pcmips_watts_per_mips: float = 0.035  # PCMIPS^(fog) = 126 / 3600 = 0.035 W/MIPS
    np_fog_watts_per_gbps: float = 2.57  # NP^(fog): Power per bit for internal fog networking (Watts/Gbps)


@dataclass
class CloudServerParameters:
    """Parameters for Cloud servers from Table 2."""
    power_watts: float = 630.0  # PCS^(power): Cloud server power consumption (Watts)
    capacity_mips: float = 18000.0  # CS^(MIPS): Number of MIPS per cloud node
    pue_cloud: float = 1.1  # PUE^(cloud): Power Usage Effectiveness of cloud layer
    pcmips_watts_per_mips: float = 0.035  # PCMIPS^(cloud) = 630 / 18000 = 0.035 W/MIPS
    np_cloud_watts_per_gbps: float = 2.48  # Power consumption per bit for internal networking


@dataclass
class TaskClassDefinition:
    """Application intensity classification from Table 4."""
    name: str
    class_type: str
    mips_required: float
    frequency_ratio: float  # Percentage of tasks in simulation
    typical_data_size_mb: float = 15.0


DEFAULT_TASK_CLASSES: Dict[str, TaskClassDefinition] = {
    "A": TaskClassDefinition(
        name="Number Plate / Health / Sustainable Agriculture",
        class_type="A",
        mips_required=500.0,
        frequency_ratio=0.60,
        typical_data_size_mb=10.0,
    ),
    "B": TaskClassDefinition(
        name="Fire Detection / Video Surveillance",
        class_type="B",
        mips_required=2000.0,
        frequency_ratio=0.30,
        typical_data_size_mb=15.0,
    ),
    "C": TaskClassDefinition(
        name="Augmented Reality / Virtual Reality",
        class_type="C",
        mips_required=6000.0,
        frequency_ratio=0.10,
        typical_data_size_mb=25.0,
    ),
}


@dataclass
class ResearchSystemParameters:
    """Full parameter repository modeling Tables 2, 3, and 4."""
    uav: UAVParameters = field(default_factory=UAVParameters)
    access_net: AccessNetworkParameters = field(default_factory=AccessNetworkParameters)
    metro_net: MetroNetworkParameters = field(default_factory=MetroNetworkParameters)
    core_net: CoreNetworkParameters = field(default_factory=CoreNetworkParameters)
    fog: FogNodeParameters = field(default_factory=FogNodeParameters)
    cloud: CloudServerParameters = field(default_factory=CloudServerParameters)
    task_classes: Dict[str, TaskClassDefinition] = field(default_factory=lambda: DEFAULT_TASK_CLASSES.copy())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def save_json(self, path: Path | str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, path: Path | str) -> "ResearchSystemParameters":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        params = cls()
        if "uav" in data:
            params.uav = UAVParameters(**data["uav"])
        if "access_net" in data:
            params.access_net = AccessNetworkParameters(**data["access_net"])
        if "metro_net" in data:
            params.metro_net = MetroNetworkParameters(**data["metro_net"])
        if "core_net" in data:
            params.core_net = CoreNetworkParameters(**data["core_net"])
        if "fog" in data:
            params.fog = FogNodeParameters(**data["fog"])
        if "cloud" in data:
            params.cloud = CloudServerParameters(**data["cloud"])
        if "task_classes" in data:
            params.task_classes = {
                k: TaskClassDefinition(**v) for k, v in data["task_classes"].items()
            }
        return params
