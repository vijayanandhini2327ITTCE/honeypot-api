"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class Message(BaseModel):
    """Message model"""
    sender: str = Field(..., description="Sender of the message: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="ISO-8601 timestamp")


class Metadata(BaseModel):
    """Metadata about the conversation"""
    channel: Optional[str] = Field(None, description="Communication channel (SMS, WhatsApp, Email, Chat)")
    language: Optional[str] = Field(None, description="Language used")
    locale: Optional[str] = Field(None, description="Country or region")


class IncomingRequest(BaseModel):
    """Incoming message request model"""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Current incoming message")
    conversationHistory: Optional[List[Message]] = Field(
        default=[],
        description="Previous messages in conversation"
    )
    metadata: Optional[Metadata] = Field(None, description="Conversation metadata")


class AgentResponse(BaseModel):
    """Agent response model"""
    status: str = Field(..., description="Response status")
    reply: str = Field(..., description="Agent's reply message")


class ExtractedIntelligence(BaseModel):
    """Extracted intelligence data"""
    bankAccounts: List[str] = Field(default=[], description="Extracted bank account numbers")
    upiIds: List[str] = Field(default=[], description="Extracted UPI IDs")
    phishingLinks: List[str] = Field(default=[], description="Extracted phishing links")
    phoneNumbers: List[str] = Field(default=[], description="Extracted phone numbers")
    suspiciousKeywords: List[str] = Field(default=[], description="Suspicious keywords found")


class FinalResultPayload(BaseModel):
    """Final result payload to send to GUVI"""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: Dict[str, List[str]]
    agentNotes: str
