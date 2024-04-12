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
from tests.resources.test_support.constant_low import (
    FAILED_RESULT_DEFECT,
    INTERMEDIATE_STATE_DEFECT,
)


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
        "Timeout has occurred, command failed"
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
        ObsState.RESOURCING,
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
    sdp_sim.SetDirectObsState(ObsState.EMPTY)
    csp_sim.ReleaseAllResources()
    mccs_sim.ReleaseAllResources()

    assert event_recorder.has_change_event_occurred(
        sdp_sim,
        "obsState",
        ObsState.EMPTY,
    )
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
@pytest.mark.parametrize("defective_device", ["csp_subarray", "sdp_subarray"])
def test_abort_with_sdp_csp_in_empty(
    event_recorder,
    central_node_low,
    command_input_factory,
    simulator_factory,
    defective_device,
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

    # Set SDP into FAILED RESULT to change from RESOURCING to EMPTY
    failed_result_defect = FAILED_RESULT_DEFECT
    failed_result_defect["target_obsstates"] = [
        ObsState.RESOURCING,
        ObsState.EMPTY,
    ]
    defective_device_proxy = central_node_low.subarray_devices.get(
        defective_device
    )
    defective_device_proxy.SetDefective(json.dumps(failed_result_defect))

    assert wait_and_validate_device_attribute_value(
        defective_device_proxy,
        "defective",
        json.dumps(failed_result_defect),
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
        f"ska_low/tm_leaf_node/{defective_device}01"
        in assertion_data["attribute_value"][1]
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        defective_device_proxy,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        defective_device_proxy,
        "obsState",
        ObsState.EMPTY,
    )
    if defective_device_proxy.dev_name() != csp_sim.dev_name():
        assert event_recorder.has_change_event_occurred(
            csp_sim,
            "obsState",
            ObsState.IDLE,
        )
    elif defective_device_proxy.dev_name() != sdp_sim.dev_name():
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
    defective_device_proxy.SetDefective(json.dumps({"enabled": False}))

    central_node_low.subarray_node.Abort()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@pytest.mark.test
@pytest.mark.SKA_low
def test_abort_with_mccs_in_empty(
    event_recorder,
    central_node_low,
    command_input_factory,
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

    # Set SDP into FAILED RESULT to change from RESOURCING to EMPTY
    failed_result_defect = FAILED_RESULT_DEFECT
    failed_result_defect["target_obsstates"] = [
        ObsState.RESOURCING,
        ObsState.EMPTY,
    ]
    mccs_device_proxy = central_node_low.subarray_devices.get("mccs_subarray")
    mccs_device_proxy.SetDefective(json.dumps(failed_result_defect))

    assert wait_and_validate_device_attribute_value(
        mccs_device_proxy,
        "defective",
        json.dumps(failed_result_defect),
        is_json=True,
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)

    assertion_data = event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], Anything),
    )
    assert (
        "Exception occurred on the following devices:"
        + " ska_low/tm_subarray_node/1"
        in assertion_data["attribute_value"][1]
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        mccs_device_proxy,
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        mccs_device_proxy,
        "obsState",
        ObsState.EMPTY,
    )
    mccs_device_proxy.SetDefective(json.dumps({"enabled": False}))

    central_node_low.subarray_node.Abort()

    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )
