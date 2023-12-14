import pytest
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import (
    check_subarray_obs_state,
    device_received_this_command,
    get_device_simulators,
    get_recorded_commands,
    prepare_json_args_for_commands,
)


class TestSubarrayNodeObsStateTransitions(object):
    """This class implement test cases to validate obs state of sub array"""

    @pytest.mark.parametrize(
        "source_obs_state, trigger, destination_obs_state",
        [
            ("ABORTED", "Restart", "EMPTY"),
            ("READY", "End", "IDLE"),
        ],
    )
    @pytest.mark.skip(reason="Configure issue")
    @pytest.mark.SKA_mid
    def test_subarray_obs_transitions_valid_data(
        self,
        subarray_node,
        simulator_factory,
        source_obs_state,
        trigger,
        destination_obs_state,
    ):
        """
        Test to verify transitions that are triggered by a command
        and followed by a completion transition, or
        individual transitions that start with a transient state.
        assuming that external subsystems work fine.
        Glossary:
        - "subarray_node": fixture for a TMC SubarrayNode under test
        - "simulator_factory": fixture for SimulatorFactory class,
        which provides simulated subarray and master devices
        - "source_obs_state": a TMC SubarrayNode initial allowed obsState,
           required for triggered a command
        - "trigger": a command name
        - "destination_obs_state": a TMC SubarrayNode final obsState,
           representing a successful completion of triggered command
        """
        csp_sim, sdp_sim, dish_sim_1, dish_sim_2 = get_device_simulators(
            simulator_factory
        )

        obs_state_transition_duration_sec = 30

        delay_command_params_str = '{"%s": %s}' % (
            trigger,
            obs_state_transition_duration_sec,
        )

        sdp_sim.setDelay(delay_command_params_str)
        csp_sim.setDelay(delay_command_params_str)
        dish_sim_1.setDelay(delay_command_params_str)
        dish_sim_2.setDelay(delay_command_params_str)

        subarray_node.move_to_on()

        subarray_node.force_change_of_obs_state(source_obs_state)

        subarray_node.execute_transition(trigger)

        # As we set Obs State transition duration to 30 so wait timeout here
        # provided as 32 sec. It validate after 32 sec excepted
        # obs state change
        expected_timeout_sec = obs_state_transition_duration_sec + 2

        assert check_subarray_obs_state(
            obs_state=destination_obs_state, timeout=expected_timeout_sec
        )

    @pytest.mark.SKA_mid
    @pytest.mark.parametrize(
        "source_obs_state, trigger, args_for_command,\
            intermediate_obs_state, destination_obs_state,\
            args_for_csp, args_for_sdp",
        [
            (
                "IDLE",
                "Configure",
                "configure_mid",
                ObsState.CONFIGURING,
                ObsState.READY,
                "csp_configure_mid",
                "sdp_configure_mid",
            ),
            (
                "EMPTY",
                "AssignResources",
                "assign_resources_mid",
                ObsState.RESOURCING,
                ObsState.IDLE,
                "csp_assign_resources_mid",
                "sdp_assign_resources_mid",
            ),
            (
                "READY",
                "Scan",
                "scan_mid",
                ObsState.SCANNING,
                ObsState.READY,
                "csp_scan_mid",
                "sdp_scan_mid",
            ),
        ],
    )
    @pytest.mark.SKA_mid
    def test_subarray_pair_transition(
        self,
        subarray_node,
        command_input_factory,
        simulator_factory,
        event_recorder,
        source_obs_state,
        trigger,
        args_for_command,
        intermediate_obs_state,
        destination_obs_state,
        args_for_csp,
        args_for_sdp,
    ):
        """This test case validate pair of transition triggered by command"""
        input_json = prepare_json_args_for_commands(
            args_for_command, command_input_factory
        )
        csp_input_json = prepare_json_args_for_commands(
            args_for_csp, command_input_factory
        )
        sdp_input_json = prepare_json_args_for_commands(
            args_for_sdp, command_input_factory
        )

        csp_sim, sdp_sim, _, _ = get_device_simulators(simulator_factory)

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
        event_recorder.subscribe_event(csp_sim, "commandCallInfo")
        event_recorder.subscribe_event(sdp_sim, "commandCallInfo")

        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state(source_obs_state)

        subarray_node.execute_transition(trigger, argin=input_json)

        # Validate subarray node goes into CONFIGURING obs state first
        # This assertion fail if obsState attribute value is not
        # changed to CONFIGURING within 7 events for obsState of subarray node
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", intermediate_obs_state
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", destination_obs_state
        )
        assert device_received_this_command(sdp_sim, trigger, sdp_input_json)
        assert device_received_this_command(csp_sim, trigger, csp_input_json)
        assert len(get_recorded_commands(csp_sim)) == 1
        assert len(get_recorded_commands(sdp_sim)) == 1
