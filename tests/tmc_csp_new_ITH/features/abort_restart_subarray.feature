Feature: subarray 1 obsState may be Aborted and Restarted
  This feature covers the call of the Abort command from all
  the states that permit it and the subsequent call of the Reset command.

  The goal is to verify that the subarray
  processes correctly the Abort command and the subsequent Restart
  command from any allowed state.

  This is critical also for tests, as the procedure to reset the state
  of the subarray relies on Abort-Restart, that brings the subarray
  to the EMPTY pre-test state.


  Relevant transitions (taken from list_of_transitions.text):

  Transition("12. RESOURCING --> (CMD: Abort) --> ABORTING")
  Transition("19. IDLE --> (CMD: Abort) --> ABORTING")
  Transition("25. CONFIGURING --> (CMD: Abort) --> ABORTING")
  Transition("28. READY --> (CMD: Abort) --> ABORTING")
  Transition("34. SCANNING --> (CMD: Abort) --> ABORTING")
  Transition("37. ABORTING --> (AUTO: Abort complete) --> ABORTED")
  Transition("40. ABORTED --> (CMD: Restart) --> RESTARTING")
  Transition("43. RESTARTING --> (AUTO: Restart Complete) --> EMPTY")

  Background:
    Given the telescope is in ON state
    Given the subarray 1 can be used

  
  @Transition("12. RESOURCING --> (CMD: Abort) --> ABORTING")
  @Transition("37. ABORTING --> (AUTO: Abort complete) --> ABORTED")
  @XTP-62548 @XTP-62547 @XTP-28347
  Scenario: RESOURCING to ABORTING to ABORTED - CMD Abort
    Given the subarray 1 is in the RESOURCING state
    When the Abort command is sent to the subarray 1
    Then the subarray 1 should transition to the ABORTING state
    And the subarray 1 should transition to the ABORTED state

  @Transition("19. IDLE --> (CMD: Abort) --> ABORTING")
  @Transition("37. ABORTING --> (AUTO: Abort complete) --> ABORTED")
  @XTP-62715 @XTP-62547 @XTP-28347
  Scenario: IDLE to ABORTING to ABORTED - CMD Abort
    Given the subarray 1 is in the IDLE state
    When the Abort command is sent to the subarray 1
    Then the subarray 1 should transition to the ABORTING state
    And the subarray 1 should transition to the ABORTED state

  @Transition("25. CONFIGURING --> (CMD: Abort) --> ABORTING")
  @Transition("37. ABORTING --> (AUTO: Abort complete) --> ABORTED")
  @XTP-62716 @XTP-62547 @XTP-28347
  Scenario: CONFIGURING to ABORTING to ABORTED - CMD Abort
    Given the subarray 1 is in the CONFIGURING state
    When the Abort command is sent to the subarray 1
    Then the subarray 1 should transition to the ABORTING state
    And the subarray 1 should transition to the ABORTED state

  @Transition("28. READY --> (CMD: Abort) --> ABORTING")
  @Transition("37. ABORTING --> (AUTO: Abort complete) --> ABORTED")
  @XTP-62717 @XTP-62547 @XTP-28347
  Scenario: READY to ABORTING to ABORTED - CMD Abort
    Given the subarray 1 is in the READY state
    When the Abort command is sent to the subarray 1
    Then the subarray 1 should transition to the ABORTING state
    And the subarray 1 should transition to the ABORTED state

  @Transition("34. SCANNING --> (CMD: Abort) --> ABORTING")
  @Transition("37. ABORTING --> (AUTO: Abort complete) --> ABORTED")
  @XTP-62718 @XTP-62547 @XTP-28347
  Scenario: SCANNING to ABORTING to ABORTED - CMD Abort
    Given the subarray 1 is in the SCANNING state
    When the Abort command is sent to the subarray 1
    Then the subarray 1 should transition to the ABORTING state
    And the subarray 1 should transition to the ABORTED state

  @Transition("40. ABORTED --> (CMD: Restart) --> RESTARTING")
  @Transition("43. RESTARTING --> (AUTO: Restart Complete) --> EMPTY")
  @XTP-62719 @XTP-62547 @XTP-28347
  Scenario: ABORTED to RESTARTING to EMPTY - CMD Restart
    Given the subarray 1 is in the ABORTED state
    When the Restart command is sent to the subarray 1
    Then the subarray 1 should transition to the RESTARTING state
    And the subarray 1 should transition to the EMPTY state

# TODO: shouldn't we have a step for the completion of the LRC
  # also for these tests?