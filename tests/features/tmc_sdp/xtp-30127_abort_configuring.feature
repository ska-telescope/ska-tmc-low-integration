@XTP-30127 @XTP-29227 @Team_SAHYADRI @tmc_sdp
Scenario: Abort configuring SDP using TMC
    Given TMC subarray <subarray_id> and SDP subarray <subarray_id> busy configuring
    When I command it to Abort
    Then the SDP subarray transitions to ObsState ABORTED
    And the TMC subarray transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |