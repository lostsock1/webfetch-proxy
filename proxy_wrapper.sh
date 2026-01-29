#!/bin/bash
# 🔥 VIBECOE Proxy Wrapper for Shell Scripts
# Provides proxy-enabled versions of common web tools

# Add VIBECOE proxy to Python path
export PYTHONPATH="/Users/djesys/#VIBECOE/webfetch-prxy:$PYTHONPATH"

# Proxy-enabled curl wrapper
proxy_curl() {
    local url="$1"
    shift
    local args=("$@")
    
    # Try using Python proxy wrapper first
    if python3 -c "
import sys
sys.path.insert(0, '/Users/djesys/opencode')
try:
    from webfetch_proxy_integration import fetch_through_proxy
    import requests
    import json
    
    url = '$url'
    args = '${args[@]}'
    
    # Simple argument parsing for common curl options
    timeout = 10
    method = 'GET'
    data = None
    headers = {}
    
    # Parse arguments
    i=0
    while [ $i -lt ${#args[@]} ]; do
        case '${args[i]}' in
            -X) method='${args[i+1]}'; ((i+=2)); continue ;;
            -H) IFS=':' read -r key value <<< '${args[i+1]}'; headers[key.strip()]="${value# }"; ((i+=2)); continue ;;
            -d) data='${args[i+1]}'; ((i+=2)); continue ;;
            --max-time) timeout='${args[i+1]}'; ((i+=2)); continue ;;
            -s) ((i+=1)); continue ;;  # Silent mode, ignore
            *) ((i+=1)); continue ;;
        esac
    done
    
    # Make request through proxy
    kwargs = {'timeout': timeout}
    if headers:
        kwargs['headers'] = headers
    if data:
        kwargs['data'] = data
        
    response = fetch_through_proxy(url, method=method, **kwargs)
    print(response.text if hasattr(response, 'text') else response.content.decode())
    exit(0)
except Exception as e:
    print(f'# PYTHON_PROXY_ERROR: {e}', file=sys.stderr)
    exit(1)
" 2>/dev/null; then
        return $?
    else
        # Fallback to regular curl
        echo "# FALLING_BACK_TO_DIRECT_CURL" >&2
        curl "$url" "$@"
    fi
}

# Proxy-enabled wget wrapper
proxy_wget() {
    local url="$1"
    shift
    local args=("$@")
    
    # Simple wget simulation using curl
    proxy_curl "$url" "${args[@]}"
}

# Check proxy health
proxy_health() {
    python3 -c "
import sys
sys.path.insert(0, '/Users/djesys/opencode')
try:
    from webfetch_proxy_integration import get_proxy_status
    status = get_proxy_status()
    print('PROXY_ENABLED' if status['enabled'] else 'PROXY_DISABLED')
except:
    print('PROXY_ERROR')
" 2>/dev/null
}

# Bulk fetch URLs
proxy_bulk_fetch() {
    local urls_file="$1"
    if [ ! -f "$urls_file" ]; then
        echo "Error: URLs file not found: $urls_file"
        return 1
    fi
    
    python3 -c "
import sys
sys.path.insert(0, '/Users/djesys/opencode')
try:
    from webfetch_proxy_integration import bulk_fetch_proxy
    
    with open('$urls_file', 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    results = bulk_fetch_proxy(urls)
    for i, result in enumerate(results):
        if result.get('success'):
            print(f'✅ URL {i+1}: SUCCESS ({result.get(\"status_code\", \"?\")})')
        else:
            print(f'❌ URL {i+1}: FAILED ({result.get(\"error\", \"Unknown\")})')
except Exception as e:
    print(f'# BULK_FETCH_ERROR: {e}')
" 2>/dev/null
}

# Export functions for use in other scripts
export -f proxy_curl
export -f proxy_wget  
export -f proxy_health
export -f proxy_bulk_fetch

# Auto-load in current shell if sourced
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    echo "🔥 VIBECOE Proxy wrapper loaded"
    if [ "$1" = "--check" ]; then
        proxy_health
    fi
fi