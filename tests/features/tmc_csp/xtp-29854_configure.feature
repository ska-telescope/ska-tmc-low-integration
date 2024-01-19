Feature: Configure a CSP subarray for a scan using TMC

	
	@XTP-29855 @XTP-29682
    Given the Telescope is in ON state
    And the subarray <subarray_id> obsState is IDLE
    When I configure with <config_id> to the subarray
    Then the CSP subarray transitions to READY obsState
    And CSP subarray config_id reflects correctly configured <config_id>
    And the TMC subarray transitions to READY obsState
    Examples:
        | subarray_id    |    config_id                              |
        | 1              |    sbi-mvp01-20200325-00001-science_A     |
