Feature: Handling Invalid Station Id in MCCS Subarray
@XTP-34263 @tmc_mccs @Team_himalaya
Scenario: Invalid Station Id provided to MCCS Subarray
   Given a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP
   And the Telescope is in the ON state.
   And the TMC subarray is in EMPTY obsState
   When I assign resources with invalid <station_id> to the MCCS subarray using TMC
   Then the MCCS subarray should throw the error for invalid station id.
   And the MCCS subarray should remain in EMPTY ObsState.
   And the TMC propagate the error to the client.
   AND CSP,SDP Subarray transitions to ObsState IDLE
   And the TMC SubarrayNode <subarray_id> stuck in RESOURCING
   When I issue the Abort command on TMC SubarrayNode <subarray_id>
   Then the CSP, SDP and TMC subarray <subarray_id> transitions to obsState ABORTED
   When I issue the Restart command on TMC SubarrayNode <subarray_id>
   Then the CSP, SDP and TMC subarray <subarray_id> transitions to obsState EMPTY
   Examples:
   | station_id       |
   | 15               |