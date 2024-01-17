Feature: Assign resources to CSP subarray using TMC

    @XTP-29657 @XTP-29227 @tmc_csp
    Scenario: Assign resources to CSP subarray using TMC
        Given the Telescope is in ON state
        And TMC subarray <subarray_id> is in EMPTY ObsState
        When I assign resources with <subarray_id> the to the subarray
        Then the CSP subarray must be in IDLE obsState
        And  the TMC subarray obsState is transitioned to IDLE        
        Examples : 
            | subarray_id |
            | 1           |