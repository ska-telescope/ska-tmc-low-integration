import logging

import pytest
from ska_ser_logging import configure_logging
from tango import DevState

from tests.resources.test_harness.utils.enums import SimulatorDeviceType

configure_logging(logging.DEBUG)
LOGGER = logging.getLogger(__name__)


class TestLowCentralNodeOnCommand:
    @pytest.mark.SKA_low
    def test_low_central_node_on_command(
        self,
        central_node_low,
        event_recorder,
        simulator_factory,
    ):
        """
        Test to verify transitions that are triggered by On
        command and followed by a completion transition
        assuming that external subsystems work fine.
        Glossary:
        - "central_node_low": fixture for a TMC CentralNode Low under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixture for creating simulator devices for
        low Telescope respectively.
        """
        csp_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_CSP_MASTER_DEVICE
        )
        sdp_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.LOW_SDP_MASTER_DEVICE
        )
        mccs_master_sim = simulator_factory.get_or_create_simulator_device(
            SimulatorDeviceType.MCCS_MASTER_DEVICE
        )
        event_recorder.subscribe_event(csp_master_sim, "State")
        event_recorder.subscribe_event(sdp_master_sim, "State")
        event_recorder.subscribe_event(mccs_master_sim, "State")
        event_recorder.subscribe_event(
            central_node_low.central_node, "telescopeState"
        )
        central_node_low.move_to_on()
        assert event_recorder.has_change_event_occurred(
            csp_master_sim,
            "State",
            DevState.ON,
        )
        assert event_recorder.has_change_event_occurred(
            sdp_master_sim,
            "State",
            DevState.ON,
        )
        assert event_recorder.has_change_event_occurred(
            mccs_master_sim,
            "State",
            DevState.ON,
        )
        assert event_recorder.has_change_event_occurred(
            central_node_low.central_node,
            "telescopeState",
            DevState.ON,
        )
