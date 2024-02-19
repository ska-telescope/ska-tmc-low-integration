"""
This module defines a Pytest BDD test scenario for checking the rejection of
invalid JSON inputs during the Configure command execution on a
Telescope Monitoring and Control (TMC) system
The scenario includes steps to set up the TMC, configure the subarray,
and validate the rejection
of various invalid JSON inputs.
"""
import json

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.result_code import ResultCode
from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_centralnode_commands,
    prepare_json_args_for_commands,
)


@pytest.mark.kk
@pytest.mark.SKA_low
@scenario(
    "../features/tmc/check_invalid_json_not_allowed.feature",
    "Invalid json rejected by TMC Low for Configure command",
)
def test_invalid_json_in_configure_obsState():
    """
    Test SubarrayNode Low Configure command with invalid json data.
    """


@given("the TMC is On")
def given_tmc(central_node_low, event_recorder):
    """Ensure the TMC is in the 'On' state."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given("the subarray is in IDLE obsState")
def tmc_check_status(event_recorder, central_node_low, command_input_factory):
    """Set the subarray to 'IDLE' observation state."""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    central_node_low.store_resources(assign_input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.RESOURCING
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node, "obsState", ObsState.IDLE
    )


@when(
    parsers.parse("the command Configure is invoked with {invalid_json} input")
)
def send(subarray_node_low, invalid_json, command_input_factory):
    """Invoke the Configure command with different invalid JSON inputs."""

    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    if invalid_json == "csp_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["csp"]
        pytest.command_result = subarray_node_low.subarray_node.Configure(
            json.dumps(invalid_configure_json)
        )
    elif invalid_json == "sdp_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["sdp"]
        pytest.command_result = subarray_node_low.subarray_node.Configure(
            json.dumps(invalid_configure_json)
        )
    elif invalid_json == "tmc_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["tmc"]
        pytest.command_result = subarray_node_low.subarray_node.Configure(
            json.dumps(invalid_configure_json)
        )
    elif invalid_json == "scan_duration_key_missing":
        invalid_configure_json = json.loads(configure_json)
        del invalid_configure_json["tmc"]["scan_duration"]
        pytest.command_result = subarray_node_low.subarray_node.Configure(
            json.dumps(invalid_configure_json)
        )
    elif invalid_json == "empty_string":
        invalid_configure_json = {}
        pytest.command_result = subarray_node_low.subarray_node.Configure(
            json.dumps(invalid_configure_json)
        )


@then(
    parsers.parse(
        "the TMC should reject the {invalid_json} with ResultCode.Rejected"
    )
)
def invalid_command_rejection(invalid_json):
    """Verify that the TMC rejects the invalid JSON with the expected
    ResultCode  and validation messages."""
    # asserting validation resultcode
    assert pytest.command_result[0][0] == ResultCode.REJECTED
    # asserting validations message as per invalid json
    if invalid_json == "csp_key_missing":
        assert (
            "Malformed input string. The key: `csp` is missing."
            in pytest.command_result[1][0]
        )
    elif invalid_json == "sdp_key_missing":
        assert (
            "Malformed input string. The key: `sdp` is missing."
            in pytest.command_result[1][0]
        )
    elif invalid_json == "tmc_key_missing":
        assert (
            "Malformed input string. The key: `tmc` is missing."
            in pytest.command_result[1][0]
        )
    elif invalid_json == "scan_duration_key_missing":
        assert "Malformed input string" in pytest.command_result[1][0]
    elif invalid_json == "empty_string":
        assert "Malformed input string" in pytest.command_result[1][0]


@then("TMC subarray remains in IDLE obsState")
def tmc_status(event_recorder, subarray_node_low):
    """Ensure that the TMC subarray remains in the 'IDLE' observation state
    after rejection."""
    assert subarray_node_low.subarray_node.obsState == ObsState.IDLE


@then(
    "TMC successfully executes the Configure \
command for the subarray with a valid json"
)
def tmc_accepts_next_commands(
    command_input_factory, subarray_node_low, event_recorder, central_node_low
):
    """Execute the Configure command with a valid JSON and verify successful
    execution."""
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    LOGGER.info(f"Input argin for Configure: {configure_json}")

    # Invoke Configure() Command on TMC
    LOGGER.info("Invoking Configure command on TMC SubarrayNode")
    subarray_node_low.store_configuration_data(configure_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )

    # teardown
    LOGGER.info("Invoking END on TMC")
    subarray_node_low.end_observation()
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )
    release_json = prepare_json_args_for_centralnode_commands(
        "release_resources_low", command_input_factory
    )
    central_node_low.invoke_release_resources(release_json)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
