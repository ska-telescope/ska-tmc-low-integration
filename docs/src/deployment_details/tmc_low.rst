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

    #. **Subarray Node** :["01", "02"]

    #. **Csp Master Leaf Node** : ["01"] 

    #. **Csp Subarray Leaf Node** : ["01", "02"]

    #. **Sdp Master Leaf Node** : ["01"]

    #. **Sdp Subarray Leaf Node** : ["01", "02"]

    #. **MCCS Master Leaf Node** : ["01"]

    #. **MCCS Subarray Leaf Node** : ["01", "02"]




* b. **file** : User can provide custom device server configuration file to  nodes.Default is  `configuration files <https://gitlab.com/ska-telescope/ska-tmc/ska-tmc-low-integration/-/blob/main/charts/ska-tmc-low/data/>`_

* c. **enabled** : User can opt to disable any node by setting this value to False.Default is True for all nodes.

* d. **tmc_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SubarrayNode.

* e. **csp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspSubarrayLeafNode.

* f. **sdp_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpSubarrayLeafNode.

* g. **csp_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of CspMasterLeafNode.

* h. **sdp_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of SdpMasterLeafNode.

* i. **csp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of CSP Subarray.

* j. **sdp_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of SDP Subarray.

* k. **csp_master** : This value is present under global, User can use this to change the FQDN of CSP Master.

* l. **sdp_master** : This value is present under global, User can use this to change the FQDN of SDP Master.

* m. **mccs_master** : This value is present under global, User can use this to change the FQDN of MCCS Master.

* n. **mccs_master_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Master Leaf Node.

* o. **mccs_subarray_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Subarray.

* p. **mccs_subarray_ln_prefix** : This value is present under global, User can use this to change the FQDN prefix of MCCS Subarray Leaf Node.




Additional few Central node specific configurations are:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
a. **subarray_count** : User can set this subarray count according to number of subarray node devices  are deployed. default is 2. 
