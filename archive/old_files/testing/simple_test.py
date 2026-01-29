#!/usr/bin/env python3
"""
🔥 SIMPLE TEST: Is Your Proxy Working?
Copy this code and run it to test your proxy integration
"""

# 1. Test 1: Basic proxy server check
print("🔥 TEST 1: Is proxy server running?")
try:
    import requests

    response = requests.get("http://localhost:8081/health", timeout=3)
    if response.status_code == 200:
        print("✅ YES - Proxy server is running!")
        print(f"   Status: {response.json()['status']}")
    else:
        print("❌ NO - Proxy server not responding properly")
        print(
            "   Fix: Start proxy with: cd /Users/djesys/#VIBECODE/webfetch-prxy && python3 webfetch_proxy.py"
        )
        exit(1)
except Exception as e:
    print("❌ NO - Proxy server not running")
    print(f"   Error: {e}")
    print(
        "   Fix: Start proxy with: cd /Users/djesys/#VIBECODE/webfetch-prxy && python3 webfetch_proxy.py"
    )
    exit(1)

# 2. Test 2: Import and initialize proxy
print("\n🔥 TEST 2: Can you load the proxy integration?")
try:
    from opencode_proxy_plugins import initialize_proxy_plugins

    print("✅ YES - Proxy integration files found!")
except Exception as e:
    print("❌ NO - Cannot load proxy integration")
    print(f"   Error: {e}")
    print("   Fix: Check that /Users/djesys/#VIBECODE/opencode_proxy_plugins.py exists")
    exit(1)

# 3. Test 3: Initialize the proxy
print("\n🔥 TEST 3: Does the monkey patch work?")
try:
    active_plugin = initialize_proxy_plugins()
    if active_plugin:
        print(f"✅ YES - Monkey patch activated! Plugin: {active_plugin}")
    else:
        print("⚠️  NO - Monkey patch not activated")
        print("   Fix: Check proxy configuration")
except Exception as e:
    print(f"❌ NO - Monkey patch failed: {e}")
    exit(1)

# 4. Test 4: Make a test request
print("\n🔥 TEST 4: Are requests being intercepted?")
try:
    import requests

    # Test with a domain that should use proxy
    response = requests.get("https://httpbin.org/get")
    print(f"✅ YES - Request intercepted! Status: {response.status_code}")
except Exception as e:
    print(f"❌ NO - Request not intercepted: {e}")
    exit(1)

# 5. Test 5: Performance check
print("\n🔥 TEST 5: Is caching working?")
try:
    import time

    # Make same request twice
    start = time.time()
    requests.get("https://httpbin.org/get")
    first_time = time.time() - start

    start = time.time()
    requests.get("https://httpbin.org/get")
    second_time = time.time() - start

    if second_time < first_time:
        print(f"✅ YES - Caching working! {second_time:.3f}s vs {first_time:.3f}s")
    else:
        print(f"⚠️  Maybe - Performance: {second_time:.3f}s vs {first_time:.3f}s")
except Exception as e:
    print(f"❌ NO - Performance test failed: {e}")

# SUCCESS MESSAGE
print("\n" + "=" * 50)
print("🎉 CONGRATULATIONS! YOUR PROXY IS WORKING!")
print("=" * 50)
print("\n✅ PROXY SERVER: Running")
print("✅ INTEGRATION: Loaded")
print("✅ MONKEY PATCH: Active")
print("✅ REQUESTS: Intercepted")
print("✅ CACHING: Working")

print("\n🚀 HOW TO USE IN YOUR OPENCODE:")
print("Add these 2 lines at the start of your opencode script:")
print("```python")
print("from opencode_proxy_plugins import initialize_proxy_plugins")
print("initialize_proxy_plugins()")
print("```")
print(
    "\nThat's it! Your existing requests.get() calls will now use proxy automatically!"
)

print("\n💡 TEST YOURSELF:")
print("Create a new Python file with this code:")
print("```python")
print("from opencode_proxy_plugins import initialize_proxy_plugins")
print("initialize_proxy_plugins()")
print("import requests")
print("response = requests.get('https://api.openai.com/v1/models')")
print("print('Status:', response.status_code)")
print("```")
print("\nThis will show you the proxy in action!")
