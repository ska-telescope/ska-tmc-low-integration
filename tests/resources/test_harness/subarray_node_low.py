import json
import logging

from ska_ser_logging import configure_logging
from ska_tango_base.control_model import HealthState
from tango import DeviceProxy, DevState

from tests.resources.test_harness.constant import (
    device_dict_low,
    low_centralnode,
    low_csp_master,
    low_csp_subarray1,
    low_csp_subarray_leaf_node,
    low_sdp_master,
    low_sdp_subarray1,
    low_sdp_subarray_leaf_node,
    mccs_subarray1,
    mccs_subarray_leaf_node,
    tmc_low_subarraynode1,
)
from tests.resources.test_harness.helpers import (
    SIMULATED_DEVICES_DICT,
    check_subarray_obs_state,
)
from tests.resources.test_harness.utils.constant import (
    ABORTED,
    IDLE,
    ON,
    READY,
)
from tests.resources.test_harness.utils.enums import SubarrayObsState
from tests.resources.test_harness.utils.obs_state_resetter_low import (
    ObsStateResetterFactoryLow,
)
from tests.resources.test_harness.utils.sync_decorators import (
    sync_abort,
    sync_assign_resources,
    sync_configure,
    sync_end,
    sync_release_resources,
    sync_restart,
)
from tests.resources.test_support.common_utils.common_helpers import Resource

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)

device_dict = {
    # TODO use this as as list when multiple subarray considered in testing
    "sdp_subarray": low_sdp_subarray1,
    "csp_subarray": low_csp_subarray1,
    "csp_master": low_csp_master,
    "tmc_subarraynode": tmc_low_subarraynode1,
    "sdp_master": low_sdp_master,
    "centralnode": low_centralnode,
    "mccs_subarray1": mccs_subarray1,
    "csp_subarray_leaf_node": low_csp_subarray_leaf_node,
    "sdp_subarray_leaf_node": low_sdp_subarray_leaf_node,
    "mccs_subarray_leaf_node": mccs_subarray_leaf_node,
}


class SubarrayNodeWrapperLow:
    """Subarray Node Low class which implement methods required for test cases
    to test subarray node.
    """

    def __init__(self) -> None:
        self.tmc_subarraynode1 = tmc_low_subarraynode1
        self.central_node = DeviceProxy(low_centralnode)
        self.subarray_node = DeviceProxy(tmc_low_subarraynode1)
        self.csp_subarray_leaf_node = DeviceProxy(low_csp_subarray_leaf_node)
        self.sdp_subarray_leaf_node = DeviceProxy(low_sdp_subarray_leaf_node)
        self.mccs_subarray_leaf_node = DeviceProxy(mccs_subarray_leaf_node)
        self._state = DevState.OFF
        self._obs_state = SubarrayObsState.EMPTY
        self.csp_subarray1 = low_csp_subarray1
        self.sdp_subarray1 = low_sdp_subarray1
        self.mccs_subarray1 = mccs_subarray1
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(low_csp_subarray1),
            "sdp_subarray": DeviceProxy(low_sdp_subarray1),
            "mccs_subarray": DeviceProxy(mccs_subarray1),
        }
        # Subarray state
        self.ON_STATE = ON
        self.IDLE_OBS_STATE = IDLE
        self.READY_OBS_STATE = READY
        self.ABORTED_OBS_STATE = ABORTED

    @property
    def state(self) -> DevState:
        """TMC SubarrayNode operational state"""
        self._state = Resource(self.tmc_subarraynode1).get("State")
        return self._state

    @state.setter
    def state(self, value):
        """Sets value for TMC subarrayNode operational state

        Args:
            value (DevState): operational state value
        """
        self._state = value

    @property
    def obs_state(self):
        """TMC SubarrayNode observation state"""
        self._obs_state = Resource(self.tmc_subarraynode1).get("obsState")
        return self._obs_state

    @obs_state.setter
    def obs_state(self, value):
        """Sets value for TMC subarrayNode observation state

        Args:
            value (DevState): observation state value
        """
        self._obs_state = value

    @property
    def health_state(self) -> HealthState:
        """Telescope health state representing overall health of telescope"""
        self._health_state = Resource(self.tmc_subarraynode1).get(
            "healthState"
        )
        return self._health_state

    @health_state.setter
    def health_state(self, value):
        """Telescope health state representing overall health of telescope

        Args:
            value (HealthState): telescope health state value
        """
        self._health_state = value

    @property
    def obs_state(self):
        """TMC SubarrayNode observation state"""
        self._obs_state = Resource(self.tmc_subarraynode1).get("obsState")
        return self._obs_state

    @obs_state.setter
    def obs_state(self, value):
        """Sets value for TMC subarrayNode observation state

        Args:
            value (DevState): observation state value
        """
        self._obs_state = value

    @sync_configure(device_dict=device_dict_low)
    def store_configuration_data(self, input_string: str):
        """Invoke configure command on subarray Node
        Args:
            input_string (str): config input json
        Returns:
            (result, message): result, message tuple
        """
        result, message = self.subarray_node.Configure(input_string)
        LOGGER.info("Invoked Configure on SubarrayNode")
        return result, message

    @sync_end(device_dict=device_dict_low)
    def end_observation(self):
        result, message = self.subarray_node.End()
        LOGGER.info("Invoked End on SubarrayNode")
        return result, message

    @sync_abort(device_dict=device_dict_low)
    def abort_subarray(self):
        result, message = self.subarray_node.Abort()
        LOGGER.info("Invoked Abort on SubarrayNode")
        return result, message

    @sync_restart(device_dict=device_dict_low)
    def restart_subarray(self):
        result, message = self.subarray_node.Restart()
        LOGGER.info("Invoked Restart on SubarrayNode")
        return result, message

    @sync_assign_resources(device_dict=device_dict_low)
    def store_resources(self, assign_json: str):
        """Invoke Assign Resource command on subarray Node
        Args:
            assign_json (str): Assign resource input json
        """
        # This methods needs to change, with subsequent changes in the Tear
        # Down of the fixtures. Will be done as an improvement later.
        result, message = self.central_node.AssignResources(assign_json)
        LOGGER.info("Invoked AssignResources on CentralNode")
        return result, message

    @sync_release_resources(device_dict=device_dict_low)
    def release_resources_subarray(self):
        result, message = self.subarray_node.ReleaseAllResources()
        LOGGER.info("Invoked Release Resource on SubarrayNode")
        return result, message

    def store_scan_data(self, input_string):
        result, message = self.subarray_node.Scan(input_string)
        LOGGER.info("Invoked Scan on SubarrayNode")
        return result, message

    def execute_transition(self, command_name: str, argin=None):
        """Execute provided command on subarray
        Args:
            command_name (str): Name of command to execute
        """
        if command_name is not None:
            result, message = self.subarray_node.command_inout(
                command_name, argin
            )
            LOGGER.info(f"Invoked {command_name} on SubarrayNode")
            return result, message

    def move_to_on(self):
        # Move subarray to ON state
        if self.state != self.ON_STATE:
            Resource(self.tmc_subarraynode1).assert_attribute("State").equals(
                "OFF"
            )
            result, message = self.subarray_node.On()
            LOGGER.info("Invoked ON on SubarrayNode")
            return result, message

    def move_to_off(self):
        # Move Subarray to OFF state
        Resource(self.tmc_subarraynode1).assert_attribute("State").equals("ON")
        result, message = self.subarray_node.Off()
        LOGGER.info("Invoked OFF on SubarrayNode")
        return result, message

    def _reset_simulator_devices(self):
        """Reset Simulator devices to it's original state"""
        if (
            SIMULATED_DEVICES_DICT["csp_and_sdp"]
            or SIMULATED_DEVICES_DICT["all_mocks"]
        ):
            sim_device_fqdn_list = [self.sdp_subarray1, self.csp_subarray1]
        elif SIMULATED_DEVICES_DICT["csp_and_mccs"]:
            sim_device_fqdn_list = [self.csp_subarray1]
        elif SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            sim_device_fqdn_list = [self.sdp_subarray1]
        for sim_device_fqdn in sim_device_fqdn_list:
            device = DeviceProxy(sim_device_fqdn)
            device.ResetDelay()
            device.SetDirectHealthState(HealthState.UNKNOWN)
            device.SetDefective(json.dumps({"enabled": False}))

    def set_subarray_id(self, subarray_id):
        self.subarray_node = DeviceProxy(
            f"ska_low/tm_subarray_node/{subarray_id}"
        )
        subarray_id = "{:02d}".format(int(subarray_id))
        self.subarray_devices = {
            "csp_subarray": DeviceProxy(f"low-csp/subarray/{subarray_id}"),
            "sdp_subarray": DeviceProxy(f"low-sdp/subarray/{subarray_id}"),
            "mccs_subarray": DeviceProxy(f"low-mccs/subarray/{subarray_id}"),
        }
        self.csp_subarray_leaf_node = DeviceProxy(
            f"ska_low/tm_leaf_node/csp_subarray{subarray_id}"
        )
        self.sdp_subarray_leaf_node = DeviceProxy(
            f"ska_low/tm_leaf_node/sdp_subarray{subarray_id}"
        )
        self.mccs_subarray_leaf_node = DeviceProxy(
            f"ska_low/tm_leaf_node/mccs_subarray{subarray_id}"
        )

    def force_change_of_obs_state(
        self,
        dest_state_name: str,
        assign_input_json: str = "",
        configure_input_json: str = "",
        scan_input_json: str = "",
    ) -> None:
        """Forces a change in the SubarrayNode's obsState to the provided
          obsState.
        This method creates an ObsStateResetter object using the provided
        destination obsState name and resets the SubarrayNode's state
        accordingly.
        Args:
            dest_state_name (str): The destination obsState to set for the
              SubarrayNode.
            assign_input_json (str, optional): JSON input for assignment
            configuration.
            Defaults to an empty string.
            configure_input_json (str, optional): JSON input for configuration
             settings.
            Defaults to an empty string.
            scan_input_json (str, optional): JSON input for scan configuration.
                Defaults to an empty string.
        Returns:
            None: This method does not return any value.
        Raises:
            Any specific exceptions that might be raised during the reset
            process.
        """
        factory_obj = ObsStateResetterFactoryLow()
        obs_state_resetter = factory_obj.create_obs_state_resetter(
            dest_state_name, self
        )
        if assign_input_json:
            obs_state_resetter.assign_input = assign_input_json
        if configure_input_json:
            obs_state_resetter.configure_input = configure_input_json
        if scan_input_json:
            obs_state_resetter.scan_input = scan_input_json
        obs_state_resetter.reset()
        self._clear_command_call_and_transition_data()

    def clear_all_data(self):
        """Method to clear the observations
        and put the SubarrayNode in EMPTY"""
        if self.obs_state in [
            "IDLE",
            "RESOURCING",
            "READY",
            "CONFIGURING",
            "SCANNING",
        ]:
            self.abort_subarray()
            self.restart_subarray()
        elif self.obs_state == "ABORTED":
            self.restart_subarray()

    def _clear_command_call_and_transition_data(self, clear_transition=False):
        """Clears the command call data"""
        if SIMULATED_DEVICES_DICT["csp_and_sdp"]:
            for sim_device in [
                self.sdp_subarray1,
                self.csp_subarray1,
                self.mccs_subarray1,
            ]:
                device = DeviceProxy(sim_device)
                device.ClearCommandCallInfo()
                if clear_transition:
                    device.ResetTransitions()
        elif SIMULATED_DEVICES_DICT["csp_and_mccs"]:
            for sim_device in [
                self.csp_subarray1,
                mccs_subarray1,
            ]:
                device = DeviceProxy(sim_device)
                device.ClearCommandCallInfo()
                if clear_transition:
                    device.ResetTransitions()
        elif SIMULATED_DEVICES_DICT["sdp_and_mccs"]:
            for sim_device in [
                self.sdp_subarray1,
                mccs_subarray1,
            ]:
                device = DeviceProxy(sim_device)
                device.ClearCommandCallInfo()
                if clear_transition:
                    device.ResetTransitions()
        elif SIMULATED_DEVICES_DICT["all_mocks"]:
            for sim_device in [
                self.sdp_subarray1,
                self.csp_subarray1,
                mccs_subarray1,
            ]:
                device = DeviceProxy(sim_device)
                device.ClearCommandCallInfo()
                if clear_transition:
                    device.ResetTransitions()
        else:
            LOGGER.info("Devices deployed are real")

    def tear_down(self):
        """Tear down after each test run"""

        LOGGER.info("Calling Tear down for subarray")
        self._clear_command_call_and_transition_data(clear_transition=True)

        if self.obs_state in ("RESOURCING", "CONFIGURING", "SCANNING"):
            """Invoke Abort and Restart"""
            LOGGER.info("Invoking Abort on Subarray")
            self.abort_subarray()
            self.restart_subarray()
        elif self.obs_state == "ABORTED":
            """Invoke Restart"""
            LOGGER.info("Invoking Restart on Subarray")
            self.restart_subarray()
        else:
            self.force_change_of_obs_state("EMPTY")

        # Move Subarray to OFF state
        self.move_to_off()
        self._reset_simulator_devices()
        assert check_subarray_obs_state("EMPTY")
