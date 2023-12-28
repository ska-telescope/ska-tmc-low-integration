@XTP-29336
Scenario: Configure a SDP subarray for a scan using TMC
       Given the Telescope is in ON state
       And TMC subarray in obsState <obsstate>
       When I configure with <scan_type> to the subarray <subarray_id>
       Then the SDP subarray <subarray_id> obsState is READY
       And the TMC subarray <subarray_id> obsState is transitioned to READY
       Examples:
       | subarray_id    |    scan_type       | obsstate |
       | 1              |    "science_A"     | IDLE     |
       | 1              |    "science_A"     | READY    |