"""Test TMC Low executes multiple scan with same configuration successfully"""


import pytest
from pytest_bdd import parsers, scenario, when

from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import (
    prepare_json_args_for_commands,
    update_scan_id,
)
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import (
    JsonFactory,
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


@when(parsers.parse("reperform scan with same configuration and new scan id"))
def reexecute_scan_command(
    command_input_factory: JsonFactory,
    event_recorder: EventRecorder,
    subarray_node_low: SubarrayNodeWrapperLow,
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
