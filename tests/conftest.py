"""Test configuration file for ska_tmc_low_integration"""
import json
import logging
import os
import time
from os.path import dirname, join

import pytest
import tango
from pytest_bdd import given
from ska_ser_logging import configure_logging
from ska_tango_testing.mock.tango.event_callback import (
    MockTangoEventCallbackGroup,
)
from tango import DevState

from tests.resources.test_harness.central_node_low import CentralNodeWrapperLow
from tests.resources.test_harness.central_node_with_csp_low import (
    CentralNodeCspWrapperLow,
)
from tests.resources.test_harness.event_recorder import EventRecorder
from tests.resources.test_harness.helpers import set_admin_mode_values_mccs
from tests.resources.test_harness.simulator_factory import SimulatorFactory
from tests.resources.test_harness.subarray_node_low import (
    SubarrayNodeWrapperLow,
)
from tests.resources.test_harness.subarray_node_with_csp_low import (
    SubarrayNodeCspWrapperLow,
)
from tests.resources.test_harness.utils.common_utils import JsonFactory

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


def get_input_str(path):
    """
    Returns input json string
    :rtype: String
    """
    with open(path, "r", encoding="UTF-8") as file:
        input_arg = file.read()
    return input_arg


@pytest.fixture()
def json_factory():
    """
    Json factory for getting json files
    """

    def _get_json(slug):
        return get_input_str(join(dirname(__file__), "data", f"{slug}.json"))

    return _get_json


TELESCOPE_ENV = os.getenv("TELESCOPE")

TIMEOUT = 200


def update_configure_json(
    configure_json: str,
    scan_duration: float,
    transaction_id: str,
    scan_type: str,
    config_id: str,
) -> str:
    """
    Returns a json with updated values for the given keys
    """
    config_dict = json.loads(configure_json)

    config_dict["tmc"]["scan_duration"] = scan_duration
    config_dict["transaction_id"] = transaction_id
    config_dict["sdp"]["scan_type"] = scan_type
    config_dict["csp"]["common"]["config_id"] = config_id
    return json.dumps(config_dict)


def update_scan_json(scan_json: str, scan_id: int, transaction_id: str) -> str:
    """
    Returns a json with updated values for the given keys
    """
    scan_dict = json.loads(scan_json)

    scan_dict["scan_id"] = scan_id
    scan_dict["transaction_id"] = transaction_id
    return json.dumps(scan_dict)


@pytest.fixture()
def change_event_callbacks() -> MockTangoEventCallbackGroup:
    """subarray_node
    Return a dictionary of Tango device change event callbacks with
    asynchrony support.

    :return: a collections.defaultdict that returns change event
        callbacks by name.
    """
    return MockTangoEventCallbackGroup(
        "longRunningCommandResult",
        timeout=50.0,
    )


@pytest.fixture()
def central_node_low() -> CentralNodeWrapperLow:
    """Return CentralNode for Low Telescope and calls tear down"""
    central_node_low = CentralNodeWrapperLow()
    yield central_node_low
    # this will call after test complete
    central_node_low.tear_down()


@pytest.fixture()
def subarray_node_low() -> SubarrayNodeWrapperLow:
    """Return SubarrayNode and calls tear down"""
    subarray = SubarrayNodeWrapperLow()
    yield subarray
    # this will call after test complete
    subarray.tear_down()


@pytest.fixture()
def subarray_node_real_csp_low() -> SubarrayNodeCspWrapperLow:
    """Return SubarrayNode and calls tear down"""
    subarray = SubarrayNodeCspWrapperLow()
    yield subarray
    # this will call after test complete
    subarray.tear_down()


@pytest.fixture()
def central_node_real_csp_low() -> CentralNodeCspWrapperLow:
    """Return CentralNode for Low Telescope and calls tear down"""
    central_node_low = CentralNodeCspWrapperLow()
    yield central_node_low
    # this will call after test complete
    central_node_low.tear_down()


@pytest.fixture()
def command_input_factory() -> JsonFactory:
    """Return Json Factory"""
    return JsonFactory()


@pytest.fixture()
def simulator_factory() -> SimulatorFactory:
    """Return Simulator Factory for Low Telescope"""
    return SimulatorFactory()


@pytest.fixture(scope="module")
def stored_unique_id():
    """store the unique_ids"""
    return []


@pytest.fixture()
def event_recorder() -> EventRecorder:
    """Return EventRecorder and clear events"""
    event_rec = EventRecorder()
    yield event_rec
    event_rec.clear_events()


@pytest.fixture(scope="session", autouse=True)
def set_admin_mode_mccs():
    """Fixture to set admin mode values"""
    set_admin_mode_values_mccs()


def wait_for_obsstate_state_change(
    target_mode: int, device: str, timeout_seconds: int
):
    """Returns True if the pointingState is changed to a expected value"""
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        if device.obsState.value == target_mode:
            return True
        time.sleep(1)

    return False


def updated_assign_str(assign_json: str, station_id: int) -> str:
    """
    Returns a json with updated values for the given keys
    """
    assign_json = json.loads(assign_json)

    for subarray_beam in assign_json["mccs"]["subarray_beams"]:
        for aperture in subarray_beam["apertures"]:
            aperture["station_id"] = station_id

    updated_assign_str = json.dumps(assign_json)
    return updated_assign_str


@given("the Telescope is in ON state")
def telescope_is_in_on_state(central_node_low, event_recorder):
    """Move the telescope to the ON state and verify the state change.

    Args:
        central_node_low (CentralNodeLow): An instance of the CentralNodeLow
        class representing the central node.
        event_recorder (EventRecorder): An instance of the EventRecorder class
        for recording events.

    """
    central_node_low.move_to_on()
    event_recorder.subscribe_event(
        central_node_low.central_node, "telescopeState"
    )
    assert event_recorder.has_change_event_occurred(
        central_node_low.central_node,
        "telescopeState",
        DevState.ON,
    )
