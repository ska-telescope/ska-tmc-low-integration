import pytest
from ska_tango_base.control_model import HealthState, ObsState

from tests.resources.test_harness.helpers import (
    get_device_simulators,
    prepare_json_args_for_commands,
)


class TestSubarrayHealthState(object):
    """This class implement test cases to verify HealthState
    of Subarray Node.
    This tests implement rows of following excel sheet
    https://docs.google.com/spreadsheets/d/1XbNb8We7fK-EhmOcw3S-h0V_Pu-WAfPTkEd13MSmIns/edit#gid=747888622
    """

    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_ok(
        self, subarray_node, simulator_factory, event_recorder
    ):
        # Row 1
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        csp_sa_sim.SetDirectHealthState(HealthState.OK)
        sdp_sa_sim.SetDirectHealthState(HealthState.OK)
        dish_master_sim_1.SetDirectHealthState(HealthState.OK)
        dish_master_sim_2.SetDirectHealthState(HealthState.OK)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")

        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim, "healthState", HealthState.OK
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim, "healthState", HealthState.OK
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1, "healthState", HealthState.OK
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2, "healthState", HealthState.OK
        )

        # Subarray node react automatically
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.OK,
        ), "Expected Subarray Node HealthState to be OK"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            (
                HealthState.FAILED,
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
                HealthState.FAILED,
                HealthState.OK,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_failed_when_csp_or_sdp_failed(
        self,
        subarray_node,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        # Row 2 to 4
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        csp_sa_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sa_sim.SetDirectHealthState(sdp_subarray_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim,
            "healthState",
            csp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim,
            "healthState",
            sdp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1,
            "healthState",
            dish_master1_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2,
            "healthState",
            dish_master2_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.FAILED,
        ), "Expected Subarray Node HealthState to be FAILED"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            (
                HealthState.UNKNOWN,
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
                HealthState.UNKNOWN,
                HealthState.OK,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_failed_when_csp_or_sdp_unknown(
        self,
        subarray_node,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        # Row 7 to 9
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        csp_sa_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sa_sim.SetDirectHealthState(sdp_subarray_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim,
            "healthState",
            csp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim,
            "healthState",
            sdp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1,
            "healthState",
            dish_master1_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2,
            "healthState",
            dish_master2_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.UNKNOWN,
        ), "Expected Subarray Node HealthState to be UNKNOWN"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            (
                HealthState.DEGRADED,
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
                HealthState.DEGRADED,
                HealthState.OK,
                HealthState.OK,
            ),
        ],
    )
    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_degraded_when_csp_or_sdp_degraded(
        self,
        subarray_node,
        simulator_factory,
        event_recorder,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        # Row 12 to 14
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        csp_sa_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sa_sim.SetDirectHealthState(sdp_subarray_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim,
            "healthState",
            csp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim,
            "healthState",
            sdp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1,
            "healthState",
            dish_master1_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2,
            "healthState",
            dish_master2_health_state,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.DEGRADED,
        ), "Expected Subarray Node HealthState to be DEGRADED"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
            (
                HealthState.OK,
                HealthState.OK,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
            (
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.FAILED,
                HealthState.FAILED,
            ),
        ],
    )
    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_failed_when_all_dish_failed(
        self,
        subarray_node,
        simulator_factory,
        event_recorder,
        command_input_factory,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        # Row 5 and 6
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        self._assign_dishes_to_subarray(
            subarray_node, command_input_factory, event_recorder
        )

        csp_sa_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sa_sim.SetDirectHealthState(sdp_subarray_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim,
            "healthState",
            csp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim,
            "healthState",
            sdp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1,
            "healthState",
            dish_master1_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2,
            "healthState",
            dish_master2_health_state,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.FAILED,
        ), "Expected Subarray Node HealthState to be FAILED"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
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
                HealthState.OK,
                HealthState.OK,
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
            ),
            (
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
                HealthState.UNKNOWN,
            ),
        ],
    )
    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_failed_when_dish_unknown(
        self,
        subarray_node,
        simulator_factory,
        event_recorder,
        command_input_factory,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        # Row 10 and 11
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        self._assign_dishes_to_subarray(
            subarray_node, command_input_factory, event_recorder
        )

        csp_sa_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sa_sim.SetDirectHealthState(sdp_subarray_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim,
            "healthState",
            csp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim,
            "healthState",
            sdp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1,
            "healthState",
            dish_master1_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2,
            "healthState",
            dish_master2_health_state,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.UNKNOWN,
        ), "Expected Subarray Node HealthState to be UNKNOWN"

    @pytest.mark.parametrize(
        "csp_subarray_health_state, sdp_subarray_health_state, \
        dish_master1_health_state, dish_master2_health_state",
        [
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
                HealthState.OK,
                HealthState.OK,
                HealthState.DEGRADED,
                HealthState.DEGRADED,
            ),
            (
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.DEGRADED,
                HealthState.DEGRADED,
            ),
        ],
    )
    @pytest.mark.skip("pipeline issue")
    @pytest.mark.SKA_mid
    def test_health_state_degraded_when_one_or_more_dish_degraded_or_failed(
        self,
        subarray_node,
        simulator_factory,
        event_recorder,
        command_input_factory,
        csp_subarray_health_state,
        sdp_subarray_health_state,
        dish_master1_health_state,
        dish_master2_health_state,
    ):
        # Row 15 to 17
        (
            csp_sa_sim,
            sdp_sa_sim,
            dish_master_sim_1,
            dish_master_sim_2,
        ) = get_device_simulators(simulator_factory)

        self._assign_dishes_to_subarray(
            subarray_node, command_input_factory, event_recorder
        )

        csp_sa_sim.SetDirectHealthState(csp_subarray_health_state)
        sdp_sa_sim.SetDirectHealthState(sdp_subarray_health_state)
        dish_master_sim_1.SetDirectHealthState(dish_master1_health_state)
        dish_master_sim_2.SetDirectHealthState(dish_master2_health_state)
        event_recorder.subscribe_event(csp_sa_sim, "healthState")
        event_recorder.subscribe_event(sdp_sa_sim, "healthState")
        event_recorder.subscribe_event(dish_master_sim_1, "healthState")
        event_recorder.subscribe_event(dish_master_sim_2, "healthState")
        event_recorder.subscribe_event(
            subarray_node.subarray_node, "healthState"
        )
        assert event_recorder.has_change_event_occurred(
            csp_sa_sim,
            "healthState",
            csp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            sdp_sa_sim,
            "healthState",
            sdp_subarray_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_1,
            "healthState",
            dish_master1_health_state,
        )

        assert event_recorder.has_change_event_occurred(
            dish_master_sim_2,
            "healthState",
            dish_master2_health_state,
        )
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node,
            "healthState",
            HealthState.DEGRADED,
        ), "Expected Subarray Node HealthState to be DEGRADED"

    def _assign_dishes_to_subarray(
        self, subarray_node, command_input_factory, event_recorder
    ):
        subarray_node.move_to_on()
        subarray_node.force_change_of_obs_state("EMPTY")
        input_json = prepare_json_args_for_commands(
            "assign_resources_mid", command_input_factory
        )

        event_recorder.subscribe_event(subarray_node.subarray_node, "obsState")

        subarray_node.execute_transition("AssignResources", argin=input_json)
        assert event_recorder.has_change_event_occurred(
            subarray_node.subarray_node, "obsState", ObsState.IDLE
        ), "Waiting for subarray node to complete"
