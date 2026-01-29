#!/usr/bin/env python3
"""
🔥 VIBECODE WebFetch Proxy Plugin - Test Suite
Tests the OpenCode plugin functionality
"""

import sys
import os
import json
import time
import requests

# Add VIBECODE proxy to path
VIBECODE_PROXY_PATH = "/Users/djesys/#VIBECODE/webfetch-prxy"
if VIBECODE_PROXY_PATH not in sys.path:
    sys.path.insert(0, VIBECODE_PROXY_PATH)

print("🔥 VIBECODE WebFetch Proxy Plugin Test")
print("=" * 50)

# Test 1: Check if proxy is running
print("\n[1] Checking proxy health...")
try:
    response = requests.get("http://localhost:8082/health", timeout=5)
    if response.status_code == 200:
        health = response.json()
        print(f"   ✅ Proxy is healthy")
        print(f"   Status: {health.get('status')}")
        print(f"   Cache: {health.get('components', {}).get('cache')}")
    else:
        print(f"   ⚠️  Proxy returned status {response.status_code}")
except requests.exceptions.ConnectionError:
    print("   ❌ Proxy not running - starting it...")
    # Start the proxy
    proxy_script = f"{VIBECODE_PROXY_PATH}/webfetch_proxy.py"
    import subprocess

    subprocess.Popen(
        ["python3", proxy_script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    time.sleep(3)
    print("   🚀 Proxy starting...")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Test single fetch through proxy
print("\n[2] Testing single fetch through proxy...")
try:
    proxy_data = {
        "url": "https://httpbin.org/get",
        "method": "GET",
        "timeout": 30,
        "cache_enabled": True,
        "intelligence_tags": ["test", "plugin"],
    }

    headers = {"Content-Type": "application/json", "Authorization": "Bearer test-key"}

    response = requests.post(
        "http://localhost:8082/fetch", json=proxy_data, headers=headers, timeout=35
    )

    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Fetch successful")
        print(f"   Status: {result.get('status_code')}")
        print(f"   Cached: {result.get('cached', False)}")
        print(f"   Time: {result.get('execution_time', 0):.3f}s")
    else:
        print(f"   ❌ Fetch failed: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test bulk fetch
print("\n[3] Testing bulk fetch through proxy...")
try:
    bulk_data = {
        "urls": [
            "https://httpbin.org/get",
            "https://httpbin.org/json",
            "https://httpbin.org/html",
        ],
        "concurrent_limit": 3,
        "intelligence_tags": ["test", "bulk"],
    }

    headers = {"Content-Type": "application/json", "Authorization": "Bearer test-key"}

    response = requests.post(
        "http://localhost:8082/fetch/bulk", json=bulk_data, headers=headers, timeout=45
    )

    if response.status_code == 200:
        result = response.json()
        successful = result.get("successful", 0)
        total = result.get("total_urls", 0)
        print(f"   ✅ Bulk fetch complete")
        print(f"   Successful: {successful}/{total}")
    else:
        print(f"   ❌ Bulk fetch failed: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check blocked requests
print("\n[4] Checking blocked requests...")
try:
    response = requests.get("http://localhost:8082/blocked/requests", timeout=5)
    if response.status_code == 200:
        result = response.json()
        blocked = result.get("blocked_requests", [])
        print(f"   ✅ Blocked requests retrieved")
        print(f"   Total blocked: {result.get('total', 0)}")
    else:
        print(f"   ⚠️  Could not retrieve blocked requests")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Check intelligence records
print("\n[5] Checking intelligence records...")
try:
    response = requests.get(
        "http://localhost:8082/intelligence/list?limit=5", timeout=5
    )
    if response.status_code == 200:
        result = response.json()
        records = result.get("records", [])
        print(f"   ✅ Intelligence records retrieved")
        print(f"   Total records: {result.get('total_records', 0)}")
    else:
        print(f"   ⚠️  Could not retrieve intelligence records")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Plugin test completed")

# Summary
print("\n📊 Summary:")
print("   - Proxy server: http://localhost:8082")
print("   - Health check: http://localhost:8082/health")
print("   - Single fetch: POST /fetch")
print("   - Bulk fetch: POST /fetch/bulk")
print("   - Blocked: GET /blocked/requests")
print("   - Intelligence: GET /intelligence/list")
