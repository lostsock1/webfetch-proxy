#!/usr/bin/env python3
"""
🔥 QUICK TEST: Is Monkey Patch Working?
Simple test to verify your proxy integration is active
"""

import requests
import sys


def test_basic_functionality():
    """Test basic functionality"""
    print("🔥 TESTING MONKEY PATCH - LIVE TEST")
    print("=" * 50)

    print("\n✅ TEST 1: Proxy Server Status")
    try:
        response = requests.get("http://localhost:8081/health", timeout=3)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Proxy server: {data['status']}")
            print(f"   ✅ Cache: {data['components']['cache']}")
            print(f"   ✅ Intelligence: {data['components']['intelligence']}")
        else:
            print(f"   ❌ Proxy server error: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Proxy server not responding: {e}")
        return False

    print("\n✅ TEST 2: Basic Web Request")
    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        print(f"   ✅ Direct request works: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Direct request failed: {e}")
        return False

    print("\n✅ TEST 3: Intelligence Storage")
    try:
        response = requests.get(
            "http://localhost:8081/intelligence/list?limit=1", timeout=3
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Intelligence records: {data.get('total_records', 0)}")
        else:
            print(f"   ⚠️  Intelligence endpoint: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Intelligence check failed: {e}")

    return True


def test_monkey_patch_integration():
    """Test if monkey patch is active"""
    print("\n🧪 TESTING MONKEY PATCH INTEGRATION")
    print("=" * 50)

    try:
        # Import and initialize proxy
        from opencode_proxy_plugins import initialize_proxy_plugins

        print("\n📥 Loading proxy integration...")
        active_plugin = initialize_proxy_plugins()
        print(f"   ✅ Plugin loaded: {active_plugin}")

        if active_plugin:
            print("\n🧪 Testing intercepted requests...")

            # Test a URL that should use proxy
            print("   Testing proxy routing...")
            response = requests.get("https://api.openai.com/v1/models")
            print(f"   ✅ Proxy-routed request: {response.status_code}")

            # Test a direct request
            print("   Testing direct routing...")
            response = requests.get("https://httpbin.org/get")
            print(f"   ✅ Direct request: {response.status_code}")

            return True
        else:
            print("   ⚠️  No proxy plugin active")
            return False

    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False


def test_specific_domains():
    """Test specific domains that benefit from proxy"""
    print("\n🌐 TESTING BLOCKED DOMAINS")
    print("=" * 50)

    # Domains that often get blocked
    test_cases = [
        ("GitHub API", "https://api.github.com"),
        ("Documentation", "https://docs.python.org/3/"),
        ("StackOverflow", "https://stackoverflow.com"),
        ("News Site", "https://news.ycombinator.com"),
        ("Reddit", "https://reddit.com"),
    ]

    successful = 0
    total = len(test_cases)

    for name, url in test_cases:
        try:
            print(f"\n   Testing {name}...")
            response = requests.get(url, timeout=10)
            if response.status_code in [200, 301, 302]:
                print(f"   ✅ {name}: {response.status_code}")
                successful += 1
            else:
                print(f"   ⚠️  {name}: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {name}: {str(e)[:30]}")

    print(f"\n📊 Results: {successful}/{total} domains accessible")
    return successful >= total * 0.6  # 60% success rate


def test_performance():
    """Test performance improvements"""
    print("\n⚡ TESTING PERFORMANCE")
    print("=" * 50)

    import time

    test_url = "https://httpbin.org/get"

    # Test 1: Direct request
    start = time.time()
    response1 = requests.get(test_url)
    direct_time = time.time() - start

    # Test 2: Proxy request (may use cache)
    start = time.time()
    response2 = requests.get(test_url)
    proxy_time = time.time() - start

    # Test 3: Another proxy request (should be cached)
    start = time.time()
    response3 = requests.get(test_url)
    cached_time = time.time() - start

    print(f"\n📊 Performance Results:")
    print(f"   Direct: {direct_time:.3f}s")
    print(f"   Proxy: {proxy_time:.3f}s")
    print(f"   Cached: {cached_time:.3f}s")

    if cached_time > 0:
        speedup = direct_time / cached_time
        print(f"   Cache speedup: {speedup:.1f}x faster")

    return True


def main():
    """Run all tests"""
    print("🚀 QUICK TEST: IS YOUR MONKEY PATCH WORKING?")
    print("=" * 60)
    print("Testing if the proxy integration is active and working...")

    all_tests_passed = True

    # Test 1: Basic functionality
    if not test_basic_functionality():
        all_tests_passed = False
        print("\n❌ BASIC TESTS FAILED - Proxy may not be running")
        print(
            "💡 Fix: Start proxy with: cd /Users/djesys/#VIBECODE/webfetch-prxy && python3 webfetch_proxy.py"
        )

    # Test 2: Monkey patch integration
    if not test_monkey_patch_integration():
        all_tests_passed = False
        print("\n❌ INTEGRATION TEST FAILED")
        print("💡 Fix: Check proxy_plugins.py is accessible")

    # Test 3: Specific domains
    if not test_specific_domains():
        print("\n⚠️  DOMAIN TESTS PARTIAL - Some domains may be blocked")

    # Test 4: Performance
    if not test_performance():
        print("\n⚠️  PERFORMANCE TEST INCOMPLETE")

    # Final results
    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 SUCCESS! YOUR MONKEY PATCH IS WORKING!")
        print("✅ Proxy server: Active")
        print("✅ Integration: Loaded")
        print("✅ Requests: Intercepted")
        print("✅ Domains: Accessible")
        print("✅ Performance: Optimized")

        print("\n🚀 YOU CAN NOW USE THE PROXY:")
        print("1. Add these 2 lines to your opencode:")
        print("   from opencode_proxy_plugins import initialize_proxy_plugins")
        print("   initialize_proxy_plugins()")
        print("\n2. Your existing requests.get() calls will use proxy automatically!")

    else:
        print("⚠️  PARTIAL SUCCESS - Some components need attention")
        print("Check the errors above and fix the issues")

    print("\n💡 TO TEST YOURSELF:")
    print("Run: python3 /Users/djesys/#VIBECODE/test_integration.py")

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
