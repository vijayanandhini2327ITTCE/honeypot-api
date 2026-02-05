"""
Intelligence Extraction Module
Extracts and stores scam-related intelligence from conversations
"""

import re
from typing import List, Set, Dict
from urllib.parse import urlparse


class IntelligenceExtractor:
    """Extracts actionable intelligence from scam conversations"""
    
    def __init__(self):
        self.bank_accounts: List[str] = []
        self.upi_ids: List[str] = []
        self.phishing_links: List[str] = []
        self.phone_numbers: List[str] = []
        self.suspicious_keywords: List[str] = []
        
        # Patterns for extraction
        self.patterns = {
            "phone": r'\+?\d[\d\s\-\(\)]{8,}\d',
            "upi": r'[\w\.\-]+@[\w]+',
            "url": r'https?://[^\s]+|www\.[^\s]+',
            "bank_account": r'\b\d{9,18}\b',
            "ifsc": r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
            "card": r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
        }
        
        # Known scam keywords to track
        self.scam_keywords = [
            "verify now", "urgent action", "account blocked", "suspended",
            "click here", "limited time", "act now", "confirm immediately",
            "prize", "winner", "congratulations", "reward",
            "refund pending", "cashback", "bonus",
            "legal action", "arrest warrant", "court notice",
            "suspicious activity", "unauthorized access",
            "update kyc", "re-kyc", "pan update", "aadhaar update"
        ]
    
    def extract_from_message(self, message: str) -> Dict[str, List[str]]:
        """
        Extract all intelligence from a message
        
        Args:
            message: Message text to analyze
        
        Returns:
            Dictionary of extracted items
        """
        extracted = {
            "phone_numbers": [],
            "upi_ids": [],
            "urls": [],
            "bank_accounts": [],
            "keywords": []
        }
        
        # Extract phone numbers
        phones = self._extract_pattern(message, "phone")
        for phone in phones:
            cleaned_phone = self._clean_phone_number(phone)
            if cleaned_phone and cleaned_phone not in self.phone_numbers:
                self.phone_numbers.append(cleaned_phone)
                extracted["phone_numbers"].append(cleaned_phone)
        
        # Extract UPI IDs
        upis = self._extract_pattern(message, "upi")
        for upi in upis:
            if upi not in self.upi_ids and "@" in upi:
                self.upi_ids.append(upi)
                extracted["upi_ids"].append(upi)
        
        # Extract URLs
        urls = self._extract_pattern(message, "url")
        for url in urls:
            if url not in self.phishing_links:
                self.phishing_links.append(url)
                extracted["urls"].append(url)
        
        # Extract bank accounts
        accounts = self._extract_pattern(message, "bank_account")
        for account in accounts:
            if account not in self.bank_accounts and len(account) >= 9:
                self.bank_accounts.append(account)
                extracted["bank_accounts"].append(account)
        
        # Extract suspicious keywords
        message_lower = message.lower()
        for keyword in self.scam_keywords:
            if keyword in message_lower and keyword not in self.suspicious_keywords:
                self.suspicious_keywords.append(keyword)
                extracted["keywords"].append(keyword)
        
        return extracted
    
    def _extract_pattern(self, text: str, pattern_name: str) -> List[str]:
        """Extract matches for a specific pattern"""
        if pattern_name not in self.patterns:
            return []
        
        pattern = self.patterns[pattern_name]
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_matches = []
        for match in matches:
            if match not in seen:
                seen.add(match)
                unique_matches.append(match)
        
        return unique_matches
    
    def _clean_phone_number(self, phone: str) -> str:
        """Clean and validate phone number"""
        # Remove spaces, dashes, parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Must be 10-15 digits
        if len(cleaned) < 10 or len(cleaned) > 15:
            return ""
        
        # Must be all digits (possibly with leading +)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        if not cleaned.isdigit():
            return ""
        
        # Add back + if it was there
        if phone.strip().startswith('+'):
            return '+' + cleaned
        
        return cleaned
    
    def analyze_url(self, url: str) -> Dict[str, any]:
        """Analyze a URL for suspicious characteristics"""
        analysis = {
            "url": url,
            "is_suspicious": False,
            "indicators": []
        }
        
        try:
            parsed = urlparse(url)
            
            # Check for IP address instead of domain
            if re.match(r'^\d+\.\d+\.\d+\.\d+$', parsed.netloc):
                analysis["is_suspicious"] = True
                analysis["indicators"].append("IP address instead of domain")
            
            # Check for suspicious TLDs
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top']
            if any(parsed.netloc.endswith(tld) for tld in suspicious_tlds):
                analysis["is_suspicious"] = True
                analysis["indicators"].append("Suspicious TLD")
            
            # Check for too many subdomains
            domain_parts = parsed.netloc.split('.')
            if len(domain_parts) > 4:
                analysis["is_suspicious"] = True
                analysis["indicators"].append("Excessive subdomains")
            
            # Check for suspicious keywords in domain
            suspicious_words = ['verify', 'secure', 'account', 'update', 'confirm', 'banking']
            if any(word in parsed.netloc.lower() for word in suspicious_words):
                analysis["is_suspicious"] = True
                analysis["indicators"].append("Suspicious keywords in domain")
            
        except Exception:
            analysis["is_suspicious"] = True
            analysis["indicators"].append("Malformed URL")
        
        return analysis
    
    def get_intelligence_summary(self) -> Dict[str, any]:
        """Get a summary of all collected intelligence"""
        return {
            "bank_accounts": self.bank_accounts,
            "upi_ids": self.upi_ids,
            "phishing_links": self.phishing_links,
            "phone_numbers": self.phone_numbers,
            "suspicious_keywords": self.suspicious_keywords,
            "total_indicators": (
                len(self.bank_accounts) +
                len(self.upi_ids) +
                len(self.phishing_links) +
                len(self.phone_numbers) +
                len(self.suspicious_keywords)
            )
        }
    
    def generate_summary(self) -> str:
        """Generate a human-readable summary of the intelligence"""
        summary_parts = []
        
        if self.phone_numbers:
            summary_parts.append(f"Extracted {len(self.phone_numbers)} phone number(s)")
        
        if self.upi_ids:
            summary_parts.append(f"Extracted {len(self.upi_ids)} UPI ID(s)")
        
        if self.phishing_links:
            summary_parts.append(f"Identified {len(self.phishing_links)} suspicious link(s)")
        
        if self.bank_accounts:
            summary_parts.append(f"Extracted {len(self.bank_accounts)} bank account number(s)")
        
        if self.suspicious_keywords:
            top_keywords = self.suspicious_keywords[:5]
            summary_parts.append(f"Key tactics: {', '.join(top_keywords)}")
        
        if not summary_parts:
            return "Limited intelligence extracted from conversation"
        
        return ". ".join(summary_parts) + "."
    
    def get_scam_type(self) -> str:
        """Determine the type of scam based on collected intelligence"""
        keywords_text = " ".join(self.suspicious_keywords).lower()
        
        if any(word in keywords_text for word in ["prize", "winner", "won", "lottery"]):
            return "Prize/Lottery Scam"
        
        if any(word in keywords_text for word in ["bank", "account", "blocked", "suspended"]):
            return "Bank Account Scam"
        
        if any(word in keywords_text for word in ["kyc", "update", "verify"]):
            return "KYC/Verification Scam"
        
        if any(word in keywords_text for word in ["refund", "cashback"]):
            return "Refund Scam"
        
        if any(word in keywords_text for word in ["legal", "arrest", "court"]):
            return "Threat/Extortion Scam"
        
        if self.phishing_links:
            return "Phishing Scam"
        
        return "General Fraud"
