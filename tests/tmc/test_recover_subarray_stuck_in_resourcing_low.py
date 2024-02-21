"""Test cases for recovery of subarray stuck in RESOURCING
ObsState for low"""
import json

import pytest
from ska_control_model import ObsState
from ska_tango_testing.mock.placeholders import Anything
from tango import DevState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_centralnode_commands,
    wait_and_validate_device_attribute_value,
)
from tests.resources.test_harness.utils.enums import SimulatorDeviceType
from tests.resources.test_support.constant_low import INTERMEDIATE_STATE_DEFECT


@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_low(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """AssignResources and ReleaseResources is executed."""
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
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    sdp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    assert wait_and_validate_device_attribute_value(
        sdp_sim,
        "defective",
        json.dumps(INTERMEDIATE_STATE_DEFECT),
        is_json=True,
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)

    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert (
        "Timeout has occured, command failed"
        in assertion_data["attribute_value"][1]
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices["sdp_subarray"],
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.IDLE,
    )
    sdp_sim.SetDefective(json.dumps({"enabled": False}))
    csp_sim.ReleaseAllResources()
    mccs_sim.ReleaseAllResources()
    assert event_recorder.has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_with_sdp_empty_with_abort(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """recover subarray when sdp is in empty with abort."""
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
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    sdp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    assert wait_and_validate_device_attribute_value(
        sdp_sim,
        "defective",
        json.dumps(INTERMEDIATE_STATE_DEFECT),
        is_json=True,
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)

    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert (
        "Exception occurred on the following devices:\n"
        "ska_low/tm_leaf_node/sdp_subarray01"
        in assertion_data["attribute_value"][1]
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.IDLE,
    )
    sdp_sim.SetDefective(json.dumps({"enabled": False}))

    central_node_low.subarray_node.Abort()
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    central_node_low.subarray_node.Restart()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_with_csp_empty_with_abort(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """recover subarray when csp is in empty with abort."""
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
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    csp_sim, sdp_sim = get_device_simulators(simulator_factory)
    mccs_sim = simulator_factory.get_or_create_simulator_device(
        SimulatorDeviceType.MCCS_SUBARRAY_DEVICE
    )
    csp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    assert wait_and_validate_device_attribute_value(
        sdp_sim,
        "defective",
        json.dumps(INTERMEDIATE_STATE_DEFECT),
        is_json=True,
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert (
        "Exception occurred on the following devices:\n"
        "ska_low/tm_leaf_node/csp_subarray01"
        in assertion_data["attribute_value"][1]
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        csp_sim,
        "obsState",
        ObsState.EMPTY,
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.IDLE,
    )
    assert event_recorder.has_change_event_occurred(
        mccs_sim,
        "obsState",
        ObsState.IDLE,
    )
    csp_sim.SetDefective(json.dumps({"enabled": False}))

    central_node_low.perform_action("Abort")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    central_node_low.perform_action("Restart")

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@pytest.mark.SKA_low
def test_recover_subarray_stuck_in_resourcing_with_abort(
    event_recorder, central_node_low, command_input_factory, simulator_factory
):
    """AssignResources and ReleaseResources is executed."""
    """recover subarray when sdp is in empty with abort."""
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
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["sdp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(
        central_node_low.subarray_devices["mccs_subarray"], "obsState"
    )
    central_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    _, sdp_sim = get_device_simulators(simulator_factory)
    sdp_sim.SetDefective(json.dumps(INTERMEDIATE_STATE_DEFECT))
    assert wait_and_validate_device_attribute_value(
        sdp_sim,
        "defective",
        json.dumps(INTERMEDIATE_STATE_DEFECT),
        is_json=True,
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)

    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert (
        "Timeout has occured, command failed"
        in assertion_data["attribute_value"][1]
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.RESOURCING,
    )

    central_node_low.subarray_node.Abort()
    sdp_sim.SetDefective(json.dumps({"enabled": False}))
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
    central_node_low.subarray_node.Restart()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
