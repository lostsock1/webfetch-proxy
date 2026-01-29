#!/bin/bash
# 🔥 SHADOW Webfetch Proxy - Easy Start Script

echo "🔥 SHADOW Webfetch Proxy - STARTING..."
echo "=================================="

# Kill any existing proxy processes
echo "🗑️ Stopping existing processes..."
pkill -f "shadow_proxy_simple.py" 2>/dev/null || true
pkill -f "webfetch_proxy" 2>/dev/null || true
pkill -f "sunproxyadmin" 2>/dev/null || true
sleep 2

# Start the simple proxy
echo "🚀 Starting simple proxy on port 8082..."
echo "📺 Proxy will show requests on screen"
echo "⏹️ Press Ctrl+C to stop"
echo ""
echo "=================================="

cd "$(dirname "$0")"
python3 shadow_proxy_simple.py