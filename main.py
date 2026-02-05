"""
AI-Powered Agentic Honeypot for Scam Detection
Main FastAPI application
"""

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime
import logging
import requests
import os

from scam_detector import ScamDetector
from ai_agent import HoneypotAgent
from intelligence_extractor import IntelligenceExtractor
from models import (
    Message,
    IncomingRequest,
    AgentResponse,
    ExtractedIntelligence,
    FinalResultPayload
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honeypot API",
    description="AI-powered system for scam detection and intelligence extraction",
    version="1.0.0"
)

# Configuration - Get from environment variables for cloud deployment
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")  # Change default or set env var
GUVI_CALLBACK_URL = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"

# Log the API key being used (first 5 chars only for security)
logger.info(f"API Key configured: {API_KEY[:5]}..." if len(API_KEY) > 5 else "API Key not set!")

# Initialize components
scam_detector = ScamDetector()
honeypot_agent = HoneypotAgent()
intelligence_extractor = IntelligenceExtractor()

# Session storage (in production, use Redis or database)
sessions: Dict[str, Dict[str, Any]] = {}


def verify_api_key(x_api_key: str = Header(...)) -> bool:
    """Verify API key from header"""
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key[:5]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")
    return True


@app.post("/api/message", response_model=AgentResponse)
async def process_message(
    request: IncomingRequest,
    x_api_key: str = Header(...)
):
    """
    Main endpoint to process incoming messages
    Detects scam intent and engages with AI agent
    """
    try:
        # Verify API key
        verify_api_key(x_api_key)
        
        session_id = request.sessionId
        current_message = request.message
        conversation_history = request.conversationHistory or []
        
        logger.info(f"Processing message for session: {session_id}")
        logger.info(f"Message from {current_message.sender}: {current_message.text}")
        
        # Initialize or retrieve session
        if session_id not in sessions:
            sessions[session_id] = {
                "messages": [],
                "scam_detected": False,
                "intelligence": IntelligenceExtractor(),
                "engagement_count": 0,
                "started_at": datetime.now().isoformat()
            }
        
        session = sessions[session_id]
        session["messages"].append(current_message.dict())
        session["engagement_count"] += 1
        
        # Detect scam intent
        full_conversation = conversation_history + [current_message]
        is_scam, scam_confidence, scam_indicators = scam_detector.detect_scam(
            current_message.text,
            conversation_history
        )
        
        logger.info(f"Scam detection - Is scam: {is_scam}, Confidence: {scam_confidence:.2f}")
        
        if is_scam:
            session["scam_detected"] = True
            
            # Extract intelligence from current message
            session["intelligence"].extract_from_message(current_message.text)
            
            # Generate AI agent response
            agent_reply = honeypot_agent.generate_response(
                current_message.text,
                conversation_history,
                scam_indicators,
                session["engagement_count"]
            )
            
            # Store agent response
            agent_message = Message(
                sender="user",
                text=agent_reply,
                timestamp=datetime.now().isoformat()
            )
            session["messages"].append(agent_message.dict())
            
            # Check if we should end conversation and send final result
            should_end = honeypot_agent.should_end_conversation(
                session["engagement_count"],
                session["intelligence"]
            )
            
            if should_end:
                logger.info(f"Ending conversation for session {session_id}")
                await send_final_result(session_id, session)
            
            return AgentResponse(
                status="success",
                reply=agent_reply
            )
        else:
            # Not a scam - respond normally or politely disengage
            reply = "I'm not sure I understand. Could you clarify?"
            
            return AgentResponse(
                status="success",
                reply=reply
            )
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


async def send_final_result(session_id: str, session: Dict[str, Any]):
    """
    Send final intelligence report to GUVI evaluation endpoint
    """
    try:
        intelligence = session["intelligence"]
        
        # Prepare extracted intelligence
        extracted_intelligence = {
            "bankAccounts": intelligence.bank_accounts,
            "upiIds": intelligence.upi_ids,
            "phishingLinks": intelligence.phishing_links,
            "phoneNumbers": intelligence.phone_numbers,
            "suspiciousKeywords": intelligence.suspicious_keywords
        }
        
        # Prepare payload
        payload = {
            "sessionId": session_id,
            "scamDetected": session["scam_detected"],
            "totalMessagesExchanged": session["engagement_count"],
            "extractedIntelligence": extracted_intelligence,
            "agentNotes": intelligence.generate_summary()
        }
        
        logger.info(f"Sending final result for session {session_id}")
        logger.info(f"Payload: {payload}")
        
        # Send to GUVI endpoint
        response = requests.post(
            GUVI_CALLBACK_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent final result for session {session_id}")
        else:
            logger.error(f"Failed to send final result: {response.status_code} - {response.text}")
            
    except Exception as e:
        logger.error(f"Error sending final result: {str(e)}", exc_info=True)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(sessions)
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Agentic Honeypot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/sessions/{session_id}")
async def get_session(session_id: str, x_api_key: str = Header(...)):
    """Get session details (for debugging)"""
    verify_api_key(x_api_key)
    
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "sessionId": session_id,
        "scamDetected": sessions[session_id]["scam_detected"],
        "messageCount": len(sessions[session_id]["messages"]),
        "engagementCount": sessions[session_id]["engagement_count"]
    }


if __name__ == "__main__":
    # Get port from environment variable (for cloud platforms like Render, Heroku, Railway)
    port = int(os.getenv("PORT", 8000))
    
    logger.info(f"Starting server on port {port}")
    logger.info(f"API Key: {API_KEY[:5]}..." if len(API_KEY) > 5 else "No API key set!")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
