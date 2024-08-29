import copy
import functools
import os
import time
from datetime import datetime
from logging import getLogger
from threading import Event, RLock, Timer
from typing import Callable, Dict, List, Tuple

import pandas as pd
import tango
from ska_ser_logging.configuration import configure_logging

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
        self,
        attributes_dictionary: Dict[str, Dict[str, List]],
        timeout: int = 100,
    ) -> None:
        """Initialization method for the AttributeEventWatcher class."""
        self.__attributes_to_watch: Dict[str, Dict[str, List]] = copy.deepcopy(
            attributes_dictionary
        )
        self.__expected_correct_events_count: int = 0
        self.__received_correct_events_count: int = 0
        self.__stop: bool = False
        self.__init_time: datetime = datetime.utcnow()
        self.__events_count_lock: RLock = RLock()
        self.__received_all_events = Event()
        self.__timeout_event: Event = Event()
        self.__timeout_thread: Timer = Timer(timeout, self.set_timeout_event)
        self.__watcher_id: str = ""
        self.subscription_proxies_and_ids: Dict[tango.DeviceProxy, List] = {}

        for attribute_events in self.__attributes_to_watch.values():
            self.__expected_correct_events_count += sum(
                len(expected_values)
                for expected_values in attribute_events.values()
            )

        LOGGER.debug(
            "Initialization of AttributeEventWatcher class completed with the"
            + " following details: \nAttribute dictionary: %s\nExpected "
            + "Events count: %s",
            self.__attributes_to_watch,
            self.__expected_correct_events_count,
        )

    def stop_watching(self) -> None:
        """A method to stop watching the attribute changes and unsubscribing
        all event subscriptions"""
        LOGGER.debug("Stopping the watch loop and unsubscribing to events.")
        self.__stop = True
        self.__timeout_thread.cancel()

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
        LOGGER.debug("Timeout occurred, setting the timeout event")
        self.__timeout_event.set()

    def set_watcher_id(self, watcher_id: str) -> None:
        """Set the Watcher ID to improve logging."""
        LOGGER.debug("Setting the watcher id to: %s", watcher_id)
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
                    device_proxy.read_attribute(attribute_name).value
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
            "Missed events are the values of values in the dictionary: %s",
            self.__attributes_to_watch,
        )

    def read_attribute_values_to_ensure_completion(self) -> bool:
        """After the timeout has occurred, read the attribute values to check
        if the necessary states were reached and it was a case of missing event
        or if it actually failed.

        :returns: bool
            True if event missing
            False if failure
        """
        # Read all remaining attribute values to check if they are correct
        for (
            device_name,
            attributes_dictionary,
        ) in self.__attributes_to_watch.items():
            for (
                attribute_name,
                expected_values,
            ) in attributes_dictionary.items():
                if expected_values:
                    device_proxy = tango.DeviceProxy(device_name)
                    attribute_value = device_proxy.read_attribute(
                        attribute_name
                    ).value

                    # If any value is incorrect return False
                    if attribute_value != expected_values[-1]:
                        return False

        # All correct, return True
        return True

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
                attribute_value,
            )
            return None

        LOGGER.debug(
            "Received an event while waiting for command completion."
            + " %s/%s: %s",
            device_name,
            attribute_name,
            attribute_value,
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

        LOGGER.debug(
            "Expected value list for the attribute: %s is %s",
            attribute_name,
            expected_value_list,
        )
        if attribute_value == expected_value_list[0]:
            # One of the expected events have been seen, removing it from
            # expectations
            self.__attributes_to_watch[device_name][
                attribute_name
            ] = expected_value_list[1:]

            # Updating the received events count
            with self.__events_count_lock:
                self.__received_correct_events_count += 1
                LOGGER.debug(
                    "Updated the received events count to: %s",
                    self.__received_correct_events_count,
                )

                if (
                    self.__expected_correct_events_count
                    == self.__received_correct_events_count
                ):
                    LOGGER.debug("All events received!")
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
                if self.read_attribute_values_to_ensure_completion():
                    LOGGER.exception(
                        "Timeout occurred while waiting for attribute events, "
                        + "but the device states are as expected. Events "
                        + "were missed from the following dictionary: %s",
                        self.__attributes_to_watch,
                    )
                    self.stop_watching()
                else:
                    self.log_states()
                    LOGGER.error(
                        "Timeout occurred while waiting for attribute events."
                    )
                    raise TimeoutError(
                        "Timeout occurred while waiting for attribute events. "
                        + f"Expected: {self.__expected_correct_events_count}"
                        + " events, received only:"
                        + f" {self.__received_correct_events_count}"
                        + "\nMissed events are the part of following "
                        + f"dictionary: {self.__attributes_to_watch}"
                    )

            if self.__received_all_events.is_set():
                self.stop_watching()

            time.sleep(1)


def wait_for_command_completion(
    attributes_dictionary: Dict[str, Dict[str, List]], timeout: int = 100
) -> Callable[[Callable], Callable]:
    """Wait on attribute events for command completion based on the mapping
    of device names and expected attribute values.

    :param attributes_dictionary: A list of all attributes to monitor with
        device FQDNs, attribute name and expected value/values
        Example: {
            "ska_low/tm_subarray_node/1": {
                "obsState": [ObsState.RESOURCING, ObsState.IDLE]
            }
        }
    :type attributes_dictionary: Dict[str, Dict[str, List]]
    :param timeout: Timeout for attribute watcher
    :type timeout: int, default=100

    :returns: `Callable[Callable, Callable]`
    """
    LOGGER.debug(
        "Decorator called with values- \nAttributes to watch: %s\nTimeout: %s",
        attributes_dictionary,
        timeout,
    )

    def decorator_wait_for_command_completion(func: Callable) -> Callable:
        """Decorator method for the above function"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Tuple:
            """Wrapper method for the wait function"""
            watcher = AttributeEventWatcher(attributes_dictionary, timeout)
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
