"""
TMC Low executes multiple scans with different resources and configurations
"""

import json

import pytest
from pytest_bdd import parsers, scenario, when
from ska_tango_base.commands import ResultCode
from ska_tango_base.control_model import ObsState

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    update_eb_pb_ids,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_39894_tmc_sdp_long_sequence.feature",
    "TMC Low executes multiple scans with different "
    "resources and configurations",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes multiple-scan with different resources and configurations
    """


@when(
    parsers.parse(
        "I reassign with new resources to TMC SubarrayNode {subarray_id}"
    )
)
def reassign_resources(
    central_node_low,
    event_recorder,
    command_input_factory,
    subarray_id,
    subarray_node_low,
):
    """A method to move subarray into the IDLE ObsState"""

    assign_input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low_multiple_scan", command_input_factory
    )
    input_json = update_eb_pb_ids(assign_input_json)
    assign_str = json.loads(input_json)
    # Here we are adding this to get an event of ObsState CONFIGURING from
    # SDP Subarray
    assign_str["sdp"]["processing_blocks"][0]["parameters"][
        "time-to-ready"
    ] = 2

    _, unique_id = central_node_low.store_resources(json.dumps(assign_str))

    check_subarray_instance(
        subarray_node_low.subarray_devices.get("sdp_subarray"), subarray_id
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_devices.get("sdp_subarray"),
        "obsState",
        ObsState.IDLE,
    )

    check_subarray_instance(subarray_node_low.subarray_node, subarray_id)
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.IDLE,
    )

    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(int(ResultCode.OK))),
        lookahead=10,
    )
