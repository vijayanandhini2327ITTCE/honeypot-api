"""
Scam Detection Module
Uses pattern matching and heuristics to detect scam intent
"""

import re
from typing import List, Tuple, Dict
from models import Message


class ScamDetector:
    """Detects scam intent in messages"""
    
    def __init__(self):
        # Common scam keywords and patterns
        self.urgent_keywords = [
            "urgent", "immediately", "now", "asap", "today",
            "expire", "expires", "expired", "suspend", "suspended",
            "block", "blocked", "freeze", "frozen"
        ]
        
        self.financial_keywords = [
            "bank", "account", "credit card", "debit card", "atm",
            "upi", "payment", "transaction", "transfer", "money",
            "refund", "cashback", "reward", "prize", "lottery",
            "tax", "penalty", "fine", "charge"
        ]
        
        self.verification_keywords = [
            "verify", "confirm", "update", "validate", "authenticate",
            "click", "link", "website", "login", "password",
            "otp", "cvv", "pin", "security code"
        ]
        
        self.threat_keywords = [
            "arrest", "legal action", "police", "court", "lawsuit",
            "fraud", "investigation", "suspicious activity", "unauthorized"
        ]
        
        self.reward_keywords = [
            "won", "winner", "congratulations", "prize", "reward",
            "free", "gift", "bonus", "cashback", "claim"
        ]
        
        # Regex patterns for sensitive information
        self.patterns = {
            "phone": r'\+?[\d\s\-\(\)]{10,}',
            "upi": r'[\w\.\-]+@[\w]+',
            "url": r'https?://[^\s]+|www\.[^\s]+',
            "bank_account": r'\b\d{9,18}\b',
            "amount": r'(?:Rs\.?|INR|₹)\s*[\d,]+(?:\.\d{2})?'
        }
    
    def detect_scam(
        self,
        message_text: str,
        conversation_history: List[Message]
    ) -> Tuple[bool, float, List[str]]:
        """
        Detect if a message is a scam
        
        Returns:
            - is_scam: Boolean indicating if scam detected
            - confidence: Confidence score (0-1)
            - indicators: List of scam indicators found
        """
        indicators = []
        score = 0.0
        
        message_lower = message_text.lower()
        
        # Check for urgent language
        urgent_count = sum(1 for kw in self.urgent_keywords if kw in message_lower)
        if urgent_count > 0:
            indicators.append(f"Urgent language ({urgent_count} keywords)")
            score += min(urgent_count * 0.15, 0.3)
        
        # Check for financial keywords
        financial_count = sum(1 for kw in self.financial_keywords if kw in message_lower)
        if financial_count > 0:
            indicators.append(f"Financial context ({financial_count} keywords)")
            score += min(financial_count * 0.1, 0.2)
        
        # Check for verification requests
        verification_count = sum(1 for kw in self.verification_keywords if kw in message_lower)
        if verification_count > 0:
            indicators.append(f"Verification request ({verification_count} keywords)")
            score += min(verification_count * 0.15, 0.3)
        
        # Check for threats
        threat_count = sum(1 for kw in self.threat_keywords if kw in message_lower)
        if threat_count > 0:
            indicators.append(f"Threatening language ({threat_count} keywords)")
            score += min(threat_count * 0.2, 0.4)
        
        # Check for reward/prize scams
        reward_count = sum(1 for kw in self.reward_keywords if kw in message_lower)
        if reward_count > 0:
            indicators.append(f"Reward/Prize mention ({reward_count} keywords)")
            score += min(reward_count * 0.15, 0.3)
        
        # Check for suspicious URLs
        urls = re.findall(self.patterns["url"], message_text)
        if urls:
            indicators.append(f"Contains URLs ({len(urls)})")
            score += min(len(urls) * 0.2, 0.4)
        
        # Check for phone numbers
        phones = re.findall(self.patterns["phone"], message_text)
        if phones and any(kw in message_lower for kw in ["call", "contact", "whatsapp"]):
            indicators.append(f"Phone numbers with contact request")
            score += 0.2
        
        # Check for combination patterns (highly suspicious)
        if urgent_count > 0 and financial_count > 0:
            indicators.append("Urgent + Financial = High risk pattern")
            score += 0.3
        
        if verification_count > 0 and urls:
            indicators.append("Verification + URL = Phishing pattern")
            score += 0.4
        
        if threat_count > 0 and financial_count > 0:
            indicators.append("Threat + Financial = Extortion pattern")
            score += 0.4
        
        # Analyze conversation history for escalation
        if len(conversation_history) > 0:
            escalation = self._detect_escalation(conversation_history, message_text)
            if escalation:
                indicators.append("Escalating pressure detected")
                score += 0.2
        
        # Cap score at 1.0
        confidence = min(score, 1.0)
        
        # Determine if scam (threshold: 0.4)
        is_scam = confidence >= 0.4
        
        return is_scam, confidence, indicators
    
    def _detect_escalation(
        self,
        conversation_history: List[Message],
        current_message: str
    ) -> bool:
        """Detect if scammer is escalating pressure"""
        if len(conversation_history) < 2:
            return False
        
        # Count urgent keywords in recent messages
        recent_messages = conversation_history[-3:]
        urgent_counts = []
        
        for msg in recent_messages:
            if msg.sender == "scammer":
                count = sum(1 for kw in self.urgent_keywords if kw in msg.text.lower())
                urgent_counts.append(count)
        
        # Check current message
        current_urgent = sum(1 for kw in self.urgent_keywords if kw in current_message.lower())
        urgent_counts.append(current_urgent)
        
        # Escalation if urgent language is increasing
        if len(urgent_counts) >= 2:
            return urgent_counts[-1] > urgent_counts[0]
        
        return False
    
    def extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract various patterns from text"""
        results = {}
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.findall(pattern, text)
            results[pattern_name] = list(set(matches))  # Remove duplicates
        
        return results
