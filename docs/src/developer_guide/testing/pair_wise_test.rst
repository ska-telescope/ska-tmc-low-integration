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
To test with tmc_sdp execute the command `make k8s-test MARK=tmc_sdp SDP_SIMULATION_ENABLED=false`.

* ``ON`` -               Testing On command on TMC with Real-SDP in place.
    
* ``Off`` - Testing Off command on TMC  with Real-SDP in place.

* ``AssignResources`` -  Testing AssignResources command on TMC with Real-SDP in place.
    
* ``ReleaseResources`` - Testing ReleaseResources command on TMC with Real-SDP in place.

* ``Standby`` -  Testing StandBy command on TMC with Real-SDP in place.
    
* ``Scan`` - Testing Scan command on TMC with Real-SDP in place.

* ``EndScan`` - Testing EndScan command on TMC with Real-SDP in place.


