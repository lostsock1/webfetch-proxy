#!/usr/bin/env python3
"""
Test script to validate the web2 agent's proxy usage.
"""

import sys

sys.path.insert(0, "/Users/djesys/#VIBECODE/webfetch-prxy")

from opencode_plugin import (
    initialize_plugin,
    webfetch,
    bulk_webfetch,
    get_plugin_status,
)

print("🚀 VIBECODE Proxy - Web2 Agent Validation")
print("=" * 50)

# 1. Initialize Plugin (simulate agent startup)
print("\n[1] Initializing Plugin...")
init_result = initialize_plugin()
print(f"   Plugin Status: {'✅ Enabled' if init_result else '❌ Failed'}")

# 2. Get Plugin Status
status = get_plugin_status()
print(f"\n[2] Plugin Status:")
print(f"   Proxy URL: {status.get('proxy_url')}")
print(f"   Fallback: {'Enabled' if status.get('fallback_enabled') else 'Disabled'}")

# 3. Test Single Fetch (simulate agent web search)
print("\n[3] Testing webfetch (via proxy)...")
result = webfetch("https://api.github.com/repos/python/cpython")
print(f"   URL: {result.get('url')}")
print(f"   Status: {result.get('status_code')}")
print(f"   Success: {'✅' if result.get('success') else '❌'}")
if result.get("success"):
    print(f"   Content Preview: {result.get('content')[:200]}...")

# 4. Final Status
final_status = get_plugin_status()
print(f"\n[4] Final Statistics:")
print(f"   Total Requests: {final_status.get('request_count')}")
print(f"   Cache Hits: {final_status.get('cache_hits')}")
print(f"   Cache Hit Rate: {final_status.get('cache_hit_rate'):.2f}%")

print("\n✅ Validation Complete")
