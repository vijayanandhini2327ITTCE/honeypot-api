"""
Enhanced AI Agent with Claude API Integration (Optional)
This provides even more natural and adaptive responses

To use this, you need an Anthropic API key.
Set it in your .env file: ANTHROPIC_API_KEY=your-key-here
"""

import os
from typing import List, Dict
from models import Message
from ai_agent import HoneypotAgent


class EnhancedHoneypotAgent(HoneypotAgent):
    """
    Enhanced agent that can optionally use Claude API for more sophisticated responses
    Falls back to rule-based responses if API is not available
    """
    
    def __init__(self, use_claude_api: bool = False):
        super().__init__()
        self.use_claude_api = use_claude_api
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        if self.use_claude_api and not self.anthropic_api_key:
            print("Warning: Claude API requested but ANTHROPIC_API_KEY not found. Using rule-based responses.")
            self.use_claude_api = False
    
    def generate_response(
        self,
        scammer_message: str,
        conversation_history: List[Message],
        scam_indicators: List[str],
        engagement_count: int
    ) -> str:
        """
        Generate response using Claude API if enabled, otherwise use rule-based
        """
        
        if self.use_claude_api:
            try:
                return self._generate_claude_response(
                    scammer_message,
                    conversation_history,
                    scam_indicators,
                    engagement_count
                )
            except Exception as e:
                print(f"Claude API error: {e}. Falling back to rule-based responses.")
                # Fall back to parent class method
                return super().generate_response(
                    scammer_message,
                    conversation_history,
                    scam_indicators,
                    engagement_count
                )
        else:
            # Use rule-based responses
            return super().generate_response(
                scammer_message,
                conversation_history,
                scam_indicators,
                engagement_count
            )
    
    def _generate_claude_response(
        self,
        scammer_message: str,
        conversation_history: List[Message],
        scam_indicators: List[str],
        engagement_count: int
    ) -> str:
        """
        Generate response using Claude API
        """
        import requests
        
        # Build conversation context
        context = self._build_context(conversation_history)
        
        # Determine persona based on stage
        persona = self._get_persona_for_stage(engagement_count)
        
        # Build prompt
        prompt = f"""You are roleplaying as a potential scam victim in a honeypot scenario. Your goal is to:
1. Maintain a believable human persona
2. Keep the scammer engaged without revealing you've detected the scam
3. Extract information from the scammer
4. Respond naturally based on your stage in the conversation

Current Stage: {persona['stage']}
Your Persona: {persona['description']}

Scam Indicators Detected: {', '.join(scam_indicators)}

Conversation History:
{context}

Scammer's Latest Message: {scammer_message}

Generate a response that:
- Sounds like a real person (use natural language, maybe some grammatical imperfections)
- {persona['goal']}
- Is brief (1-2 sentences max)
- Does NOT reveal you know this is a scam

Your response:"""

        # Call Claude API
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.anthropic_api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            json={
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 150,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_reply = data["content"][0]["text"].strip()
            
            # Remove quotes if present
            if agent_reply.startswith('"') and agent_reply.endswith('"'):
                agent_reply = agent_reply[1:-1]
            
            return agent_reply
        else:
            raise Exception(f"API error: {response.status_code}")
    
    def _build_context(self, conversation_history: List[Message]) -> str:
        """Build conversation context string"""
        if not conversation_history:
            return "This is the first message."
        
        context_lines = []
        for msg in conversation_history[-5:]:  # Last 5 messages
            sender_label = "Scammer" if msg.sender == "scammer" else "You"
            context_lines.append(f"{sender_label}: {msg.text}")
        
        return "\n".join(context_lines)
    
    def _get_persona_for_stage(self, engagement_count: int) -> Dict[str, str]:
        """Get persona description for current conversation stage"""
        
        if engagement_count <= 3:
            return {
                "stage": "Initial Contact (1-3)",
                "description": "Confused and questioning. You don't understand what's happening.",
                "goal": "Ask questions about who they are and why they're contacting you"
            }
        elif engagement_count <= 7:
            return {
                "stage": "Concern (4-7)",
                "description": "Worried but seeking clarification. You're starting to believe them.",
                "goal": "Express concern and ask for more details about the situation"
            }
        elif engagement_count <= 12:
            return {
                "stage": "Compliance (8-12)",
                "description": "Willing to help but experiencing technical difficulties.",
                "goal": "Appear cooperative but introduce delays or technical issues"
            }
        else:
            return {
                "stage": "Information Gathering (13+)",
                "description": "Cautious and asking for verification.",
                "goal": "Ask for official details, employee IDs, office addresses, or documentation"
            }


# Example usage in main.py:
# from enhanced_ai_agent import EnhancedHoneypotAgent
# honeypot_agent = EnhancedHoneypotAgent(use_claude_api=True)
