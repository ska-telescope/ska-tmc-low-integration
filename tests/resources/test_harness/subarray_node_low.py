import logging

from ska_ser_logging import configure_logging
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
    mccs_subarray_leaf_node,
    tmc_low_subarraynode1,
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
        self.obs_state = SubarrayObsState.EMPTY
        self.csp_subarray1 = low_csp_subarray1
        self.sdp_subarray1 = low_sdp_subarray1
        # Subarray state
        self.ON_STATE = ON
        self.IDLE_OBS_STATE = IDLE
        self.READY_OBS_STATE = READY
        self.ABORTED_OBS_STATE = ABORTED

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

    def execute_transition(self, command_name: str, argin=None):
        """Execute provided command on subarray
        Args:
            command_name (str): Name of command to execute
        """
        # This methods needs to change, with subsequent changes in the Tear
        # Down of the fixtures. Will be done as an improvement later.
        if command_name == "AssignResources":
            result, message = self.central_node.AssignResources(argin)
            LOGGER.info("Invoked Assign Resource on CentralNode")
            return result, message
        else:
            return super().execute_transition(command_name, argin)

    def force_change_of_obs_state(self, dest_state_name: str) -> None:
        """Force SubarrayNode obsState to provided obsState

        Args:
            dest_state_name (str): Destination obsState
        """
        factory_obj = ObsStateResetterFactoryLow()
        obs_state_resetter = factory_obj.create_obs_state_resetter(
            dest_state_name, self
        )
        obs_state_resetter.reset()
        self._clear_command_call_and_transition_data()

    def _clear_command_call_and_transition_data(self, clear_transition=False):
        """Clears the command call data"""
        for sim_device in [
            low_sdp_subarray1,
        ]:
            device = DeviceProxy(sim_device)
            device.ClearCommandCallInfo()
            if clear_transition:
                device.ResetTransitions()

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
