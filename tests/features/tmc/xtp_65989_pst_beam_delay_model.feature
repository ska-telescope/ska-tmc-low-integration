@XTP-65989
Scenario: TMC generates delay values for PST Beams
    Given the telescope is in ON state
    And subarray is in obsState IDLE
    When I configure the subarray
    Then CSP Subarray Leaf Node starts generating delay values for PST Beams
