"""
Simulation Environment modeling Euro-28 UAV-Fog-Cloud infrastructure.
Based on Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import Dict, List, Optional
from config.parameters import ResearchSystemParameters
from config.settings import EURO_28_CITIES, DEFAULT_CLOUD_CITY
from models.uav import UAV
from models.fog_node import FogNode
from models.cloud_server import CloudServer
from models.network import TelecommunicationNetwork


class SimulationEnvironment:
    """
    Encapsulates the complete multi-tier execution environment:
    - 28 European cities with Fog Nodes
    - Central Cloud Data Center
    - Active UAV fleets with Gateway clustering
    - Multi-tier Telecommunication Network (Access, Metro, Core)
    """
    def __init__(
        self,
        params: Optional[ResearchSystemParameters] = None,
        cloud_city: str = DEFAULT_CLOUD_CITY,
        num_fog_nodes: int = 28
    ):
        self.params = params or ResearchSystemParameters()
        self.cloud_city = cloud_city
        self.network = TelecommunicationNetwork(
            access_params=self.params.access_net,
            metro_params=self.params.metro_net,
            core_params=self.params.core_net
        )
        
        # Initialize Fog nodes for Euro-28 cities (or a subset up to num_fog_nodes)
        city_names = list(EURO_28_CITIES.keys())[:num_fog_nodes]
        self.fog_nodes: Dict[str, FogNode] = {
            city: FogNode(node_id=f"fog_{city}", city=city, params=self.params.fog)
            for city in city_names
        }

        # Central Cloud server
        self.cloud_server = CloudServer(
            server_id=f"cloud_{cloud_city}",
            city=cloud_city,
            params=self.params.cloud
        )

        # UAV repository (populated dynamically per scenario)
        self.uavs: Dict[str, UAV] = {}

    def get_or_create_uav(self, uav_id: str, city: str) -> UAV:
        """Retrieves an existing UAV or spawns a new one in the given city."""
        if uav_id not in self.uavs:
            self.uavs[uav_id] = UAV(uav_id=uav_id, city=city, params=self.params.uav)
        return self.uavs[uav_id]

    def reset(self) -> None:
        """Resets all node capacities and task queues."""
        for fog in self.fog_nodes.values():
            fog.reset()
        self.cloud_server.reset()
        for uav in self.uavs.values():
            uav.reset()
