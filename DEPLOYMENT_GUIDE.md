# Deployment Guide - Agentic Honeypot API

Complete guide for deploying the AI-powered scam detection honeypot system.

---

## 📋 Pre-Deployment Checklist

- [ ] Python 3.9+ installed
- [ ] pip installed
- [ ] Git installed (optional)
- [ ] Domain/Server ready (for production)
- [ ] API key chosen (strong, unique)

---

## 🚀 Deployment Options

### Option 1: Local Development (Recommended for Testing)

#### Step 1: Setup
```bash
# Navigate to project directory
cd honeypot-api

# Install dependencies
pip install -r requirements.txt
```

#### Step 2: Configure
```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your API key
nano .env
# or
vi .env
```

Set this in `.env`:
```
API_KEY=your-strong-secret-key-here-change-this
```

Or edit `main.py` directly:
```python
API_KEY = "your-strong-secret-key-here-change-this"
```

#### Step 3: Run
```bash
# Option A: Using startup script
chmod +x start.sh
./start.sh

# Option B: Direct Python
python main.py

# Option C: Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Step 4: Test
```bash
# In another terminal
python test_client.py
```

Visit `http://localhost:8000/docs` for interactive API documentation.

---

### Option 2: Docker Deployment

#### Prerequisites
- Docker installed
- Docker Compose installed (optional)

#### Step 1: Build Image
```bash
docker build -t honeypot-api .
```

#### Step 2: Run Container
```bash
# Run with environment variable
docker run -d \
  -p 8000:8000 \
  -e API_KEY=your-secret-key-here \
  --name honeypot-api \
  honeypot-api
```

#### Or use Docker Compose:
```bash
# Set API_KEY in .env file first
echo "API_KEY=your-secret-key-here" > .env

# Start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

### Option 3: Production Deployment (Linux Server)

#### Step 1: Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Install nginx (for reverse proxy)
sudo apt install nginx -y
```

#### Step 2: Deploy Application
```bash
# Create application directory
sudo mkdir -p /opt/honeypot-api
cd /opt/honeypot-api

# Copy project files
# (Upload files via scp, git clone, or other method)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Step 3: Create Systemd Service
```bash
sudo nano /etc/systemd/system/honeypot-api.service
```

Add this content:
```ini
[Unit]
Description=Honeypot API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/honeypot-api
Environment="PATH=/opt/honeypot-api/venv/bin"
Environment="API_KEY=your-secret-key-here"
ExecStart=/opt/honeypot-api/venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

#### Step 4: Configure Nginx Reverse Proxy
```bash
sudo nano /etc/nginx/sites-available/honeypot-api
```

Add this content:
```nginx
server {
    listen 80;
    server_name your-domain.com;  # Change this

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/honeypot-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Step 5: Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable honeypot-api
sudo systemctl start honeypot-api
sudo systemctl status honeypot-api
```

#### Step 6: Setup SSL (Optional but Recommended)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

---

### Option 4: Cloud Platform Deployment

#### Heroku
```bash
# Install Heroku CLI
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
heroku create your-app-name
heroku config:set API_KEY=your-secret-key-here
git push heroku main
```

#### AWS EC2
1. Launch EC2 instance (Ubuntu 22.04)
2. Install Python and dependencies
3. Follow "Production Deployment" steps above
4. Configure security group to allow port 80/443

#### Google Cloud Run
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/honeypot-api
gcloud run deploy --image gcr.io/PROJECT-ID/honeypot-api --platform managed
```

#### DigitalOcean App Platform
1. Connect GitHub repository
2. Set environment variables in dashboard
3. Deploy automatically

---

## 🔧 Post-Deployment Configuration

### 1. Test the Deployment
```bash
# Health check
curl http://your-domain.com/health

# Test API with your key
curl -X POST http://your-domain.com/api/message \
  -H "x-api-key: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your account will be blocked",
      "timestamp": "2026-01-30T10:00:00Z"
    },
    "conversationHistory": []
  }'
```

### 2. Monitor Logs
```bash
# Systemd service
sudo journalctl -u honeypot-api -f

# Docker
docker logs -f honeypot-api

# Direct run
tail -f logs/app.log
```

### 3. Setup Monitoring (Optional)
```bash
# Install monitoring tools
pip install prometheus-fastapi-instrumentator

# Add to main.py:
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

---

## 🔒 Security Hardening

### 1. Strong API Key
```bash
# Generate strong API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. Rate Limiting
Add to `main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

@app.post("/api/message")
@limiter.limit("10/minute")
async def process_message(...):
    ...
```

### 3. HTTPS Only
```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

### 4. Firewall
```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 📊 Monitoring & Maintenance

### Check Service Status
```bash
sudo systemctl status honeypot-api
```

### View Recent Logs
```bash
sudo journalctl -u honeypot-api -n 100
```

### Restart Service
```bash
sudo systemctl restart honeypot-api
```

### Update Application
```bash
cd /opt/honeypot-api
git pull  # or upload new files
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart honeypot-api
```

---

## 🧪 Testing in Production

### Test Script
```python
import requests
import time

API_URL = "https://your-domain.com"
API_KEY = "your-secret-key"

def test_production():
    # Health check
    health = requests.get(f"{API_URL}/health")
    assert health.status_code == 200
    print("✓ Health check passed")
    
    # Test scam detection
    response = requests.post(
        f"{API_URL}/api/message",
        headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
        json={
            "sessionId": f"test-{int(time.time())}",
            "message": {
                "sender": "scammer",
                "text": "Your bank account will be blocked",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
            },
            "conversationHistory": []
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    print(f"✓ Scam detection working: {data['reply']}")

if __name__ == "__main__":
    test_production()
```

---

## 🐛 Troubleshooting

### Issue: Port 8000 already in use
```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill it
sudo kill -9 <PID>
```

### Issue: Permission denied
```bash
# Fix permissions
sudo chown -R $USER:$USER /opt/honeypot-api
```

### Issue: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: API returns 500 error
```bash
# Check logs
sudo journalctl -u honeypot-api -n 50

# Check Python errors
python main.py  # Run directly to see errors
```

---

## 📈 Scaling

### Horizontal Scaling with Load Balancer
```nginx
upstream honeypot_backend {
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    location / {
        proxy_pass http://honeypot_backend;
    }
}
```

### Using Gunicorn for Production
```bash
pip install gunicorn

# Run with workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 📝 Maintenance Checklist

Weekly:
- [ ] Check logs for errors
- [ ] Monitor disk space
- [ ] Review intelligence reports

Monthly:
- [ ] Update dependencies
- [ ] Review and rotate API keys
- [ ] Backup configuration
- [ ] Check SSL certificate expiry

---

## 🆘 Support

For issues:
1. Check logs first
2. Review this guide
3. Test with `test_client.py`
4. Check API documentation at `/docs`

---

**Your honeypot API is now deployed and ready to catch scammers! 🎯**
