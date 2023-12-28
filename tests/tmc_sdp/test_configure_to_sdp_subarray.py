"""
Test TMC-SDP Configure functionality.
"""
import json
import logging

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

from tests.resources.test_support.common_utils.tmc_helpers import (
    prepare_json_args_for_commands,
)

LOGGER = logging.getLogger(__name__)


@pytest.mark.real_sdp
@pytest.mark.configure
@scenario(
    "../features/tmc_sdp/configure_sdp_subarray.feature",
    """Configure SDP subarray for a scan using TMC""",
)
def test_configure_sdp_subarray():
    """
    Test case to verify TMC-SDP Configure() functionality
    """


@given("the Telescope is in ON state")
def telescope_is_in_on_state(central_node_low, event_recorder):
    """Move the telescope to the ON state and verify the state change."""
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(parsers.parse("the TMC subarray {subarray_id} obsState is {obsstate}"))
def tmc_subarray_is_in_obsstate(
    subarray_id, obsstate, central_node_low, event_recorder
):
    """Verify the specified TMC subarray is in the given observation state."""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState[obsstate],
    )


@when(
    parsers.parse("I configure with {scan_type} to the subarray {subarray_id}")
)
def configure_sdp_subarray(
    scan_type, subarray_node_low, command_input_factory
):
    """Method to configure SDP subarray."""
    configure_input_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )
    configure_input_json = json.loads(configure_input_json)
    configure_input_json["sdp"]["scan_type"] = scan_type
    configure_input_json = json.dumps(configure_input_json)

    subarray_node_low.store_configuration_data(configure_input_json)


@then(parsers.parse("the SDP subarray {subarray_id} obsState is {obsstate}"))
def check_sdp_is_in_obsstate(
    subarray_id, obsstate, central_node_low, event_recorder
):
    """Method to check SDP subarray is in the expected observation state."""
    event_recorder.subscribe_event(
        central_node_low.subarray_devices.get("sdp_subarray"), "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState[obsstate],
    )


@then(
    parsers.parse(
        "the TMC subarray {subarray_id} obsState is transitioned to READY"
    )
)
def check_tmc_is_in_ready_obsstate(central_node_low, event_recorder):
    """Method to check TMC subarray is in the READY observation state."""
    event_recorder.subscribe_event(central_node_low.subarray_node, "obsState")
    assert event_recorder.has_change_event_occurred(
        central_node_low.subarray_node,
        "obsState",
        ObsState.READY,
    )
