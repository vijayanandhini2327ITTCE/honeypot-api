"""
AI Agent Module
Generates human-like responses to engage scammers
"""

import random
from typing import List, Dict, Any
from models import Message
from intelligence_extractor import IntelligenceExtractor


class HoneypotAgent:
    """AI agent that engages scammers with human-like responses"""
    
    def __init__(self):
        # Response strategies based on scam type and conversation stage
        self.confused_responses = [
            "I don't understand. What do you mean?",
            "Can you explain that again?",
            "I'm not sure what you're asking for.",
            "This is confusing. Can you clarify?",
            "Sorry, I didn't get that. Could you repeat?"
        ]
        
        self.concerned_responses = [
            "Oh no! Is this serious?",
            "This sounds urgent. What should I do?",
            "I'm worried now. Can you help me?",
            "Is my account really in danger?",
            "Should I be concerned about this?"
        ]
        
        self.compliance_starters = [
            "Okay, I want to help.",
            "I'll do what you say.",
            "Please tell me what to do.",
            "I don't want any problems.",
            "How can I fix this?"
        ]
        
        self.info_gathering = [
            "Can you tell me more about this?",
            "What exactly happened?",
            "Who are you with?",
            "How did you get my number?",
            "Is this from my bank?"
        ]
        
        self.technical_difficulties = [
            "The link isn't working. Can you send another?",
            "I'm having trouble with the website.",
            "My internet is slow. Can you wait?",
            "I can't open that link. Do you have another way?",
            "The page won't load. What should I do?"
        ]
        
        self.delay_tactics = [
            "Let me check my account first.",
            "Give me a moment, I need to find my phone.",
            "I'm at work right now. Can I do this later?",
            "I need to talk to my son/daughter about this.",
            "Can you call back in 10 minutes?"
        ]
    
    def generate_response(
        self,
        scammer_message: str,
        conversation_history: List[Message],
        scam_indicators: List[str],
        engagement_count: int
    ) -> str:
        """
        Generate a human-like response based on context
        
        Args:
            scammer_message: Current message from scammer
            conversation_history: Previous conversation
            scam_indicators: Detected scam patterns
            engagement_count: Number of exchanges so far
        
        Returns:
            Human-like response string
        """
        message_lower = scammer_message.lower()
        
        # Stage 1: Initial confusion (messages 1-3)
        if engagement_count <= 3:
            return self._generate_initial_response(scammer_message, message_lower)
        
        # Stage 2: Show concern and ask questions (messages 4-7)
        elif engagement_count <= 7:
            return self._generate_concerned_response(scammer_message, message_lower, scam_indicators)
        
        # Stage 3: Pretend compliance with delays (messages 8-12)
        elif engagement_count <= 12:
            return self._generate_compliant_response(scammer_message, message_lower)
        
        # Stage 4: Technical difficulties and information extraction (messages 13+)
        else:
            return self._generate_extraction_response(scammer_message, message_lower)
    
    def _generate_initial_response(self, message: str, message_lower: str) -> str:
        """Generate initial confused/questioning response"""
        
        # Ask who they are
        if any(word in message_lower for word in ["bank", "account"]):
            return random.choice([
                "Who is this? Which bank are you calling from?",
                "Is this really my bank? How do I know?",
                "I didn't expect a call. What's this about?"
            ])
        
        # Express confusion about urgency
        if any(word in message_lower for word in ["urgent", "immediately", "now"]):
            return random.choice([
                "Why is this so urgent? What happened?",
                "I don't understand. Why do I need to do this now?",
                "Can you explain why this can't wait?"
            ])
        
        # Question verification requests
        if any(word in message_lower for word in ["verify", "confirm", "update"]):
            return random.choice([
                "Why do you need me to verify? I didn't request anything.",
                "How do I know this is legitimate?",
                "Can I verify this through the official website instead?"
            ])
        
        return random.choice(self.confused_responses)
    
    def _generate_concerned_response(
        self,
        message: str,
        message_lower: str,
        scam_indicators: List[str]
    ) -> str:
        """Generate concerned response with information gathering"""
        
        # Show concern about threats
        if any(word in message_lower for word in ["suspend", "block", "legal", "arrest"]):
            return random.choice([
                "Oh no! What did I do wrong?",
                "This is scary. Can you tell me what's happening?",
                "I don't want any legal trouble. Please explain."
            ])
        
        # Ask about rewards/prizes
        if any(word in message_lower for word in ["won", "prize", "reward", "congratulations"]):
            return random.choice([
                "Really? I won something? What is it?",
                "How did I win? I don't remember entering anything.",
                "This sounds too good to be true. Is it real?"
            ])
        
        # Question about money/payment
        if any(word in message_lower for word in ["pay", "money", "transfer", "upi"]):
            return random.choice([
                "How much money are we talking about?",
                "Why do I need to pay? For what?",
                "Can you explain the charges to me?"
            ])
        
        # Ask for more details
        return random.choice(self.info_gathering)
    
    def _generate_compliant_response(self, message: str, message_lower: str) -> str:
        """Generate seemingly compliant response with delays"""
        
        # If asked to click link
        if "link" in message_lower or "http" in message:
            return random.choice([
                "I'm trying to click but nothing is happening.",
                "The link takes me to a weird page. Is this right?",
                "My phone says this site might not be secure. Should I continue?",
                "Can you send the official website link instead?"
            ])
        
        # If asked for personal info
        if any(word in message_lower for word in ["otp", "password", "cvv", "pin"]):
            return random.choice([
                "Let me get my card. One moment.",
                "I need to find where I wrote that down.",
                "Is it safe to share this over the phone?",
                "My son told me never to share this. Are you sure it's okay?"
            ])
        
        # If asked to install app/software
        if any(word in message_lower for word in ["install", "download", "app", "anydesk", "teamviewer"]):
            return random.choice([
                "I'm not very good with technology. Can you help me?",
                "My phone is asking for permissions. What should I allow?",
                "This is taking forever to download. Is that normal?",
                "I don't see that app in the Play Store. Where is it?"
            ])
        
        # General delay
        return random.choice(self.delay_tactics)
    
    def _generate_extraction_response(self, message: str, message_lower: str) -> str:
        """Generate response to extract more information"""
        
        # Ask about their organization
        responses = [
            "What's the name of your company again?",
            "Can you give me your employee ID number?",
            "What department are you from?",
            "Do you have an office I can visit?",
            "Can I get a reference number for this case?",
            "Who is your supervisor? I'd like to speak with them.",
            "What's your callback number?",
            "Is there an email address I can contact?",
            "Can you send me this in writing?",
            "Do you have any official documentation?"
        ]
        
        return random.choice(responses)
    
    def should_end_conversation(
        self,
        engagement_count: int,
        intelligence: IntelligenceExtractor
    ) -> bool:
        """
        Determine if conversation should end
        
        Ends when:
        - Sufficient intelligence gathered
        - Too many exchanges (>15)
        - Scammer gives up
        """
        
        # End after 15-20 exchanges
        if engagement_count >= 15:
            # Check if we have good intelligence
            has_intelligence = (
                len(intelligence.phone_numbers) > 0 or
                len(intelligence.upi_ids) > 0 or
                len(intelligence.phishing_links) > 0 or
                len(intelligence.bank_accounts) > 0
            )
            
            return True
        
        # End after 20 no matter what
        if engagement_count >= 20:
            return True
        
        return False
    
    def generate_final_message(self) -> str:
        """Generate final message before ending conversation"""
        return random.choice([
            "I need to think about this. Let me call you back.",
            "My son just told me this might be a scam. I'm not comfortable continuing.",
            "I'm going to visit my bank branch instead.",
            "This doesn't feel right. I'm going to hang up now.",
            "I'll handle this later. Thank you."
        ])
