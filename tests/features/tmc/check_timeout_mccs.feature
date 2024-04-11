Scenario: Timeout Error Reported by TMC Low Configure Command for Defective MCCS Subarray

Given the telescope is is ON state
And the TMC subarray is in the idle observation state
When the MCCS Subarray is identified as defective and configure command is executed on the TMC Low
Then the Configure command times out and reports an error