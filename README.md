# Agentic Honey-Pot for Scam Detection & Intelligence Extraction

An AI-powered honeypot system that detects scam intent and autonomously engages scammers to extract useful intelligence without revealing detection.

## 🎯 Features

- **Scam Detection**: Advanced pattern matching and heuristic-based detection
- **AI Agent**: Human-like conversational agent that engages scammers
- **Intelligence Extraction**: Automatically extracts phone numbers, UPI IDs, phishing links, bank accounts, and suspicious keywords
- **Multi-turn Conversations**: Maintains context across multiple message exchanges
- **Adaptive Responses**: Agent behavior adapts based on conversation stage and scam type
- **Automatic Reporting**: Sends final intelligence to GUVI evaluation endpoint

## 📋 Requirements

- Python 3.9+
- FastAPI
- Uvicorn
- Pydantic
- Requests

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd honeypot-api

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `main.py` and set your API key:

```python
API_KEY = "your-secret-api-key-here"  # Change this!
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and set your API_KEY
```

### 3. Run the Server

```bash
# Development mode
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

### 4. Test the API

```bash
# Run the test client
python test_client.py
```

## 📡 API Documentation

### Authentication

All requests must include the API key in the header:

```
x-api-key: your-secret-api-key-here
Content-Type: application/json
```

### Main Endpoint

**POST** `/api/message`

Processes incoming messages and returns agent responses.

#### Request Body

```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify now!",
    "timestamp": "2026-01-30T10:15:30Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Previous message",
      "timestamp": "2026-01-30T10:14:00Z"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

#### Response

```json
{
  "status": "success",
  "reply": "Why is my account being blocked? What happened?"
}
```

### Health Check

**GET** `/health`

Returns the health status of the API.

```json
{
  "status": "healthy",
  "timestamp": "2026-01-30T10:15:30Z",
  "active_sessions": 5
}
```

## 🧠 How It Works

### 1. Scam Detection

The system analyzes messages for:
- **Urgent language**: "immediately", "now", "urgent"
- **Financial keywords**: "bank", "account", "UPI", "payment"
- **Verification requests**: "verify", "confirm", "update"
- **Threats**: "arrest", "legal action", "suspended"
- **Rewards**: "prize", "winner", "congratulations"
- **Suspicious URLs and phone numbers**

### 2. AI Agent Engagement

The agent uses a **4-stage conversation strategy**:

1. **Initial Confusion (1-3 messages)**: Questions who they are, expresses confusion
2. **Concern & Information Gathering (4-7 messages)**: Shows concern, asks for details
3. **Pretend Compliance (8-12 messages)**: Appears cooperative but introduces delays
4. **Intelligence Extraction (13+ messages)**: Asks specific questions to extract data

### 3. Intelligence Extraction

Automatically extracts:
- **Phone numbers**: Any phone format
- **UPI IDs**: username@provider
- **Phishing links**: Suspicious URLs
- **Bank accounts**: Account numbers
- **Suspicious keywords**: Scam tactics and phrases

### 4. Final Reporting

When the conversation reaches a natural end (15-20 exchanges or sufficient intelligence), the system automatically sends a final report to:

```
POST https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

## 📊 Example Scenarios

### Bank Fraud Scam

```
Scammer: Your bank account will be blocked today. Verify immediately.
Agent: Who is this? Which bank are you calling from?

Scammer: This is from SBI. Click here to verify: http://fake-sbi.com
Agent: Is this really my bank? How do I know this is legitimate?

Scammer: You must verify now or lose access permanently!
Agent: Oh no! What did I do wrong? Can you explain what's happening?
```

### UPI Fraud Scam

```
Scammer: You've won ₹50,000! Send your UPI ID to claim.
Agent: Really? I won something? What is it?

Scammer: Yes! Send your UPI ID to scammer@paytm
Agent: How did I win? I don't remember entering anything.

Scammer: Just send your UPI ID now!
Agent: Let me check my account first. Give me a moment.
```

## 🔧 Configuration Options

### Detection Threshold

Adjust scam detection sensitivity in `scam_detector.py`:

```python
# Default threshold: 0.4
is_scam = confidence >= 0.4  # Lower = more sensitive
```

### Conversation Length

Adjust max conversation turns in `ai_agent.py`:

```python
if engagement_count >= 15:  # Change this value
    return True
```

### Response Styles

Customize agent responses in `ai_agent.py`:

```python
self.confused_responses = [
    "Your custom response here",
    # Add more...
]
```

## 🐳 Docker Deployment

```bash
# Build the image
docker build -t honeypot-api .

# Run the container
docker run -p 8000:8000 -e API_KEY=your-key-here honeypot-api
```

## 📁 Project Structure

```
honeypot-api/
├── main.py                      # FastAPI application
├── models.py                    # Pydantic models
├── scam_detector.py             # Scam detection logic
├── ai_agent.py                  # AI agent responses
├── intelligence_extractor.py    # Intelligence extraction
├── test_client.py               # Testing client
├── requirements.txt             # Dependencies
├── Dockerfile                   # Docker configuration
├── .env.example                 # Environment variables template
└── README.md                    # Documentation
```

## 🧪 Testing

### Manual Testing

```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: your-secret-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify now!",
      "timestamp": "2026-01-30T10:15:30Z"
    },
    "conversationHistory": []
  }'
```

### Automated Testing

```bash
python test_client.py
```

## 🔒 Security Considerations

- **API Key**: Always use a strong, unique API key
- **Rate Limiting**: Consider adding rate limiting in production
- **Data Storage**: Session data is in-memory by default (use Redis/DB for production)
- **Logging**: Sensitive information is logged - secure your logs
- **HTTPS**: Always use HTTPS in production

## 🎯 Evaluation Criteria

The system is evaluated on:

1. **Scam Detection Accuracy**: How well it identifies scams
2. **Engagement Quality**: How natural and convincing the agent is
3. **Intelligence Extraction**: Quality and quantity of extracted data
4. **API Stability**: Response time and reliability
5. **Ethical Behavior**: Responsible handling of data

## 📝 Response Strategy

### Stage 1: Initial Contact (Messages 1-3)
- Express confusion
- Question legitimacy
- Ask who they are

### Stage 2: Concern (Messages 4-7)
- Show worry
- Ask for more details
- Gather information about the scam type

### Stage 3: Compliance (Messages 8-12)
- Appear cooperative
- Introduce technical difficulties
- Create delays to extract more info

### Stage 4: Extraction (Messages 13+)
- Ask specific questions
- Request documentation
- Try to identify the organization

## 🚨 Ethical Guidelines

✅ **DO:**
- Engage scammers to waste their time
- Extract intelligence for law enforcement
- Protect potential victims

❌ **DON'T:**
- Impersonate real individuals
- Provide instructions for illegal activities
- Harass individuals
- Share extracted data publicly

## 🐛 Troubleshooting

### API returns 401 Unauthorized
- Check that `x-api-key` header is set correctly
- Verify API key matches in `main.py`

### Agent not detecting scams
- Lower the detection threshold in `scam_detector.py`
- Check scam indicators with logs

### Final result not sent to GUVI
- Verify GUVI_CALLBACK_URL is correct
- Check network connectivity
- Review logs for errors

## 📞 Support

For issues or questions:
1. Check the logs for error details
2. Review the test client output
3. Verify API key configuration
4. Ensure all dependencies are installed

## 🏆 Best Practices

1. **Let the agent run**: Don't end conversations too early
2. **Monitor logs**: Track intelligence extraction in real-time
3. **Adjust responses**: Customize agent personality as needed
4. **Test thoroughly**: Use various scam scenarios
5. **Secure your API**: Use strong keys and HTTPS

## 📄 License

This project is created for the GUVI Hackathon.

---

**Built with ❤️ for scam detection and prevention**
