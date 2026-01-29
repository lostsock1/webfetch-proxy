# 🔥 VIBECODE WebFetch Proxy

Advanced webfetch proxy with intelligence gathering for OpenCode agents.

## Quick Start

```bash
cd /Users/djesys/#VIBECODE/webfetch-prxy

# Start proxy server
python3 webfetch_proxy.py

# Test plugin
python3 test_plugin.py
```

## Plugin Usage

```python
import sys
sys.path.insert(0, "/Users/djesys/#VIBECODE/webfetch-prxy")

from opencode_plugin import initialize_plugin, webfetch, bulk_webfetch, get_plugin_status

# Initialize
initialize_plugin()

# Single fetch
result = webfetch("https://example.com")

# Bulk fetch
results = bulk_webfetch(["https://a.com", "https://b.com"])

# Status
print(get_plugin_status())
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/fetch` | Single URL fetch |
| POST | `/fetch/bulk` | Bulk URL fetch |
| GET | `/blocked/requests` | Blocked requests log |
| POST | `/housekeeping/cleanup` | Clean obsolete files |

## Configuration

- **Proxy URL**: `http://localhost:8082`
- **API Key**: `Bearer test-key`
- **Cache**: Redis (`redis://localhost:6379/0`)
- **TTL**: 3600 seconds

## Files

```
webfetch-prxy/
├── webfetch_proxy.py           # Main proxy server
├── opencode_plugin.py          # OpenCode plugin
├── opencode_proxy_plugins.py   # Plugin architecture
├── config.yaml                 # Configuration
├── proxy_config.json           # Integration settings
├── test_plugin.py              # Test suite
├── test_proxy_integration.py   # Integration tests
├── webfetch_proxy_integration.py  # Legacy integration
├── proxy_wrapper.sh            # Shell wrapper
├── __init__.py                 # Package init
├── intelligence/               # Intelligence data
├── logs/                       # Proxy logs
└── archive/                    # Archived files
```
