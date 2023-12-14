import pytest
from tango import DevState

from tests.resources.test_harness.helpers import get_master_device_simulators
from tests.resources.test_harness.utils.enums import DishMode


class TestMidCentralNodeStateTransition(object):
    @pytest.mark.SKA_mid
    def test_mid_centralnode_state_transitions(
        self,
        central_node_mid,
        event_recorder,
        simulator_factory,
    ):
        """
        Test to verify transitions that are triggered by On
        command and followed by a completion transition
        assuming that external subsystems work fine.
        Glossary:
        - "central_node_mid": fixture for a TMC CentralNode Mid under test
        which provides simulated master devices
        - "event_recorder": fixture for a MockTangoEventCallbackGroup
        for validating the subscribing and receiving events.
        - "simulator_factory": fixtur for creating simulator devices for
        mid Telescope respectively.
        """
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim1,
            dish_master_sim2,
        ) = get_master_device_simulators(simulator_factory)

        event_recorder.subscribe_event(csp_master_sim, "State")
        event_recorder.subscribe_event(sdp_master_sim, "State")
        event_recorder.subscribe_event(dish_master_sim1, "DishMode")
        event_recorder.subscribe_event(dish_master_sim2, "DishMode")
        central_node_mid.move_to_on()

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
        # As there is inconsistancy between the states of Dish Master and other
        # subsystem that's why Dishmode is considered for DishMaster
        # transitions. Here is the link for reference.
        # https://confluence.skatelescope.org/display/SE/Subarray+obsMode+and+
        # Dish+states+and+modes

        assert event_recorder.has_change_event_occurred(
            dish_master_sim1,
            "DishMode",
            DishMode.STANDBY_FP,
        )
        assert event_recorder.has_change_event_occurred(
            dish_master_sim2,
            "DishMode",
            DishMode.STANDBY_FP,
        )
