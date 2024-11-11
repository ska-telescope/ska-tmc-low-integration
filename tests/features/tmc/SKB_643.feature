@SKA_low
Scenario Outline: Verify SKB-643
    Given Subarray Node is in observation state EMPTY
    When I invoke the assign command on Subarray Node with only <resource_type> resource
    Then Subarray Node transitions to observation state IDLE

Examples:
    | resource_type |
    | pst           |
    | pss           |
