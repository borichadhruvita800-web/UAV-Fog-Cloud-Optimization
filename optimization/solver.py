"""
Solver wrapper for MILP optimization.
Integrates PuLP with HiGHS and CBC solvers.
"""

from typing import Tuple, Optional
import pulp


class SolverManager:
    """
    Manages selection and execution of MILP solvers (HiGHS / CBC).
    """
    @staticmethod
    def get_solver(preferred: str = "HiGHS", time_limit_sec: int = 30, msg: bool = False) -> pulp.LpSolver:
        """
        Returns an initialized solver instance with fallback.
        Priority:
        1. HiGHS (high performance, modern simplex/interior-point branch-and-bound)
        2. PULP_CBC_CMD (COIN-OR CBC bundled binary)
        """
        # 1. Try HiGHS directly if available
        if preferred.upper() == "HIGHS":
            try:
                solver = pulp.HiGHS(msg=msg, timeLimit=time_limit_sec)
                if solver.available():
                    return solver
            except Exception:
                pass

        # 2. Try PULP_CBC_CMD
        try:
            cbc_solver = pulp.PULP_CBC_CMD(timeLimit=time_limit_sec, msg=msg)
            if cbc_solver.available():
                return cbc_solver
        except Exception:
            pass

        # 3. Default fallback
        return pulp.HiGHS(msg=msg) if pulp.HiGHS().available() else pulp.PULP_CBC_CMD(msg=msg)

    @staticmethod
    def list_available_solvers() -> list:
        """List all verified available solvers on host."""
        return pulp.listSolvers(onlyAvailable=True)
