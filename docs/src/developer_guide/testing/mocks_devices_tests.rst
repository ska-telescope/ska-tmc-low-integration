======================================
TMC Low Integration Testing Guidelines
=======================================

**********************
Mocked Device Testing
**********************

Pairwise testing is a way of testing the TMC code with mocked subsystems in place.

Commands Implemented
^^^^^^^^^^^^^^^^^^^^

To execute the tests, run the command `make k8s-test MARK=SKA_low`.

* ``ON`` - Test the On command on TMC with multiple subsystems.
* ``Off`` - Test the Off command on TMC with multiple subsystems.
* ``AssignResources`` - Test the AssignResources command on TMC with multiple subsystems.
* ``ReleaseResources`` - Test the ReleaseResources command on TMC with multiple subsystems.
* ``Standby`` - Test the Standby command on TMC with multiple subsystems.
* ``Configure`` - Test the Configure command on TMC with multiple subsystems.
* ``End`` - Test the End command on TMC with multiple subsystems.
* ``Scan`` - Test the Scan command on TMC with multiple subsystems.
* ``EndScan`` - Test the EndScan command on TMC with multiple subsystems.
* ``Abort`` - Test the Abort command on TMC with multiple subsystems.
* ``Restart`` - Test the Restart command on TMC with multiple subsystems.

Negative test cases Implemented
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Timeout 
^^^^^^^^

The following tests verify the timeout behavior of the Configure command on various leaf nodes:

- **Test Configure Timeout on CSP, SDP, and MCCS Leaf Nodes**

   - Induces a fault in the CSP, SDP, and MCCS Leaf Nodes to simulate a timeout scenario.
   - Verifies that the subarray transitions to the CONFIGURING state.
   - Checks that the long-running command result indicates a timeout and specifies the respective Leaf Node as the source of the failure.

Error Propagation
^^^^^^^^^^^^^^^^^

- Test case to verify error propagation for the Configure command of MCCS Leaf Nodes. This test ensures that when the MCCS Subarray is identified as defective, and the Configure command is executed on the TMC Low, the command reports an error.

Invalid Json
^^^^^^^^^^^^^

- This scenario tests the rejection of invalid JSON inputs during the Configure command execution on a Telescope Monitoring and Control (TMC) system. It includes steps to set up the TMC, configure the subarray, and validate the rejection of various invalid JSON inputs.

Command Not Allowed
^^^^^^^^^^^^^^^^^^^

The following tests verify the command not allowed error propagation for the AssignResources command on various leaf nodes:

- **Command Not Allowed Exception Propagation from CSP, SDP, and MCCS Leaf Nodes**

  - Induces a command not allowed exception in the Leaf Nodes to simulate a failure scenario.
  - Verifies that the long-running command result indicates a failure and specifies the Leaf Node as the source of the failure.