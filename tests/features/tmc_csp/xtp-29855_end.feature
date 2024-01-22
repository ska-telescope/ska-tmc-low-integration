Feature: End from CSP Subarray using TMC

	
	@XTP-29855 @XTP-29682
    Given the Telescope is in ON state
    And a subarray <subarray_id> in the READY obsState
    When I issue End command to the subarray
    Then the CSP subarray transitions to IDLE obsState
    And TMC subarray transitions to IDLE obsState
    Example:
        | subarray_id   |
        |  1            |