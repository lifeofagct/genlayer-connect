# { "Depends": "py-genlayer:test" }
"""
AI Weather Insurance Contract
==============================

Example contract showing how to use GenLayer-Connect's Weather API.

This contract provides weather-based insurance:
- Users create policies for specific events
- AI checks weather conditions
- Automatic payouts if weather is unfavorable
"""

from genlayer import *


class WeatherInsurance(gl.Contract):
    """
    Smart insurance contract that uses real weather data to determine payouts.
    
    Use Case: Event organizers can insure outdoor events against bad weather.
    """
    
    def __init__(self):
        self.policies = {}  # policy_id -> policy data
        self.policy_counter = 0
        
    @gl.public.write
    def create_policy(
        self, 
        event_name: str,
        location: str,
        event_date: str,
        coverage_amount: int,
        conditions: str
    ) -> str:
        """
        Create a weather insurance policy.
        
        Args:
            event_name: Name of event to insure
            location: Event location (city)
            event_date: Date of event (YYYY-MM-DD)
            coverage_amount: Payout amount if claim approved
            conditions: Weather conditions that trigger payout
                       (e.g., "rain", "temperature below 15C", "wind over 40km/h")
        
        Returns:
            Policy ID
        """
        self.policy_counter += 1
        policy_id = f"POL-{self.policy_counter}"
        
        self.policies[policy_id] = {
            "id": policy_id,
            "owner": gl.message_sender_address,
            "event_name": event_name,
            "location": location,
            "event_date": event_date,
            "coverage_amount": coverage_amount,
            "conditions": conditions,
            "status": "active",
            "claim_filed": False,
            "payout_amount": 0
        }
        
        return policy_id
    
    @gl.public.write
    def check_weather_and_claim(self, policy_id: str) -> str:
        """
        Check weather conditions and automatically process claim.
        
        Uses AI to:
        1. Fetch real weather data
        2. Compare against policy conditions
        3. Decide if payout is warranted
        
        Args:
            policy_id: Policy to check
            
        Returns:
            Claim decision and reasoning
        """
        if policy_id not in self.policies:
            return "ERROR: Policy not found"
        
        policy = self.policies[policy_id]
        
        if policy["status"] != "active":
            return "ERROR: Policy is not active"
        
        if policy["claim_filed"]:
            return "ERROR: Claim already filed for this policy"
        
        # Fetch weather data using AI
        weather_prompt = f"""Fetch current weather data for {policy['location']}.

Return:
- Temperature (Celsius)
- Conditions (sunny, cloudy, rainy, snowy, etc.)
- Wind speed (km/h)
- Precipitation
- Overall assessment

Use a real weather API like OpenWeatherMap."""
        
        def get_weather():
            return gl.exec_prompt(weather_prompt).strip()
        
        weather_data = gl.eq_principle_strict_eq(get_weather)
        
        # AI decides if claim should be paid
        claim_prompt = f"""You are an AI insurance adjuster reviewing a weather insurance claim.

POLICY DETAILS:
- Event: {policy['event_name']}
- Location: {policy['location']}
- Trigger Conditions: {policy['conditions']}
- Coverage Amount: {policy['coverage_amount']} tokens

CURRENT WEATHER DATA:
{weather_data}

TASK:
Determine if the current weather meets the policy trigger conditions.

Respond in this format:
DECISION: [APPROVED or DENIED]
REASONING: [Brief explanation]
PAYOUT: [Amount if approved, 0 if denied]

Be fair and objective. Only approve if conditions clearly match the policy terms."""
        
        def evaluate_claim():
            return gl.exec_prompt(claim_prompt).strip()
        
        # Use leader mode for faster claim processing
        decision = gl.eq_principle_leader_mode(evaluate_claim)
        
        # Parse decision
        policy["claim_filed"] = True
        
        if "APPROVED" in decision.upper():
            policy["status"] = "claimed"
            policy["payout_amount"] = policy["coverage_amount"]
            self.policies[policy_id] = policy
            return f"✅ CLAIM APPROVED

{decision}

Payout: {policy['coverage_amount']} tokens

Weather Data:
{weather_data}"
        else:
            policy["status"] = "expired"
            self.policies[policy_id] = policy
            return f"❌ CLAIM DENIED

{decision}

Weather Data:
{weather_data}"
    
    @gl.public.view
    def get_policy(self, policy_id: str) -> str:
        """Get policy details"""
        if policy_id not in self.policies:
            return "Policy not found"
        
        policy = self.policies[policy_id]
        
        return f"""
Policy ID: {policy['id']}
Owner: {policy['owner']}
Event: {policy['event_name']}
Location: {policy['location']}
Date: {policy['event_date']}
Trigger Conditions: {policy['conditions']}
Coverage: {policy['coverage_amount']} tokens
Status: {policy['status']}
Claim Filed: {policy['claim_filed']}
Payout: {policy['payout_amount']} tokens
"""
    
    @gl.public.view
    def preview_weather_check(self, location: str) -> str:
        """
        Preview current weather without filing a claim.
        Useful for checking conditions before creating policy.
        """
        weather_prompt = f"""Fetch current weather for {location}.

Return in simple format:
Temperature: [temp]°C
Conditions: [description]
Wind: [speed] km/h
Precipitation: [yes/no]"""
        
        def get_weather():
            return gl.exec_prompt(weather_prompt).strip()
        
        return gl.eq_principle_strict_eq(get_weather)
