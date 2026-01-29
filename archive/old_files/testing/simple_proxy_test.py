#!/usr/bin/env python3
"""
Simple test for webfetch proxy functionality
"""

import asyncio
import aiohttp
import json
import sys
import os

sys.path.append("/Users/djesys/#VIBECODE/webfetch-prxy")


async def test_proxy_functionality():
    """Test basic proxy functionality"""
    print("🔥 Testing #VIBECODE Webfetch Proxy")
    print("=" * 50)

    try:
        # Test direct HTTP request
        async with aiohttp.ClientSession() as session:
            print("\n[1] Testing direct HTTP request...")
            async with session.get("https://httpbin.org/get") as response:
                data = await response.json()
                print(f"   ✅ Direct request successful: {response.status}")

        # Test proxy endpoint
        print("\n[2] Testing proxy endpoint...")
        proxy_url = "http://localhost:8081/fetch"

        request_data = {
            "url": "https://httpbin.org/get",
            "method": "GET",
            "intelligence_tags": ["test", "#VIBECODE"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                proxy_url,
                json=request_data,
                headers={"Authorization": "Bearer test-key"},
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    print(
                        f"   ✅ Proxy request successful: {result.get('status_code')}"
                    )
                    print(f"   ✅ Success: {result.get('success')}")
                    print(f"   ✅ Size: {result.get('size')} bytes")
                else:
                    print(f"   ❌ Proxy request failed: {response.status}")
                    text = await response.text()
                    print(f"   Error: {text[:200]}")

        # Test health endpoint
        print("\n[3] Testing health endpoint...")
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8081/health") as response:
                if response.status == 200:
                    health = await response.json()
                    print(f"   ✅ Health check: {health.get('status')}")
                    print(f"   ✅ Cache: {health.get('components', {}).get('cache')}")
                    print(
                        f"   ✅ Intelligence: {health.get('components', {}).get('intelligence')}"
                    )
                else:
                    print(f"   ❌ Health check failed: {response.status}")

        print("\n[4] Testing intelligence storage...")
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:8081/intelligence/list?limit=5"
            ) as response:
                if response.status == 200:
                    intel = await response.json()
                    print(f"   ✅ Intelligence records: {intel.get('total_records')}")

                    if intel.get("records"):
                        print("   📋 Recent records:")
                        for record in intel.get("records", [])[:3]:
                            print(
                                f"      - {record.get('url')} ({record.get('size')} bytes)"
                            )
                            print(f"        Tags: {', '.join(record.get('tags', []))}")
                else:
                    print(f"   ❌ Intelligence list failed: {response.status}")

        print("\n[5] Testing bulk fetch...")
        bulk_data = {
            "urls": ["https://httpbin.org/get", "https://httpbin.org/json"],
            "concurrent_limit": 2,
            "intelligence_tags": ["bulk", "test"],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8081/fetch/bulk",
                json=bulk_data,
                headers={"Authorization": "Bearer test-key"},
            ) as response:
                if response.status == 200:
                    results = await response.json()
                    print(f"   ✅ Bulk fetch successful")
                    print(f"   ✅ Total URLs: {results.get('total_urls')}")
                    print(f"   ✅ Successful: {results.get('successful')}")
                    print(f"   ✅ Failed: {results.get('failed')}")
                else:
                    print(f"   ❌ Bulk fetch failed: {response.status}")

        print("\n✅ ALL TESTS COMPLETED")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_proxy_functionality())
