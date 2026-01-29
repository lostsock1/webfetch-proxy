#!/usr/bin/env python3
"""
🔥 SHADOW Webfetch Proxy Test Suite
Comprehensive testing and demonstration script
"""

import asyncio
import json
import time
import requests
import sys
from typing import Dict, List, Any


def test_proxy_endpoints():
    """Test all proxy endpoints"""
    base_url = "http://localhost:8081"
    headers = {"Authorization": "Bearer test-key", "Content-Type": "application/json"}

    print("🔥 SHADOW WEBFETCH PROXY TEST SUITE")
    print("=" * 50)

    # Test 1: Health check
    print("\n[1] Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"   ✅ Health: {health_data['status']}")
            print(f"   ✅ Cache: {health_data['components']['cache']}")
            print(f"   ✅ Intelligence: {health_data['components']['intelligence']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False

    # Test 2: Root endpoint
    print("\n[2] Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            root_data = response.json()
            print(f"   ✅ Service: {root_data['service']}")
            print(f"   ✅ Version: {root_data['version']}")
            print(f"   ✅ Features: {len(root_data['features'])} available")
        else:
            print(f"   ❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Root endpoint error: {e}")

    # Test 3: Single URL fetch
    print("\n[3] Testing single URL fetch...")
    try:
        payload = {
            "url": "https://httpbin.org/get",
            "method": "GET",
            "intelligence_tags": ["test", "single_fetch"],
            "timeout": 10,
        }

        response = requests.post(
            f"{base_url}/fetch", json=payload, headers=headers, timeout=15
        )

        if response.status_code == 200:
            fetch_data = response.json()
            print(f"   ✅ Fetch status: {fetch_data['status_code']}")
            print(f"   ✅ Success: {fetch_data['success']}")
            print(f"   ✅ Execution time: {fetch_data['execution_time']:.3f}s")
            print(f"   ✅ Size: {fetch_data['size']} bytes")
            print(f"   ✅ URL: {fetch_data['url']}")
        else:
            print(f"   ❌ Fetch failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Fetch error: {e}")
        return False

    # Test 4: Bulk fetch
    print("\n[4] Testing bulk fetch...")
    try:
        payload = {
            "urls": [
                "https://httpbin.org/get",
                "https://httpbin.org/json",
                "https://httpbin.org/status/200",
            ],
            "concurrent_limit": 3,
            "intelligence_tags": ["test", "bulk_fetch"],
            "common_headers": {"X-Test": "bulk-request"},
        }

        response = requests.post(
            f"{base_url}/fetch/bulk", json=payload, headers=headers, timeout=30
        )

        if response.status_code == 200:
            bulk_data = response.json()
            print(f"   ✅ Total URLs: {bulk_data['total_urls']}")
            print(f"   ✅ Successful: {bulk_data['successful']}")
            print(f"   ✅ Failed: {bulk_data['failed']}")

            # Show result summary
            for result in bulk_data["results"]:
                status = "✅" if result["success"] else "❌"
                print(f"   {status} {result['url']}: {result['status_code']}")
        else:
            print(f"   ❌ Bulk fetch failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Bulk fetch error: {e}")
        return False

    # Test 5: Intelligence list
    print("\n[5] Testing intelligence endpoint...")
    try:
        response = requests.get(f"{base_url}/intelligence/list?limit=5", timeout=5)
        if response.status_code == 200:
            intel_data = response.json()
            print(f"   ✅ Total records: {intel_data['total_records']}")

            if intel_data["records"]:
                print("   📋 Recent intelligence records:")
                for record in intel_data["records"][:3]:
                    print(f"      - {record['url']}")
                    print(f"        Tags: {', '.join(record['tags'])}")
                    print(f"        Size: {record['size']} bytes")
            else:
                print("   ℹ️  No intelligence records found")
        else:
            print(f"   ❌ Intelligence endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Intelligence error: {e}")

    # Test 6: Config endpoint
    print("\n[6] Testing config endpoint...")
    try:
        response = requests.get(f"{base_url}/config", timeout=5)
        if response.status_code == 200:
            config_data = response.json()
            print(f"   ✅ Proxy port: {config_data['proxy']['port']}")
            print(f"   ✅ Cache enabled: {config_data['caching']['enabled']}")
            print(
                f"   ✅ Intelligence enabled: {config_data['intelligence']['enabled']}"
            )
            print(
                f"   ✅ Rate limiting: {config_data['security']['rate_limiting']['enabled']}"
            )
        else:
            print(f"   ❌ Config endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Config error: {e}")

    return True


def test_redis_cache():
    """Test Redis cache functionality"""
    print("\n[7] Testing Redis cache...")
    try:
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()

        # Test cache operations
        test_key = "test:cache:key"
        test_value = '{"test": "data", "timestamp": "' + str(time.time()) + '"}'

        r.setex(test_key, 60, test_value)
        retrieved = r.get(test_key)

        if retrieved:
            print(f"   ✅ Cache write/read successful")
            print(f"   ✅ Test key exists: {r.exists(test_key) > 0}")
            print(f"   ✅ Cache TTL: {r.ttl(test_key)} seconds")

            # Cleanup
            r.delete(test_key)
        else:
            print(f"   ❌ Cache read failed")
            return False

    except ImportError:
        print(f"   ⚠️  Redis not available (package not installed)")
        return True
    except Exception as e:
        print(f"   ❌ Redis cache error: {e}")
        return False

    return True


def test_performance():
    """Test proxy performance"""
    print("\n[8] Testing performance...")
    try:
        base_url = "http://localhost:8081"
        headers = {
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
        }

        # Single request performance
        start_time = time.time()
        payload = {
            "url": "https://httpbin.org/delay/1",
            "timeout": 5,
            "cache_enabled": True,
        }

        response = requests.post(
            f"{base_url}/fetch", json=payload, headers=headers, timeout=10
        )

        total_time = time.time() - start_time

        if response.status_code == 200:
            print(f"   ✅ Single request time: {total_time:.3f}s")
            print(
                f"   ✅ Proxy response: {response.json().get('execution_time', 0):.3f}s"
            )
        else:
            print(f"   ⚠️  Performance test failed: {response.status_code}")

        # Test cached request
        print(f"   📊 Testing cached request...")
        start_time = time.time()

        response2 = requests.post(
            f"{base_url}/fetch", json=payload, headers=headers, timeout=10
        )

        cached_time = time.time() - start_time

        if response2.status_code == 200:
            print(f"   ✅ Cached request time: {cached_time:.3f}s")
            speedup = total_time / cached_time if cached_time > 0 else 0
            print(f"   ⚡ Cache speedup: {speedup:.1f}x faster")

    except Exception as e:
        print(f"   ❌ Performance test error: {e}")
        return False

    return True


def demonstrate_osint_workflow():
    """Demonstrate OSINT workflow"""
    print("\n[9] Demonstrating OSINT workflow...")
    try:
        base_url = "http://localhost:8081"
        headers = {
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
        }

        # Domain reconnaissance URLs
        test_domain = "example.com"
        urls = [
            f"http://{test_domain}",
            f"https://{test_domain}",
            f"http://{test_domain}/robots.txt",
            f"http://{test_domain}/sitemap.xml",
        ]

        payload = {
            "urls": urls,
            "concurrent_limit": 2,
            "intelligence_tags": ["osint", "demonstration", test_domain],
            "common_headers": {"User-Agent": "SHADOW-OSINT-Bot/1.0 (Reconnaissance)"},
        }

        print(f"   🔍 Running OSINT reconnaissance on {test_domain}")
        start_time = time.time()

        response = requests.post(
            f"{base_url}/fetch/bulk", json=payload, headers=headers, timeout=20
        )

        execution_time = time.time() - start_time

        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ OSINT workflow completed in {execution_time:.3f}s")
            print(f"   ✅ Total URLs processed: {results['total_urls']}")
            print(f"   ✅ Successful fetches: {results['successful']}")
            print(f"   ✅ Failed fetches: {results['failed']}")

            # Show successful results
            successful_results = [r for r in results["results"] if r["success"]]
            if successful_results:
                print(f"   📋 Successful targets:")
                for result in successful_results:
                    print(f"      - {result['url']}: {result['status_code']}")
        else:
            print(f"   ❌ OSINT workflow failed: {response.status_code}")

    except Exception as e:
        print(f"   ❌ OSINT workflow error: {e}")


def main():
    """Main test execution"""
    print("Starting comprehensive proxy testing...")

    # Check if proxy is running
    try:
        response = requests.get("http://localhost:8081/health", timeout=3)
        if response.status_code != 200:
            print("❌ Proxy is not responding properly")
            print(
                "Please start the proxy with: cd /tmp/shadow-webfetch-proxy && ./start_proxy.sh"
            )
            return 1
    except Exception:
        print("❌ Proxy is not running")
        print(
            "Please start the proxy with: cd /tmp/shadow-webfetch-proxy && ./start_proxy.sh"
        )
        return 1

    # Run all tests
    all_passed = True

    tests = [
        test_proxy_endpoints,
        test_redis_cache,
        test_performance,
        demonstrate_osint_workflow,
    ]

    for test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Test {test_func.__name__} failed: {e}")
            all_passed = False

    # Final summary
    print("\n" + "=" * 50)
    if all_passed:
        print("🔥 ALL TESTS PASSED!")
        print("✅ Proxy is fully functional and ready for operations")
        print("\n🎯 Next Steps:")
        print("1. Review intelligence records in /tmp/shadow-intelligence/")
        print("2. Test with your own URLs and use cases")
        print("3. Integrate with your existing SHADOW tools")
        print("4. Configure custom settings in config.yaml")
        print("\n📖 See README.md for complete documentation")
        return 0
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Check the error messages above and verify your setup")
        return 1


if __name__ == "__main__":
    sys.exit(main())
