@L2-3437
Feature: Receive data from LFAA
	#The SKA1_LOW TMC shall receive the following data from the LFAA via its I.S1L.TM_LFAA.001 interface as per \[RD7\]:
	#1. Alarms (par. 2.4.3)
	#2. failure indications and data to be used for failure prediction (par. 2.4.5.3)
	#3. Events (par. 2.4.4)
	#4. Logs (par. 2.4.5.1)
	#5. Capabilities (par. 2.4.6)
	#6. LFAA Operational Mode (par. 2.2.1)
	#7. operational and health status (par. 2.4.1)
	#8. software, hardware and firmware versions (par. 2.7.2)
	#9. LRU serial numbers (par. 2.7.2)
	#10. item part number,
	#11. item physical position (slot),
	#12. data that is sent to the TMC, to which SDP will subscribe (par. 2.5)
	#\\Note: Paragraph references are to the ICD.

	
	@XTP-35236 @XTP-34276 @Team_HIMALAYA
	Scenario: MCCS Controller report the error when one of the subarray beam is unavailable
		Given a Telescope consisting of TMC,MCCS,emulated SDP and emulated CSP
		And the telescope is in ON state
		And the TMC subarray is in EMPTY obsState
		When one of the MCCS subarraybeam is made unavailable
		And I assign resources with the <subarray_id> to the TMC subarray using TMC
		Then MCCS controller should throw the error and report to TMC
		And TMC should propogate the error to client 
		And the TMC SubarrayNode remains in ObsState RESOURCING
		Examples:
		    | subarray_id |
		    | 1           |