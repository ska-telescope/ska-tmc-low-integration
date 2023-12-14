import json
import logging

from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy

from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.enums import SubarrayObsState

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class SubarrayNodeCspWrapperLow(SubarrayNodeWrapperLow):
    """Subarray Node Low class with real csp which implement methods required
    for test cases to test subarray node.
    """

    def _reset_simulator_devices(self):
        """Reset Simulator devices to it's original state"""
        for sim_device_fqdn in [self.sdp_subarray1]:
            device = DeviceProxy(sim_device_fqdn)
            device.ResetDelay()
            device.SetDirectHealthState(HealthState.UNKNOWN)
            device.SetDefective(json.dumps({"enabled": False}))

    def force_change_of_obs_state_mock(
        self, device_name: str, obs_state: SubarrayObsState
    ):
        """
        Method changes mock device obsState to desired obsState.
        :param device_name: FQDN of the mock device
        :type device_name:str
        :param obs_state: Desired observation state for the mock device.
        :type obs_state: SubarrayObsState
        """
        device_proxy = DeviceProxy(device_name)
        device_proxy.SetDirectObsState(obs_state)
        device_proxy.SetDirectObsState(obs_state)
