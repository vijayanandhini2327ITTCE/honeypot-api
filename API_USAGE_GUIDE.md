# API Usage Guide

## Quick Reference

**Base URL**: `http://localhost:8000` (or your deployed URL)

**Authentication**: Include API key in header
```
x-api-key: your-secret-api-key-here
```

---

## Endpoints

### 1. Process Message

**POST** `/api/message`

Main endpoint for scam detection and agent engagement.

#### Example: First Message

```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately at http://fake-bank.com",
      "timestamp": "2026-01-30T10:15:30Z"
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Response**:
```json
{
  "status": "success",
  "reply": "Who is this? Which bank are you calling from?"
}
```

#### Example: Follow-up Message

```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session-123",
    "message": {
      "sender": "scammer",
      "text": "This is State Bank. You must verify within 1 hour or we will suspend your account.",
      "timestamp": "2026-01-30T10:17:10Z"
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your bank account will be blocked today. Verify immediately at http://fake-bank.com",
        "timestamp": "2026-01-30T10:15:30Z"
      },
      {
        "sender": "user",
        "text": "Who is this? Which bank are you calling from?",
        "timestamp": "2026-01-30T10:16:00Z"
      }
    ],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Response**:
```json
{
  "status": "success",
  "reply": "Oh no! What did I do wrong? Can you tell me what's happening?"
}
```

---

### 2. Health Check

**GET** `/health`

Check if the API is running.

```bash
curl http://localhost:8000/health
```

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T10:15:30.123456",
  "active_sessions": 3
}
```

---

### 3. Get Session Info

**GET** `/sessions/{sessionId}`

Retrieve information about a specific session (for debugging).

```bash
curl http://localhost:8000/sessions/session-123
```

**Response**:
```json
{
  "sessionId": "session-123",
  "scamDetected": true,
  "messageCount": 10,
  "engagementCount": 5
}
```

---

## Common Scam Scenarios

### Bank Fraud
```json
{
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your SBI account has been suspended. Verify at http://sbi-verify.tk within 1 hour to avoid permanent closure."
  }
}
```

### UPI Scam
```json
{
  "message": {
    "sender": "scammer",
    "text": "Congratulations! You've won ₹50,000 cashback. Send your UPI ID to claim: winner@paytm"
  }
}
```

### KYC Update Scam
```json
{
  "message": {
    "sender": "scammer",
    "text": "Your KYC needs urgent update. Click here and enter your card details: http://kyc-update.xyz"
  }
}
```

### Refund Scam
```json
{
  "message": {
    "sender": "scammer",
    "text": "You have a pending refund of ₹5,000. Share your bank account number and IFSC code to receive it."
  }
}
```

### Threat Scam
```json
{
  "message": {
    "sender": "scammer",
    "text": "This is Income Tax Department. You have unpaid taxes. Legal action will be taken if not paid immediately."
  }
}
```

---

## Python Integration Example

```python
import requests
from datetime import datetime

class ScamHoneypot:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.sessions = {}
    
    def process_message(self, session_id, message_text, sender="scammer"):
        """Send a message to the honeypot"""
        
        # Get or create session
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        
        # Prepare payload
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": sender,
                "text": message_text,
                "timestamp": datetime.now().isoformat() + "Z"
            },
            "conversationHistory": self.sessions[session_id],
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }
        
        # Send request
        response = requests.post(
            f"{self.api_url}/api/message",
            headers=self.headers,
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_reply = data["reply"]
            
            # Update conversation history
            self.sessions[session_id].append({
                "sender": sender,
                "text": message_text,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            self.sessions[session_id].append({
                "sender": "user",
                "text": agent_reply,
                "timestamp": datetime.now().isoformat() + "Z"
            })
            
            return agent_reply
        else:
            raise Exception(f"API Error: {response.status_code}")

# Usage
honeypot = ScamHoneypot(
    api_url="http://localhost:8000",
    api_key="your-secret-api-key-here"
)

# Start conversation
reply = honeypot.process_message(
    session_id="test-001",
    message_text="Your account will be blocked. Verify now!"
)
print(f"Agent: {reply}")

# Continue conversation
reply = honeypot.process_message(
    session_id="test-001",
    message_text="Click this link: http://fake-bank.com"
)
print(f"Agent: {reply}")
```

---

## JavaScript/Node.js Integration Example

```javascript
const axios = require('axios');

class ScamHoneypot {
    constructor(apiUrl, apiKey) {
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.sessions = {};
    }
    
    async processMessage(sessionId, messageText, sender = 'scammer') {
        // Get or create session
        if (!this.sessions[sessionId]) {
            this.sessions[sessionId] = [];
        }
        
        // Prepare payload
        const payload = {
            sessionId: sessionId,
            message: {
                sender: sender,
                text: messageText,
                timestamp: new Date().toISOString()
            },
            conversationHistory: this.sessions[sessionId],
            metadata: {
                channel: 'SMS',
                language: 'English',
                locale: 'IN'
            }
        };
        
        // Send request
        const response = await axios.post(
            `${this.apiUrl}/api/message`,
            payload,
            {
                headers: {
                    'x-api-key': this.apiKey,
                    'Content-Type': 'application/json'
                }
            }
        );
        
        const agentReply = response.data.reply;
        
        // Update conversation history
        this.sessions[sessionId].push({
            sender: sender,
            text: messageText,
            timestamp: new Date().toISOString()
        });
        this.sessions[sessionId].push({
            sender: 'user',
            text: agentReply,
            timestamp: new Date().toISOString()
        });
        
        return agentReply;
    }
}

// Usage
const honeypot = new ScamHoneypot(
    'http://localhost:8000',
    'your-secret-api-key-here'
);

(async () => {
    const reply1 = await honeypot.processMessage(
        'test-001',
        'Your account will be blocked. Verify now!'
    );
    console.log('Agent:', reply1);
    
    const reply2 = await honeypot.processMessage(
        'test-001',
        'Click this link: http://fake-bank.com'
    );
    console.log('Agent:', reply2);
})();
```

---

## Error Responses

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

**Solution**: Check your `x-api-key` header

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "sessionId"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Solution**: Ensure all required fields are present

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: [error message]"
}
```

**Solution**: Check server logs for details

---

## Expected Intelligence Report

After 15-20 message exchanges, the system sends this to GUVI:

```json
{
  "sessionId": "session-123",
  "scamDetected": true,
  "totalMessagesExchanged": 18,
  "extractedIntelligence": {
    "bankAccounts": ["123456789012"],
    "upiIds": ["scammer@paytm", "fraud@phonepe"],
    "phishingLinks": [
      "http://fake-bank.com",
      "http://sbi-verify.tk"
    ],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": [
      "urgent",
      "verify now",
      "account blocked",
      "click here",
      "limited time"
    ]
  },
  "agentNotes": "Extracted 2 UPI IDs and 2 phishing links. Scammer used urgency tactics and payment redirection. Identified as Bank Account Scam."
}
```

---

## Best Practices

1. **Session IDs**: Use unique, non-sequential session IDs
2. **Conversation History**: Always include complete history for context
3. **Timestamps**: Use ISO-8601 format with timezone
4. **Error Handling**: Implement retry logic for network errors
5. **Rate Limiting**: Don't send more than 1 request per second
6. **Logging**: Log all interactions for analysis

---

## Testing Tips

1. **Test Various Scam Types**: Bank fraud, UPI scams, KYC updates, prize scams
2. **Test Conversation Flow**: Ensure agent adapts through all 4 stages
3. **Test Intelligence Extraction**: Verify all data types are captured
4. **Test Edge Cases**: Very short messages, long messages, special characters
5. **Monitor Logs**: Check for scam detection accuracy

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
