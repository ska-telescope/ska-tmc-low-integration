@XTP-29582 @tmc_sdp
Scenario: Abort invocation using TMC
        Given TMC and SDP subarray busy assigning resources
        When I command it to Abort
        Then the SDP subarray should go into an aborted obsstate
        And the TMC subarray obsState transitions to ABORTED
        