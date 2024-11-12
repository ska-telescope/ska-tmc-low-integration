@SKA_low
Scenario Outline: Verify SKB-643
    Given TMC Subarray is in observation state EMPTY
    When I invoke the assign command on TMC Subarray
    Then TMC Subarray invokes assign on csp with json containing beams_id for pst and pss
    Then TMC Subarray transitions to observation state IDLE

Examples:
    | resource_type |
    | pst           |
    | pss           |
