@XTP-30128 @XTP-29227 @tmc_sdp
Scenario: TMC executes an Abort on SDP subarray where ObsState is Scanning
    Given TMC subarray <subarray_id> and SDP subarray <subarray_id> ObsState is SCANNING
    When I command it to Abort
    Then the SDP subarray transitions to ObsState ABORTED
    And the subarray transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |
