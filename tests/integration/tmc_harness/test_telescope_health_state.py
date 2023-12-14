import pytest
from ska_tango_base.control_model import HealthState

from tests.resources.test_harness.helpers import get_master_device_simulators


class TestTelescopeHealthState(object):
    """This class implement test cases to verify telescopeHealthState
    of CentralNode
    This tests implement rows of decision table for telescopeHealthState,
    following excel sheet
    https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=825874621
    """

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            # decision table row 5 to row 9
            (
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.SKA_mid
    def test_telescope_health_state_failed(
        self,
        central_node_mid,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_master_device_simulators(simulator_factory)
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.FAILED,
        )

    @pytest.mark.skip(reason="Requires new SubarrayNode image version")
    @pytest.mark.SKA_mid
    def test_telescope_state_ok(
        self,
        central_node_mid,
        subarray_node,
        event_recorder,
        simulator_factory,
    ):
        # decision table row 3
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_master_device_simulators(simulator_factory)

        csp_master_sim.SetDirectHealthState(HealthState.OK)
        sdp_master_sim.SetDirectHealthState(HealthState.OK)
        dish_master_sim_1.SetDirectHealthState(HealthState.OK)
        dish_master_sim_2.SetDirectHealthState(HealthState.OK)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.OK,
        ), "Expected Telescope HealthState to be OK"

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            # decision table row 11 to row 15
            (
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
            ),
            (
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.DEGRADED,
            ),
        ],
    )
    @pytest.mark.SKA_mid
    def test_telescope_health_state_degraded(
        self,
        central_node_mid,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_master_device_simulators(simulator_factory)
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.DEGRADED,
        ), "Expected Telescope HealthState to be DEGRADED"

    @pytest.mark.parametrize(
        "csp_master_health_state, sdp_master_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            # decision table row 17 to row 21
            (
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
            ),
            (
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
            ),
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
            ),
        ],
    )
    @pytest.mark.SKA_mid
    def test_telescope_health_state_unknown(
        self,
        central_node_mid,
        simulator_factory,
        event_recorder,
        csp_master_health_state,
        sdp_master_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        (
            csp_master_sim,
            sdp_master_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_master_device_simulators(simulator_factory)
        csp_master_sim.SetDirectHealthState(csp_master_health_state)
        sdp_master_sim.SetDirectHealthState(sdp_master_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)

        event_recorder.subscribe_event(
            central_node_mid.central_node, "telescopeHealthState"
        )

        assert event_recorder.has_change_event_occurred(
            central_node_mid.central_node,
            "telescopeHealthState",
            HealthState.UNKNOWN,
        ), "Expected Telescope HealthState to be UNKNOWN"
