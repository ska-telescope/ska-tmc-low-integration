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

	
	@XTP-34263 @XTP-34276 @Team_HIMALAYA
	Scenario: The TMC Low Subarray reports the exception triggered by the MCCS controller when it encounters an invalid station ID.
		Given a Telescope consisting of TMC-MCCS, emulated SDP and emulated CSP
		And the Telescope is in the ON state
		And the TMC subarray is in EMPTY obsState
		When I assign resources with invalid <station_id> to the MCCS subarray using TMC with <subarray_id>
		Then the MCCS controller should throw the error for invalid station id
		And the MCCS subarray should remain in EMPTY ObsState
		And the TMC propogate the error to the client
		And the TMC SubarrayNode remains in RESOURCING obsState
		Examples:
		    | station_id       | subarray_id |
		    | 15               | 1           |