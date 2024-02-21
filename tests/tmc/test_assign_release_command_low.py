"""Test cases for AssignResources and ReleaseResources
 Command for low"""
import json

import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.constant import (
    COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY,
)
from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.constant_low import INTERMEDIATE_STATE_DEFECT


@pytest.mark.SKA_low
def test_assign_release_defective_csp(
    central_node_low,
    event_recorder,
    simulator_factory,
    command_input_factory,
):
    """Verify defective exception raised when csp set to defective."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    csp_sim, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")
    csp_sim.SetDefective(
        json.dumps(COMMAND_FAILED_WITH_EXCEPTION_OBSSTATE_EMPTY)
    )
    result, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED
    exception_message = (
        "Exception occurred on the following devices:"
        + " ska_low/tm_subarray_node/1:"
        + " Exception occurred on the following devices:"
    )
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(unique_id[0], Anything),
    )
    csp_sim.SetDefective(json.dumps({"enabled": False}))

    assert "AssignResources" in assertion_data["attribute_value"][0]
    assert exception_message in assertion_data["attribute_value"][1]


@pytest.mark.SKA_low
def test_assign_release_timeout_sdp(
    central_node_low,
    event_recorder,
    simulator_factory,
    command_input_factory,
):
    """Verify defective exception raised when csp set to defective."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    _, sdp_sim = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(sdp_sim, "obsState")
    sdp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    result, unique_id = central_node_low.perform_action(
        "AssignResources", assign_input_json
    )
    assert unique_id[0].endswith("AssignResources")
    assert result[0] == ResultCode.QUEUED
    exception_message = "Timeout has occured, command failed"
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        attribute_name="longRunningCommandResult",
        attribute_value=(unique_id[0], Anything),
    )
    sdp_sim.SetDefective(json.dumps({"enabled": False}))
    assert "AssignResources" in assertion_data["attribute_value"][0]
    assert exception_message in assertion_data["attribute_value"][1]


@pytest.mark.SKA_low
def test_release_exception_propagation(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """Verify timeout exception raised when csp set to defective."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    release_input_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )

    event_recorder.subscribe_event(
        central_node_low.subarray_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
    csp_sim, _ = get_device_simulators(simulator_factory)
    event_recorder.subscribe_event(csp_sim, "obsState")

    central_node_low.perform_action("AssignResources", assign_input_json)

    csp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    result, unique_id = central_node_low.perform_action(
        "ReleaseResources", release_input_json
    )
    assert unique_id[0].endswith("ReleaseResources")
    assert result[0] == ResultCode.QUEUED
    exception_message = (
        "Exception occurred on the following devices:"
        + " ska_low/tm_subarray_node/1:"
        + " Exception occurred on the following devices:"
    )

    event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], exception_message),
    )
    event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.FAILED.value)),
    )
    csp_sim.SetDefective(json.dumps({"enabled": False}))


@pytest.mark.SKA_low
def test_assign_release_timeout_csp(
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

    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )

    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    csp_subarray_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))

    _, unique_id = central_node_low.store_resources(assign_input_json)
    ERROR_MESSAGE = "Timeout has occurred, command failed"
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert ERROR_MESSAGE in assertion_data["attribute_value"][1]
    csp_subarray_sim.SetDefective(json.dumps({"enabled": False}))
