Feature: Default

	
	@XTP-34886 @XTP-29227 @Team_HIMALAYA
	Scenario: TMC Subarray report the exception triggered by the SDP subarray when it encounters a duplicate eb-id/pb-id.
		Given a Telescope consisting of TMC, SDP, simulated CSP and simulated MCCS
		And The TMC and SDP subarray <subarray_id> in the IDLE obsState
   		When TMC executes another AssignResources command with a <duplicate_id> from the JSON
		And SDP subarray <subarray_id> throws an exception and remain in IDLE obsState
		And TMC subarray <subarray_id> remain in RESOURCING obsState
		Then exception is propagated to central node
		Examples:
		| duplicate_id | subarray_id |
		| eb_id        | 1           |
		| pb_id        | 1           |