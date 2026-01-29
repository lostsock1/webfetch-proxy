# 🔥 WebFetch Proxy - Advanced Web Content Fetching Service

![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Redis](https://img.shields.io/badge/Redis-7.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

A sophisticated web content fetching proxy service with intelligence gathering, caching, and seamless integration for AI/LLM systems. Built for OpenCode agents and other AI platforms requiring reliable web content access.

## ✨ Features

### 🎯 Core Capabilities
- **High-Performance Proxy**: Async HTTP/HTTPS proxy with configurable concurrency
- **Intelligent Caching**: Redis-backed caching with TTL and size limits
- **OSINT Integration**: Built-in intelligence gathering and tagging
- **Security Controls**: Rate limiting, domain filtering, API key authentication
- **Visual Monitoring**: Real-time request visualization and logging

### 🔧 Technical Features
- **Async Architecture**: Built on FastAPI with aiohttp for maximum performance
- **Plugin System**: Extensible plugin architecture for different AI platforms
- **Content Analysis**: Automatic content type detection and formatting
- **Fallback System**: Graceful degradation when proxy is unavailable
- **Comprehensive Logging**: Structured logs with intelligence data storage

### 🛡️ Security & Compliance
- **SSL Verification**: Configurable SSL certificate verification
- **Rate Limiting**: Per-minute and per-hour request limits
- **Domain Controls**: Whitelist/blacklist domain filtering
- **API Authentication**: Bearer token authentication support
- **Privacy Protection**: Request anonymization and data minimization

## 🚀 Quick Start

### Prerequisites
```bash
# Install system dependencies
brew install redis  # macOS
# or
sudo apt install redis-server  # Ubuntu

# Install Python dependencies
pip install fastapi uvicorn aiohttp redis asyncio pyyaml pydantic
```

### Running the Proxy
```bash
# Clone repository
git clone https://github.com/lostsock1/webfetch-proxy.git
cd webfetch-proxy

# Start Redis
redis-server --daemonize yes

# Start proxy server
python3 webfetch_proxy.py

# Alternative: Use startup script
./start.sh
```

### Testing the Proxy
```bash
# Test basic functionality
python3 test_plugin.py

# Test integration
python3 test_proxy_integration.py

# Run comprehensive tests
python3 agent_test.py
```

## 📖 Usage

### Basic API Usage
```python
import requests

# Single fetch request
response = requests.post(
    "http://localhost:8082/fetch",
    json={
        "url": "https://example.com",
        "method": "GET",
        "headers": {"User-Agent": "Custom-Agent/1.0"},
        "timeout": 30
    },
    headers={"Authorization": "Bearer test-key"}
)

# Bulk fetch
response = requests.post(
    "http://localhost:8082/fetch/bulk",
    json={
        "urls": ["https://example1.com", "https://example2.com"],
        "concurrent_limit": 5
    }
)
```

### OpenCode Integration
```python
import sys
sys.path.insert(0, "/path/to/webfetch-proxy")

from opencode_plugin import initialize_plugin, webfetch, bulk_webfetch

# Initialize plugin
initialize_plugin()

# Single fetch
result = webfetch("https://example.com", format="markdown")

# Bulk fetch
results = bulk_webfetch([
    "https://news.ycombinator.com",
    "https://github.com/trending"
], concurrent_limit=3)

# Check status
from opencode_plugin import get_plugin_status
print(get_plugin_status())
```

### Command Line Usage
```bash
# Start proxy server
python3 webfetch_proxy.py --host 0.0.0.0 --port 8082

# Check proxy status
./status.sh

# Run maintenance
python3 maintenance.py --cleanup

# View logs
tail -f logs/proxy.log
```

## 🔌 API Reference

### Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `GET` | `/health` | Health check | Optional |
| `POST` | `/fetch` | Single URL fetch | Required |
| `POST` | `/fetch/bulk` | Bulk URL fetch | Required |
| `GET` | `/stats` | Proxy statistics | Optional |
| `GET` | `/blocked/requests` | Blocked requests log | Required |
| `POST` | `/housekeeping/cleanup` | Clean obsolete files | Required |
| `GET` | `/intelligence/tags` | List intelligence tags | Required |

### Request Models

**Single Fetch:**
```json
{
  "url": "https://example.com",
  "method": "GET",
  "headers": {"User-Agent": "Custom/1.0"},
  "timeout": 30,
  "follow_redirects": true,
  "verify_ssl": true,
  "cache_enabled": true,
  "intelligence_tags": ["osint", "reconnaissance"]
}
```

**Bulk Fetch:**
```json
{
  "urls": ["https://site1.com", "https://site2.com"],
  "concurrent_limit": 5,
  "common_headers": {"Accept": "text/html"},
  "intelligence_tags": ["bulk", "analysis"]
}
```

## ⚙️ Configuration

### `config.yaml`
```yaml
proxy:
  host: "0.0.0.0"
  port: 8082
  workers: 1
  timeout: 30
  max_concurrent: 100
  show_requests: true

caching:
  enabled: true
  ttl: 3600
  redis_url: "redis://localhost:6379/0"
  max_size_mb: 100

security:
  api_key: "your-secret-key"
  allowed_domains: []
  blocked_domains: ["localhost", "127.0.0.1"]
  rate_limiting:
    enabled: true
    requests_per_minute: 60
    requests_per_hour: 1000

intelligence:
  enabled: true
  storage_path: "./intelligence"
  auto_tagging: true
  content_analysis: true
```

### Environment Variables
```bash
export WEBFETCH_PROXY_HOST="0.0.0.0"
export WEBFETCH_PROXY_PORT="8082"
export WEBFETCH_REDIS_URL="redis://localhost:6379/0"
export WEBFETCH_API_KEY="your-secret-key"
export WEBFETCH_CACHE_TTL="3600"
```

## 🏗️ Architecture

### Project Structure
```
webfetch-proxy/
├── webfetch_proxy.py           # Main proxy server (35K+ lines)
├── opencode_plugin.py          # OpenCode integration plugin
├── opencode_proxy_plugins.py   # Plugin architecture
├── webfetch_proxy_integration.py # Integration utilities
├── test_proxy_integration.py   # Integration tests
├── test_plugin.py              # Plugin testing
├── agent_test.py               # Agent testing
├── config.yaml                 # Configuration file
├── proxy_config.json           # Proxy configuration
├── proxy_wrapper.sh            # Shell wrapper script
├── start.sh                    # Startup script
├── status.sh                   # Status monitoring script
├── maintenance.py              # Maintenance utilities
├── README.md                   # Documentation
├── __init__.py                 # Python package init
├── logs/                       # Log directory
├── intelligence/               # Intelligence data (JSON)
├── archive/                    # Archived files and docs
└── images/                     # Image assets
```

### Core Components
1. **Proxy Server** (`webfetch_proxy.py`): FastAPI-based async HTTP proxy
2. **Plugin System**: Platform-specific integration plugins
3. **Cache Layer**: Redis-backed response caching
4. **Intelligence Engine**: Content analysis and tagging
5. **Security Module**: Authentication and rate limiting
6. **Monitoring System**: Real-time request visualization

### Data Flow
```
Client Request → Authentication → Rate Limiting → Cache Check → 
→ Domain Filtering → HTTP Fetch → Content Analysis → 
→ Intelligence Tagging → Cache Storage → Response
```

## 🔍 Intelligence Features

### Automatic Tagging
- **Content Analysis**: Detects content type (HTML, JSON, XML, etc.)
- **Domain Classification**: Categorizes by domain type (news, social, etc.)
- **OSINT Patterns**: Identifies reconnaissance and scanning patterns
- **Metadata Extraction**: Extracts titles, descriptions, keywords

### Storage Format
```json
{
  "request_id": "8cb584ff",
  "timestamp": "2026-01-26T02:33:01",
  "url": "https://example.com",
  "method": "GET",
  "status_code": 200,
  "content_type": "text/html",
  "size_bytes": 15432,
  "execution_time_ms": 245,
  "tags": ["web", "osint", "reconnaissance"],
  "metadata": {
    "title": "Example Domain",
    "description": "Example description",
    "keywords": ["example", "domain"]
  },
  "headers": {...},
  "cache_hit": false
}
```

## 🚢 Deployment

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8082

CMD ["python", "webfetch_proxy.py"]
```

### Systemd Service (Linux)
```ini
[Unit]
Description=WebFetch Proxy Service
After=network.target redis.service

[Service]
Type=simple
User=webfetch
WorkingDirectory=/opt/webfetch-proxy
ExecStart=/usr/bin/python3 webfetch_proxy.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: webfetch-proxy
spec:
  replicas: 2
  selector:
    matchLabels:
      app: webfetch-proxy
  template:
    metadata:
      labels:
        app: webfetch-proxy
    spec:
      containers:
      - name: proxy
        image: webfetch-proxy:latest
        ports:
        - containerPort: 8082
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
```

## 📊 Monitoring & Metrics

### Health Checks
```bash
# Check proxy health
curl http://localhost:8082/health

# Get statistics
curl http://localhost:8082/stats

# View logs
tail -f logs/proxy.log
```

### Performance Metrics
- **Request Latency**: Average/95th percentile response times
- **Cache Hit Rate**: Percentage of requests served from cache
- **Error Rate**: HTTP error rate by status code
- **Concurrency**: Active concurrent requests
- **Throughput**: Requests per second/minute

## 🔧 Development

### Setting Up Development Environment
```bash
# Clone repository
git clone https://github.com/lostsock1/webfetch-proxy.git
cd webfetch-proxy

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

### Adding New Features
1. **New Plugin**: Extend `opencode_plugin.py` base class
2. **New Endpoint**: Add route in `webfetch_proxy.py`
3. **New Intelligence Tag**: Update `config.yaml` patterns
4. **New Cache Strategy**: Implement in caching module

### Testing
```bash
# Run unit tests
python -m pytest tests/unit

# Run integration tests
python -m pytest tests/integration

# Run all tests with coverage
coverage run -m pytest
coverage report
```

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- Follow PEP 8 style guide
- Add type hints for all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **FastAPI Team**: For the excellent async web framework
- **Redis Community**: For the robust caching solution
- **aiohttp Maintainers**: For the async HTTP client library
- **OpenCode Community**: For inspiration and testing

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/lostsock1/webfetch-proxy/issues)
- **Documentation**: [Project Wiki](https://github.com/lostsock1/webfetch-proxy/wiki)
- **Email**: Open an issue for support requests

---

**Built with ❤️ for the AI/LLM community.** Keep fetching! 🔥