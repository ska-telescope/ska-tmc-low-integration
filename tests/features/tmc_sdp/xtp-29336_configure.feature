@XTP-29227 @XTP-29336 @tmc_sdp
Scenario: Configure a SDP subarray for a scan using TMC
		Given the Telescope is in ON state
		And TMC subarray in obsState IDLE
		When I configure with <scan_type> to the subarray <subarray_id>
		Then the SDP subarray <subarray_id> obsState is transitioned READY
		And SDP subarray scanType reflects correctly configured <scan_type>
		And the TMC subarray <subarray_id> obsState is transitioned to READY
		Examples:
		| subarray_id    |    scan_type    |
		| 1              |    target:a     |