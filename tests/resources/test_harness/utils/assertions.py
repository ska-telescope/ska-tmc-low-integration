import json
from datetime import datetime
from typing import Any

import tango
from ska_control_model import ResultCode
from ska_tango_testing.integration.assertions import (
    _get_tracer,
    _print_passed_event_args,
)


def has_desired_result_code_message_in_lrcr_event(
    assertpy_context: Any,
    device_name: str,
    exception_messages: list[str],
    unique_id: str,
    result_code: ResultCode,
):
    """Methos

    Args:
        assertpy_context (Any): _description_
        device_name (str): _description_
        exception_messages (list[str]): _description_
        unique_id (str): _description_
        result_code (ResultCode): _description_

    Returns:
        _type_: _description_
    """
    # check assertpy_context has a tracer object
    tracer = _get_tracer(assertpy_context)
    # quick trick: if device_name is a device proxy, get the name
    if isinstance(device_name, tango.DeviceProxy):
        device_name = device_name.dev_name()

    # start time is needed in case of error
    run_query_time = datetime.now()

    result = tracer.query_events(
        lambda e: e.has_device(device_name)
        and e.has_attribute("longRunningCommandResult")
        and e.attribute_value[0] == unique_id
        and json.loads(e.attribute_value[1])[0] == result_code
        and all(
            exception_message in json.loads(e.attribute_value[1])[1]
            for exception_message in exception_messages
        ),
        timeout=getattr(assertpy_context, "event_timeout", None),
    )
    if len(result) == 0:
        event_list = "\n".join([str(event) for event in tracer.events])
        msg = "Expected to find an event matching the predicate"
        if hasattr(assertpy_context, "event_timeout"):
            msg += f" within {assertpy_context.event_timeout} seconds"
        else:
            msg += " in already existing events"
        msg += ", but none was found.\n\n"
        msg += f"Events captured by TANGO_TRACER:\n{event_list}"
        msg += "\n\nTANGO_TRACER Query arguments: "
        msg += _print_passed_event_args(
            device_name,
            "longRunningCommandResult",
            (unique_id, result_code, exception_messages),
        )
        msg += "\nQuery start time: " + str(run_query_time)
        msg += "\nQuery end time: " + str(datetime.now())

        return assertpy_context.error(msg)

    return assertpy_context
