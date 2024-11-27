# Test Steps and Scenarios from tests/tmc_csp_new_ITH/test_abort.py

Last updated on: 29 October 2024 12:07:20

## Scenarios

- RESOURCING to ABORTING to ABORTED - CMD Abort (`test_resourcing_to_aborting_to_aborted`)
- IDLE to ABORTING to ABORTED - CMD Abort (`test_idle_to_aborting_to_aborted`)
- CONFIGURING to ABORTING to ABORTED - CMD Abort (`test_configuring_to_aborting_to_aborted`)
- READY to ABORTING to ABORTED - CMD Abort (`test_ready_to_aborting_to_aborted`)
- SCANNING to ABORTING to ABORTED - CMD Abort (`test_scanning_to_aborting_to_aborted`)
- ABORTED to RESTARTING to EMPTY - CMD Restart (`test_aborted_to_restarting`)

## Steps

### Given: the subarray {subarray} is in the ABORTED state

**Function:** `subarray_in_aborted_state`

**Signature:**
```python
def subarray_in_aborted_state(context_fixt, tmc, default_commands_inputs):
```

**Description:**
Ensure the subarray is in the ABORTED state.

This step performs the following actions:
1. Sets the starting_state in the test context to ABORTED.
2. Forces the subarray to the IDLE state to ensure it's in a state
   where Abort can be sent.
3. Sends the Abort command to transition the subarray
   to the ABORTED state.

---

### When: the Abort command is sent to the subarray {subarray}

**Function:** `send_abort_command`

**Signature:**
```python
def send_abort_command(context_fixt, tmc, event_tracer):
```

**Description:**
Send the Abort command to the subarray.

This step sends the Abort command without waiting for termination.
If the starting state is transient, it verifies that the
expected state transition hasn't occurred prematurely.

---

### When: the Restart command is sent to the subarray {subarray}

**Function:** `send_restart_command`

**Signature:**
```python
def send_restart_command(context_fixt, tmc):
```

**Description:**
Send the Restart command to the subarray.

This step sends the Restart command without waiting for termination.

---

### Then: the subarray {subarray} should transition to the ABORTING state

**Function:** `verify_aborting_state`

**Signature:**
```python
def verify_aborting_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify that the subarray transitions to the ABORTING state.

This step checks that the TMC Subarray Node, CSP Subarray, and SDP Subarray
devices transition to the ABORTING state within the specified timeout.
It verifies the previous state for the TMC Subarray Node.

---

### Then: the subarray {subarray} should transition to the ABORTED state

**Function:** `verify_aborted_state`

**Signature:**
```python
def verify_aborted_state(tmc, csp, sdp, event_tracer):
```

**Description:**
Verify that the subarray transitions to the ABORTED state.

This step checks that all relevant devices (TMC, CSP, SDP) transition from
ABORTING to ABORTED state within the specified timeout.

---

### Then: the subarray {subarray} should transition to the RESTARTING state

**Function:** `verify_restarting_state`

**Signature:**
```python
def verify_restarting_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify that the subarray transitions to the RESTARTING state.

This step performs the following actions:
1. Checks that all relevant devices transition from
   ABORTED to RESTARTING state
   within the specified timeout.
2. Updates the starting state in the test context to RESTARTING.
3. Verifies that the correct Tango command (Aborted) was received
   by the SDP emulator.

---

### Then: the subarray {subarray} should transition to the EMPTY state

**Function:** `verify_empty_state`

**Signature:**
```python
def verify_empty_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify that the subarray transitions to the EMPTY state.

This step checks that all relevant devices (TMC, CSP, SDP) transition from
the previous state (stored in the test context) to the EMPTY state within
the specified timeout.

---

