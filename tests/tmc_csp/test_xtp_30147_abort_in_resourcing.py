"""Module for TMC-CSP Abort command tests"""

import pytest
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)


@pytest.mark.tmc_csp
@pytest.mark.skip(
    reason="Issue on CSP - CBF subarray side, waiting for SKB-285 fix"
)
@scenario(
    "../features/tmc_csp/xtp-30147_abort_in_resourcing.feature",
    "Abort assigning using TMC",
)
def test_abort_in_resourcing():
    """BDD test scenario for verifying successful execution of
    the Abort command in Resourcing state with TMC and CSP devices for
    pairwise testing."""


@given("TMC and CSP subarray busy assigning resources")
def subarray_busy_assigning(
    central_node_real_csp_low,
    event_recorder,
    command_input_factory,
):
    """Subarray busy Assigning"""
    # Turning the devices ON
    central_node_real_csp_low.set_subarray_id(1)
    central_node_real_csp_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    # Invoking AssignResources command
    central_node_real_csp_low.store_resources(input_json)
    event_recorder.subscribe_event(
        central_node_real_csp_low.subarray_node, "obsState"
    )
    event_recorder.subscribe_event(
        central_node_real_csp_low.csp_subarray_leaf_node, "cspSubarrayObsState"
    )
    event_recorder.subscribe_event(
        central_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )

    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.csp_subarray_leaf_node,
        "cspSubarrayObsState",
        ObsState.RESOURCING,
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.RESOURCING,
    )


@when("I command it to Abort")
def abort_subarray(subarray_node_real_csp_low):
    """Abort command invoked on Subarray Node"""
    subarray_node_real_csp_low.abort_subarray()


@then("the CSP subarray should go into an aborted obsState")
def csp_subarray_in_aborted_obs_state(
    subarray_node_real_csp_low, event_recorder
):
    """CSP Subarray in ABORTED obsState."""
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )


@then("the TMC subarray node obsState transitions to ABORTED")
def subarray_in_aborted_obs_state(subarray_node_real_csp_low, event_recorder):
    """Subarray Node in ABORTED obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
        lookahead=10,
    )
    event_recorder.clear_events()