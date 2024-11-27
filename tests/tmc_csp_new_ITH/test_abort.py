"""Verify the Abort command works as expected from all appropriate states.

The purpose of these scenarios is to verify that the subarray obsState
can be successfully aborted and restarted from any state, ensuring so
that a tear down procedure to reset the subarray to a known EMPTY state is
feasible.

The states that permit the Abort command are:
- RESOURCING
- IDLE
- CONFIGURING
- READY
- SCANNING

The Abort command is expected to transition the subarray to the ABORTING.

After the subarray is in the ABORTING state, the subsequent expected
transition is the automatic transition to the ABORTED state. After that,
the Restarted command can be called, and it will transition the subarray
to the RESTARTING state, and then to the EMPTY state.
"""


import pytest
from assertpy import assert_that
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_tango_testing.integration import TangoEventTracer

from tests.tmc_csp_new_ITH.conftest import SubarrayTestContextData

ASSERTIONS_TIMEOUT = 100

# ------------------------------------------------------------
# Scenario Definition


# @pytest.mark.xfail(
#     reason=(
#         "It may fail because right now we cannot detect the passage "
#         "trough an 'ABORTING' state in the SDP emulator subarray."
#     )
# )
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/abort_restart_subarray.feature",
    "RESOURCING to ABORTING to ABORTED - CMD Abort",
)
def test_resourcing_to_aborting_to_aborted():
    """Test RESOURCING to ABORTING to ABORTED transitions."""


# @pytest.mark.xfail(
#     reason=(
#         "It may fail because right now we cannot detect the passage "
#         "trough an 'ABORTING' state in the SDP emulator subarray."
#     )
# )
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/abort_restart_subarray.feature",
    "IDLE to ABORTING to ABORTED - CMD Abort",
)
def test_idle_to_aborting_to_aborted():
    """Test IDLE to ABORTING to ABORTED transitions."""


# @pytest.mark.xfail(
#     reason=(
#         "It may fail because right now we cannot detect the passage "
#         "trough an 'ABORTING' state in the SDP emulator subarray."
#     )
# )
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/abort_restart_subarray.feature",
    "CONFIGURING to ABORTING to ABORTED - CMD Abort",
)
def test_configuring_to_aborting_to_aborted():
    """Test CONFIGURING to ABORTING to ABORTED transitions."""


# @pytest.mark.xfail(
#     reason=(
#         "It may fail because right now we cannot detect the passage "
#         "trough an 'ABORTING' state in the SDP emulator subarray."
#     )
# )
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/abort_restart_subarray.feature",
    "READY to ABORTING to ABORTED - CMD Abort",
)
def test_ready_to_aborting_to_aborted():
    """Test READY to ABORTING to ABORTED transitions."""


# @pytest.mark.xfail(
#     reason=(
#         "It may fail because right now we cannot detect the passage "
#         "trough an 'ABORTING' state in the SDP emulator subarray."
#     )
# )
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/abort_restart_subarray.feature",
    "SCANNING to ABORTING to ABORTED - CMD Abort",
)
def test_scanning_to_aborting_to_aborted():
    """Test SCANNING to ABORTING to ABORTED transitions."""


# @pytest.mark.skip(reason="Facing issues in new test case harness")
@pytest.mark.tmc_csp_new_ITH
@scenario(
    "../tmc_csp_new_ITH/features/abort_restart_subarray.feature",
    "ABORTED to RESTARTING to EMPTY - CMD Restart",
)
def test_aborted_to_restarting():
    """Test ABORTED to RESTARTING transition."""


# ----------------------------------------------------------
# Given Steps


@given(parsers.parse("the subarray {subarray} is in the ABORTED state"))
def subarray_in_aborted_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """
    Ensure the subarray is in the ABORTED state.

    This step performs the following actions:
    1. Sets the starting_state in the test context to ABORTED.
    2. Forces the subarray to the IDLE state to ensure it's in a state
       where Abort can be sent.
    3. Sends the Abort command to transition the subarray
       to the ABORTED state.
    """
    context_fixt.starting_state = ObsState.ABORTED

    # move to a state where the Abort command can be sent
    tmc.force_change_of_obs_state(
        ObsState.IDLE,
        default_commands_inputs,
        wait_termination=True,
    )

    # send the Abort command
    tmc.abort(wait_termination=True)


# ----------------------------------------------------------
# (Common) When Step


@when(parsers.parse("the Abort command is sent to the subarray {subarray}"))
def send_abort_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    event_tracer: TangoEventTracer,
):
    """
    Send the Abort command to the subarray.

    This step sends the Abort command without waiting for termination.
    If the starting state is transient, it verifies that the
    expected state transition hasn't occurred prematurely.
    """
    context_fixt.when_action_name = "Abort"

    tmc.abort(wait_termination=False)

    if context_fixt.is_starting_state_transient():
        assert_that(event_tracer).described_as(
            "FAILED ASSUMPTION: "
            "TMC Subarray Node device "
            f"({tmc.subarray_node}) "
            "Abort command invocation has been performed "
            f"after obsState is {str(context_fixt.starting_state)}, "
            "probably because an automatic transaction triggered."
        ).hasnt_change_event_occurred(
            tmc.subarray_node,
            "obsState",
            context_fixt.expected_next_state,
            previous_value=context_fixt.starting_state,
        )


@when(parsers.parse("the Restart command is sent to the subarray {subarray}"))
def send_restart_command(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
):
    """
    Send the Restart command to the subarray.

    This step sends the Restart command without waiting for termination.
    """
    context_fixt.when_action_name = "Restart"

    tmc.restart(wait_termination=False)


# ----------------------------------------------------------
# (Common) Then Steps


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the ABORTING state"
    )
)
def verify_aborting_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the ABORTING state.

    This step checks that the TMC Subarray Node, CSP Subarray, and SDP Subarray
    devices transition to the ABORTING state within the specified timeout.
    It verifies the previous state for the TMC Subarray Node.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move to ABORTING."
        "TMC, in particular, is expected to move exactly from the "
        f"{str(context_fixt.starting_state)} state to ABORTING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.ABORTING,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTING,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.ABORTING,
    )

    # NOTE: since the previous state may be transient, we cannot guarantee
    # for the sub-devices to still be in that state, so we don't check it.


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the ABORTED state"
    )
)
def verify_aborted_state(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the ABORTED state.

    This step checks that all relevant devices (TMC, CSP, SDP) transition from
    ABORTING to ABORTED state within the specified timeout.
    """
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        "from ABORTING to ABORTED."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.ABORTED,
        previous_value=ObsState.ABORTING,
    )


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the RESTARTING state"
    )
)
def verify_restarting_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the RESTARTING state.

    This step performs the following actions:
    1. Checks that all relevant devices transition from
       ABORTED to RESTARTING state
       within the specified timeout.
    2. Updates the starting state in the test context to RESTARTING.
    3. Verifies that the correct Tango command (Aborted) was received
       by the SDP emulator."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        "from ABORTED to RESTARTING."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.RESTARTING,
        previous_value=ObsState.ABORTED,
    )

    context_fixt.starting_state = ObsState.RESTARTING


@then(
    parsers.parse(
        "the subarray {subarray} should transition to the EMPTY state"
    )
)
def verify_empty_state(
    context_fixt,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """
    Verify that the subarray transitions to the EMPTY state.

    This step checks that all relevant devices (TMC, CSP, SDP) transition from
    the previous state (stored in the test context) to the EMPTY state within
    the specified timeout."""
    assert_that(event_tracer).described_as(
        f"Both TMC Subarray Node device ({tmc.subarray_node})"
        f", CSP Subarray device ({csp.csp_subarray}) "
        f"and SDP Subarray device ({sdp.sdp_subarray}) "
        "ObsState attribute values should move "
        f"from {str(context_fixt.starting_state)} to EMPTY."
    ).within_timeout(ASSERTIONS_TIMEOUT).has_change_event_occurred(
        tmc.subarray_node,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        csp.csp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    ).has_change_event_occurred(
        sdp.sdp_subarray,
        "obsState",
        ObsState.EMPTY,
        previous_value=context_fixt.starting_state,
    )
