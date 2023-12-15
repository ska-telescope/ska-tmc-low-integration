import pytest
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import prepare_json_args_for_commands


class TestSubarrayConfigure:
    """This class implement test cases to validate obsState of sub array"""

    @pytest.mark.real_csp
    @pytest.mark.parametrize(
        "source_obs_state, trigger, args_for_command,\
        intermediate_obs_state, destination_obs_state",
        [
            (
                "IDLE",
                "Configure",
                "configure_low",
                ObsState.CONFIGURING,
                ObsState.READY,
            ),
        ],
    )
    @pytest.mark.real_csp
    def test_subarray_low_configure(
        self,
        subarray_node_real_csp_low,
        central_node_real_csp_low,
        command_input_factory,
        event_recorder,
        source_obs_state,
        trigger,
        args_for_command,
        intermediate_obs_state,
        destination_obs_state,
    ):
        """This test case validate pair of transition triggered by command"""
        central_node_real_csp_low.move_to_on()

        input_json = prepare_json_args_for_commands(
            args_for_command, command_input_factory
        )
        event_recorder.subscribe_event(
            subarray_node_real_csp_low.subarray_node, "obsState"
        )
        central_node_real_csp_low.set_serial_number_of_cbf_processor()

        central_node_real_csp_low.store_resources(
            central_node_real_csp_low.assign_input
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_real_csp_low.subarray_node, "obsState", ObsState.IDLE
        )
        subarray_node_real_csp_low.execute_transition(
            trigger, argin=input_json
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node_real_csp_low.subarray_node,
            "obsState",
            intermediate_obs_state,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node_real_csp_low.subarray_node,
            "obsState",
            destination_obs_state,
        )
        subarray_node_real_csp_low.end_observation()

        assert event_recorder.has_change_event_occurred(
            subarray_node_real_csp_low.subarray_node, "obsState", ObsState.IDLE
        )
        central_node_real_csp_low.invoke_release_resources(
            central_node_real_csp_low.release_input
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node_real_csp_low.subarray_node,
            "obsState",
            ObsState.EMPTY,
        )
