Scenario: TMC generates delay values
    Given the telescope is in ON state
    And subarray is in obsState IDLE
    When I configure the subarray
    Then CSP subarray leaf node starts generating delay values