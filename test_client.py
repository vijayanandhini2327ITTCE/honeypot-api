"""
Test client for the Honeypot API
"""

import requests
import json
from datetime import datetime


class HoneypotTestClient:
    """Client to test the honeypot API"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "your-secret-api-key-here"):
        self.base_url = base_url
        self.api_key = api_key
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
    
    def send_message(self, session_id: str, message: str, conversation_history: list = None):
        """Send a message to the API"""
        
        if conversation_history is None:
            conversation_history = []
        
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": message,
                "timestamp": datetime.now().isoformat() + "Z"
            },
            "conversationHistory": conversation_history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        response = requests.post(
            f"{self.base_url}/api/message",
            headers=self.headers,
            json=payload
        )
        
        return response
    
    def test_scam_scenario(self):
        """Test a complete scam scenario"""
        
        session_id = "test-session-001"
        conversation_history = []
        
        # Test messages simulating a scam
        test_messages = [
            "Your bank account will be blocked today. Verify immediately.",
            "You need to update your KYC details urgently.",
            "Click this link to verify: http://fake-bank-verify.com",
            "Enter your card details to confirm your identity.",
            "This is your last warning. Act now or face legal action."
        ]
        
        print("=" * 60)
        print("TESTING SCAM SCENARIO")
        print("=" * 60)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n--- Message {i} ---")
            print(f"Scammer: {message}")
            
            response = self.send_message(session_id, message, conversation_history)
            
            if response.status_code == 200:
                data = response.json()
                agent_reply = data.get("reply", "")
                print(f"Agent: {agent_reply}")
                
                # Update conversation history
                conversation_history.append({
                    "sender": "scammer",
                    "text": message,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
                conversation_history.append({
                    "sender": "user",
                    "text": agent_reply,
                    "timestamp": datetime.now().isoformat() + "Z"
                })
            else:
                print(f"Error: {response.status_code} - {response.text}")
                break
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED")
        print("=" * 60)
    
    def test_legitimate_message(self):
        """Test with a legitimate message"""
        
        session_id = "test-session-002"
        message = "Hi, this is John from the support team. How can I help you today?"
        
        print("\n" + "=" * 60)
        print("TESTING LEGITIMATE MESSAGE")
        print("=" * 60)
        print(f"Message: {message}")
        
        response = self.send_message(session_id, message)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data.get('reply', '')}")
        else:
            print(f"Error: {response.status_code} - {response.text}")
        
        print("=" * 60)
    
    def check_health(self):
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        
        if response.status_code == 200:
            print("✓ API is healthy")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"✗ API health check failed: {response.status_code}")


if __name__ == "__main__":
    # Initialize client
    client = HoneypotTestClient()
    
    # Check health
    print("\n=== HEALTH CHECK ===")
    client.check_health()
    
    # Test scam scenario
    print("\n")
    client.test_scam_scenario()
    
    # Test legitimate message
    print("\n")
    client.test_legitimate_message()
