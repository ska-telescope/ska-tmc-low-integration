@XTP-29292
Scenario: Assign resources to SDP subarray using TMC
        Given the Telescope is in ON state
        And the subarray <subarray_id> obsState is EMPTY
        When I assign resources with the <receptors> to the subarray <subarray_id>
        Then the sdp subarray <subarray_id> obsState is IDLE
        And  the TMC subarray <subarray_id> obsState is transitioned to IDLE
        And the correct resources <receptors> are assigned to sdp subarray and TMC subarray          
        Examples: 
            | subarray_id | receptors             |
            | 1          | "C10", "C136", "C1", "C217", "C13", "C42"|

