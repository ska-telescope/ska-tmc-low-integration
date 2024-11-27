# Feature
## Feature: test telescope state transactions

This feature covers transitions in the telescope state model
that are triggered by commands ON, OFF and STANDBY.

This set of tests is just a bare porting of the original tests
from the old ITH, and it is not meant to be exhaustive or stable.
It will likely evolve in the future.

Background:
- Given a tracked telescope

@XTP-62944 @XTP-62547 @XTP-28347
### Scenario: ON to OFF - CMD TelescopeOff

- Given the telescope is in ON state
- When the TelescopeOff command is sent to the telescope central node
- Then the telescope should transition to the OFF state

@XTP-62946 @XTP-62547 @XTP-28347
### Scenario: ON to STANDBY - CMD TelescopeStandby

- Given the telescope is in ON state
- When the TelescopeStandby command is sent to the telescope central node
- Then the telescope should transition to the STANDBY state

@XTP-62964 @XTP-62547 @XTP-28347
### Scenario: OFF to ON - CMD TelescopeOn

- Given the telescope is in OFF state
- When the TelescopeOn command is sent to the telescope central node
- Then the telescope should transition to the ON state