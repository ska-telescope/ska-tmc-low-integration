###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----
[0.17.4]
* Integrate TMC SubarrayNode v0.23.0 to support PSS and PST as optional keys under TMC-CSP schema
    * To mitigate the dependency for PST observation to be based on having pst and pss  keys (mandatory)under CSP section,
    * As per the SKA Tel model pss and pst are not the mandatory fields, considering every observation would not be around PST.
    But the way TMC was supporting the PST observation, was considering these keys as mandatory.
    And that breaks the code when the observation is not for PST.
    * So the changes on TMC Subarray node v0.23.0 has done to handle this condition, considering the PST and PSS are optionals
    
Fixed
-----
[0.17.3]
********
* Updated Subarray Node v0.22.3 to resolve SKB-477.

[0.17.2]
********
* Updated Subarray Node v0.22.2 to resolve SKB-476.

[0.17.1]
*********
* Updated Central Node v0.16.3 and Subarray Node v0.21.4 related to SKB-438

[0.17.0]
*********
* TMC Low release with base class version 1.0.0
* Updated centralnode: 0.16.2
* Updated subarraynode: 0.21.2
* Updated cspleafnodes: 0.18.2
* Updated sdpleafnodes: 0.16.1
* Updated mccsleafnodes: 0.4.0 
* Update the telmodel version to 1.18.2
* Fix bug SKB-355

[0.16.0]
*********
* REL-1557 
* Updated AssignResources and Configure schemas for verification as per SKA Tel Model v > 1.17.0
* Verified TMC-MCCS interface with MCCS chart v0.13.0
* Utilised OSO-TMC low AssignResources v4.0(supporting TMC-MCCS v3.0) and Configure schema v4.0 (PST observations)
* Updated Central node version 0.15.2 with SKA Tel Model v1.17.0 to support validations for AssignResources and       ReleaseResources
* Utilised Subarray node version 0.19.1 with SKA Tel Model v1.18.1 to support validations for AssignResources, Configure and Scan schema

[master]
*********
* Bug SKB-296 is fixed
* Bug SKB-187 is fixed

[0.15.1]
************
* Updated Central node version to 0.15.0
* Updated Subarray Node version to 0.18.1 with MCCS scan command issue to fix SKB-395
* Added "MccsScanInterfaceURL" property that can be configured during deployment to set MCCS Scan interface url.


[0.15.0]
************
* Integrate TMC SubarrayNode latest image with SKB-355 and Bug fix 
  for interface URL for CSP, SDP and MCCS Scan and Configure commands.
* Utilised ska-csp-lmc-low v0.13.1 for SKB-355 bug verification via XTP-29657
* Integrate TMC CspSubarrayLeafNode latest image v0.162 with SKB-329, SKB-328 and SKB-327 bug fix
* Affected BDD test case - XTP-32140
* Updated randomly failing test cases - TMC configure with mocks, TMC-SDP Abort in Configuring, TMC-CSP abort in Resouring

[0.14.1]
************
* Fixed SKB-300
