"""Test Telescope on command in low"""
import pytest

from tests.conftest import LOGGER
from tests.resources.test_support.common_utils.telescope_controls import (
    BaseTelescopeControl,
)
from tests.resources.test_support.common_utils.tmc_helpers import (
    TmcHelper,
    tear_down,
)
from tests.resources.test_support.constant_low import (
    DEVICE_STATE_OFF_INFO,
    DEVICE_STATE_ON_INFO,
    DEVICE_STATE_STANDBY_INFO,
    ON_OFF_DEVICE_COMMAND_DICT,
    centralnode,
    tmc_subarraynode1,
)


@pytest.mark.SKA_low
@pytest.mark.skip(reason="Unskip after repository setup")
def test_telescope_on():
    """TelescopeOn() is executed."""
    try:
        telescope_control = BaseTelescopeControl()
        tmc_helper = TmcHelper(centralnode, tmc_subarraynode1)

        # Verify Telescope is Off/Standby
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_STANDBY_INFO, "State"
        )
        LOGGER.info("Starting up the Telescope")

        # Checking the availability of Telescope
        tmc_helper.check_telescope_availability()

        # Invoke TelescopeOn() command on TMC
        tmc_helper.set_to_on(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOn command is invoked successfully")

        # Verify State transitions after TelescopeOn
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_ON_INFO, "State"
        )
        # Checking the availability of Telescope
        tmc_helper.check_telescope_availability()

        # Invoke TelescopeOff() command on TMC
        tmc_helper.set_to_off(**ON_OFF_DEVICE_COMMAND_DICT)
        LOGGER.info("TelescopeOff command is invoked successfully")

        # Verify State transitions after TelescopeOff
        assert telescope_control.is_in_valid_state(
            DEVICE_STATE_OFF_INFO, "State"
        )
        LOGGER.info("test_telescope_on Tests complete.")

    except Exception as e:
        LOGGER.exception("The exception is: %s", e)
        tear_down(**ON_OFF_DEVICE_COMMAND_DICT)
