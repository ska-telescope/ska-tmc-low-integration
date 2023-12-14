import logging

from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

from tests.resources.test_harness.central_node import CentralNodeWrapper
from tests.resources.test_harness.constant import (
    device_dict_low,
    low_centralnode,
    low_csp_master,
    low_csp_master_leaf_node,
    low_csp_subarray1,
    low_sdp_master,
    low_sdp_master_leaf_node,
    low_sdp_subarray1,
    mccs_controller,
    mccs_master_leaf_node,
    mccs_subarray1,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_harness.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_release_resources,
    sync_restart,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)
# TODO: Currently the code for MCCS has been commented as it will be enabled
#  in the upcoming sprints of PI-20


class CentralNodeWrapperLow(CentralNodeWrapper):
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Low CentralNode,
    defined by the SKA Control Model."""

    def __init__(self) -> None:
        super().__init__()
        self.central_node = DeviceProxy(low_centralnode)
        self.subarray_node = DeviceProxy(tmc_low_subarraynode1)
        self.csp_master_leaf_node = DeviceProxy(low_csp_master_leaf_node)
        self.sdp_master_leaf_node = DeviceProxy(low_sdp_master_leaf_node)
        self.mccs_master_leaf_node = DeviceProxy(mccs_master_leaf_node)
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(low_csp_subarray1),
            "sdp_subarray": DeviceProxy(low_sdp_subarray1),
            "mccs_subarray": DeviceProxy(mccs_subarray1),
        }
        self.csp_subarray1 = DeviceProxy(low_csp_subarray1)
        self.sdp_master = DeviceProxy(low_sdp_master)
        self.csp_master = DeviceProxy(low_csp_master)
        self.mccs_master = DeviceProxy(mccs_controller)
        self._state = DevState.OFF
        self.json_factory = JsonFactory()
        self.release_input = (
            self.json_factory.create_centralnode_configuration(
                "release_resources_low"
            )
        )
        self.assign_input = self.json_factory.create_centralnode_configuration(
            "assign_resources_low"
        )

    def move_to_off(self):
        """
        A method to invoke TelescopeOff command to
        put telescope in OFF state

        """
        self.central_node.TelescopeOff()
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("sdp_subarray"),
        ]
        for device in device_to_on_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(DevState.OFF)

    @sync_assign_resources(device_dict=device_dict_low)
    def store_resources(self, assign_json: str):
        """Invoke Assign Resource command on central Node
        Args:
            assign_json (str): Assign resource input json
        """
        result, message = self.central_node.AssignResources(assign_json)
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    @sync_release_resources(device_dict=device_dict_low)
    def invoke_release_resources(self, input_string: str):
        """Invoke Release Resource command on central Node
        Args:
            input_string (str): Release resource input json
        """
        result, message = self.central_node.ReleaseResources(input_string)
        return result, message

    @sync_abort(device_dict=device_dict_low)
    def subarray_abort(self):
        """Invoke Abort command on subarray Node"""
        result, message = self.subarray_node.Abort()
        return result, message

    @sync_restart(device_dict=device_dict_low)
    def subarray_restart(self):
        """Invoke Restart command on subarray Node"""
        result, message = self.subarray_node.Restart()
        return result, message

    def _reset_health_state_for_mock_devices(self):
        """Reset Mock devices"""
        super()._reset_health_state_for_mock_devices()
        self.mccs_master.SetDirectHealthState(HealthState.UNKNOWN)

    def tear_down(self):
        """Handle Tear down of central Node"""
        # reset HealthState.UNKNOWN for mock devices
        LOGGER.info("Calling Tear down for central node.")
        self._reset_health_state_for_mock_devices()
        if self.subarray_node.obsState == ObsState.IDLE:
            LOGGER.info("Calling ReleaseResources on CentralNode")
            self.invoke_release_resources(self.release_input)
        elif self.subarray_node.obsState == ObsState.RESOURCING:
            LOGGER.info("Calling Abort and Restart on SubarrayNode")
            self.subarray_abort()
            self.subarray_restart()
        elif self.subarray_node.obsState == ObsState.ABORTED:
            self.subarray_restart()
        self.move_to_off()
