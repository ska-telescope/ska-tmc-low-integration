"""Configurations needed for the tests using the new harness."""

# pylint: disable=redefined-outer-name


import logging
import os
from dataclasses import dataclass
from typing import Any

import pytest
from pytest_bdd import given, parsers
from ska_control_model import ObsState
from ska_integration_test_harness.facades.csp_facade import CSPFacade
from ska_integration_test_harness.facades.sdp_facade import SDPFacade
from ska_integration_test_harness.facades.tmc_facade import TMCFacade
from ska_integration_test_harness.init.test_harness_builder import (
    TestHarnessBuilder,
)
from ska_integration_test_harness.inputs.json_input import DictJSONInput
from ska_integration_test_harness.inputs.test_harness_inputs import (
    TestHarnessInputs,
)
from ska_integration_test_harness.structure.telescope_wrapper import (
    TelescopeWrapper,
)
from ska_tango_testing.integration import TangoEventTracer, log_events

from tests.tmc_csp_new_ITH.utils.my_file_json_input import MyFileJSONInput

# ------------------------------------------------------------
# Test Harness fixtures

DEFAULT_VCC_CONFIG_INPUT = DictJSONInput(
    {
        "interface": "https://schema.skao.int/ska-mid-cbf-initsysparam/1.0",
        "tm_data_sources": [
            "car://gitlab.com/ska-telescope/ska-telmodel-data?"
            + "ska-sdp-tmlite-repository-1.0.0#tmdata"
        ],
        "tm_data_filepath": (
            "instrument/ska1_mid_psi/ska-mid-cbf-system-parameters.json",
        ),
    }
)


@pytest.fixture
def default_commands_inputs() -> TestHarnessInputs:
    """Default JSON inputs for TMC commands."""
    return TestHarnessInputs(
        assign_input=MyFileJSONInput("centralnode", "assign_resources_low"),
        configure_input=MyFileJSONInput("subarray", "configure_low"),
        scan_input=MyFileJSONInput("subarray", "scan_low"),
        release_input=MyFileJSONInput("centralnode", "release_resources_low"),
        default_vcc_config_input=DEFAULT_VCC_CONFIG_INPUT,
    )


@pytest.fixture
def telescope_wrapper(
    default_commands_inputs: TestHarnessInputs,
) -> TelescopeWrapper:
    """Create an unique test harness with proxies to all devices."""
    test_harness_builder = TestHarnessBuilder()

    # import from a configuration file device names and emulation directives
    # for TMC, CSP, SDP and the Dishes
    test_harness_builder.read_config_file(
        "tests/tmc_csp_new_ITH/test_harness_config.yaml"
    )
    test_harness_builder.validate_configurations()

    # set the default inputs for the TMC commands,
    # which will be used for teardown procedures
    test_harness_builder.set_default_inputs(default_commands_inputs)
    test_harness_builder.validate_default_inputs()
    test_harness_builder.set_kubernetes_namespace(os.getenv("KUBE_NAMESPACE"))

    # build the wrapper of the telescope and it's sub-systems
    telescope = test_harness_builder.build()
    telescope.actions_default_timeout = 60
    yield telescope
    return

    # after a test is completed, reset the telescope to its initial state
    # (obsState=READY, telescopeState=OFF, no resources assigned)
    n_tries = 1
    for i in range(n_tries):
        try:
            telescope.tear_down()
            break
        # pylint: disable=broad-exception-caught
        except Exception as e:
            logging.error("Error during tear down: %s", e)
            if i == n_tries - 1:
                raise e


@pytest.fixture
def tmc(telescope_wrapper: TelescopeWrapper) -> TMCFacade:
    """Create a facade to TMC devices."""
    return TMCFacade(telescope_wrapper)


@pytest.fixture
def csp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to CSP devices."""
    return CSPFacade(telescope_wrapper)


@pytest.fixture
def sdp(telescope_wrapper: TelescopeWrapper):
    """Create a facade to SDP devices."""
    return SDPFacade(telescope_wrapper)


# TODO: Add MCCS facade

# ----------------------------------------------------------
# Tango event tracer


@pytest.fixture
def event_tracer() -> TangoEventTracer:
    """Create an event tracer."""
    return TangoEventTracer(
        event_enum_mapping={"obsState": ObsState},
    )


# ------------------------------------------------------------
# Other fixtures and common steps


@dataclass
class SubarrayTestContextData:
    """A class to store shared variables between steps."""

    starting_state: ObsState | None = None
    """The state of the system before the WHEN step."""

    expected_next_state: ObsState | None = None
    """The expected state to be reached if no WHEN step is executed.

    It is meaningful when the starting state is transient and so it will
    automatically change to another state (different both from the starting
    state and the expected next state).

    Leave empty if the starting state is not transient.
    """

    when_action_result: Any | None = None
    """The result of the WHEN step command."""

    when_action_name: str | None = None
    """The name of the Tango command executed in the WHEN step."""

    def is_starting_state_transient(self) -> bool:
        """Check if the starting state is transient."""
        return self.expected_next_state is not None


@pytest.fixture
def context_fixt() -> SubarrayTestContextData:
    """A collection of variables shared between steps.

    The shared variables are the following:

    - previous_state: the previous state of the subarray.
    - expected_next_state: the expected next state of the subarray (specified
        only if the previous st
    - trigger: the trigger that caused the state change.

    :return: the shared variables.
    """
    return SubarrayTestContextData()


def _setup_event_subscriptions(
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Subscribe TMC, CSP and SDP devices to track and log obsState events.

    :param tmc: the TMC facade.
    :param csp: the CSP facade.
    :param sdp: the SDP facade.
    :param event_tracer: the event tracer.
    """
    event_tracer.subscribe_event(tmc.subarray_node, "obsState")
    event_tracer.subscribe_event(csp.csp_subarray, "obsState")
    event_tracer.subscribe_event(sdp.sdp_subarray, "obsState")
    event_tracer.subscribe_event(tmc.central_node, "longRunningCommandResult")
    event_tracer.subscribe_event(tmc.subarray_node, "longRunningCommandResult")

    log_events(
        {
            tmc.subarray_node: [
                "obsState",
                "longRunningCommandResult",
            ],
            csp.csp_subarray: ["obsState"],
            sdp.sdp_subarray: ["obsState", "commandCallInfo"],
            tmc.central_node: ["longRunningCommandResult"],
        },
        event_enum_mapping={"obsState": ObsState},
    )


@given("the telescope is in ON state")
def given_the_telescope_is_in_on_state(
    tmc: TMCFacade,
):
    """Ensure the telescope is in ON state."""
    tmc.move_to_on(wait_termination=True)


@given(parsers.parse("the subarray {subarray_id} can be used"))
def subarray_can_be_used(
    subarray_id: str,
    tmc: TMCFacade,
    csp: CSPFacade,
    sdp: SDPFacade,
    event_tracer: TangoEventTracer,
):
    """Set up the subarray (and the subscriptions) to be used in the test."""
    # tmc.set_subarray_id(int(subarray_id))
    _setup_event_subscriptions(tmc, csp, sdp, event_tracer)


@given(parsers.parse("the subarray {subarray} is in the RESOURCING state"))
def subarray_in_resourcing_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the RESOURCING state."""
    context_fixt.starting_state = ObsState.RESOURCING
    context_fixt.expected_next_state = ObsState.IDLE

    tmc.force_change_of_obs_state(
        ObsState.RESOURCING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray {subarray} is in the IDLE state"))
def subarray_in_idle_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the IDLE state."""
    context_fixt.starting_state = ObsState.IDLE

    tmc.force_change_of_obs_state(
        ObsState.EMPTY,
        default_commands_inputs,
        wait_termination=True,
    )

    json_input = MyFileJSONInput(
        "centralnode", "assign_resources_mid"
    ).with_attribute("subarray_id", 1)

    context_fixt.when_action_result = tmc.assign_resources(
        json_input,
        wait_termination=True,
    )


@given(parsers.parse("the subarray {subarray} is in the CONFIGURING state"))
def subarray_in_configuring_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the CONFIGURING state."""
    context_fixt.starting_state = ObsState.CONFIGURING
    context_fixt.expected_next_state = ObsState.READY

    tmc.force_change_of_obs_state(
        ObsState.CONFIGURING,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray {subarray} is in the READY state"))
def subarray_in_ready_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the READY state."""
    context_fixt.starting_state = ObsState.READY

    tmc.force_change_of_obs_state(
        ObsState.READY,
        default_commands_inputs,
        wait_termination=True,
    )


@given(parsers.parse("the subarray {subarray} is in the SCANNING state"))
def subarray_in_scanning_state(
    context_fixt: SubarrayTestContextData,
    tmc: TMCFacade,
    default_commands_inputs: TestHarnessInputs,
):
    """Ensure the subarray is in the SCANNING state."""
    context_fixt.starting_state = ObsState.SCANNING
    context_fixt.expected_next_state = ObsState.READY

    tmc.force_change_of_obs_state(
        ObsState.SCANNING,
        default_commands_inputs,
        wait_termination=True,
    )
