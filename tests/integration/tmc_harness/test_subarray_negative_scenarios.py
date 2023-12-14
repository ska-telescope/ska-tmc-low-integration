"""Implement negative scenario test cases for subarray
"""
import json

import pytest
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.constant import INTERMEDIATE_STATE_DEFECT
from tests.resources.test_harness.helpers import (
    device_received_this_command,
    get_recorded_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType


class TestSubarrayNodeNegative(object):
    @pytest.mark.skip
    @pytest.mark.SKA_mid
    def test_subarray_assign_csp_unresponsive(
        self,
        subarray_node,
        command_input_factory,
        simulator_factory,
        event_recorder,
    ):
        input_json = prepare_json_args_for_commands(
            "assign_resources_mid", command_input_factory
        )
        csp_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MID_CSP_DEVICE
        )
        # Subscribe for long running command result attribute
        # so that error message from subarray can be validated
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "longRunningCommandResult"
        )

        subarray_node.move_to_on()

        subarray_node.force_change_of_obs_state("EMPTY")

        # Set csp defective and execute configure command
        csp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

        _, unique_id = subarray_node.execute_transition(
            "AssignResources", argin=input_json
        )

        exception_message = (
            "Exception occured on device"
            ": ska_mid/tm_leaf_node/csp_subarray01: Timeout has "
            "occured, command failed"
        )

        expected_long_running_command_result = (
            unique_id[0],
            exception_message,
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "longRunningCommandResult",
            expected_long_running_command_result,
        )

    @pytest.mark.SKA_mid
    def test_subarray_configure_when_csp_stuck_in_configuring(
        self,
        subarray_node,
        command_input_factory,
        simulator_factory,
        event_recorder,
    ):
        input_json = prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        )
        csp_input_json = prepare_json_args_for_commands(
            "csp_configure_mid", command_input_factory
        )
        csp_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MID_CSP_DEVICE
        )

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
        event_recorder.subscribe_event(csp_sim, "commandCallInfo")
        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state("IDLE")

        # CSP should go to configuring in no more than 0.1 sec
        obs_state_duration_params = '[["CONFIGURING",0.1]]'
        csp_sim.AddTransition(obs_state_duration_params)

        subarray_node.execute_transition("Configure", argin=input_json)

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", ObsState.CONFIGURING
        )

        with pytest.raises(AssertionError):
            assert event_recorder.has_change_event_occurred(
                subarray_node.subarray_node, "obsState", ObsState.READY
            )

        # Add assert for commandCallInfo data
        assert device_received_this_command(
            csp_sim, "Configure", csp_input_json
        )

    @pytest.mark.SKA_mid
    def test_subarray_configure_when_sdp_stuck_in_configuring(
        self,
        subarray_node,
        command_input_factory,
        simulator_factory,
        event_recorder,
    ):
        input_json = prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        )
        sdp_input_json = prepare_json_args_for_commands(
            "sdp_configure_mid", command_input_factory
        )
        sdp_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MID_SDP_DEVICE
        )

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
        event_recorder.subscribe_event(sdp_sim, "commandCallInfo")
        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state("IDLE")

        # SDP should go to configuring in no more than 0.1 sec
        obs_state_duration_params = '[["CONFIGURING",0.1]]'
        sdp_sim.AddTransition(obs_state_duration_params)

        subarray_node.execute_transition("Configure", argin=input_json)

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", ObsState.CONFIGURING
        )
        with pytest.raises(AssertionError):
            assert event_recorder.has_change_event_occurred(
                subarray_node.subarray_node, "obsState", ObsState.READY
            )
        assert device_received_this_command(
            sdp_sim, "Configure", sdp_input_json
        )
        assert len(get_recorded_commands(sdp_sim)) == 1

    @pytest.mark.skip(reason="ResetTransitions error")
    @pytest.mark.SKA_mid
    def test_subarray_configure_when_dish_stuck_in_slew(
        self,
        subarray_node,
        command_input_factory,
        simulator_factory,
        event_recorder,
    ):
        input_json = prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        )
        dish_input_json = prepare_json_args_for_commands(
            "dish_configure_mid", command_input_factory
        )
        dish_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.DISH_DEVICE
        )

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state("IDLE")

        # Dish master should go to slew in no more than 0.1 sec
        pointing_state_duration_params = '[["SLEW",0.1]]'
        dish_sim.AddTransition(pointing_state_duration_params)

        subarray_node.execute_transition("Configure", argin=input_json)

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", ObsState.CONFIGURING
        )
        with pytest.raises(AssertionError):
            assert event_recorder.has_change_event_occurred(
                subarray_node.subarray_node, "obsState", ObsState.READY
            )
        assert device_received_this_command(
            dish_sim, "ConfigureBand2", dish_input_json
        )

    @pytest.mark.skip(reason="Random failure")
    @pytest.mark.SKA_mid
    def test_subarray_configure_when_csp_goes_to_fault_then_ready(
        self,
        subarray_node,
        command_input_factory,
        simulator_factory,
        event_recorder,
    ):
        input_json = prepare_json_args_for_commands(
            "configure_mid", command_input_factory
        )
        csp_input_json = prepare_json_args_for_commands(
            "csp_configure_mid", command_input_factory
        )
        csp_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MID_CSP_DEVICE
        )

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")
        event_recorder.subscribe_event(csp_sim, "obsState")
        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state("IDLE")

        # CSP should go to configuring in no more than 0.1 sec
        obs_state_duration_params = '[["FAULT",0.1],["READY",0.1]]'
        csp_sim.AddTransition(obs_state_duration_params)

        subarray_node.execute_transition("Configure", argin=input_json)

        assert event_recorder.has_change_event_occurred(
            csp_sim, "obsState", ObsState.FAULT
        )
        assert event_recorder.has_change_event_occurred(
            csp_sim, "obsState", ObsState.READY
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", ObsState.CONFIGURING
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", ObsState.READY
        )
        assert device_received_this_command(
            csp_sim, "Configure", csp_input_json
        )
