"""Test TMC Low executes configure-scan sequence of commands successfully"""

import logging

import pytest
from pytest_bdd import parsers, scenario, when
from ska_ser_logging import configure_logging
from ska_tango_base.commands import ResultCode

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_centralnode_commands,
    update_eb_pb_ids,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_harness.utils.common_utils import (
    check_configure_successful,
    check_obsstate_sdp_in_first_configure,
    check_scan_successful,
)

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp-35244_long_sequence_configure_scan.feature",
    "TMC Low executes configure-scan sequence of commands successfully",
)
def test_tmc_sdp_long_sequences():
    """
    TMC Low executes configure-scan sequence of commands successfully
    """


@when(parsers.parse("I assign resources to TMC SubarrayNode {subarray_id}"))
def assign_resources_to_subarray(
    central_node_low, command_input_factory, event_recorder
):
    """Method to assign resources to subarray."""
    event_recorder.subscribe_event(
        central_node_low.central_node, "longRunningCommandResult"
    )

    input_json = prepare_json_args_for_centralnode_commands(
        "assign_resources_low", command_input_factory
    )
    input_json = update_eb_pb_ids(input_json)
    _, unique_id = central_node_low.store_resources(input_json)
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "longRunningCommandResult",
        (unique_id[0], str(ResultCode.OK.value)),
    )


@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for each {scan_types} and {scan_ids}"
    )
)
def execute_configure_scan_sequence(
    subarray_node,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """A method to invoke configure and scan  command"""

    check_subarray_instance(subarray_node.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "configure1_low", command_input_factory
    )

    configure_cycle = "initial"
    processed_scan_type = ""

    combined_dict = dict(zip(eval(scan_ids), eval(scan_types)))

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node.store_configuration_data(configure_json)

        if configure_cycle == "initial":
            check_obsstate_sdp_in_first_configure(
                event_recorder, subarray_node
            )
            configure_cycle = "Next"

        check_configure_successful(
            subarray_node,
            event_recorder,
            unique_id,
            scan_type,
            processed_scan_type,
        )

        scan_json = prepare_json_args_for_commands(
            "scan_low", command_input_factory
        )
        scan_json = update_scan_id(scan_json, scan_id)
        _, unique_id = subarray_node.execute_transition(
            "Scan", argin=scan_json
        )
        check_scan_successful(
            subarray_node, event_recorder, scan_id, unique_id
        )
        processed_scan_type = scan_type

        LOGGER.debug(
            f"Configure-scan sequence completed for {scan_id} "
            f"and scan_type {scan_type}"
        )
