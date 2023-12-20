import logging
import os

from ska_control_model import ObsState
from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

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
    sync_release_resources,
    sync_restart,
)

# sync_assign_resources,
from tests.resources.test_support.common_utils.common_helpers import Resource

SDP_SIMULATION_ENABLED = os.getenv("SDP_SIMULATION_ENABLED")
CSP_SIMULATION_ENABLED = os.getenv("CSP_SIMULATION_ENABLED")
MCCS_SIMULATION_ENABLED = os.getenv("MCCS_SIMULATION_ENABLED")
configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class CentralNodeWrapperLow(object):
    """A wrapper class to implement common tango specific details
    and standard set of commands for TMC Low CentralNode,
    defined by the SKA Control Model."""

    def __init__(self) -> None:
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
        self.simulated_devices_dict = self.get_simulated_devices_info()
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

    @property
    def state(self) -> DevState:
        """TMC Low CentralNode operational state"""
        self._state = Resource(self.central_node).get("State")
        return self._state

    @state.setter
    def state(self, value):
        """Sets value for TMC CentralNode operational state

        Args:
            value (DevState): operational state value
        """
        self._state = value

    @property
    def telescope_health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        self._telescope_health_state = Resource(self.central_node).get(
            "telescopeHealthState"
        )
        return self._telescope_health_state

    @telescope_health_state.setter
    def telescope_health_state(self, value):
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        self._telescope_health_state = value

    @property
    def telescope_state(self) -> DevState:
        """Telescope state representing overall state of telescope"""

        self._telescope_state = Resource(self.central_node).get(
            "telescopeState"
        )
        return self._telescope_state

    @telescope_state.setter
    def telescope_state(self, value):
        """Telescope state representing overall state of telescope

        Args:
            value (DevState): telescope state value
        """
        self._telescope_state = value

    # def move_to_on(self):
    #     """
    #     A method to invoke TelescopeOn command to
    #     put telescope in ON state
    #     """
    #     LOGGER.info("Starting up the Telescope")
    #     self.central_node.TelescopeOn()
    #     device_to_on_list = [
    #         self.subarray_devices.get("csp_subarray"),
    #         self.subarray_devices.get("sdp_subarray"),
    #         self.subarray_devices.get("mccs_subarray"),
    #     ]
    #     for device in device_to_on_list:
    #         device_proxy = DeviceProxy(device)
    #         device_proxy.SetDirectState(DevState.ON)

    # def set_standby(self):
    #     """
    #     A method to invoke TelescopeStandby command to
    #     put telescope in STANDBY state

    #     """
    #     self.central_node.TelescopeStandBy()
    #     device_to_on_list = [
    #         self.subarray_devices.get("csp_subarray"),
    #         self.subarray_devices.get("sdp_subarray"),
    #         self.subarray_devices.get("mccs_subarray"),
    #     ]
    #     for device in device_to_on_list:
    #         device_proxy = DeviceProxy(device)
    #         device_proxy.SetDirectState(DevState.STANDBY)

    def move_to_off(self):
        """
        A method to invoke TelescopeOff command to
        put telescope in OFF state

        """
        self.central_node.TelescopeOff()
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(DevState.OFF)

    # @sync_assign_resources(device_dict=device_dict_low)
    # def store_resources(self, assign_json: str):
    #     """Invoke Assign Resource command on central Node
    #     Args:
    #         assign_json (str): Assign resource input json
    #     """
    #     result, message = self.central_node.AssignResources(assign_json)
    #     LOGGER.info("Invoked AssignResources on CentralNode")
    #     return result, message

    # @sync_release_resources(device_dict=device_dict_low)
    # def invoke_release_resources(self, input_string: str):
    #     """Invoke Release Resource command on central Node
    #     Args:
    #         input_string (str): Release resource input json
    #     """
    #     result, message = self.central_node.ReleaseResources(input_string)
    #     return result, message

    # @sync_abort(device_dict=device_dict_low)
    # def subarray_abort(self):
    #     """Invoke Abort command on subarray Node"""
    #     result, message = self.subarray_node.Abort()
    #     return result, message

    # @sync_restart(device_dict=device_dict_low)
    # def subarray_restart(self):
    #     """Invoke Restart command on subarray Node"""
    #     result, message = self.subarray_node.Restart()
    #     return result, message

    # def _reset_health_state_for_mock_devices(self):
    #     """Reset Mock devices"""

    #     for mock_device in [
    #         self.sdp_master,
    #         self.csp_master,
    #         self.mccs_master,
    #     ]:
    #         device = DeviceProxy(mock_device)
    #         device.SetDirectHealthState(HealthState.UNKNOWN)

    # def perform_action(self, command_name: str, input_json: str):
    #     """Execute provided command on centralnode
    #     Args:
    #         command_name (str): Name of command to execute
    #         input_json (str): Json send as input to execute command
    #     """

    #     result, message = self.central_node.command_inout(
    #         command_name, input_json
    #     )
    #     return result, message

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

    def move_to_on(self):
        """
        A method to invoke TelescopeOn command to
        put telescope in ON state
        """
        LOGGER.info("Starting up the Telescope")
        LOGGER.info(
            f"Received simulated devices: {self.simulated_devices_dict}"
        )
        if self.simulated_devices_dict["all_mocks"]:
            LOGGER.info("Invoking commands with all Mocks")
            self.central_node.TelescopeOn()
            self.set_values_with_all_mocks(DevState.ON)

        elif self.simulated_devices_dict["csp_and_sdp"]:
            LOGGER.info("Invoking command with csp and sdp simulated")
            self.central_node.TelescopeOn()
            self.set_value_with_csp_sdp_mocks(DevState.ON)

        elif self.simulated_devices_dict["csp_and_mccs"]:
            LOGGER.info("Invoking command with csp and MCCS simulated")
            self.central_node.TelescopeOn()
            self.set_values_with_csp_mccs_mocks(DevState.ON)

        elif self.simulated_devices_dict["sdp_and_mccs"]:
            LOGGER.info("Invoking command with sdp and mccss simulated")
            self.central_node.TelescopeOn()
            self.set_values_with_sdp_mccs_mocks(DevState.ON)
        else:
            LOGGER.info("Invoke command with all real sub-systems")
            self.central_node.TelescopeOn()

    def set_standby(self):
        """
        A method to invoke TelescopeStandby command to
        put telescope in STANDBY state

        """
        LOGGER.info("Putting Telescope in Standby state")
        if self.simulated_devices_dict["all_mocks"]:
            LOGGER.info("Invoking commands with all Mocks")
            self.central_node.TelescopeStandBy()
            self.set_values_with_all_mocks(DevState.STANDBY)

        elif self.simulated_devices_dict["csp_and_sdp"]:
            LOGGER.info("Invoking command with csp and sdp simulated")
            self.central_node.TelescopeStandBy()
            self.set_value_with_csp_sdp_mocks(DevState.STANDBY)

        elif self.simulated_devices_dict["csp_and_mccs"]:
            LOGGER.info("Invoking command with csp and mccs simulated")
            self.central_node.TelescopeStandBy()
            self.set_values_with_csp_mccs_mocks(DevState.STANDBY)

        elif self.simulated_devices_dict["sdp_and_mccs"]:
            LOGGER.info("Invoking command with sdp and mccs simulated")
            self.central_node.TelescopeStandBy()
            self.set_values_with_sdp_mccs_mocks(DevState.STANDBY)
        else:
            LOGGER.info("Invoke command with all real sub-systems")
            self.central_node.TelescopeStandBy()

    @sync_release_resources(device_dict=device_dict_low)
    def invoke_release_resources(self, input_string):
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
        if (
            self.simulated_devices_dict["csp_and_sdp"]
            or self.simulated_devices_dict["all_mocks"]
        ):
            for mock_device in [
                self.sdp_master,
                self.csp_master,
            ]:
                device = DeviceProxy(mock_device)
                device.SetDirectHealthState(HealthState.UNKNOWN)
        elif self.simulated_devices_dict["csp_and_mccs"]:
            for mock_device in [
                self.csp_master,
            ]:
                device = DeviceProxy(mock_device)
                device.SetDirectHealthState(HealthState.UNKNOWN)
        elif self.simulated_devices_dict["sdp_and_mccs"]:
            for mock_device in [
                self.sdp_master,
            ]:
                device = DeviceProxy(mock_device)
                device.SetDirectHealthState(HealthState.UNKNOWN)
        else:
            LOGGER.info("No devices to reset healthState")

    def perform_action(self, command_name: str, input_json: str):
        """Execute provided command on centralnode
        Args:
            command_name (str): Name of command to execute
            input_json (str): Json send as input to execute command
        """

        result, message = self.central_node.command_inout(
            command_name, input_json
        )
        return result, message

    def set_values_with_all_mocks(self, subarray_state):
        """
        A method to set values on mock CSP, SDP and MCCS devices.
        Args:
            subarray_state: DevState - subarray state value for
                                        CSP and SDP Subarrays
        """
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(subarray_state)

    def set_value_with_csp_sdp_mocks(self, subarray_state):
        """
        A method to set values on mock CSP and SDP devices.
        Args:
            subarray_state: DevState - subarray state value for
                                    CSP and SDP Subarrays
        """
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("sdp_subarray"),
        ]
        for device in device_to_on_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(subarray_state)

    def set_values_with_csp_mccs_mocks(self, subarray_state):
        """
        A method to set values on mock CSP and MCCS devices.
        Args:
            subarray_state: DevState - subarray state value for
                                    CSP Subarray
        """
        device_to_on_list = [
            self.subarray_devices.get("csp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(subarray_state)

    def set_values_with_sdp_mccs_mocks(self, subarray_state):
        """
        A method to set values on mock SDP and MCCS devices.
        Args:
            subarray_state: DevState - subarray state value for
                                    SDP Subarray
        """
        device_to_on_list = [
            self.subarray_devices.get("sdp_subarray"),
            self.subarray_devices.get("mccs_subarray"),
        ]
        for device in device_to_on_list:
            device_proxy = DeviceProxy(device)
            device_proxy.SetDirectState(subarray_state)

    def get_simulated_devices_info(self) -> dict:
        """
        A method to get simulated devices present in the deployement.

        return: dict
        """
        self.is_csp_simulated = CSP_SIMULATION_ENABLED.lower() == "true"
        self.is_sdp_simulated = SDP_SIMULATION_ENABLED.lower() == "true"
        self.is_mccs_simulated = MCCS_SIMULATION_ENABLED.lower() == "true"
        return {
            "csp_and_sdp": all(
                [self.is_csp_simulated, self.is_sdp_simulated]
            ),  # real MCCS enabled
            "csp_and_mccs": all(
                [self.is_csp_simulated, self.is_mccs_simulated]
            ),  # real SDP enabled
            "sdp_and_mccs": all(
                [self.is_sdp_simulated, self.is_mccs_simulated]
            ),  # real CSP.LMC enabled
            "all_mocks": all(
                [
                    self.is_csp_simulated,
                    self.is_sdp_simulated,
                    self.is_mccs_simulated,
                ]
            ),
        }
