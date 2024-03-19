Feature: Switch off the telescope having TMC and MCCS subsystems	
	@XTP-33992 @XTP-30488 @Team_HIMALAYA
	Scenario: Switch off the telescope having TMC and MCCS subsystems 
		Given a Telescope consisting of TMC,MCCS,simulated SDP and simulated CSP
		And telescope state is ON
		When I switch off the telescope
		Then the MCCS must go to OFF State
		And telescope state is OFF
		And the mccs subarray must go to OFF State