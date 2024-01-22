"""Test module to test TMC-CSP End functionality."""
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
from tests.resources.test_harness.utils.common_utils import JsonFactory


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-29855_end.feature",
    "End Command to CSP subarray using TMC",
)
def test_tmc_csp_end_functionality(central_node_low) -> None:
    """
    Test case to verify TMC-CSP observation End functionality
    """
    assert central_node_low.central_node.ping() > 0
    assert central_node_low.subarray_devices["csp_subarray"].ping() > 0


@given("the Telescope is in ON state")
def check_telescope_is_in_on_state(
    central_node_low: CentralNodeWrapperLow, event_recorder: EventRecorder
) -> None:
    """Ensure telescope is in ON state."""
    if central_node_low.telescope_state != "ON":
        central_node_low.csp_master.adminMode = 0
        central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
        lookahead=15,
    )


@given(parsers.parse("a subarray {subarray_id} in the READY obsState"))
def move_subarray_node_to_ready_obsstate(
    central_node_low: CentralNodeWrapperLow,
    subarray_node: SubarrayNodeWrapperLow,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    central_node_low.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    # Create json for AssignResources commands with requested subarray_id
    assign_input = json.loads(assign_input_json)
    assign_input["subarray_id"] = int(subarray_id)
    central_node_low.perform_action(
        "AssignResources", json.dumps(assign_input)
    )

    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    subarray_node.execute_transition("Configure", argin=configure_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )


@when("I issue End command to the subarray")
def invoke_end_command(subarray_node_low: SubarrayNodeWrapperLow) -> None:
    """Invoke End command."""
    subarray_node_low.execute_transition("End")


@then("the CSP subarray transitions to IDLE obsState")
def check_if_csp_subarray_moved_to_idle_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow, event_recorder
):
    """Ensure CSP subarray is moved to IDLE obsstate"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.IDLE,
    )


@then("TMC subarray transitions to IDLE obsState")
def check_if_tmc_subarray_moved_to_idle_obsstate(
    subarray_node_low: SubarrayNodeWrapperLow, event_recorder: EventRecorder
) -> None:
    """Ensure TMC Subarray is moved to IDLE obsstate"""
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
