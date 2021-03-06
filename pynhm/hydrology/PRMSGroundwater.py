from typing import Union

import numpy as np

from pynhm.base.storageUnit import StorageUnit

from ..base.adapter import Adapter
from ..base.control import Control

adaptable = Union[str, np.ndarray, Adapter]


class PRMSGroundwater(StorageUnit):
    """PRMS groundwater reservoir

    Args:
    """

    def __init__(
        self,
        control: Control,
        soil_to_gw: adaptable,
        ssr_to_gw: adaptable,
        dprst_seep_hru: adaptable,
        verbose: bool = False,
    ) -> "PRMSGroundwater":

        super().__init__(
            control=control,
            verbose=verbose,
        )
        self.name = "PRMSGroundwater"

        self.set_inputs(locals())
        return

    def set_initial_conditions(self):
        # initialize groundwater reservoir storage
        self.gwres_stor = self.gwstor_init.copy()
        self.gwres_stor_old = self.gwstor_init.copy()
        return

    @staticmethod
    def get_parameters() -> tuple:
        """Get groundwater reservoir parameters

        Returns:
            parameters: input parameters

        """
        return (
            "nhru",
            "ngw",
            "hru_area",
            "gwflow_coef",
            "gwsink_coef",
            "gwstor_init",
            "gwstor_min",
        )

    @staticmethod
    def get_inputs() -> tuple:
        """Get groundwater reservoir input variables

        Returns:
            variables: input variables

        """
        return (
            "soil_to_gw",
            "ssr_to_gw",
            "dprst_seep_hru",
        )

    @staticmethod
    def get_variables() -> tuple:
        """Get groundwater reservoir output variables

        Returns:
            variables: output variables

        """
        return (
            "gwres_flow",
            "gwres_in",
            "gwres_sink",
            "gwres_stor",
        )

    @staticmethod
    def get_init_values() -> dict:
        """Get groundwater reservoir initial values

        Returns:
            dict: initial values for named variables
        """
        # No GW res values need initialized prior to calculation.
        return {}

    def _advance_variables(self) -> None:
        """Advance the groundwater reservoir variables
        Returns:
            None
        """
        self.gwres_stor_old = self.gwres_stor
        return

    def calculate(self, simulation_time):
        """Calculate groundwater reservoir terms for a time step

        Args:
            simulation_time: current simulation time

        Returns:
            None

        """

        self._simulation_time = simulation_time

        gwarea = self.hru_area

        # calculate volume terms
        # gwstor_min_vol = self.gwstor_min * gwarea
        gwres_stor = self.gwres_stor * gwarea
        soil_to_gw_vol = self.soil_to_gw * gwarea
        ssr_to_gw_vol = self.ssr_to_gw * gwarea
        dprst_seep_hru_vol = self.dprst_seep_hru * gwarea

        # initialize calculation variables
        gwres_in = soil_to_gw_vol + ssr_to_gw_vol + dprst_seep_hru_vol

        # todo: what about route order

        gwres_stor += gwres_in

        gwres_flow = gwres_stor * self.gwflow_coef

        gwres_stor -= gwres_flow

        gwres_sink = gwres_stor * self.gwsink_coef
        idx = np.where(gwres_sink > gwres_stor)
        gwres_sink[idx] = gwres_stor[idx]

        gwres_stor -= gwres_sink

        # output variables
        self.gwres_stor = gwres_stor / gwarea
        self.gwres_in = (
            gwres_in  # for some stupid reason this is left in acre-inches
        )
        self.gwres_flow = gwres_flow / gwarea
        self.gwres_sink = gwres_sink / gwarea

        return
