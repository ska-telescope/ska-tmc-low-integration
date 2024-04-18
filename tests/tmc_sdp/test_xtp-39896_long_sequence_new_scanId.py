"""Test TMC Low executes multiple scan with same configuration successfully"""

import pytest
from pytest_bdd import parsers, scenario, when

from tests.resources.test_harness.helpers import (
    check_subarray_instance,
    prepare_json_args_for_commands,
    update_scan_id,
    update_scan_type,
)
from tests.resources.test_harness.utils.common_utils import (
    check_configure_successful,
    check_obsstate_sdp_in_first_configure,
    check_scan_successful,
)


@pytest.mark.tmc_sdp
@scenario(
    "../features/tmc_sdp/xtp_39894_tmc_sdp_long_sequence.feature",
    "TMC Low executes multiple scan with same configuration successfully",
)
def test_tmc_sdp_successive_scan_sequences():
    """
    Test case to verify TMC-SDP  functionality TMC Low executes multiple scan
    with same configuration successfully
    """


# pylint: disable=eval-used
@when(
    parsers.parse(
        "configure and scan TMC SubarrayNode {subarray_id} "
        "for each {scan_types} and {scan_ids}"
    )
)
def execute_configure_scan_sequence(
    subarray_node_low,
    command_input_factory,
    scan_ids,
    event_recorder,
    subarray_id,
    scan_types,
):
    """A method to invoke configure and scan command"""

    check_subarray_instance(subarray_node_low.subarray_node, subarray_id)
    configure_json = prepare_json_args_for_commands(
        "configure_low", command_input_factory
    )

    configure_cycle = "initial"
    processed_scan_type = ""

    combined_dict = dict(zip(eval(scan_ids), eval(scan_types)))

    for scan_id, scan_type in combined_dict.items():
        configure_json = update_scan_type(configure_json, scan_type)
        _, unique_id = subarray_node_low.store_configuration_data(
            configure_json
        )
        if configure_cycle == "initial":
            check_obsstate_sdp_in_first_configure(
                event_recorder, subarray_node_low
            )
            configure_cycle = "Next"
        check_configure_successful(
            subarray_node_low,
            event_recorder,
            unique_id,
            scan_type,
            processed_scan_type,
        )
        scan_json = prepare_json_args_for_commands(
            "scan_low", command_input_factory
        )
        scan_json = update_scan_id(scan_json, scan_id)
        _, unique_id = subarray_node_low.execute_transition(
            "Scan", argin=scan_json
        )
        check_scan_successful(
            subarray_node_low, event_recorder, scan_id, unique_id
        )
        processed_scan_type = scan_type


@when(parsers.parse("reperform scan with same configuration and new scan id"))
def reexecute_scan_command(
    command_input_factory,
    event_recorder,
    subarray_node_low,
):
    """A method to invoke scan command with new scan_id"""

    scan_id = 10
    scan_json = prepare_json_args_for_commands(
        "scan_low", command_input_factory
    )

    scan_json = update_scan_id(scan_json, scan_id)
    _, unique_id = subarray_node_low.execute_transition(
        "Scan", argin=scan_json
    )

    check_scan_successful(
        subarray_node_low, event_recorder, scan_id, unique_id
    )
