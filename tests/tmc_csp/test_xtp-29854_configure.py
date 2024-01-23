"""Test module to test TMC-CSP Configure functionality."""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-29854_configure.feature",
    "Configure CSP subarray using TMC",
)
def test_tmc_csp_configure_functionality(central_node_low) -> None:
    """
    Test case to verify TMC-CSP Configure functionality
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["csp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_low: CentralNodeWrapperLow, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("the subarray {subarray_id} obsState is IDLE"))
def move_subarray_node_to_idle_obsstate(
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
    command_input_factory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to IDLE obsstate."""
    central_node_low.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    central_node_low.store_resources(json.dumps(assign_input))

    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )


@when("I configure the subarray")
def invoke_configure_command(
    subarray_node_low: SubarrayNodeWrapperLow, command_input_factory
) -> None:
    """Invoke Configure command."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node_low.execute_transition(
        "Configure", argin=configure_input_json
    )


@then("the CSP subarray transitions to READY obsState")
def check_if_csp_subarray_moved_to_ready_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow, event_recorder: EventRecorder
) -> None:
    """Ensure CSP subarray is moved to READY obsstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then("the TMC subarray transitions to READY obsState")
def check_if_tmc_subarray_moved_to_ready_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to READY obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
