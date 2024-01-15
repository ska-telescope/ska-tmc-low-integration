Scenario: Standby the telescope having TMC and CSP subsystems 
    Given a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS 
    And telescope state is ON
    When I put the telescope to STANDBY
    Then the csp controller and subarray stays in ON state
    Then telescope state is STANDBY