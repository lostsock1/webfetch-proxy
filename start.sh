#!/bin/bash
# Start WebFetch Proxy Server

echo "🚀 Starting WebFetch Proxy Server..."

# Check if Redis is running
if ! command -v redis-cli &> /dev/null; then
    echo "⚠️  Redis is not installed. Installing via pip..."
    pip install redis
fi

# Try to connect to Redis
if redis-cli ping &> /dev/null; then
    echo "✅ Redis is running"
else
    echo "⚠️  Redis is not running. Starting Redis server..."
    # Try to start Redis (platform dependent)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start redis 2>/dev/null || redis-server --daemonize yes
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start redis 2>/dev/null || redis-server --daemonize yes
    else
        echo "❓ Cannot start Redis automatically on this platform"
        echo "   Please start Redis manually: redis-server --daemonize yes"
    fi
    sleep 2
fi

# Check Python dependencies
echo "📦 Checking Python dependencies..."
python3 -c "import fastapi, uvicorn, aiohttp, redis, yaml, pydantic" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Missing dependencies. Installing..."
    pip install -r requirements.txt
fi

# Start the proxy server
echo "🌐 Starting WebFetch Proxy on http://localhost:8082"
echo "📊 Health check: http://localhost:8082/health"
echo "📝 Logs: ./logs/proxy.log"
echo ""

python3 webfetch_proxy.py