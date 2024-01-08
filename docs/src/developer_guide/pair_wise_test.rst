############################################
TMC LOW integration Testing guidelines
#############################################

****************************
Pair wise testing - TMC-SDP
****************************

Pair wise testing is way of testing the TMC code with real SDP subsystem in place. 
using latest `test-harness` implemented. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with tmc_sdp pair execute the command `make k8s-test MARK=tmc_sdp SDP_SIMULATION_ENABLED=false`.

* ``On``               -  Testing On command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.
    
* ``Off``              -  Testing Off command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.

* ``Standby``          -  Testing Standby command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.

* ``AssignResources``  -  Testing AssignResources command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.
    
* ``ReleaseResources`` -  Testing ReleaseResources command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.
    
* ``Configure``        -  Testing Configure command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.

* ``End``              -  Testing End command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.

* ``Scan``             -  Testing Scan command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.

* ``EndScan``          -  Testing EndScan command on TMC with real SDP controller and SDP Subarrays and mocked/simulated CSP and Mccs subsystems.