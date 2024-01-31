@XTP-30129 @XTP-29227 @tmc_sdp
Scenario: TMC executes an Abort on SDP subarray
    Given the telescope is in ON state
    And TMC and SDP subarray <subarray_id> is in <obsstate> ObsState
    When I issued the Abort command to the TMC subarray
    Then the SDP subarray transitions to ObsState ABORTED
    And the TMC subarray transitions to ObsState ABORTED
    Examples:
    | subarray_id | obsstate |
    | 1           | IDLE     |
    | 1           | READY    |