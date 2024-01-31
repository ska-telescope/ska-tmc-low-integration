@XTP-30128 @XTP-29227 @tmc_sdp
Scenario: Abort scanning SDP using TMC
    Given TMC subarray <subarray_id> and SDP subarray busy scanning
    When I command it to Abort
    Then the SDP subarray transitions to ObsState ABORTED
    And the TMC subarray transitions to ObsState ABORTED
    Examples:
        | subarray_id |
        | 1           |
