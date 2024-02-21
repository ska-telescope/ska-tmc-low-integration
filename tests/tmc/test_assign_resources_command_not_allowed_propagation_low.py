"""Test cases for AssignResources Command not allowed for LOW."""
import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import COMMAND_NOT_ALLOWED_DEFECT
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


class TestAssignCommandNotAllowedPropagation:
    """Test the command not allowed error propagation for the assign resources
    command for TMC."""

    # TODO: Add test for MCCS after Error Propagation is updated in Subarray
    # Node to function for MCCS Devices
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
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        # Event Subscriptions
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
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
        csp_subarray_sim.SetDefective(COMMAND_NOT_ALLOWED_DEFECT)

        _, unique_id = central_node_low.store_resources(assign_input_json)

        ERROR_MESSAGE = (
            "The invocation of the AssignResources command is "
            + "failed on Csp Subarray Device low-csp/subarray/01"
        )
        assertion_data = event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert ERROR_MESSAGE in assertion_data["attribute_value"][1]

        # Manually setting the obsState to EMPTY to circumvent the Restart
        # command bug. Will be removed once the Bug is fixed under HM-371
        mccs_subarray_sim.SetDirectObsState(ObsState.EMPTY)
        assert event_recorder.has_change_event_occurred(
            mccs_subarray_sim,
            "obsState",
            ObsState.EMPTY,
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
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )

        # Event Subscriptions
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
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
        sdp_subarray_sim.SetDirectObsState(ObsState.RESOURCING)

        _, unique_id = central_node_low.store_resources(assign_input_json)

        ERROR_MESSAGE = (
            "ska_tmc_common.exceptions.InvalidObsStateError: AssignResources "
            + "command is not allowed in current observation state on device"
        )
        assertion_data = event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert ERROR_MESSAGE in assertion_data["attribute_value"][1]
        # Revert Defects on Devices
        sdp_subarray_sim.SetDirectObsState(ObsState.EMPTY)

        # Manually setting the obsState to EMPTY to circumvent the Restart
        # command bug. Will be removed once the Bug is fixed under HM-371
        mccs_subarray_sim.SetDirectObsState(ObsState.EMPTY)
        assert event_recorder.has_change_event_occurred(
            mccs_subarray_sim,
            "obsState",
            ObsState.EMPTY,
        )
