#!/bin/bash
# 🔥 SHADOW Webfetch Proxy Status Check

echo "🔥 SHADOW Webfetch Proxy Status"
echo "============================"

# Check Redis (optional)
echo -n "Redis: "
if pgrep -f "redis-server" > /dev/null 2>&1; then
    echo -e "\033[0;32m[✓] Running\033[0m"
else
    echo -e "\033[0;31m[✗] Not running\033[0m"
fi

# Check Simple Proxy
echo -n "Proxy: "
if curl -s --connect-timeout 2 http://localhost:8082/health > /dev/null 2>&1; then
    echo -e "\033[0;32m[✓] Running (port 8082)\033[0m"
else
    echo -e "\033[0;31m[✗] Not running\033[0m"
fi

# Check Intelligence
echo -n "Intelligence: "
if [[ -d "/Users/djesys/#VIBECODE/intelligence" ]]; then
    intel_count=$(ls /Users/djesys/#VIBECODE/intelligence/intel_*.json 2>/dev/null | wc -l)
    echo -e "\033[0;32m[✓] Available ($intel_count records)\033[0m"
else
    echo -e "\033[0;33m[!] Directory not found\033[0m"
fi

# Show endpoints
echo ""
echo "🌐 Endpoints:"
echo "   Health:    http://localhost:8082/health"
echo "   Intelligence: http://localhost:8082/intelligence"
echo "   Status:    http://localhost:8082/status"
echo "   Cache:     http://localhost:8082/clear-cache"
echo ""
echo "🚀 Quick Commands:"
echo "   Start:     ./start.sh"
echo "   Stop:      pkill -f shadow_proxy_simple"
echo "   Test:      curl http://localhost:8082/health"