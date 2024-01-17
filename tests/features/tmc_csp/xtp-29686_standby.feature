Feature: Standby the telescope having TMC and CSP subsystems

	
	@XTP-29686 @XTP-29682
	Scenario: Standby the telescope having TMC and CSP subsystems
		Given a Telescope consisting of TMC,CSP,simulated SDP and simulated MCCS 
		And telescope state is ON
		When  I invoke STANDBY command  
		Then telescope state is STANDBY
		And the csp subarray and controller stays in ON state