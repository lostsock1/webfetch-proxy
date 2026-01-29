#!/usr/bin/env python3
"""
🔥 MONKEY PATCH DEMONSTRATION
Step-by-step walkthrough of how monkey patching works
"""

import requests
import json
import time


def original_requests_get(url, **kwargs):
    """This is what requests.get() normally does"""
    print(f"  🔍 Original requests.get() called for: {url}")
    print(f"     Headers: {kwargs.get('headers', {})}")


# Step 1: Store the original function
print("STEP 1: SAVING ORIGINAL FUNCTION")
print("=" * 40)

original_requests_get = requests.get
print(f"✅ Saved original requests.get() function")
print(f"   Function ID: {id(requests.get)}")

print("\nSTEP 2: TESTING ORIGINAL FUNCTION")
print("=" * 40)

# Test original function
original_requests_get("https://httpbin.org/get")
print("✅ Original function works normally")

print("\nSTEP 3: CREATING PROXY WRAPPER")
print("=" * 40)


def proxy_requests_get(url, **kwargs):
    """Enhanced version that uses proxy"""
    print(f"  🔍 Proxy requests.get() called for: {url}")

    # Smart decision: should we use proxy?
    domain = url.split("/")[2] if "://" in url else "unknown"
    should_use_proxy = domain in ["api.openai.com", "docs.python.org", "github.com"]

    if should_use_proxy:
        print(f"     📡 Using proxy for domain: {domain}")
        # Simulate proxy request
        proxy_response = type(
            "ProxyResponse",
            (),
            {
                "status_code": 200,
                "content": b'{"proxied": true}',
                "headers": {"via": "proxy"},
                "url": url,
            },
        )()
        print(f"     ✅ Proxy request successful")
        return proxy_response
    else:
        print(f"     🔄 Using direct request for domain: {domain}")
        # Fallback to original function
        return original_requests_get(url, **kwargs)


print(f"✅ Created proxy wrapper function")
print(f"   Wrapper ID: {id(proxy_requests_get)}")

print("\nSTEP 4: APPLYING MONKEY PATCH")
print("=" * 40)

# The magic moment: replace the function
requests.get = proxy_requests_get
print(f"✅ Monkey patch applied!")
print(f"   requests.get ID: {id(requests.get)}")
print(f"   Now pointing to: {requests.get.__name__}")

print("\nSTEP 5: TESTING MONKEY PATCH")
print("=" * 40)

print("\n🧪 Test 1: Domain that uses proxy")
result1 = requests.get("https://api.openai.com/v1/models")
print(f"   Result: {result1.status_code}")

print("\n🧪 Test 2: Domain that uses direct")
result2 = requests.get("https://httpbin.org/get")
print(f"   Result: {result2.status_code}")

print("\n🧪 Test 3: Another proxy domain")
result3 = requests.get("https://docs.python.org/3/")
print(f"   Result: {result3.status_code}")

print("\nSTEP 6: RESTORING ORIGINAL")
print("=" * 40)

# Can restore original if needed
requests.get = original_requests_get
print(f"✅ Original function restored")
print(f"   requests.get ID: {id(requests.get)}")

print("\n🧪 Test 4: Back to original behavior")
result4 = requests.get("https://httpbin.org/get")
print(f"   Result: {result4.status_code}")


def demo_advanced_monkey_patch():
    """Demonstrate more advanced monkey patching features"""
    print("\n\n🚀 ADVANCED MONKEY PATCH FEATURES")
    print("=" * 50)

    # Save all original functions
    original_functions = {
        "get": requests.get,
        "post": requests.post,
        "session_get": requests.Session.get,
        "session_post": requests.Session.post,
    }

    print("1. Saving multiple functions...")
    for name, func in original_functions.items():
        print(f"   ✅ {name} saved")

    # Create enhanced session
    def enhanced_session_request(self, method, url, **kwargs):
        print(f"  🎯 Enhanced Session.{method}() for: {url}")
        print(f"     Session: {self.__class__.__name__}")

        # Add some intelligence
        headers = kwargs.get("headers", {})
        headers["X-Proxy-Enhanced"] = "true"
        kwargs["headers"] = headers

        # Call original method
        return original_functions[f"session_{method.lower()}"](
            self, method, url, **kwargs
        )

    print("\n2. Applying session monkey patches...")
    requests.Session.get = lambda self, url, **kwargs: enhanced_session_request(
        self, "GET", url, **kwargs
    )
    requests.Session.post = lambda self, url, **kwargs: enhanced_session_request(
        self, "POST", url, **kwargs
    )
    print(f"   ✅ Session methods enhanced")

    # Test enhanced session
    print("\n3. Testing enhanced session...")
    session = requests.Session()
    response = session.get("https://httpbin.org/get")
    print(f"   Result: {response.status_code}")

    # Restore all functions
    print("\n4. Restoring all original functions...")
    for name, func in original_functions.items():
        setattr(requests, name.replace("session_", ""), func)
    print(f"   ✅ All functions restored")


def demonstrate_seamless_integration():
    """Show how this looks in real opencode usage"""
    print("\n\n🎯 REAL-WORLD OPENCODE INTEGRATION")
    print("=" * 50)

    print("This is how your opencode integration will look:")
    print()
    print("=" * 30)
    print("# Your existing opencode code (NO CHANGES NEEDED)")
    print("import requests")
    print()
    print("# Step 1: Initialize proxy (ONE TIME SETUP)")
    print("from opencode_proxy_plugins import initialize_proxy_plugins")
    print("initialize_proxy_plugins()")
    print()
    print("# Step 2: Your existing code works unchanged")
    print("def my_opencode_function():")
    print("    # These calls automatically use proxy when needed!")
    print("    response1 = requests.get('https://api.openai.com/v1/models')")
    print(
        "    response2 = requests.post('https://api.anthropic.com/v1/messages', json={...})"
    )
    print(
        "    response3 = requests.get('https://docs.python.org/3/library/requests.html')"
    )
    print("    ")
    print("    return response1.json(), response2.json(), response3.text")
    print("=" * 30)

    print("\n✨ Benefits:")
    print("   • Zero code changes required")
    print("   • Automatic proxy usage")
    print("   • Graceful fallback")
    print("   • Intelligence gathering")
    print("   • Performance optimization")


if __name__ == "__main__":
    demonstrate_seamless_integration()
    demo_advanced_monkey_patch()
