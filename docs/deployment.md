# FastStockAPI Deployment Guide

This comprehensive guide covers multiple deployment options for FastStockAPI, from local development to production environments.

##  Quick Deployment Options

### Option 1: Railway (Recommended for Beginners)
```bash
# 1. Connect your GitHub repository to Railway
# 2. Railway auto-detects FastAPI and deploys automatically
# 3. Your API will be live at: https://your-project.railway.app
```

### Option 2: Render
```bash
# 1. Connect GitHub repo to Render
# 2. Set build command: `pip install -r requirements.txt`
# 3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
```

### Option 3: Heroku
```bash
# 1. Create Heroku app
# 2. Set buildpack to Python
# 3. Deploy via Git or GitHub integration
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Docker Compose (Full Stack)
```yaml
version: '3.8'

services:
  fastapi:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:password@postgres:5432/fastapi
    depends_on:
      - redis
      - postgres
    volumes:
      - ./data:/app/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=fastapi
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - fastapi
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
```

### Build and Run
```bash
# Build the image
docker build -t faststockapi .

# Run locally
docker run -p 8000:8000 faststockapi

# Or use docker-compose
docker-compose up -d
```

## ☁️ Cloud Platform Deployments

### Railway Deployment
1. **Connect Repository**
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub repository
   - Railway auto-detects FastAPI

2. **Environment Variables**
   ```
   ENVIRONMENT=production
   REDIS_URL=${{ REDIS_URL }}
   DATABASE_URL=${{ DATABASE_URL }}
   ```

3. **Domain Setup**
   - Railway provides a `.railway.app` domain
   - Add custom domain in settings

### Render Deployment
1. **Create Web Service**
   - Connect GitHub repository
   - Set runtime to Python 3

2. **Build Settings**
   ```bash
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 2
   ```

3. **Environment**
   ```
   PYTHON_VERSION=3.11.0
   ENVIRONMENT=production
   ```

### Heroku Deployment
1. **Create App**
   ```bash
   heroku create your-fastapi-app
   ```

2. **Set Buildpack**
   ```bash
   heroku buildpacks:set heroku/python
   ```

3. **Environment Variables**
   ```bash
   heroku config:set ENVIRONMENT=production
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

### AWS EC2 Deployment
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Clone repository
git clone https://github.com/your-username/fastapi-project.git
cd fastapi-project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Gunicorn
pip install gunicorn

# Create systemd service
sudo nano /etc/systemd/system/fastapi.service
```

**Service File:**
```ini
[Unit]
Description=FastAPI Application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/fastapi-project
Environment="PATH=/home/ubuntu/fastapi-project/venv/bin"
ExecStart=/home/ubuntu/fastapi-project/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable fastapi
sudo systemctl start fastapi

# Check status
sudo systemctl status fastapi
```

### Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/fastapi', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/fastapi']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - run
      - deploy
      - fastapi-service
      - --image=gcr.io/$PROJECT_ID/fastapi
      - --platform=managed
      - --port=8000
      - --memory=1Gi
      - --cpu=1
      - --max-instances=10
      - --concurrency=80
```

### Azure Container Instances
```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image fastapi:v1 .

# Deploy to ACI
az container create \
  --resource-group myResourceGroup \
  --name fastapi-container \
  --image myregistry.azurecr.io/fastapi:v1 \
  --cpu 1 \
  --memory 1 \
  --registry-login-server myregistry.azurecr.io \
  --registry-username myregistry \
  --registry-password $REGISTRY_PASSWORD \
  --ip-address public \
  --ports 8000 \
  --environment-variables ENVIRONMENT=production
```

## Environment Configuration

### Environment Variables
```bash
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/fastapi

# Redis (Caching)
REDIS_URL=redis://localhost:6379

# External APIs
ALPHA_VANTAGE_API_KEY=your-key
FINNHUB_API_KEY=your-key
BINANCE_API_KEY=your-key

# Email (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuration Management
```python
# config.py
import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key")

    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./fastapi.db")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # API Keys
    alpha_vantage_key: Optional[str] = os.getenv("ALPHA_VANTAGE_API_KEY")
    finnhub_key: Optional[str] = os.getenv("FINNHUB_API_KEY")
    binance_key: Optional[str] = os.getenv("BINANCE_API_KEY")

    # Rate Limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

    class Config:
        env_file = ".env"

settings = Settings()
```

## Monitoring and Logging

### Application Monitoring
```python
# monitoring.py
import time
import psutil
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time

        # Log request details
        print(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.3f}s")

        # Add custom headers
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Server-Memory"] = str(psutil.virtual_memory().percent)

        return response
```

### Health Checks
```python
# health.py
from fastapi import APIRouter
import psutil
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "memory_usage": psutil.virtual_memory().percent,
        "cpu_usage": psutil.cpu_percent(),
        "disk_usage": psutil.disk_usage('/').percent
    }

@router.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": time.time() - psutil.boot_time(),
        "memory": {
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available,
            "percent": psutil.virtual_memory().percent
        },
        "cpu": {
            "cores": psutil.cpu_count(),
            "usage_percent": psutil.cpu_percent(percpu=True)
        },
        "disk": {
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free,
            "percent": psutil.disk_usage('/').percent
        }
    }
```

### Logging Configuration
```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # JSON formatter for production
    json_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler("app.log")
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)

    return logger
```

## 🔒 Security Best Practices

### HTTPS Configuration
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-domain.crt;
    ssl_certificate_key /etc/ssl/private/your-domain.key;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### CORS Configuration
```python
# cors.py
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app):
    origins = [
        "http://localhost:3000",    # React dev
        "http://localhost:5173",    # Vite dev
        "https://your-frontend.com", # Production frontend
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )
```

### Rate Limiting
```python
# rate_limiting.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

def setup_rate_limiting(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
```

## Performance Optimization

### Gunicorn Configuration
```python
# gunicorn.conf.py
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "fastapi"

# Server mechanics
daemon = False
pidfile = "/var/run/gunicorn.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None
```

### Database Optimization
```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fastapi.db")

# Production database configuration
if DATABASE_URL.startswith("postgresql"):
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        echo=False
    )
else:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Caching Strategy
```python
# caching.py
from redis import Redis
import json
import os
from typing import Optional, Any

class Cache:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis = Redis.from_url(self.redis_url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except:
            return None

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        try:
            return self.redis.setex(key, ttl, json.dumps(value))
        except:
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.redis.delete(key))
        except:
            return False

cache = Cache()
```

## 🔄 CI/CD Pipeline

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          python -m pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Railway
        run: |
          # Railway deployment commands
          curl -fsSL https://railway.app/install.sh | sh
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          railway deploy
```

## Monitoring and Alerting

### Prometheus Metrics
```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()

    response = await call_next(request)

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()

    REQUEST_LATENCY.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(time.time() - start_time)

    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

### Error Tracking
```python
# error_tracking.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastAPIIntegration
from sentry_sdk.integrations.redis import RedisIntegration

def setup_error_tracking():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[
            FastAPIIntegration(),
            RedisIntegration(),
        ],
        environment=os.getenv("ENVIRONMENT", "development"),
        traces_sample_rate=1.0,
    )
```

## Troubleshooting

### Common Deployment Issues

1. **Port Binding**
   ```bash
   # Ensure your app binds to 0.0.0.0, not 127.0.0.1
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

2. **Static Files**
   ```python
   # For serving static files in production
   from fastapi.staticfiles import StaticFiles
   app.mount("/static", StaticFiles(directory="static"), name="static")
   ```

3. **Database Connection**
   ```bash
   # Test database connection
   python -c "from app.database import engine; print('DB connected' if engine else 'DB failed')"
   ```

4. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   # or
   htop
   ```

### Performance Tuning

1. **Worker Processes**
   ```bash
   # Use multiple workers for better performance
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

2. **Connection Pooling**
   ```python
   # Configure database connection pooling
   engine = create_engine(
       DATABASE_URL,
       pool_size=10,
       max_overflow=20,
       pool_timeout=30,
   )
   ```

3. **Caching**
   ```python
   # Implement Redis caching for frequently accessed data
   @app.get("/api/data")
   @cache(expire=300)
   async def get_data():
       return expensive_operation()
   ```

This deployment guide covers everything from simple deployments to enterprise-grade production setups. Choose the deployment method that best fits your needs and scale as your application grows.

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

## Production Deployment Options

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

## Environment Configuration

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

## Database Setup

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

## Monitoring & Logging

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

##  CI/CD Pipeline

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

##  Support

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
