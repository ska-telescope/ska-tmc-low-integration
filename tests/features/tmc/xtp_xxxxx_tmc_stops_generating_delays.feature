@XTP-XXXXX
Scenario: TMC stops generating delay values for PST Beams
    Given the telescope is in ON state
    And subarray is configured and generating delay values for PST Beams
    When I end the observation
    Then CSP Subarray Leaf Node stops generating delay values for PST Beams