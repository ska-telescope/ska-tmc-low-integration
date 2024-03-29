TMC Low Deployment
=======================

TMC Low deployment comes with following components:

1. **Central Node** 

2. **Subarray Node**

3. **Csp Master Leaf Node**

4. **Csp Subarray Leaf Node**

5. **Sdp Master Leaf Node**

6. **Sdp Subarray Leaf Node**

7. **MCCS Master Leaf Node**

8. **MCCS Subarray Leaf Node**


Configurable options
---------------------

* a. **instances** : User can provide the array of device server deployment instances required for node.

    Default for nodes are:

    #. **Central Node** : ["01"] 

    #. **Csp Master Leaf Node** : ["01"] 

    #. **Sdp Master Leaf Node** : ["01"]

    #. **MCCS Master Leaf Node** : ["01"]

* b. **subarray_count** : User can set this subarray count according to number device server deployment instances required for node..

    Default Value is 2.
    
    #. **Subarray Node** 

    #. **Csp Subarray Leaf Node** 

    #. **Sdp Subarray Leaf Node** 

    #. **MCCS Subarray Leaf Node** 

* c. **file** : User can provide custom device server configuration file to  nodes.Default is  `configuration files <https://gitlab.com/ska-telescope/ska-tmc/ska-tmc-low-integration/-/blob/main/charts/ska-tmc-low/data/>`_

* d. **enabled** : User can opt to disable any node by setting this value to False.Default is True for all nodes.

* e. **tmc_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SubarrayNode.

* f. **csp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspSubarrayLeafNode.

* g. **sdp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpSubarrayLeafNode.

* h. **csp_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspMasterLeafNode.

* i. **sdp_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpMasterLeafNode.

* j. **csp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of CSP Subarray.

* k. **sdp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SDP Subarray.

* l. **csp_master** : This value is present under global, User can use this to change the FQDN of CSP Master.

* m. **sdp_master** : This value is present under global, User can use this to change the FQDN of SDP Master.

* n. **mccs_master** : This value is present under global, User can use this to change the FQDN of MCCS Master.

* o. **mccs_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Master Leaf Node.

* p. **mccs_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Subarray.

* q. **mccs_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Subarray Leaf Node.



