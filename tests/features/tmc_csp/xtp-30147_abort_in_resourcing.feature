@XTP-30147 @tmc_csp
Scenario: Abort assigning using TMC
    Given TMC and CSP subarray busy assigning resources
    When I command it to Abort
    Then the CSP subarray should go into an aborted obsState
    And the TMC subarray obsState transitions to ABORTED