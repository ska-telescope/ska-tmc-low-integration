import functools
import os
import time
from contextlib import contextmanager
from datetime import datetime
from logging import getLogger
from threading import Event, RLock, Timer
from typing import Callable, Dict, List, Tuple

import pandas as pd
import tango
from ska_control_model import ObsState
from ska_ser_logging.configuration import configure_logging

from tests.resources.test_harness.utils.wait_helpers import Waiter
from tests.resources.test_support.common_utils.base_utils import DeviceUtils
from tests.resources.test_support.common_utils.common_helpers import Resource

MCCS_SIMULATION_ENABLED = os.getenv("MCCS_SIMULATION_ENABLED")
if MCCS_SIMULATION_ENABLED.lower() == "false":
    TIMEOUT = 600  # MCCS lower level devices take more time to turn on and off
else:
    TIMEOUT = 500

configure_logging()
LOGGER = getLogger(__name__)


class AttributeEventWatcher:
    """A class for watching attribute changes through events."""

    def __init__(
        self, attributes_list: Dict[str, Dict[str, List]], timeout: int = 100
    ) -> None:
        self.__attributes_to_watch: Dict[
            str, Dict[str, List]
        ] = attributes_list
        self.__expected_correct_events_count: int = 0
        self.__received_correct_events_count: int = 0
        for attribute_events in self.__attributes_to_watch.values():
            self.__expected_correct_events_count += sum(
                len(expected_values)
                for expected_values in attribute_events.values()
            )
        self.__stop: bool = False
        self.__init_time: datetime = datetime.utcnow()
        self.__events_count_lock: RLock = RLock()
        self.__received_all_events = Event()
        self.__timeout_event: Event = Event()
        self.__timeout_thread: Timer = Timer(timeout, self.set_timeout_event)
        self.__watcher_id: str = ""
        self.subscription_proxies_and_ids: Dict[tango.DeviceProxy, List] = {}

    def stop_watching(self) -> None:
        """A method to stop watching the attribute changes and unsubscribing
        all event subscriptions"""
        self.__stop = True
        with self.__events_count_lock:
            self.__received_correct_events_count = 0
        for (
            proxy,
            subscribtion_ids,
        ) in self.subscription_proxies_and_ids.items():
            for subscribtion_id in subscribtion_ids:
                proxy.unsubscribe_event(subscribtion_id)

    def set_timeout_event(self) -> None:
        """Set the timeout event once called."""
        self.__timeout_event.set()

    def set_watcher_id(self, watcher_id: str) -> None:
        """Set the Watcher ID to improve logging."""
        self.__watcher_id = watcher_id

    def log_states(self) -> None:
        """This method logs all the attribute values that the watcher was
        watching in a neat table."""
        states = []
        devices = []
        attributes = []

        # Extracting information to log
        for (
            device_fqdn,
            attributes_dictionary,
        ) in self.__attributes_to_watch.items():
            device_proxy = tango.DeviceProxy(device_fqdn)
            for attribute_name in attributes_dictionary.keys():
                devices.append(device_fqdn)
                attributes.append(attribute_name)
                states.append(
                    ObsState(
                        device_proxy.read_attribute(attribute_name).value
                    ).name
                )

        # Creating and setting up a DataFrame
        pd.set_option("display.colheader_justify", "left")
        pd.set_option("display.expand_frame_repr", False)
        device_states = pd.DataFrame(
            {
                "Devices": devices,
                "AttributeName": attributes,
                "State": states,
            }
        )

        # Logging the DataFrame
        LOGGER.info(
            "\nFinal device states at timeout for id:%s :\n\n%s\n",
            self.__watcher_id,
            device_states.to_string(index=False, justify="left"),
        )
        LOGGER.info(
            "Missed events are: %s",
            self.__attributes_to_watch,
        )

    def event_callback(self, event_data: tango.EventData) -> None:
        """A simple event callback method to check if the event has been
        received after starting the watcher and if the value is the expected
        value.

        :param event_data: The event data received from Tango
        :type event_data: tango.EventData

        :returns: None
        """
        attribute_name = event_data.attr_value.name.lower()
        attribute_value = event_data.attr_value.value
        device_name = event_data.device.dev_name()
        reception_time: datetime = event_data.attr_value.time.todatetime()
        if not self.is_event_recent(reception_time):
            LOGGER.debug(
                "Received an older event while waiting for command completion."
                + " %s/%s: %s",
                device_name,
                attribute_name,
                ObsState(attribute_value).name,
            )
            return None

        LOGGER.debug(
            "Received an event while waiting for command completion."
            + " %s/%s: %s",
            device_name,
            attribute_name,
            ObsState(attribute_value).name,
        )
        try:
            expected_value_list = self.__attributes_to_watch[device_name][
                attribute_name
            ]
        except KeyError as key_error:
            LOGGER.error(
                "Error occurred while accessing an attribute: %s from the "
                + "dictionary: %s for the command id: %s.\n This was with an "
                + "exception: %s",
                attribute_name,
                self.__attributes_to_watch,
                self.__watcher_id,
                key_error,
            )
            return None
        if expected_value_list == []:
            # This means all the necessary events were read
            return None
        if attribute_value == expected_value_list[0]:
            # One of the expected events have been seen, removing it from
            # expectations
            self.__attributes_to_watch[device_name][
                attribute_name
            ] = expected_value_list[1:]
            # Updating the received events count
            with self.__events_count_lock:
                self.__received_correct_events_count += 1
                if (
                    self.__expected_correct_events_count
                    == self.__received_correct_events_count
                ):
                    self.__received_all_events.set()
            return None
        return None

    def is_event_recent(self, reception_time: datetime) -> bool:
        """Check and return if the received event is received after starting
        the watcher

        :param reception_time: Time of receiving the event
        :type reception_time: datetime

        :returns: bool
        """
        return bool((reception_time - self.__init_time).total_seconds() > 0.0)

    def watch(self) -> None:
        """A method that subscribes to the events for all the attributes to
        watch and verifies them reaching the expected values."""
        # Starting the timeout thread
        self.__timeout_thread.start()
        # Subscribing to all events
        for device, attribute_dictionary in self.__attributes_to_watch.items():
            device_proxy = tango.DeviceProxy(device)
            subscribtion_ids = []
            for attribute in attribute_dictionary.keys():
                subscribtion_id = device_proxy.subscribe_event(
                    attribute,
                    tango.EventType.CHANGE_EVENT,
                    self.event_callback,
                    stateless=True,
                )
                subscribtion_ids.append(subscribtion_id)
            self.subscription_proxies_and_ids[device_proxy] = subscribtion_ids

        while not self.__stop:
            if self.__timeout_event.is_set():
                self.log_states()
                LOGGER.error(
                    "Timeout occurred while waiting for attribute events."
                )
                raise TimeoutError(
                    "Timeout occurred while waiting for attribute events."
                )
            if self.__received_all_events.is_set():
                self.stop_watching()
            time.sleep(1)


def wait_for_command_completion(
    attributes_list: Dict[str, Dict[str, List]], timeout: int = 100
) -> Callable[[Callable], Callable]:
    """Wait on attribute events for command completion based on the command
    name.

    This function refers to a mapping of commands with the related attributes
    to monitor.

    :param attribute_list: A list of all attributes to monitor with device
        FQDNs, attribute name and expected value/values
        Example: {
            "ska_low/tm_subarray_node/1": {
                "obsState": [ObsState.RESOURCING, ObsState.IDLE]
            }
        }
    :type attribute_list: Dict[str, Dict[str, List]]
    :param timeout: Timeout for attribute watcher
    :type timeout: int, default=100

    :returns: `Callable[Callable, Callable]`
    """

    def decorator_wait_for_command_completion(func: Callable) -> Callable:
        """Decorator method for the above function"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple:
            """Wrapper method for the wait function"""
            watcher = AttributeEventWatcher(attributes_list, timeout)
            result_code, unique_id = func(*args, **kwargs)
            LOGGER.info(
                "Command invoked with Result: %s and id: %s",
                result_code,
                unique_id,
            )
            watcher.set_watcher_id(unique_id[0])
            watcher.watch()
            return result_code, unique_id

        return wrapper

    return decorator_wait_for_command_completion


def sync_set_to_on(device_dict: dict):
    def decorator_sync_set_to_on(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_telescope_on()
            result = func(*args, **kwargs)
            the_waiter.wait(TIMEOUT)
            return result

        return wrapper

    return decorator_sync_set_to_on


def sync_set_to_off(device_dict: dict):
    def decorator_sync_set_to_off(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_off()
            result = func(*args, **kwargs)
            the_waiter.wait(TIMEOUT)
            return result

        return wrapper

    return decorator_sync_set_to_off


# defined as a context manager
@contextmanager
def sync_going_to_off(timeout=50, **kwargs):
    the_waiter = Waiter(**kwargs)
    the_waiter.set_wait_for_going_to_off()
    yield
    the_waiter.wait(timeout)


def sync_set_to_standby(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        the_waiter = Waiter(**kwargs)
        the_waiter.set_wait_for_going_to_standby()
        result = func(*args, **kwargs)
        the_waiter.wait(TIMEOUT)
        return result

    return wrapper


def sync_release_resources(device_dict, timeout=200):
    def decorator_sync_release_resources(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_empty()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_release_resources


def sync_assign_resources(device_dict):
    # defined as a decorator
    def decorator_sync_assign_resources(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            device = DeviceUtils(
                obs_state_device_names=[
                    device_dict.get("csp_subarray"),
                    device_dict.get("sdp_subarray"),
                    device_dict.get("tmc_subarraynode"),
                ]
            )
            device.check_devices_obsState("EMPTY")
            set_wait_for_obsstate = kwargs.get("set_wait_for_obsstate", True)
            result = func(*args, **kwargs)
            if set_wait_for_obsstate:
                the_waiter = Waiter(**device_dict)
                the_waiter.set_wait_for_assign_resources()
                the_waiter.wait(500)
            return result

        return wrapper

    return decorator_sync_assign_resources


def sync_abort(device_dict, timeout=1000):
    # define as a decorator
    def decorator_sync_abort(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_aborted()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_abort


def sync_restart(device_dict, timeout=500):
    # define as a decorator
    def decorator_sync_restart(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_going_to_empty()
            result = func(*args, **kwargs)
            the_waiter.wait(timeout)
            return result

        return wrapper

    return decorator_sync_restart


def sync_configure(device_dict):
    # defined as a decorator
    def decorator_sync_configure(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            invoked_from_ready = False
            the_waiter = Waiter(**device_dict)
            if Resource(device_dict.get("tmc_subarraynode")) == "READY":
                invoked_from_ready = True
            result = func(*args, **kwargs)
            if invoked_from_ready:
                the_waiter.set_wait_for_configuring()
                the_waiter.wait(500)
            the_waiter.set_wait_for_configure()
            the_waiter.wait(800)
            return result

        return wrapper

    return decorator_sync_configure


def sync_end(device_dict):
    # defined as a decorator
    def decorator_sync_end(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_idle()
            result = func(*args, **kwargs)
            the_waiter.wait(200)
            return result

        return wrapper

    return decorator_sync_end


def sync_endscan(device_dict):
    # defined as a decorator
    def decorator_sync_endscan(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            the_waiter = Waiter(**device_dict)
            the_waiter.set_wait_for_ready()
            result = func(*args, **kwargs)
            the_waiter.wait(200)
            return result

        return wrapper

    return decorator_sync_endscan
