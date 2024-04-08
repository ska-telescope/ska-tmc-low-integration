"""Enum to used in tests
"""
import enum
from enum import IntEnum, unique


@unique
class SubarrayState(IntEnum):
    ON = 0
    OFF = 1
    FAULT = 8
    INIT = 9
    UNKNOWN = 13


@unique
class SubarrayObsState(IntEnum):
    EMPTY = 0
    RESOURCING = 1
    IDLE = 2
    CONFIGURING = 3
    READY = 4
    SCANNING = 5


@unique
class SimulatorDeviceType(IntEnum):
    LOW_CSP_DEVICE = 5
    LOW_SDP_DEVICE = 6
    LOW_CSP_MASTER_DEVICE = 7
    LOW_SDP_MASTER_DEVICE = 8
    MCCS_MASTER_DEVICE = 9
    MCCS_SUBARRAY_DEVICE = 10


class FaultType(enum.IntEnum):
    """Enum class for raising various exceptions from helper devices."""

    NONE = 0
    COMMAND_NOT_ALLOWED = 1
    FAILED_RESULT = 2
    LONG_RUNNING_EXCEPTION = 3
    STUCK_IN_INTERMEDIATE_STATE = 4
    STUCK_IN_OBSTATE = 5


class ResultCode(enum.IntEnum):
    """Python enumerated type for command result codes."""

    OK = 0
    """The command was executed successfully."""

    STARTED = 1
    """The command has been accepted and will start immediately."""

    QUEUED = 2
    """The command has been accepted and will be executed at a future time."""

    FAILED = 3
    """The command could not be executed."""

    UNKNOWN = 4
    """The status of the command is not known."""

    REJECTED = 5
    """The command execution has been rejected."""

    NOT_ALLOWED = 6
    """The command is not allowed to be executed."""

    ABORTED = 7
    """The command in progress has been aborted."""


class AdminMode(enum.IntEnum):
    """
    Python enumerated type for device admin mode.

    An admin mode represents user intent as to how the component under
    control will be used.
    """

    ONLINE = 0
    """
    The component under control can be used for normal operations, such
    as observing. While in this mode, the control system actively
    monitors and controls the component under control.

    Control system elements that implement admin mode as a read-only
    attribute shall always report the admin mode to be ``ONLINE``.
    """

    OFFLINE = 1
    """
    The component under control shall not be monitored or controlled by
    the control system.

    Either the component under control shall not be used at all, or it
    is under external control (such as the local control of a field
    technician).

    While in this mode, the control system reports its state as
    ``DISABLE``. Since monitoring of the component is not occurring,
    the control system does not issue alarms, alerts and other events.
    """

    MAINTENANCE = 2
    """
    The component under control can be used for maintainance purposes,
    such as testing, debugging or commissioning, as part of a
    "maintenance subarray".. It may not be used for normal operations.

    While in this mode, the control system actively monitors and
    controls its component, but may only support a subset of normal
    functionality. Alarms and alerts will usually be suppressed.

    ``MAINTENANCE`` mode has different meaning for different components,
    depending on the context and functionality. Some entities may
    implement different behaviour when in ``MAINTENANCE`` mode. For each
    Tango device, the difference in behaviour and functionality in
    ``MAINTENANCE`` mode shall be documented.
    """

    NOT_FITTED = 3
    """
    The component cannot be used for any purposes because it is not
    fitted; for example, faulty equipment has been removed and not
    yet replaced, leaving nothing `in situ` to monitor.

    While in this mode, the control system reports state ``DISABLED``.
    All monitoring and control functionality is disabled because there
    is no component to monitor.
    """

    RESERVED = 4
    """
    The component is fitted, but only for redundancy purposes. It is
    additional equipment that does not take part in operations at this
    time, but is ready to take over when the operational
    equipment fails.

    While in this mode, the control system reports state ``DISABLED``.
    All monitoring and control functionality is disabled.
    """
