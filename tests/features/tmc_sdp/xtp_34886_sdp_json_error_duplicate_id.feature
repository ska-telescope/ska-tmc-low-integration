Feature: Default

	
	@XTP-34886 @XTP-29227 @Team_HIMALAYA
	Scenario: TMC Subarray report the exception triggered by the SDP subarray when it encounters a duplicate eb-id/pb-id.
		Given a Telescope consisting of TMC,SDP,simulated CSP and simulated MCCS
		And The TMC and SDP subarray <subarray_id> in the IDLE obsState using <input_json1>
		When TMC executes another AssignResources command with a <duplicate_id> from <input_json1>
		And SDP subarray <subarray_id> throws an exception and remain in IDLE obsState
		And TMC subarray <subarray_id> remain in RESOURCING obsState
		Then exception is propagated to central node
		When I issue the Abort command on TMC Subarray <subarray_id>
		And SDP Subarray and TMC Subarray <subarray_id> transitions to obsState ABORTED
		And I issue the Restart command on TMC Subarray <subarray_id>
		And the SDP and TMC Subarray <subarray_id> transitions to obsState EMPTY
		Then AssignResources command is executed with a new ID and TMC and SDP subarray <subarray_id> transitions to IDLE
		Examples:
            | subarray_id  | input_json1           | duplicate_id |
            | 1            | assign_resources_json | eb_id        |
            | 1            | assign_resources_json | pb_id        |