"""
Objective function formulation for UAV-Fog-Cloud MILP optimization.
Implements Equations (1), (2), (3), and (4) from Mohammad Aldossary, IEEE Access, 2024.
"""

from typing import Dict, Any, List, Tuple
import pulp
from config.parameters import ResearchSystemParameters
from models.task import UAVTask


class MILPObjectiveBuilder:
    """
    Constructs the objective function to minimize total power across
    (UAV + Access) + (Fog + Metro) + (Cloud + Core).
    """
    def __init__(self, params: ResearchSystemParameters):
        self.params = params

    def build_objective(
        self,
        tasks: List[UAVTask],
        theta: Dict[Tuple[str, str], pulp.LpVariable],  # (task_id, target) -> binary var
        equipment_vars: Dict[str, Any],
        base_num_uavs: int = 100,
        num_cities: int = 28
    ) -> pulp.LpAffineExpression:
        """
        Builds the linear expression for Equation (4):
        Minimize Power = (UAV + Access) + (Fog + Metro) + (Cloud + Core)
        """
        obj_expr = pulp.LpAffineExpression()

        # -------------------------------------------------------------
        # 1. UAV + Access Layer Power (Eq. 1)
        # -------------------------------------------------------------
        # Base UAV and Gateway idle/operational power across areas
        base_uav_power = base_num_uavs * self.params.uav.power_watts
        base_gw_count = max(1, (base_num_uavs + 2) // self.params.uav.gateway_uav_capacity)
        base_gw_power = base_gw_count * self.params.uav.gateway_power_watts
        obj_expr += (base_uav_power + base_gw_power)

        # Access equipment power (ONU and OLT)
        pue_net = self.params.access_net.pue_network
        for s_city, vars_dict in equipment_vars.get("access", {}).items():
            onu_var = vars_dict["onu"]
            olt_var = vars_dict["olt"]
            obj_expr += pue_net * (
                onu_var * self.params.access_net.onu_power_watts +
                olt_var * self.params.access_net.olt_power_watts
            )

        # Local UAV computation power when task is executed on UAV
        # Computing power on UAV = UAV_power * (MIPS / 800)
        for task in tasks:
            if (task.task_id, "uav") in theta:
                var_uav = theta[(task.task_id, "uav")]
                comp_coeff = (task.mips_required / self.params.uav.processing_mips) * self.params.uav.power_watts
                obj_expr += var_uav * comp_coeff

        # -------------------------------------------------------------
        # 2. Fog + Metro Area Network Power (Eq. 2)
        # -------------------------------------------------------------
        # MIPS processing in fog: PUE(fog) * MIPS_i * PCMIPS(fog)
        pue_fog = self.params.fog.pue_fog
        pcmips_fog = self.params.fog.pcmips_watts_per_mips  # 0.035 W/MIPS
        np_fog_bps = self.params.fog.np_fog_watts_per_gbps / 1.0e9  # W/bps

        for task in tasks:
            for d_target in ["fog", "fog_local"]:
                if (task.task_id, d_target) in theta:
                    var_fog = theta[(task.task_id, d_target)]
                    proc_coeff = pue_fog * (task.mips_required * pcmips_fog)
                    net_coeff = pue_fog * (np_fog_bps * task.input_data_size_bits)
                    obj_expr += var_fog * (proc_coeff + net_coeff)

        # Metro network equipment (MR and MS)
        for s_city, vars_dict in equipment_vars.get("metro", {}).items():
            mr_var = vars_dict["mr"]
            ms_var = vars_dict["ms"]
            obj_expr += pue_net * (
                mr_var * self.params.metro_net.router_power_watts +
                ms_var * self.params.metro_net.switch_power_watts
            )

        # -------------------------------------------------------------
        # 3. Cloud + Core Network Power (Eq. 3)
        # -------------------------------------------------------------
        # MIPS processing in cloud: PUE(cloud) * MIPS_i * PCMIPS(cloud)
        pue_cloud = self.params.cloud.pue_cloud
        pcmips_cloud = self.params.cloud.pcmips_watts_per_mips  # 0.035 W/MIPS
        np_cloud_bps = self.params.cloud.np_cloud_watts_per_gbps / 1.0e9  # W/bps

        for task in tasks:
            if (task.task_id, "cloud") in theta:
                var_cloud = theta[(task.task_id, "cloud")]
                proc_coeff = pue_cloud * (task.mips_required * pcmips_cloud)
                net_coeff = pue_cloud * (np_cloud_bps * task.input_data_size_bits)
                obj_expr += var_cloud * (proc_coeff + net_coeff)

        # Core network equipment (router ports, transponders, amplifiers, optical switches)
        core_vars = equipment_vars.get("core", {})
        if "router_ports" in core_vars:
            r_d = core_vars["router_ports"]
            obj_expr += pue_net * (r_d * self.params.core_net.router_port_power_watts)
        if "transponders" in core_vars:
            t_var = core_vars["transponders"]
            obj_expr += pue_net * (t_var * self.params.core_net.transponder_power_watts)
        if "amplifiers" in core_vars:
            amp_var = core_vars["amplifiers"]
            fibers = self.params.core_net.fibers_per_link
            obj_expr += pue_net * (amp_var * self.params.core_net.amplifier_power_watts * fibers)
        if "optical_switches" in core_vars:
            sw_var = core_vars["optical_switches"]
            obj_expr += pue_net * (sw_var * self.params.core_net.optical_switch_power_watts)

        return obj_expr


# Type alias for cleaner type signatures
Tuple_Key = tuple
