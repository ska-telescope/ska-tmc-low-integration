"""
This module defines a BDD (Behavior-Driven Development) test scenario
using pytest-bdd to verify the behavior of the Telescope Monitoring and
Control (TMC) system to verify the SKB-643.
"""


import json

import pytest
from assertpy import assert_that
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState
from ska_tango_base.commands import ResultCode
from ska_tango_testing.integration import TangoEventTracer, log_events
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
)
from tests.resources.test_support.constant_low import TIMEOUT


@pytest.mark.SKA_low1
@scenario(
    "../features/tmc/SKB_643.feature",
    "Verify SKB-643",
)
def test_verify_skb_643():
    """BDD test scenario for verifying SKB-643"""


@given("TMC Subarray is in observation state EMPTY")
def given_a_tmc(
    central_node_low: CentralNodeWrapperLow, event_tracer: TangoEventTracer
):
    """
    This method invokes On command from central node and verifies
    the state of telescope after the invocation.
    Args:
        central_node (CentralNodeWrapperLow): Object of Central node wrapper
        event_tracer(TangoEventTracer): object of TangoEventTracer used for
        managing the device events
    """
    event_tracer.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    event_tracer.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )
    event_tracer.subscribe_event(central_node_low.subarray_node, "obsState")
    log_events(
        {
            central_node_low.central_node: [
                "telescopeState",
                "longRunningCommandResult",
            ],
            central_node_low.subarray_node: ["obsState"],
        }
    )
    central_node_low.move_to_on()
    assert_that(event_tracer).described_as(
        'FAILED ASSUMPTION IN "GIVEN" STEP: '
        "'the telescope is is ON state'"
        "Central Node device"
        f"({central_node_low.central_node.dev_name()}) "
        "is expected to be in TelescopeState ON",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
    assert_that(event_tracer).described_as(
        "FAILED UNEXPECTED INITIAL OBSSTATE: "
        "Subarray Node device"
        f"({central_node_low.subarray_node.dev_name()}) "
        "is expected to be in EMPTY obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("I invoke the assign command on TMC Subarray")
def invoke_assign_resources(
    central_node_low: CentralNodeWrapperLow,
    command_input_factory: JsonFactory,
    event_recorder,
):
    """Invoke assign resources."""
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    _, unique_id = central_node_low.store_resources(assign_input_json)
    event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], json.dumps((int(ResultCode.OK), "Command Completed"))),
    )


@then(
    "TMC subarray invokes configure on csp with json"
    + " containing beam_ids for pst and pss"
)
def check_beam_ids_in_json(subarray_node):
    """Check beam id for csp assign json"""
    # Retrieve the JSON input from the last command call to CSP
    input_json = subarray_node.subarray_devices[
        "csp_subarray"
    ].commandCallInfo[-1][-1]

    # Parse the JSON
    csp_config = json.loads(input_json)["csp"]

    # Check for "beam_ids" in both "pst" and "pss" configurations
    for resource_type in ["pst", "pss"]:
        assert (
            resource_type in csp_config
        ), f"Expected '{resource_type}' in CSP config"

        resource_data = csp_config[resource_type]
        beam_ids_key = f"{resource_type}_beam_ids"

        # Verify the presence of the beam_ids key
        assert (
            beam_ids_key in resource_data
        ), f"Expected '{beam_ids_key}' key in {resource_type} config"

        # Verify that beam_ids is not empty
        beam_ids = resource_data[beam_ids_key]
        assert (
            beam_ids
        ), f"'{beam_ids_key}' in {resource_type} config should not be empty"


@then("TMC Subarray transitions to observation state IDLE")
def check_subarray_is_in_idle(
    event_tracer: TangoEventTracer,
    subarray_node_low: SubarrayNodeWrapperLow,
):
    """Check Subarray is in IDLE Observation state"""
    assert_that(event_tracer).described_as(
        "FAILED ASSUMPTION AFTER ASSIGN RESOURCES: "
        "Subarray Node device"
        f"({subarray_node_low.subarray_node.dev_name()}) "
        "is expected to be in IDLE obstate",
    ).within_timeout(TIMEOUT).has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
