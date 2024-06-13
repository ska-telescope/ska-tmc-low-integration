"""Test cases for AssignResources Command not allowed for LOW."""
import pytest
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import (
    COMMAND_NOT_ALLOWED_DEFECT,
    low_sdp_subarray_leaf_node,
    mccs_master_leaf_node,
)
from tests.resources.test_harness.helpers import check_for_device_event
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


class TestAssignCommandNotAllowedPropagation:
    """Test the command not allowed error propagation for the assign resources
    command for TMC."""

    @pytest.mark.SKA_low
    def test_assign_command_not_allowed_propagation_csp_ln_low(
        self,
        central_node_low,
        event_recorder,
        command_input_factory,
        simulator_factory,
    ):
        """Verify command not allowed exception propagation from CSPLeafNodes
        ."""
        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )

        # Event Subscriptions
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_recorder.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )

        # Preparing input arguments
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )

        central_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )

        # Setting Defects on Devices
        csp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)

        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )

        ERROR_MESSAGE = (
            "The invocation of the AssignResources command is "
            + "failed on Csp Subarray Device low-csp/subarray/01"
        )
        assert check_for_device_event(
            central_node_low.central_node,
            "longRunningCommandResult",
            ERROR_MESSAGE,
            event_recorder,
            unique_id=unique_id[0],
        )
        event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.FAILED.value)),
        )

    @pytest.mark.SKA_low
    def test_assign_command_not_allowed_propagation_sdp_ln_low(
        self,
        central_node_low,
        event_recorder,
        command_input_factory,
        simulator_factory,
    ):
        """Verify command not allowed exception propagation from SDPLeafNodes
        ."""
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )

        # Event Subscriptions
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_recorder.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_recorder.subscribe_event(sdp_subarray_sim, "obsState")
        # Preparing input arguments
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )

        central_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )

        # Setting Defects on Devices
        sdp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        ERROR_MESSAGE = (
            "Exception occurred on the following devices:"
            + f" {low_sdp_subarray_leaf_node}:"
            " ska_tmc_common.exceptions.CommandNotAllowed:"
            " Command is not allowed\n\n"
        )
        assertion_data = event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert ERROR_MESSAGE in assertion_data["attribute_value"][1]
        event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.FAILED.value)),
        )

    @pytest.mark.SKA_low
    def test_assign_command_not_allowed_propagation_mccs_ln_low(
        self,
        central_node_low,
        event_recorder,
        command_input_factory,
        simulator_factory,
    ):
        """Verify command not allowed exception propagation
        from MccsLeafNodes."""
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        mccs_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )

        # Event Subscriptions
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        event_recorder.subscribe_event(
            central_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            central_node_low.central_node, "longRunningCommandResult"
        )
        event_recorder.subscribe_event(mccs_subarray_sim, "obsState")
        # Preparing input arguments
        assign_input_json = prepare_json_args_for_centralnode_commands(
            "assign_resources_low", command_input_factory
        )

        central_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )

        # Setting Defects on Devices
        mccs_master_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)
        # Execute Assign command and verify successful execution
        _, unique_id = central_node_low.perform_action(
            "AssignResources", assign_input_json
        )
        # Constructing the error message
        assertion_data = event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert (
            "Exception occurred on the following devices:"
            + f" {mccs_master_leaf_node}:"
            in assertion_data["attribute_value"][1]
        )
        assert (
            "ska_tmc_common.exceptions.CommandNotAllowed"
            in assertion_data["attribute_value"][1]
        )
        event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], str(ResultCode.FAILED.value)),
        )
