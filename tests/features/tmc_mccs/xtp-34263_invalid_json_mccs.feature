Feature: Handling Invalid Station Id in MCCS controller
@XTP-34263 @XTP-34276 @tmc_mccs @Team_himalaya
Scenario: The TMC Low Subarray reports the exception triggered by the MCCS controller when it encounters an invalid station ID.
   Given a Telescope consisting of TMC-MCCS, emulated SDP and emulated CSP
   And the Telescope is in the ON state
   And the TMC subarray is in EMPTY obsState
   When I assign resources with invalid <station_id> to the MCCS subarray using TMC with <subarray_id>
   Then the MCCS controller should throw the error for invalid station id
   And the MCCS subarray should remain in EMPTY ObsState
   And the TMC propogate the error to the client
   And the TMC SubarrayNode remains in RESOURCING obsState
   And I issue the Abort command on TMC SubarrayNode
   And the TMC subarray transitions to obsState ABORTED
   And I issue the Restart command on TMC SubarrayNode
   And the TMC subarray transitions to obsState EMPTY
   Examples:
   | station_id       | subarray_id |
   | 15               | 1           |
