# Test Steps and Scenarios from tests/tmc_csp_new_ITH/test_command_triggered.py

Last updated on: 29 October 2024 12:07:20

## Scenarios

- EMPTY to RESOURCING to IDLE - CMD AssignResources (`test_empty_to_resourcing_to_idle`)
- IDLE to CONFIGURING to READY - CMD Configure (`test_idle_to_configuring_to_ready`)
- IDLE to RESOURCING to IDLE - CMD AssignResources (`test_idle_to_resourcing_to_idle`)
- IDLE to RESOURCING to EMPTY - CMD ReleaseResources (`test_idle_to_resourcing_to_empty`)
- READY to SCANNING to READY- CMD Scan (`test_ready_to_scanning_to_ready`)
- READY to IDLE - CMD End (`test_ready_to_idle`)
- READY to CONFIGURING to READY - CMD Configure (`test_ready_to_configuring_to_ready`)
- SCANNING to READY - CMD End Scan (`test_scanning_to_ready`)

## Steps

### Given: the subarray {subarray} is in the EMPTY state

**Function:** `subarray_in_empty_state`

**Signature:**
```python
def subarray_in_empty_state(context_fixt, tmc):
```

**Description:**
Set the specified subarray to the EMPTY state.

This step uses the TMCSubarrayNodeFacade to force the subarray's
ObsState to EMPTY. It does this by calling the force_change_of_obs_state
method, which bypasses normal state transition checks. The method is
invoked with ObsState.EMPTY and an empty TestHarnessInputs,
ensuring a direct transition regardless of the current state.
The operation waits for completion.

The step also updates the starting_state in the test context data
to reflect this EMPTY state, which can be useful for test assertions
or subsequent test steps.

---

### When: the AssignResources command is sent to the subarray {subarray} and the Assigned event is induced

**Function:** `send_assign_resources_command`

**Signature:**
```python
def send_assign_resources_command(context_fixt, tmc):
```

**Description:**
Send the AssignResources command to the subarray.

This step uses the tmc to send an AssignResources command
to the specified subarray. It uses a pre-defined JSON input file,
modifies the subarray_id, and sends the command without waiting for
termination. The action result is stored in the context fixture.

---

### When: the AssignResources command is sent to the subarray {subarray} to assign additional resources

**Function:** `send_assign_additional_resources_command`

**Signature:**
```python
def send_assign_additional_resources_command(context_fixt, tmc):
```

**Description:**
Send the AssignResources command to assign additional resources.

This step is similar to the basic AssignResources command, but it's
intended to assign additional resources to the subarray. Currently,
it uses the same input as the basic command, but this is noted as
needing to be changed in the future.

---

### When: the ReleaseResources command is sent to the subarray {subarray} and the All released event is induced

**Function:** `send_release_resources_command`

**Signature:**
```python
def send_release_resources_command(context_fixt, tmc):
```

**Description:**
Send the ReleaseResources command to the subarray.

This step uses the tmc to send a ReleaseResources
command to the specified subarray. It uses a pre-defined JSON input
file, modifies the subarray_id, and sends the command without waiting
for termination. The action result is stored in the context fixture.

---

### When: the Configure command is sent to the subarray {subarray}

**Function:** `send_configure_command`

**Signature:**
```python
def send_configure_command(context_fixt, tmc):
```

**Description:**
Send the Configure command to the subarray.

This step uses the tmc to send a Configure command
to the specified subarray. It uses a pre-defined JSON input file and
sends the command without waiting for termination. The action result
is stored in the context fixture.

---

### When: the Scan command is sent to the subarray {subarray}

**Function:** `send_scan_command`

**Signature:**
```python
def send_scan_command(context_fixt, tmc):
```

**Description:**
Send the Scan command to the subarray.

This step uses the tmc to send a Scan command to the
specified subarray. It uses a pre-defined JSON input file and sends
the command without waiting for termination. The action result is
stored in the context fixture.

---

### When: the End command is sent to the subarray {subarray}

**Function:** `send_end_command`

**Signature:**
```python
def send_end_command(context_fixt, tmc):
```

**Description:**
Send the End command to the subarray.

This step uses the tmc to send an End command to the
specified subarray. It sends the command without waiting for termination
and stores the action result in the context fixture.

---

### When: the EndScan command is sent to the subarray {subarray}

**Function:** `send_end_scan_command`

**Signature:**
```python
def send_end_scan_command(context_fixt, tmc):
```

**Description:**
Send the EndScan command to the subarray.

This step uses the tmc to send an EndScan command to
the specified subarray. It sends the command without waiting for
termination and stores the action result in the context fixture.

---

### Then: the subarray {subarray} should transition to the RESOURCING state

**Function:** `verify_resourcing_state`

**Signature:**
```python
def verify_resourcing_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify the subarray's transition to the RESOURCING state.

This step checks that the ObsState attribute of the TMC Subarray Node,
CSP Subarray, and SDP Subarray devices all transition from the starting
state to the RESOURCING state. It uses the event_tracer to assert that
these state changes occur within a specified timeout. For the SDP device,
it also verifies that the correct Tango command was received. Finally,
it updates the starting state in the context fixture for subsequent steps.

---

### Then: the subarray {subarray} should transition to the IDLE state

**Function:** `verify_idle_state`

**Signature:**
```python
def verify_idle_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify the subarray's transition to the IDLE state.

This step checks that the ObsState attribute of the TMC Subarray Node,
CSP Subarray, and SDP Subarray devices all transition from the starting
state to the IDLE state. It uses the event_tracer to assert that these
state changes occur within a specified timeout.

---

### Then: the subarray {subarray} should transition to the EMPTY state

**Function:** `verify_empty_state`

**Signature:**
```python
def verify_empty_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify the subarray's transition to the EMPTY state.

This step checks that the ObsState attribute of the TMC Subarray Node,
CSP Subarray, and SDP Subarray devices all transition from the starting
state to the EMPTY state. It uses the event_tracer to assert that these
state changes occur within a specified timeout.

---

### Then: the subarray {subarray} should transition to the CONFIGURING state

**Function:** `verify_configuring_state`

**Signature:**
```python
def verify_configuring_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify the subarray's transition to the CONFIGURING state.

This step checks that the ObsState attribute of the TMC Subarray Node,
CSP Subarray, and SDP Subarray devices all transition from the starting
state to the CONFIGURING state. It uses the event_tracer to assert that
these state changes occur within a specified timeout. After verification,
it updates the starting state in the context fixture for subsequent steps.

---

### Then: the subarray {subarray} should transition to the READY state

**Function:** `verify_ready_state`

**Signature:**
```python
def verify_ready_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify the subarray's transition to the READY state.

This step checks that the ObsState attribute of the TMC Subarray Node,
CSP Subarray, and SDP Subarray devices all transition from the starting
state to the READY state. It uses the event_tracer to assert that these
state changes occur within a specified timeout. After verification, it
updates the starting state in the context fixture for subsequent steps.

---

### Then: the subarray {subarray} should transition to the SCANNING state

**Function:** `verify_scanning_state`

**Signature:**
```python
def verify_scanning_state(context_fixt, tmc, csp, sdp, event_tracer):
```

**Description:**
Verify the subarray's transition to the SCANNING state.

This step checks that the ObsState attribute of the TMC Subarray Node,
CSP Subarray, and SDP Subarray devices all transition from the starting
state to the SCANNING state. It uses the event_tracer to assert that these
state changes occur within a specified timeout. After verification, it
updates the starting state in the context fixture for subsequent steps.

---

### Then: the central node reports a longRunningCommand successful completion

**Function:** `verify_long_running_command_result_on_central_node`

**Signature:**
```python
def verify_long_running_command_result_on_central_node(context_fixt, tmc, event_tracer):
```

**Description:**
Verify the successful completion of a longRunningCommand on central node.

This step checks that the TMC Central Node reports a successful completion
of a longRunningCommand. It uses the event_tracer to assert that a change
event occurred on the longRunningCommandResult attribute within a specified
timeout. The expected result is derived from the context fixture.

---

### Then: the subarray {subarray} reports a longRunningCommand successful completion

**Function:** `verify_long_running_command_result_on_subarray`

**Signature:**
```python
def verify_long_running_command_result_on_subarray(context_fixt, tmc, event_tracer):
```

**Description:**
Verify the successful completion of a longRunningCommand on the subarray.

This step checks that the TMC Subarray Node reports a successful completion
of a longRunningCommand. It uses the event_tracer to assert that a change
event occurred on the longRunningCommandResult attribute within a specified
timeout. The expected result is derived from the context fixture.

---

