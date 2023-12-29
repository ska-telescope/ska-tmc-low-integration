############################################
TMC LOW integration Testing guidelines
#############################################

****************************
Pair wise testing / Real-SDP
****************************

Pair wise testing is way of testing the TMC code with real SDP subsystem in place. 
using latest `test harness` implemented. 

Commands implemented
^^^^^^^^^^^^^^^^^^^^
To test with real_sdp execute the command `make k8s-test MARK=read_sdp SDP_SIMULATION_ENABLED=false`.

* ``AssignResources`` -  Testing AssignResources command with Real-SDP in place.
    
* ``ReleaseResources`` - Testing ReleaseResources command with Real-SDP in place.

