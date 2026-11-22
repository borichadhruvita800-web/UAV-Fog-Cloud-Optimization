"""
Network model representing Access, Metro, and Core telecommunication networks.
Based on Mohammad Aldossary, IEEE Access, 2024 (Section IV & Equations 1, 2, 3).
"""

import math
import heapq
from typing import Dict, List, Tuple, Optional, Any
from config.parameters import (
    AccessNetworkParameters,
    MetroNetworkParameters,
    CoreNetworkParameters,
)
from config.settings import EURO_28_CITIES, EURO_28_LINKS


class TelecommunicationNetwork:
    """
    Simulates the multi-tier telecommunication infrastructure connecting
    UAVs, Fog nodes, and Cloud servers across the Euro-28 topology.
    """
    def __init__(
        self,
        access_params: Optional[AccessNetworkParameters] = None,
        metro_params: Optional[MetroNetworkParameters] = None,
        core_params: Optional[CoreNetworkParameters] = None,
        cities: Optional[Dict[str, Dict[str, float]]] = None,
        links: Optional[List[Tuple[str, str]]] = None,
    ):
        self.access_params = access_params or AccessNetworkParameters()
        self.metro_params = metro_params or MetroNetworkParameters()
        self.core_params = core_params or CoreNetworkParameters()
        self.cities = cities or EURO_28_CITIES
        self.links = links or EURO_28_LINKS

        # Build adjacency graph for shortest path routing
        self.graph: Dict[str, List[Tuple[str, float]]] = {c: [] for c in self.cities}
        self._build_topology()

    def _build_topology(self) -> None:
        """Constructs graph edges with link distance (600 km per link in Euro-28)."""
        link_distance = self.core_params.default_link_distance_km  # 600.0 km
        for u, v in self.links:
            if u in self.graph and v in self.graph:
                self.graph[u].append((v, link_distance))
                self.graph[v].append((u, link_distance))

    def get_shortest_path(self, source: str, destination: str) -> Tuple[List[str], float]:
        """
        Calculates shortest path using Dijkstra's algorithm.
        Returns: (list_of_nodes_in_path, total_distance_km)
        """
        if source == destination:
            return ([source], 0.0)

        distances: Dict[str, float] = {node: float("inf") for node in self.cities}
        distances[source] = 0.0
        previous: Dict[str, Optional[str]] = {node: None for node in self.cities}
        pq: List[Tuple[float, str]] = [(0.0, source)]

        while pq:
            curr_dist, curr_node = heapq.heappop(pq)
            if curr_dist > distances[curr_node]:
                continue
            if curr_node == destination:
                break

            for neighbor, weight in self.graph.get(curr_node, []):
                dist = curr_dist + weight
                if dist < distances[neighbor]:
                    distances[neighbor] = dist
                    previous[neighbor] = curr_node
                    heapq.heappush(pq, (dist, neighbor))

        path: List[str] = []
        curr = destination
        while curr is not None:
            path.append(curr)
            curr = previous[curr]
        path.reverse()

        if not path or path[0] != source:
            # Fallback direct virtual link if disconnected
            return ([source, destination], self.core_params.default_link_distance_km)

        return (path, distances[destination])

    def calculate_amplifiers_per_link(self, distance_km: float) -> int:
        """
        Calculates number of amplifiers present on connected link (m,n):
        A_m,n = ceil(D_m,n / S - 1)
        where S is max amplifier span (80 km).
        """
        s = self.core_params.amplifier_max_span_km
        val = math.ceil(distance_km / s - 1)
        return max(0, val)

    def calculate_access_network_power(
        self,
        num_uavs: int,
        total_traffic_bps: float,
        num_gateways: Optional[int] = None
    ) -> Dict[str, float]:
        """
        Computes Access Network power according to Eq. (1):
        P_access = PUE(network) * [ ONU_num * ONU_pwr + OLT_num * OLT_pwr ] + GW_num * GW_pwr
        C10: ONU_num + OLT_num >= total_traffic / (ONU_bitrate + OLT_bitrate)
        """
        gw_count = num_gateways if num_gateways is not None else math.ceil(num_uavs / 3.0)
        gw_power = gw_count * 30.0  # 30W per gateway

        # Access equipment count required by bitrate
        total_capacity = self.access_params.onu_bitrate_bps + self.access_params.olt_bitrate_bps
        req_units = max(1, math.ceil(total_traffic_bps / max(1.0, total_capacity)))
        onu_count = req_units
        olt_count = max(1, math.ceil(onu_count / 16.0))  # 1 OLT serves multiple ONUs

        onu_power = onu_count * self.access_params.onu_power_watts  # 5W
        olt_power = olt_count * self.access_params.olt_power_watts  # 1842W
        optical_net_power = self.access_params.pue_network * (onu_power + olt_power)

        return {
            "gateway_power": gw_power,
            "onu_power": onu_power,
            "olt_power": olt_power,
            "total_access_power": gw_power + optical_net_power,
            "onu_count": onu_count,
            "olt_count": olt_count,
            "gw_count": gw_count
        }

    def calculate_metro_network_power(
        self,
        metro_traffic_bps: float
    ) -> Dict[str, float]:
        """
        Computes Metro Network power according to Eq. (2) and C11:
        MR_num + MS_num >= 2 * traffic / (MR_bitrate + MS_bitrate)
        P_metro = PUE(network) * [ MR_num * MR_pwr + MS_num * MS_pwr ]
        """
        rate_sum = self.metro_params.router_bitrate_bps + self.metro_params.switch_bitrate_bps
        min_units = max(1, math.ceil(2.0 * metro_traffic_bps / max(1.0, rate_sum)))
        mr_count = max(1, math.ceil(min_units / 2.0))
        ms_count = max(1, math.ceil(min_units / 2.0))

        mr_power = mr_count * self.metro_params.router_power_watts  # 30W
        ms_power = ms_count * self.metro_params.switch_power_watts  # 470W
        total_metro = self.access_params.pue_network * (mr_power + ms_power)

        return {
            "mr_count": mr_count,
            "ms_count": ms_count,
            "mr_power": mr_power,
            "ms_power": ms_power,
            "total_metro_power": total_metro
        }

    def calculate_core_network_power(
        self,
        core_traffic_bps: float,
        active_links: List[Tuple[str, str]],
        num_core_nodes: int = 1
    ) -> Dict[str, float]:
        """
        Computes Core Network power according to Eq. (3):
        P_core = PUE(network) * [ sum(r_d * r_pwr) + sum(l_mn * t_pwr) + sum(E_pwr * F_mn * A_mn) + sum(S_d_pwr) ]
        """
        # C9: r_d >= TU_sd / B (router port bandwidth 40 Gbps)
        b = self.core_params.router_port_bandwidth_bps
        router_ports = max(1, math.ceil(core_traffic_bps / max(1.0, b)))
        router_ports_power = router_ports * self.core_params.router_port_power_watts  # 37.1W

        # Transponders on active path hops
        num_active_hops = len(active_links)
        transponders = num_active_hops * 2  # 1 transponder at each link end
        transponder_power = transponders * self.core_params.transponder_power_watts  # 129W

        # Optical amplifiers along spans
        total_amp_power = 0.0
        fibers = self.core_params.fibers_per_link  # 2 fibers
        for _ in active_links:
            amps = self.calculate_amplifiers_per_link(self.core_params.default_link_distance_km)
            total_amp_power += self.core_params.amplifier_power_watts * fibers * amps

        # Optical switches at core destination nodes
        optical_switch_power = num_core_nodes * self.core_params.optical_switch_power_watts  # 85W

        subtotal = router_ports_power + transponder_power + total_amp_power + optical_switch_power
        total_core = self.access_params.pue_network * subtotal

        return {
            "router_ports": router_ports,
            "router_ports_power": router_ports_power,
            "transponders": transponders,
            "transponder_power": transponder_power,
            "amplifier_power": total_amp_power,
            "optical_switch_power": optical_switch_power,
            "total_core_power": total_core
        }

    def compute_transmission_latency(
        self,
        data_size_bits: float,
        source_city: str,
        destination_city: str,
        target_layer: str
    ) -> Dict[str, float]:
        """
        Computes multi-tier transmission and propagation latencies (in milliseconds).
        """
        # 1. Access Network Latency: wireless air-interface + PON
        # UAV wireless upload at nominal rate (e.g. 54 Mbps)
        t_wireless_tx_ms = (data_size_bits / 54_000_000.0) * 1000.0
        t_pon_tx_ms = (data_size_bits / self.access_params.onu_bitrate_bps) * 1000.0
        t_access_ms = t_wireless_tx_ms + t_pon_tx_ms

        if target_layer == "uav":
            # Direct UAV-to-UAV collaboration (local wireless hop)
            return {
                "t_access_ms": t_wireless_tx_ms,
                "t_metro_ms": 0.0,
                "t_core_ms": 0.0,
                "t_propagation_ms": 0.0,
                "total_comm_latency_ms": t_wireless_tx_ms
            }

        # 2. Metro Network Latency
        t_metro_tx_ms = (data_size_bits / self.metro_params.router_bitrate_bps) * 1000.0
        t_metro_prop_ms = 0.5  # Typical intra-city MAN propagation delay

        if target_layer == "fog":
            # If offloading to local fog in same city:
            if source_city == destination_city:
                total_comm = t_access_ms + t_metro_tx_ms + t_metro_prop_ms
                return {
                    "t_access_ms": t_access_ms,
                    "t_metro_ms": t_metro_tx_ms + t_metro_prop_ms,
                    "t_core_ms": 0.0,
                    "t_propagation_ms": t_metro_prop_ms,
                    "total_comm_latency_ms": total_comm
                }
            else:
                # Inter-city fog offloading traverses core network
                path, dist_km = self.get_shortest_path(source_city, destination_city)
                num_hops = max(1, len(path) - 1)
                t_core_tx_ms = num_hops * (data_size_bits / self.core_params.router_port_bandwidth_bps) * 1000.0
                t_core_prop_ms = (dist_km / self.core_params.speed_of_light_fiber_km_s) * 1000.0
                total_comm = t_access_ms + t_metro_tx_ms + t_core_tx_ms + t_core_prop_ms
                return {
                    "t_access_ms": t_access_ms,
                    "t_metro_ms": t_metro_tx_ms,
                    "t_core_ms": t_core_tx_ms,
                    "t_propagation_ms": t_core_prop_ms,
                    "total_comm_latency_ms": total_comm
                }

        # 3. Cloud Network Latency (Access + Metro + Core WAN)
        path, dist_km = self.get_shortest_path(source_city, destination_city)
        num_hops = max(1, len(path) - 1)
        t_core_tx_ms = num_hops * (data_size_bits / self.core_params.router_port_bandwidth_bps) * 1000.0
        t_core_prop_ms = (dist_km / self.core_params.speed_of_light_fiber_km_s) * 1000.0
        total_comm = t_access_ms + t_metro_tx_ms + t_core_tx_ms + t_core_prop_ms

        return {
            "t_access_ms": t_access_ms,
            "t_metro_ms": t_metro_tx_ms,
            "t_core_ms": t_core_tx_ms,
            "t_propagation_ms": t_core_prop_ms,
            "total_comm_latency_ms": total_comm
        }
