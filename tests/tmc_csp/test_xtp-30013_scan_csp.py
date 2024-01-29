"""Test module for TMC-CSP Scan functionality"""
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
    "../features/tmc_csp/xtp-30013_scan_csp.feature",
    "TMC executes a scan on CSP subarray",
)
def test_scan_command():
    """BDD test scenario for verifying successful execution of
    the Scan command with TMC and CSP devices for pairwise
    testing.
    Glossary:
        - "central_node_low": fixture for a TMC CentralNode under test
        - "event_recorder": fixture for EventRecorder class
        - "subarray_node_low": fixture for a TMC SubarrayNode under test
    """


@given("the Telescope is in ON state")
def given_a_telescope_in_on_state(
    central_node_low: CentralNodeWrapperLow,
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: EventRecorder,
):
    """Checks if CentralNode's telescopeState attribute value is on."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_recorder.subscribe_event(central_node_low.csp_master, "State")
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "State"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.csp_master,
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "State",
        DevState.ON,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("TMC subarray {subarray_id} is in READY ObsState"))
def subarray_in_ready_obsstate(
    central_node_low: CentralNodeWrapperLow,
    event_recorder: EventRecorder,
    command_input_factory: JsonFactory,
    subarray_node_low: SubarrayNodeWrapperLow,
    subarray_id: str,
) -> None:
    """Move TMC Subarray to READY obsstate."""
    central_node_low.set_subarray_id(subarray_id)
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")

    subarray_node_low.force_change_of_obs_state(
        "READY",
        assign_input_json=assign_input_json,
        configure_input_json=configure_input_json,
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
        lookahead=20,
    )


@when(
    parsers.parse("I issue the scan command to the TMC subarray {subarray_id}")
)
def invoke_scan(
    subarray_node_low: SubarrayNodeWrapperLow,
    event_recorder: EventRecorder,
    command_input_factory,
    scan_id,
    subarray_id,
):
    """Invokes Scan command on TMC"""
    input_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )
    scan_json = json.loads(input_json)
    scan_json["scan_id"] = int(scan_id)

    subarray_node_low.set_subarray_id(subarray_id)
    subarray_node_low.store_scan_data(json.dumps(scan_json))

    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["sdp_subarray"],
        "scanID",
        int(scan_id),
    )


@then(parsers.parse("the CSP subarray transitions to ObsState SCANNING"))
def csp_subarray_scanning(subarray_node_low, event_recorder):
    """Checks if Csp Subarray's obsState attribute value is SCANNING"""
    event_recorder.subscribe_event(
        subarray_node_low.subarray_devices["csp_subarray"], "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.SCANNING,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} transitions to ObsState SCANNING"
    )
)
def tmc_subarray_scanning(
    central_node_low, subarray_node_low, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is SCANNING"""
    central_node_low.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.SCANNING,
        lookahead=15,
    )


@then(
    parsers.parse(
        "the CSP subarray ObsState transitions to READY after the"
        + " scan duration elapsed"
    )
)
def csp_subarray_ObsState(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is READY"""
    central_node_mid.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_devices["csp_subarray"],
        "obsState",
        ObsState.READY,
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} ObsState transitions back to READY"
    )
)
def tmc_subarray_ready(
    central_node_mid, subarray_node, event_recorder, subarray_id
):
    """Checks if SubarrayNode's obsState attribute value is EMPTY"""
    central_node_mid.set_subarray_id(int(subarray_id))
    assert event_recorder.has_change_event_occurred(
        subarray_node.subarray_node, "obsState", ObsState.READY
    )
