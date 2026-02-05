# 🚀 Quick Start Guide - Get Running in 5 Minutes

## Prerequisites
- Python 3.9 or higher
- pip

## Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

## Step 2: Set Your API Key (30 seconds)
Open `main.py` and change this line:
```python
API_KEY = "your-secret-api-key-here"  # Change this to something secure!
```

**Example**: `API_KEY = "my-super-secret-key-12345"`

## Step 3: Run the Server (30 seconds)
```bash
python main.py
```

You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## Step 4: Test It (1 minute)

### Option A: Use the Test Client
In a new terminal:
```bash
python test_client.py
```

### Option B: Use curl
```bash
curl -X POST http://localhost:8000/api/message \
  -H "x-api-key: my-super-secret-key-12345" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today!",
      "timestamp": "2026-01-30T10:00:00Z"
    },
    "conversationHistory": []
  }'
```

### Option C: Visit the API Docs
Open browser: `http://localhost:8000/docs`

## Step 5: See It Work! (2 minutes)

Send these messages in sequence to see the agent in action:

**Message 1:**
```json
{
  "sessionId": "demo-session",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be suspended. Verify now at http://fake-bank.com",
    "timestamp": "2026-01-30T10:00:00Z"
  },
  "conversationHistory": []
}
```

**Expected Response:** Agent asks who they are

**Message 2:**
```json
{
  "sessionId": "demo-session",
  "message": {
    "sender": "scammer",
    "text": "This is State Bank. You must verify within 1 hour or we will block your account permanently.",
    "timestamp": "2026-01-30T10:01:00Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be suspended. Verify now at http://fake-bank.com",
      "timestamp": "2026-01-30T10:00:00Z"
    },
    {
      "sender": "user",
      "text": "Who is this? Which bank are you calling from?",
      "timestamp": "2026-01-30T10:00:30Z"
    }
  ]
}
```

**Expected Response:** Agent shows concern and asks questions

## That's It! 🎉

Your honeypot is now running and ready to catch scammers!

## What Happens Next?

The agent will:
1. **Detect scams** using pattern matching
2. **Engage naturally** through 4 conversation stages
3. **Extract intelligence** (phone numbers, UPI IDs, links, etc.)
4. **Report automatically** to the GUVI endpoint after 15-20 exchanges

## Common Commands

**Start server:**
```bash
python main.py
```

**Run tests:**
```bash
python test_client.py
```

**Check health:**
```bash
curl http://localhost:8000/health
```

**View API docs:**
```
http://localhost:8000/docs
```

## Troubleshooting

**"Port already in use"**
```bash
# Change port in main.py:
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # Change 8000 to 8001
```

**"Invalid API key"**
- Make sure you changed the API_KEY in main.py
- Use the same key in your x-api-key header

**"Module not found"**
```bash
pip install -r requirements.txt
```

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) for integration examples
3. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for production deployment

**Happy scam hunting! 🕵️**
