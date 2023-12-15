import pytest
import tango
from pytest_bdd import given, scenario, then, when
from ska_control_model import ObsState

from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.constant_low import (
    DEVICE_OBS_STATE_EMPTY_INFO,
)

result, message = "", ""
telescope_control = BaseTelescopeControl()


@pytest.mark.SKA_low
@scenario(
    "../features/check_abort_command.feature",
    "TMC executes Abort Command in EMPTY obsState.",
)
def test_abort_command_not_allowed_empty():
    """BDD test scenario for verifying execution of the Abort
    command in EMPTY obsState in TMC."""


@given("a Subarray in EMPTY obsState")
def given_tmc(subarray_node_low, event_recorder):
    """Subarray in EMPTY obsState"""
    event_recorder.subscribe_event(subarray_node_low.subarray_node, "obsState")
    subarray_node_low.move_to_on()
    assert event_recorder.has_change_event_occurred(
        subarray_node_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )


@when("I Abort it")
def invoke_abort_command(
    subarray_node_low,
):
    """Send a Abort command to the subarray."""
    try:
        subarray_node_low.execute_transition("Abort")
    except tango.DevFailed as ex:
        pytest.command_result = str(ex)


@then("TMC should reject the command with ResultCode.REJECTED")
def invalid_command_rejection():
    assert (
        "Abort command not permitted in observation state EMPTY"
        in pytest.command_result
    )


@then("the Subarray remains in obsState EMPTY")
def tmc_status():
    assert telescope_control.is_in_valid_state(
        DEVICE_OBS_STATE_EMPTY_INFO, "obsState"
    )
