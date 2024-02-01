"""Module for TMC-CSP Abort command tests"""

import pytest
from pytest_bdd import given, parsers, scenario, then, when
from ska_control_model import ObsState
from tango import DevState

# from tests.resources.test_support.common_utils.tmc_helpers import (
#     prepare_json_args_for_centralnode_commands,
#     prepare_json_args_for_commands,
# )


# @pytest.mark.tmc_csp
# @scenario(
#     "../features/tmc_csp/xtp-30147_abort_in_resourcing.feature",
#     "Abort assigning using TMC",
# )
# def test_abort_in_resourcing_command():
#     """BDD test scenario for verifying successful execution of
#     the Abort command in Resourcing state with TMC and CSP devices for
#     pairwise testing."""


# @pytest.mark.tmc_csp
# @scenario(
#     "../features/tmc_csp/xtp-30154_abort_in_configuring.feature",
#     "Abort configuring CSP using TMC",
# )
# def test_abort_in_configuring_command():
#     """BDD test scenario for verifying successful execution of
#     the Abort command in Configuring state with TMC and CSP devices for
#     pairwise testing."""


# @pytest.mark.tmc_csp
# @scenario(
#     "../features/tmc_csp/xtp-30155_abort_in_scanning.feature",
#     "Abort scanning CSP using TMC",
# )
# def test_abort_in_scanning_command():
#     """BDD test scenario for verifying successful execution of
#     the Abort command in Scanning state with TMC and CSP devices for pairwise
#     testing."""


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30156_abort_in_idle_ready.feature",
    "Abort resourced CSP and TMC subarray",
)
def test_abort_in_idle_ready_command():
    """BDD test scenario for verifying successful execution of
    the Abort command in Idle/Ready state with TMC and CSP devices for pairwise
    testing."""


@pytest.mark.tmc_csp
@scenario(
    "../features/tmc_csp/xtp-30167_restart_in_aborted.feature",
    "TMC executes a Restart on CSP subarray when subarray completes abort",
)
def test_restart_in_aborted_command():
    """BDD test scenario for verifying successful execution of
    the Restart command in Aborted state with TMC and CSP devices for pairwise
    testing."""


@given("the telescope is in ON state")
def telescope_in_on_state(central_node_real_csp_low, event_recorder):
    """On telescope"""
    central_node_real_csp_low.move_to_on()

    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "telescopeState",
        DevState.ON,
    )


@given(
    parsers.parse("TMC and CSP subarray {subarray_id} is in obsState ABORTED")
)
def subarray_in_aborted_state(
    subarray_node_real_csp_low, event_recorder, subarray_id
):
    """Subarray in Aborted state."""
    subarray_node_real_csp_low.set_subarray_id(subarray_id)
    subarray_node_real_csp_low.force_change_of_obs_state("ABORTED")

    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_node, "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@given(parsers.parse("TMC subarray in obsState {obsstate}"))
def subarray_in_given_obs_state(
    central_node_real_csp_low,
    subarray_node_real_csp_low,
    event_recorder,
    obsstate,
):
    """Subarray busy assigning resources"""
    # Turning the devices ON
    central_node_real_csp_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_real_csp_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_real_csp_low.central_node,
        "telescopeState",
        DevState.ON,
    )

    # Using force change of obsState
    subarray_node_real_csp_low.force_change_of_obs_state(obsstate)
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_node, "obsState"
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState[obsstate],
    )


# @given("TMC and CSP subarray busy configuring")
# def subarray_busy_configuring(
#     central_node_real_csp_low,
#     subarray_node_real_csp_low,
#     event_recorder,
#     command_input_factory,
# ):
#     """Subarray busy Configuring"""
#     # Turning the devices ON
#     central_node_real_csp_low.move_to_on()
#     event_recorder.subscribe_event(
#         central_node_real_csp_low.central_node, "telescopeState"
#     )
#     assert event_recorder.has_change_event_occurred(
#         central_node_real_csp_low.central_node,
#         "telescopeState",
#         DevState.ON,
#     )

#     input_json = prepare_json_args_for_centralnode_commands(
#         "assign_resources_low", command_input_factory
#     )
#     # Invoking AssignResources command
#     central_node_real_csp_low.store_resources(input_json)
#     event_recorder.subscribe_event(
#         central_node_real_csp_low.subarray_node, "obsState"
#     )
#     event_recorder.subscribe_event(
#         central_node_real_csp_low.subarray_devices.get("csp_subarray"),
#         "obsState",
#     )
#     assert event_recorder.has_change_event_occurred(
#         central_node_real_csp_low.subarray_node,
#         "obsState",
#         ObsState.IDLE,
#     )

#     configure_input_json = prepare_json_args_for_commands(
#         "configure_low", command_input_factory
#     )
#     # Invoking Configure command
#     subarray_node_real_csp_low.store_configuration_data(configure_input_json)

#     assert event_recorder.has_change_event_occurred(
#         central_node_real_csp_low.subarray_devices.get("csp_subarray"),
#         "obsState",
#         ObsState.CONFIGURING,
#     )
#     assert event_recorder.has_change_event_occurred(
#         central_node_real_csp_low.subarray_node,
#         "obsState",
#         ObsState.CONFIGURING,
#     )


@when("I command it to Abort")
def abort_subarray(subarray_node_real_csp_low):
    """Abort command invoked on Subarray Node"""
    subarray_node_real_csp_low.abort_subarray()


@when("I command it to Restart")
def restart_subarray(subarray_node_real_csp_low):
    """Restart command invoked on Subarray Node"""
    subarray_node_real_csp_low.restart_subarray()


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
    )


@then("the CSP subarray transitions to obsState EMPTY")
def csp_subarray_in_empty_obs_state(
    subarray_node_real_csp_low, event_recorder
):
    """CSP Subarray in EMPTY obsState."""
    event_recorder.subscribe_event(
        subarray_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
    )
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_devices.get("csp_subarray"),
        "obsState",
        ObsState.EMPTY,
    )


@then("the TMC subarray node obsState transitions to ABORTED")
def subarray_in_aborted_obs_state(subarray_node_real_csp_low, event_recorder):
    """Subarray Node in ABORTED obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.ABORTED,
    )


@then("the TMC subarray transitions to obsState EMPTY")
def subarray_in_empty_obs_state(subarray_node_real_csp_low, event_recorder):
    """Subarray Node in EMPTY obsState."""
    assert event_recorder.has_change_event_occurred(
        subarray_node_real_csp_low.subarray_node,
        "obsState",
        ObsState.EMPTY,
    )
