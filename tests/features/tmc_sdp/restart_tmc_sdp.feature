@XTP-29593 @tmc_sdp
Scenario: TMC executes a Restart on SDP subarray when subarray completes Abort
    Given the telescope is in ON state
    And TMC and SDP subarray is in ABORTED ObsState
    When I command it to Restart
    Then the SDP subarray transitions to ObsState EMPTY
    And the TMC subarray transitions to ObsState EMPTY
