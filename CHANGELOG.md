###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

Added
-----

Fixed
-----

[master]
*********
* Bug SKB-296 is fixed
* Bug SKB-187 is fixed

[0.15.1]
************
* Updated Central node version to 0.15.0
* Updated Subarray Node version to 0.18.1 with MCCS scan command issue to fix SKB-395

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
