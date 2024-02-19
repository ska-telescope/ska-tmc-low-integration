Feature: TMC performs End Configuration on MCCS subsystem
@XTP-31010 @XTP-30488 @Team_HIMALAYA @tmc_mccs
Scenario: End configure from MCCS Subarray
    Given the Telescope is in the ON state
    And the obsState of subarray is READY
    When I issue End command with the <subarray_id> to the subarray using TMC 
    Then the MCCS subarray is transitioned to IDLE obsState
    And TMC subarray is transitioned to IDLE obsState
    Examples:
    | subarray_id   |
    |  1            |