Feature: Commands with invalid json input
    Scenario: AssignResource command with invalid JSON is rejected by the TMC
        Given the TMC is in ON state
        And the subarray is in EMPTY obsState
        When the command AssignResources is invoked with <invalid_json> input
        Then TMC should reject the AssignResources command
        And TMC subarray remains in EMPTY obsState
        And TMC successfully executes AssignResources for subarray with a valid input json
        Examples:
            | invalid_json                  |
            | missing_pb_id_key             |
            | missing_scan_type_id_key      |
            | missing_count_key             |
            | missing_receptor_id_key       |


    Scenario:   Invalid json rejected by TMC for Configure command
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command Configure is invoked with <invalid_json> input
        Then the TMC should reject the <invalid_json> with ResultCode.Rejected
        And TMC subarray remains in IDLE obsState
        And TMC successfully executes the Configure command for the subarray with a valid json

        Examples:
            | invalid_json                           |
            | config_id_key_missing                  |
            | fsp_id_key_missing                     |
            | frequency_slice_id_key_missing         |
            | integration_factor_key_missing         |
            | zoom_factor_key_missing                |
            # | incorrect_fsp_id                       |


    Scenario:   Invalid json rejected by TMC Low for Configure command
        Given the TMC is On
        And the subarray is in IDLE obsState
        When the command Configure is invoked with <invalid_json> input
        Then the TMC should reject the <invalid_json> with ResultCode.Rejected
        And TMC subarray remains in IDLE obsState
        And TMC successfully executes the Configure command for the subarray with a valid json

        Examples:
            | invalid_json                   |
            | csp_key_missing                |
            | sdp_key_missing                |
            | tmc_key_missing                |
            | scan_duration_key_missing      |
            | empty_string                   |