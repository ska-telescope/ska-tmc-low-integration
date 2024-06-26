"""Test Timeout for Configure command for SDP, CSP and MCCS Leaf Nodes."""
import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import (
    INTERMEDIATE_CONFIGURING_STATE_DEFECT,
    low_csp_subarray_leaf_node,
    low_sdp_subarray_leaf_node,
    mccs_subarray_leaf_node,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)


class TestConfigureTimeout:
    """Tests for testing timeout for Configure command on LOW TMC."""

    @pytest.mark.SKA_low
    def test_configure_timeout_csp_ln(
        self,
        subarray_node_low,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """Test timeout on CSP Leaf Nodes for Configure command by inducing
        fault into the system."""
        csp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_DEVICE
        )
        # Event Subscriptions
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "State"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )

        subarray_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "State", DevState.ON
        )

        subarray_node_low.force_change_of_obs_state("IDLE")
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.IDLE
        )

        # Inducing Fault
        csp_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.CONFIGURING
        )

        assertion_data = event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert (
            "Timeout has occurred, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert (
            low_csp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )

    @pytest.mark.SKA_low
    def test_configure_timeout_sdp_ln(
        self,
        subarray_node_low,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """Test timeout on SDP Leaf Nodes for Configure command by inducing
        fault into the system."""
        sdp_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_DEVICE
        )
        # Event Subscriptions
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "State"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        subarray_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "State", DevState.ON
        )

        subarray_node_low.force_change_of_obs_state("IDLE")

        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.IDLE
        )

        # Inducing Fault
        sdp_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.CONFIGURING
        )

        assertion_data = event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert (
            "Timeout has occurred, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert (
            low_sdp_subarray_leaf_node in assertion_data["attribute_value"][1]
        )

    @pytest.mark.SKA_low
    def test_configure_timeout_mccs_ln(
        self,
        subarray_node_low,
        event_recorder,
        simulator_factory,
        command_input_factory,
    ):
        """Test timeout on Mccs Leaf Nodes for Configure command by inducing
        fault into the system."""
        mccs_subarray_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
        )
        # Event Subscriptions
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "State"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "obsState"
        )
        event_recorder.subscribe_event(
            subarray_node_low.subarray_node, "longRunningCommandResult"
        )

        # Preparing input files
        configure_input_str = prepare_json_args_for_commands(
            "configure_low", command_input_factory
        )
        subarray_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "State", DevState.ON
        )

        subarray_node_low.force_change_of_obs_state("IDLE")

        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.IDLE
        )

        # Inducing Fault
        mccs_subarray_sim.SetDefective(INTERMEDIATE_CONFIGURING_STATE_DEFECT)

        _, unique_id = subarray_node_low.execute_transition(
            "Configure", configure_input_str
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node, "obsState", ObsState.CONFIGURING
        )

        assertion_data = event_recorder.has_change_event_occurred(
            subarray_node_low.subarray_node,
            "longRunningCommandResult",
            (unique_id[0], Anything),
        )
        assert (
            "Timeout has occurred, command failed"
            in assertion_data["attribute_value"][1]
        )
        assert mccs_subarray_leaf_node in assertion_data["attribute_value"][1]
