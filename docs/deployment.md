# Deployment Guide

This guide explains how to deploy the FastAPI Stock & Crypto Data API to production.

## 🚀 Current Deployment

The API is currently deployed on **Render.com** at:
```
https://fastapi-stock-data.onrender.com
```

### Deployment Details

- **Platform**: Render.com (Free tier)
- **Runtime**: Python 3.9+
- **Web Framework**: FastAPI + Uvicorn
- **Database**: SQLite (for development)
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## 📋 Prerequisites

### Local Development

1. **Python 3.9+**
   ```bash
   python --version
   ```

2. **Git**
   ```bash
   git --version
   ```

3. **Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

### Dependencies

```bash
pip install -r requirements.txt
```

## 🏗️ Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/OMCHOKSI108/FastAPI-Stock-data-.git
cd FastAPI-Stock-data-
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create `.env` file:

```bash
# .env
PROVIDER=YFINANCE
DEBUG=True
DATABASE_URL=sqlite:///./app.db

# Optional: Binance API keys (for crypto endpoints)
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
```

### 4. Run Locally

```bash
# Development server
uvicorn app.main:app --reload

# Or with custom host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test Endpoints

```bash
# Health check
curl http://localhost:8000/health

# API docs
open http://localhost:8000/docs

# Stock price
curl "http://localhost:8000/api/v1/market/price/stock?symbol=RELIANCE.NS"

# Crypto price
curl "http://localhost:8000/crypto-price/BTCUSDT"
```

## 🌐 Production Deployment Options

### Option 1: Render.com (Current)

#### 1. Connect Repository

1. Go to [Render.com](https://render.com)
2. Connect your GitHub repository
3. Select "Web Service"

#### 2. Configure Service

```yaml
# render.yaml
services:
  - type: web
    name: fastapi-stock-data
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PROVIDER
        value: YFINANCE
      - key: DEBUG
        value: False
      - key: DATABASE_URL
        value: sqlite:///./app.db
```

#### 3. Environment Variables

Set these in Render dashboard:

- `PROVIDER=YFINANCE`
- `DEBUG=False`
- `DATABASE_URL=sqlite:///./app.db`
- `BINANCE_API_KEY` (optional)
- `BINANCE_API_SECRET` (optional)

#### 4. Deploy

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

Render will automatically deploy on push.

### Option 2: Heroku

#### 1. Create Heroku App

```bash
heroku create your-app-name
```

#### 2. Set Environment Variables

```bash
heroku config:set PROVIDER=YFINANCE
heroku config:set DEBUG=False
heroku config:set DATABASE_URL=sqlite:///./app.db
```

#### 3. Deploy

```bash
git push heroku main
```

### Option 3: AWS EC2

#### 1. Launch EC2 Instance

- **AMI**: Ubuntu 20.04 LTS
- **Instance Type**: t2.micro (free tier)
- **Security Group**: Allow SSH (22) and HTTP (80), HTTPS (443)

#### 2. Connect and Setup

```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3 python3-pip python3-venv -y

# Install Git
sudo apt install git -y
```

#### 3. Deploy Application

```bash
# Clone repository
git clone https://github.com/OMCHOKSI108/FastAPI-Stock-data-.git
cd FastAPI-Stock-data-

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export PROVIDER=YFINANCE
export DEBUG=False
export DATABASE_URL=sqlite:///./app.db
```

#### 4. Run with Gunicorn

```bash
# Install Gunicorn
pip install gunicorn

# Run application
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### 5. Setup Nginx (Optional)

```bash
# Install Nginx
sudo apt install nginx -y

# Create Nginx config
sudo nano /etc/nginx/sites-available/fastapi

# Add this content:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/fastapi /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Option 4: Docker Deployment

#### 1. Create Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Create docker-compose.yml

```yaml
version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - PROVIDER=YFINANCE
      - DEBUG=False
      - DATABASE_URL=sqlite:///./app.db
    volumes:
      - ./app.db:/app/app.db
```

#### 3. Deploy with Docker

```bash
# Build and run
docker-compose up -d

# Or with Docker directly
docker build -t fastapi-stock-data .
docker run -p 8000:8000 -e PROVIDER=YFINANCE fastapi-stock-data
```

## 🔧 Environment Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PROVIDER` | Data provider (YFINANCE, ALPHA_VANTAGE, etc.) | YFINANCE | No |
| `DEBUG` | Debug mode | False | No |
| `DATABASE_URL` | Database connection string | sqlite:///./app.db | No |
| `BINANCE_API_KEY` | Binance API key | - | No |
| `BINANCE_API_SECRET` | Binance API secret | - | No |

### Provider Configuration

```python
# app/main.py
PROVIDER = os.getenv("PROVIDER", "YFINANCE").upper()

PROVIDER_MAP = {
    "YFINANCE": yfinance_provider,
    "ALPHA_VANTAGE": alphavantage_provider,
    "BINANCE": binance_provider,
}
```

## 📊 Database Setup

### SQLite (Development)

```bash
# Default configuration
DATABASE_URL=sqlite:///./app.db
```

### PostgreSQL (Production)

```bash
# Install PostgreSQL
pip install psycopg2-binary

# Set environment variable
DATABASE_URL=postgresql://user:password@localhost/dbname
```

## 🔒 Security Considerations

### API Keys

- Store API keys in environment variables
- Never commit keys to version control
- Use different keys for development/production

### HTTPS

- Always use HTTPS in production
- Render.com provides automatic HTTPS
- For custom domains, configure SSL certificates

### Rate Limiting

```python
# Add rate limiting (optional)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(_rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
```

## 📈 Monitoring & Logging

### Application Logs

```python
# app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Health Checks

```python
# Health endpoint
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

### Performance Monitoring

```python
# Middleware for request timing
@app.middleware("http")
async def add_process_time_header(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🚀 CI/CD Pipeline

### GitHub Actions Example

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run tests
      run: |
        python -m pytest

    - name: Deploy to Render
      run: |
        curl -X POST https://api.render.com/deploy/srv-xxxxx
        -H "Authorization: Bearer ${{ secrets.RENDER_API_KEY }}"
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Binding

**Error**: `Port already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

#### 2. Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

#### 3. Database Connection

**Error**: `Database connection failed`

**Solution**:
```bash
# Check DATABASE_URL
echo $DATABASE_URL

# Test connection
python -c "from sqlalchemy import create_engine; engine = create_engine('$DATABASE_URL'); engine.connect()"
```

#### 4. Memory Issues

**Error**: `Memory limit exceeded`

**Solution**:
```bash
# Increase memory limit (Render)
# Go to Render dashboard > Service > Settings > Memory

# Or optimize code
# Use streaming responses for large data
# Implement pagination
```

### Debug Commands

```bash
# Check running processes
ps aux | grep uvicorn

# Check logs
tail -f /var/log/application.log

# Test API endpoints
curl -v http://localhost:8000/health

# Check Python version
python --version

# List installed packages
pip list
```

## 📞 Support

- **GitHub Issues**: [Report bugs](https://github.com/OMCHOKSI108/FastAPI-Stock-data-/issues)
- **Documentation**: [MkDocs site](https://your-docs-site.com)
- **API Status**: Check `/health` endpoint

## 🔄 Updates & Maintenance

### Regular Maintenance

1. **Update Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Database Backup**
   ```bash
   cp app.db app.db.backup
   ```

3. **Log Rotation**
   ```bash
   # Configure log rotation in production
   ```

4. **Security Updates**
   ```bash
   # Regularly update base images and dependencies
   pip install --upgrade pip
   pip install --upgrade -r requirements.txt
   ```

### Scaling Considerations

- **Horizontal Scaling**: Use load balancer with multiple instances
- **Database Scaling**: Migrate from SQLite to PostgreSQL
- **Caching**: Implement Redis for frequently accessed data
- **CDN**: Use CDN for static assets (if any)

This deployment guide covers all major deployment scenarios and best practices for production use.
