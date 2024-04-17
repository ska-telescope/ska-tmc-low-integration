Feature:  TMC Low executes long running sequences with real sdp devices
    Scenario Outline: TMC Low executes configure-scan sequence of commands successfully

    Given the Telescope is in ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode transitions to EMPTY ObsState

    Examples:
        |subarray_id   | scan_types                                  | scan_ids    |
        |1             |["science_A"]                                |["1"]        |
        |1             |["science_A" , "target:a"]                   |["1","2"]    |
        |1             |["science_A" , "science_A"]                  |["1","2"]    |
        |1             |["science_A" , "science_A"]                  |["1","1"]    |
        |1             |["science_A" , "target:a","callibration_B" ]|["1","2","3"]|





    Scenario Outline: TMC Low executes multiple scan with same configuration successfully

    Given the Telescope is in ON state
    When I assign resources to TMC SubarrayNode <subarray_id>
    And configure and scan TMC SubarrayNode <subarray_id> for each <scan_types> and <scan_ids>
    And reperform scan with same configuration and new scan id
    And end the configuration on TMC SubarrayNode <subarray_id>
    And release the resources on TMC SubarrayNode <subarray_id>
    Then TMC SubarrayNode transitions to EMPTY ObsState

    Examples:
        |subarray_id  |scan_ids | scan_types    |
        |1            |["1"]    |["science_A"]  |