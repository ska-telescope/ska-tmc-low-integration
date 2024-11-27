# Test Steps and Scenarios from tests/tmc_csp_new_ITH/test_telescope_state.py

Last updated on: 29 October 2024 12:07:20

## Scenarios

- ON to OFF - CMD TelescopeOff (`test_on_to_off`)
- ON to STANDBY - CMD TelescopeStandby (`test_on_to_standby`)
- OFF to ON - CMD TelescopeOn (`test_off_to_on`)

## Steps

### Given: a tracked telescope

**Function:** `tracked_telescope`

**Signature:**
```python
def tracked_telescope(event_tracer, tmc, csp):
```

**Description:**
A telescope where the event tracking is configured
to track the telescope state (over TMC central node and CSP devices).

---

### Given: the telescope is in OFF state

**Function:** `telescope_in_off_state`

**Signature:**
```python
def telescope_in_off_state(tmc):
```

**Description:**
Ensure the telescope is in the OFF state.

---

### When: the TelescopeOff command is sent to the telescope central node

**Function:** `send_telescope_off_command`

**Signature:**
```python
def send_telescope_off_command(event_tracer, tmc):
```

**Description:**
Send the TelescopeOff command to the telescope.

---

### When: the TelescopeStandby command is sent to the telescope central node

**Function:** `send_telescope_standby_command`

**Signature:**
```python
def send_telescope_standby_command(event_tracer, tmc):
```

**Description:**
Send the TelescopeStandby command to the telescope.

---

### When: the TelescopeOn command is sent to the telescope central node

**Function:** `send_telescope_on_command`

**Signature:**
```python
def send_telescope_on_command(event_tracer, tmc):
```

**Description:**
Send the TelescopeOn command to the telescope.

---

### Then: the telescope should transition to the OFF state

**Function:** `verify_off_state`

**Signature:**
```python
def verify_off_state(event_tracer, tmc, csp):
```

**Description:**
TMC and CSP devices transition to the OFF state.

---

### Then: the telescope should transition to the STANDBY state

**Function:** `verify_standby_state`

**Signature:**
```python
def verify_standby_state(event_tracer, tmc, csp):
```

**Description:**
TMC should transition to the STANDBY state.

---

### Then: the telescope should transition to the ON state

**Function:** `verify_on_state`

**Signature:**
```python
def verify_on_state(event_tracer, tmc, csp):
```

**Description:**
TMC and CSP devices transition to the ON state.

---

