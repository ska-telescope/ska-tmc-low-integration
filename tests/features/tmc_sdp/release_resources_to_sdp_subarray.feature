Scenario: Release resources from SDP Subarray using TMC
    Given a TMC and SDP
    And a subarray <subarray_id> in the IDLE obsState
    When I release all resources assigned to it
    Then the SDP subarray <subarray_id> must be in EMPTY obsState
    And TMC subarray <subarray_id> obsState transitions to EMPTY

 Example
        | subarray_id   | 
        |  1                   | 
