Feature: Handling Invalid Station Id in MCCS controller
@XTP-34263 @tmc_mccs @Team_himalaya
Scenario: Invalid Station Id provided to MCCS controller
   Given a Telescope consisting of TMC,MCCS,emulated SDP and emulated CSP
   And the Telescope is in the ON state
   And the TMC subarray is in EMPTY obsState
   When I assign resources with invalid <station_id> to the MCCS subarray using TMC with subarray_id <subarray_id>
   Then the MCCS controller should throw the error for invalid station id
   And the MCCS subarray should remain in EMPTY ObsState
   And the TMC propagate the error to the client
   And CSP,SDP Subarray transitions to ObsState IDLE
   And the TMC SubarrayNode stuck in RESOURCING
   When I issue the Abort command on TMC SubarrayNode
   Then the CSP, SDP and TMC subarray transitions to obsState ABORTED
   When I issue the Restart command on TMC SubarrayNode
   Then the CSP, SDP and TMC subarray transitions to obsState EMPTY
   Examples:
   | station_id       | subarray_id      |
   | 15               | 1                |
