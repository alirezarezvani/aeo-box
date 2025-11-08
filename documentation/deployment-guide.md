# Deployment Guide

This guide covers deploying AEO Box in various environments, from local development to production deployment.

---

## Table of Contents

- [Overview](#overview)
- [Deployment Options](#deployment-options)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
  - [CLI-Only Deployment](#cli-only-deployment)
  - [API Server Deployment](#api-server-deployment)
  - [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Dependencies Management](#dependencies-management)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Scaling and Performance](#scaling-and-performance)

---

## Overview

AEO Box can be deployed in multiple configurations:

| Deployment Type | Use Case | Complexity | Resources |
|----------------|----------|------------|-----------|
| **Local Development** | Testing, development | Low | Minimal |
| **CLI-Only** | Personal use, small teams | Low | 1 CPU, 512MB RAM |
| **API Server** | Teams, integration | Medium | 2 CPU, 2GB RAM |
| **Docker** | Consistent environments | Medium | 2 CPU, 2GB RAM |
| **Cloud Production** | Scale, high availability | High | Auto-scaling |

**Current Status** (v1.0):
- ✅ Local development fully supported
- ✅ CLI-only deployment ready
- 🚧 API server (planned for v1.5)
- 🚧 Docker support (planned for v1.5)

---

## Deployment Options

### Option 1: AEO Skill (Current - v1.0)

**Best for**: Individual users, Claude Code integration

```bash
# Install as Python package
cd answer-engine-optimization
pip install -r requirements.txt

# Use as library
python -c "from modules.content_analyzer import ContentAnalyzer; ..."

# Or install as Claude Code skill
cp -r answer-engine-optimization ~/.claude/skills/aeo
```

**Pros**:
- Simple installation
- No server required
- Works offline (graceful degradation)
- Perfect for local workflows

**Cons**:
- No REST API
- No multi-user support
- Manual execution

### Option 2: Multi-Agent System (Planned - v1.5)

**Best for**: Teams, automation, integration

```bash
# Install CLI + API
pip install aeo-box

# Run as CLI
aeo-box campaign --url https://example.com/article

# Or run as API server
aeo-box serve --host 0.0.0.0 --port 8000
```

**Pros**:
- Automated workflows
- REST API for integration
- Multi-user support
- Batch processing

**Cons**:
- Requires server
- More complex setup
- Higher resource requirements

---

## Local Development

### Prerequisites

```bash
# Check Python version (3.9+ required)
python --version

# Verify pip
pip --version

# Optional: Check git
git --version
```

### Installation Steps

#### 1. Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/alirezarezvani/aeo-box.git
cd aeo-suite
```

#### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
# Navigate to AEO Skill
cd answer-engine-optimization

# Install required packages
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest pytest-cov black flake8 mypy
```

#### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add API keys (optional)
nano .env
```

Example `.env`:

```bash
# Optional API Keys (for enhanced features)
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
GOOGLE_API_KEY=your_google_key_here

# Configuration
AEO_DATA_DIR=.aeo-data
LOG_LEVEL=INFO
CACHE_ENABLED=true
```

#### 5. Verify Installation

```bash
# Run tests
pytest tests/

# Test content analyzer
python -c "
from modules.content_analyzer import ContentAnalyzer
analyzer = ContentAnalyzer()
print('Installation successful!')
"
```

### Development Workflow

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit code ...

# 3. Run tests
pytest --cov=modules tests/

# 4. Check code style
black modules/ tests/
flake8 modules/
mypy modules/

# 5. Commit and push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-feature
```

---

## Production Deployment

### CLI-Only Deployment

**Best for**: Personal use, small teams, cron jobs

#### System Requirements

- **OS**: Linux, macOS, Windows
- **Python**: 3.9+
- **RAM**: 512MB minimum, 1GB recommended
- **Storage**: 500MB for data

#### Installation

```bash
# 1. Create production user
sudo useradd -m -s /bin/bash aeobox

# 2. Clone repository
sudo -u aeobox git clone https://github.com/alirezarezvani/aeo-box.git /opt/aeo-box
cd /opt/aeo-box/answer-engine-optimization

# 3. Create virtual environment
sudo -u aeobox python -m venv /opt/aeo-box/venv

# 4. Install dependencies
sudo -u aeobox /opt/aeo-box/venv/bin/pip install -r requirements.txt

# 5. Configure environment
sudo -u aeobox cp .env.example .env
sudo -u aeobox nano .env
```

#### Configuration

Create `/opt/aeo-box/.env`:

```bash
# Production Configuration
AEO_DATA_DIR=/var/lib/aeo-box/data
LOG_LEVEL=WARNING
LOG_FILE=/var/log/aeo-box/aeo.log
CACHE_ENABLED=true
CACHE_TTL=3600

# API Keys (from secrets management)
ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
```

#### Cron Job Setup

```bash
# Edit crontab
sudo -u aeobox crontab -e

# Add scheduled tasks
# Daily citation tracking at 2 AM
0 2 * * * /opt/aeo-box/venv/bin/python /opt/aeo-box/scripts/daily_citation_check.py

# Weekly report generation on Mondays at 9 AM
0 9 * * 1 /opt/aeo-box/venv/bin/python /opt/aeo-box/scripts/weekly_report.py
```

Example `daily_citation_check.py`:

```python
#!/usr/bin/env python
"""Daily citation tracking script."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "answer-engine-optimization"))

from modules.citation_tracker import CitationTracker

def main():
    # Load URLs from config
    with open("/etc/aeo-box/urls.json") as f:
        config = json.load(f)

    tracker = CitationTracker()

    for url in config["urls"]:
        results = tracker.track_citations(
            url=url,
            queries=config["queries"]
        )

        # Save results
        output_dir = Path("/var/lib/aeo-box/data/citations")
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / f"{url.replace('/', '_')}.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
```

---

### API Server Deployment

**Status**: Planned for v1.5

**Best for**: Teams, integrations, web applications

#### System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended)
- **Python**: 3.10+
- **RAM**: 2GB minimum, 4GB recommended
- **CPU**: 2 cores minimum
- **Storage**: 2GB for application + data

#### Installation (Future)

```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3.10 python3.10-venv nginx supervisor

# 2. Create application directory
sudo mkdir -p /opt/aeo-box
sudo chown aeobox:aeobox /opt/aeo-box

# 3. Clone and install
cd /opt/aeo-box
git clone https://github.com/alirezarezvani/aeo-box.git .
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Install AEO Box (when packaged)
pip install aeo-box[api]
```

#### Running the API Server

```bash
# Development mode
aeo-box serve --reload

# Production mode with Gunicorn
gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile /var/log/aeo-box/access.log \
  --error-logfile /var/log/aeo-box/error.log \
  aeo_box.api:app
```

#### Supervisor Configuration

Create `/etc/supervisor/conf.d/aeo-box.conf`:

```ini
[program:aeo-box]
command=/opt/aeo-box/venv/bin/gunicorn \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  aeo_box.api:app
directory=/opt/aeo-box
user=aeobox
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stdout_logfile=/var/log/aeo-box/supervisor.log
stderr_logfile=/var/log/aeo-box/supervisor_error.log
environment=PATH="/opt/aeo-box/venv/bin"
```

Start the service:

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start aeo-box
```

#### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/aeo-box`:

```nginx
upstream aeo_box {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name aeo.yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name aeo.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/aeo.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/aeo.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Logging
    access_log /var/log/nginx/aeo-box-access.log;
    error_log /var/log/nginx/aeo-box-error.log;

    # Timeouts for long-running requests
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;

    location / {
        proxy_pass http://aeo_box;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://aeo_box/health;
        access_log off;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/aeo-box /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Docker Deployment

**Status**: Planned for v1.5

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "aeo_box.api:app"]
```

#### Docker Compose

```yaml
version: '3.8'

services:
  aeo-box:
    build: .
    container_name: aeo-box
    ports:
      - "8000:8000"
    environment:
      - AEO_DATA_DIR=/app/data
      - LOG_LEVEL=INFO
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: aeo-box-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - aeo-box
    restart: unless-stopped
```

#### Running with Docker

```bash
# Build image
docker build -t aeo-box:latest .

# Run container
docker run -d \
  --name aeo-box \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -e ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY} \
  aeo-box:latest

# Or use Docker Compose
docker-compose up -d

# View logs
docker logs -f aeo-box

# Stop container
docker-compose down
```

---

## Environment Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AEO_DATA_DIR` | No | `.aeo-data` | Data storage directory |
| `LOG_LEVEL` | No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | No | `stdout` | Log file path |
| `CACHE_ENABLED` | No | `true` | Enable response caching |
| `CACHE_TTL` | No | `3600` | Cache TTL in seconds |
| `ANTHROPIC_API_KEY` | Optional | - | Claude API key |
| `OPENAI_API_KEY` | Optional | - | OpenAI API key |
| `PERPLEXITY_API_KEY` | Optional | - | Perplexity API key |
| `GOOGLE_API_KEY` | Optional | - | Google API key |
| `MAX_WORKERS` | No | `4` | API worker count |
| `REQUEST_TIMEOUT` | No | `120` | Request timeout (seconds) |

### Configuration File

Alternative to environment variables: `config.yml`

```yaml
# AEO Box Configuration
data:
  directory: /var/lib/aeo-box/data
  retention_days: 90

logging:
  level: INFO
  file: /var/log/aeo-box/aeo.log
  rotation:
    max_size: 100MB
    backup_count: 10

api:
  host: 0.0.0.0
  port: 8000
  workers: 4
  timeout: 120

cache:
  enabled: true
  ttl: 3600
  backend: memory  # memory, redis (future)

features:
  citation_tracking:
    enabled: true
    llms: [chatgpt, perplexity, claude, gemini, mistral]
  adaptive_learning:
    enabled: true
    sharing: false  # Privacy-first default

security:
  api_key_required: true
  rate_limiting:
    enabled: true
    requests_per_minute: 60
  cors:
    enabled: true
    origins: ["https://yourdomain.com"]
```

Load configuration:

```python
from pathlib import Path
import yaml

def load_config():
    config_path = Path("/etc/aeo-box/config.yml")
    if config_path.exists():
        with open(config_path) as f:
            return yaml.safe_load(f)
    return {}
```

---

## Dependencies Management

### Production Dependencies

```txt
# Core dependencies (answer-engine-optimization/requirements.txt)
anthropic>=0.18.0
openai>=1.10.0
requests>=2.31.0
pydantic>=2.5.0
python-dotenv>=1.0.0

# Optional: For enhanced features
beautifulsoup4>=4.12.0  # HTML parsing
markdown>=3.5.0         # Markdown processing
pyyaml>=6.0.1          # YAML configuration
```

### API Server Dependencies (v1.5+)

```txt
# API Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
gunicorn>=21.2.0

# Async support
aiohttp>=3.9.0
asyncio>=3.4.3

# Data validation
pydantic>=2.5.0
email-validator>=2.1.0

# Documentation
python-multipart>=0.0.6
```

### Development Dependencies

```txt
# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
pytest-mock>=3.12.0

# Code quality
black>=23.12.0
flake8>=7.0.0
mypy>=1.8.0
isort>=5.13.0

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.5.0
```

### Dependency Updates

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade anthropic

# Update all packages (use caution)
pip install --upgrade -r requirements.txt

# Freeze current versions
pip freeze > requirements-lock.txt
```

---

## Monitoring and Logging

### Logging Configuration

```python
# logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_level="INFO", log_file=None):
    """Configure application logging."""

    # Create logger
    logger = logging.getLogger("aeo_box")
    logger.setLevel(getattr(logging, log_level))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)

    # File handler (if log file specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=10
        )
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)

    return logger
```

Usage:

```python
from logging_config import setup_logging

logger = setup_logging(
    log_level="INFO",
    log_file="/var/log/aeo-box/aeo.log"
)

logger.info("Application started")
logger.error("Error occurred", exc_info=True)
```

### Application Monitoring

#### Health Check Endpoint (v1.5+)

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.5.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Application metrics."""
    return {
        "requests_total": metrics.requests_total,
        "requests_duration_seconds": metrics.avg_duration,
        "cache_hit_rate": metrics.cache_hit_rate,
        "active_workers": metrics.active_workers
    }
```

#### Monitoring with Prometheus (Future)

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'aeo-box'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

#### Log Aggregation

```bash
# Ship logs to centralized logging (ELK, Datadog, etc.)
tail -f /var/log/aeo-box/aeo.log | \
  filebeat -e -c /etc/filebeat/filebeat.yml
```

---

## Security Considerations

### API Key Management

**Never commit API keys to version control**

#### Using Environment Variables

```bash
# Set in environment
export ANTHROPIC_API_KEY="your-key-here"

# Or use secrets file
cat > /etc/aeo-box/secrets.env <<EOF
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
EOF

chmod 600 /etc/aeo-box/secrets.env
```

#### Using Secret Management Services

```python
# AWS Secrets Manager
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('aeo-box/production')
ANTHROPIC_API_KEY = secrets['ANTHROPIC_API_KEY']
```

### HTTPS Configuration

```bash
# Install Certbot for Let's Encrypt
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d aeo.yourdomain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Rate Limiting

```python
# Using slowapi for FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/analyze")
@limiter.limit("10/minute")
async def analyze_content(request: Request):
    # ... implementation
    pass
```

### Input Validation

```python
from pydantic import BaseModel, HttpUrl, validator

class AnalyzeRequest(BaseModel):
    content: str
    url: Optional[HttpUrl] = None

    @validator('content')
    def content_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Content cannot be empty')
        if len(v) > 1_000_000:  # 1MB limit
            raise ValueError('Content too large')
        return v
```

### Data Privacy

```python
# Anonymize sensitive data before logging
import hashlib

def anonymize_url(url: str) -> str:
    """Anonymize URL for logging."""
    return hashlib.sha256(url.encode()).hexdigest()[:16]

logger.info(f"Processing URL: {anonymize_url(url)}")
```

---

## Troubleshooting

### Common Issues

#### Issue: Import Error

```
ImportError: No module named 'modules'
```

**Solution**:
```bash
# Ensure you're in the correct directory
cd answer-engine-optimization

# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Or install in development mode
pip install -e .
```

#### Issue: Permission Denied

```
PermissionError: [Errno 13] Permission denied: '.aeo-data'
```

**Solution**:
```bash
# Fix directory permissions
sudo chown -R aeobox:aeobox /var/lib/aeo-box
sudo chmod -R 755 /var/lib/aeo-box
```

#### Issue: API Key Not Found

```
ValueError: ANTHROPIC_API_KEY not found in environment
```

**Solution**:
```bash
# Set environment variable
export ANTHROPIC_API_KEY="your-key-here"

# Or create .env file
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

#### Issue: Out of Memory

```
MemoryError: Cannot allocate memory
```

**Solution**:
```bash
# Increase worker memory limit
# For Gunicorn
gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 --max-requests-jitter 100 \
  aeo_box.api:app

# Or reduce batch size in code
analyzer.analyze(content, batch_size=10)  # Instead of 100
```

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or via environment
export LOG_LEVEL=DEBUG
```

### Performance Profiling

```python
# Profile function execution
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# ... run code ...

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
```

---

## Scaling and Performance

### Horizontal Scaling

#### Load Balancer Configuration

```nginx
# Nginx load balancer
upstream aeo_cluster {
    least_conn;
    server aeo-box-1:8000 weight=1;
    server aeo-box-2:8000 weight=1;
    server aeo-box-3:8000 weight=1;
}

server {
    listen 80;
    location / {
        proxy_pass http://aeo_cluster;
    }
}
```

#### Auto-Scaling (AWS Example)

```yaml
# AWS ECS Task Definition
{
  "family": "aeo-box",
  "containerDefinitions": [{
    "name": "aeo-box",
    "image": "your-registry/aeo-box:latest",
    "memory": 2048,
    "cpu": 1024,
    "essential": true,
    "environment": [
      {"name": "LOG_LEVEL", "value": "INFO"}
    ],
    "secrets": [
      {"name": "ANTHROPIC_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
    ]
  }]
}
```

### Caching Strategies

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def analyze_cached(content_hash: str):
    """Cache analysis results."""
    # Load from disk cache if available
    cache_file = Path(f".aeo-cache/{content_hash}.json")
    if cache_file.exists():
        return json.loads(cache_file.read_text())

    # Analyze and cache
    result = analyzer.analyze(content)
    cache_file.parent.mkdir(exist_ok=True)
    cache_file.write_text(json.dumps(result))
    return result

# Usage
content_hash = hashlib.sha256(content.encode()).hexdigest()
result = analyze_cached(content_hash)
```

### Database Optimization (Future)

When transitioning to database storage:

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "postgresql://user:password@localhost/aeo_box",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)

# Indexing
CREATE INDEX idx_citations_url ON citations(url);
CREATE INDEX idx_citations_timestamp ON citations(timestamp);
```

---

## Best Practices

### 1. Resource Management

```python
# Use context managers
with ContentAnalyzer() as analyzer:
    result = analyzer.analyze(content)

# Cleanup resources
def cleanup():
    cache.clear()
    temp_files.remove()
    logger.info("Cleanup completed")

atexit.register(cleanup)
```

### 2. Error Handling

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def api_call_with_retry():
    """API call with automatic retries."""
    return client.analyze(content)
```

### 3. Monitoring

```python
# Track metrics
from prometheus_client import Counter, Histogram

requests_total = Counter('requests_total', 'Total requests')
request_duration = Histogram('request_duration_seconds', 'Request duration')

@request_duration.time()
def analyze(content):
    requests_total.inc()
    return analyzer.analyze(content)
```

### 4. Graceful Shutdown

```python
import signal

def graceful_shutdown(signum, frame):
    logger.info("Shutting down gracefully...")
    # Finish current requests
    # Save state
    # Close connections
    sys.exit(0)

signal.signal(signal.SIGTERM, graceful_shutdown)
signal.signal(signal.SIGINT, graceful_shutdown)
```

---

## Checklist

### Pre-Deployment

- [ ] Environment variables configured
- [ ] API keys secured (not in code)
- [ ] Dependencies installed and locked
- [ ] Tests passing (pytest)
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Resource limits set

### Production Deployment

- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Graceful shutdown implemented
- [ ] Health checks configured
- [ ] Documentation updated

### Post-Deployment

- [ ] Health check passing
- [ ] Logs reviewed
- [ ] Performance metrics collected
- [ ] Error rates monitored
- [ ] Backup tested
- [ ] Rollback plan ready

---

## Additional Resources

- **Installation Guide**: [QUICKSTART.md](../answer-engine-optimization/QUICKSTART.md)
- **Configuration**: [SKILL.md](../answer-engine-optimization/SKILL.md)
- **API Documentation**: [API Reference](api-reference.md)
- **Architecture**: [Architecture Guide](foundation/architecture.md)
- **Cost Optimization**: [Cost Optimization Guide](cost-optimization.md)

---

**Last Updated**: 2025-01-08

For deployment support, create an issue: [GitHub Issues](https://github.com/alirezarezvani/aeo-box/issues)
