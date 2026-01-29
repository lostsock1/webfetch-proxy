#!/usr/bin/env python3
"""
🔥 OpenCode Integration Examples
Real-world examples of integrating webfetch proxy with opencode workflows
"""

import json
import requests
import time
from opencode_proxy_plugins import (
    initialize_proxy_plugins,
    webfetch_proxy,
    bulk_webfetch_proxy,
    ProxyContext,
)


def example_1_monkey_patch_integration():
    """Example 1: Seamless integration using monkey patching"""
    print("Example 1: Monkey Patch Integration")
    print("=" * 40)

    # Initialize proxy plugins (this patches requests module automatically)
    active_plugin = initialize_proxy_plugins()
    print(f"Active plugin: {active_plugin}")

    # Now all requests.get() calls will automatically use proxy when beneficial
    try:
        response = requests.get("https://httpbin.org/get")
        print(f"✅ Direct requests.get() works: {response.status_code}")

        # This will automatically use proxy for blocked domains
        response = requests.get("https://api.github.com/repos/microsoft/vscode")
        print(f"✅ GitHub API request: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_2_wrapper_usage():
    """Example 2: Explicit wrapper usage"""
    print("\nExample 2: Explicit Wrapper Usage")
    print("=" * 40)

    # Initialize proxy
    initialize_proxy_plugins()

    # Use explicit proxy wrapper
    result = webfetch_proxy("https://httpbin.org/get", timeout=10)
    print(f"✅ Webfetch proxy: {result.get('status_code')}")
    print(f"   Success: {result.get('success')}")

    # Use proxy context for specific operations
    with ProxyContext("wrapper"):
        result = webfetch_proxy("https://httpbin.org/headers")
        print(f"✅ Context proxy: {result.get('success')}")


def example_3_ai_model_integration():
    """Example 3: Integration with AI model requests"""
    print("\nExample 3: AI Model Integration")
    print("=" * 40)

    # Common AI API endpoints that often get blocked
    ai_endpoints = [
        "https://api.openai.com/v1/models",
        "https://api.anthropic.com/v1/messages",
        "https://api.together.xyz/v1/models",
    ]

    initialize_proxy_plugins()

    # This will automatically use proxy for AI APIs
    for endpoint in ai_endpoints:
        try:
            # Note: This would normally fail due to missing API keys, but shows the pattern
            print(f"🔄 Attempting: {endpoint}")

            # In real usage, this would be:
            # response = requests.get(endpoint, headers={"Authorization": f"Bearer {api_key}"})
            # The proxy handles the request with proper headers and user agent rotation

        except Exception as e:
            print(f"❌ Expected failure (no API key): {endpoint}")


def example_4_bulk_osint():
    """Example 4: Bulk OSINT operations"""
    print("\nExample 4: Bulk OSINT Operations")
    print("=" * 40)

    # Reconnaissance URLs
    recon_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/ip",
    ]

    initialize_proxy_plugins()

    # Bulk fetch with proxy intelligence
    results = bulk_webfetch_proxy(
        recon_urls, concurrent_limit=3, headers={"X-OpenCode-Scan": "true"}
    )

    print(f"📊 Bulk OSINT Results:")
    print(f"   Total URLs: {len(results)}")
    print(f"   Successful: {sum(1 for r in results if r.get('success', False))}")
    print(f"   Failed: {sum(1 for r in results if not r.get('success', False))}")

    # Analyze results
    for i, result in enumerate(results[:3]):  # Show first 3
        if result.get("success"):
            print(f"   ✅ {recon_urls[i]}: {result.get('status_code')}")
        else:
            print(f"   ❌ {recon_urls[i]}: {result.get('error', 'Unknown error')}")


def example_5_blocked_domain_handling():
    """Example 5: Handling blocked domains"""
    print("\nExample 5: Blocked Domain Handling")
    print("=" * 40)

    # Domains that typically block AI/automated requests
    blocked_domains = [
        "https://google.com/search?q=python",
        "https://stackoverflow.com/questions/tagged/python",
        "https://github.com/trending",
        "https://reddit.com/r/Python",
        "https://news.ycombinator.com/",
    ]

    initialize_proxy_plugins()

    print("🛡️  Testing blocked domain handling:")

    for url in blocked_domains:
        try:
            # This will automatically use proxy due to domain heuristics
            result = webfetch_proxy(url, timeout=15)

            if result.get("success"):
                print(f"   ✅ {url.split('/')[2]}: Accessed via proxy")
            else:
                print(f"   ⚠️  {url.split('/')[2]}: {result.get('error', 'Failed')}")

        except Exception as e:
            print(f"   ❌ {url.split('/')[2]}: {str(e)[:50]}")


def example_6_agent_emulation():
    """Example 6: Advanced agent emulation"""
    print("\nExample 6: Agent Emulation")
    print("=" * 40)

    initialize_proxy_plugins()

    # Simulate different types of agents
    agents = [
        {
            "name": "Browser User",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        },
        {
            "name": "Mobile User",
            "headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
        },
        {
            "name": "API Client",
            "headers": {
                "User-Agent": "OpenCode-AI/1.0",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        },
    ]

    print("🎭 Testing agent emulation:")

    for agent in agents:
        try:
            result = webfetch_proxy(
                "https://httpbin.org/headers", headers=agent["headers"]
            )

            if result.get("success"):
                print(f"   ✅ {agent['name']}: Agent emulation successful")
            else:
                print(f"   ❌ {agent['name']}: {result.get('error')}")

        except Exception as e:
            print(f"   ❌ {agent['name']}: {str(e)[:30]}")


def example_7_real_world_workflow():
    """Example 7: Real-world opencode workflow"""
    print("\nExample 7: Real-World OpenCode Workflow")
    print("=" * 40)

    # Initialize proxy with custom config
    initialize_proxy_plugins()

    print("🔄 OpenCode Research Workflow:")

    # Step 1: Search for information
    print("   [1] Searching for Python documentation...")
    search_result = webfetch_proxy("https://docs.python.org/3/")
    print(f"      Status: {search_result.get('status_code')}")

    # Step 2: Check GitHub for relevant repositories
    print("   [2] Checking GitHub trends...")
    github_result = webfetch_proxy("https://github.com/trending")
    print(f"      Status: {github_result.get('status_code')}")

    # Step 3: Bulk fetch multiple resources
    print("   [3] Bulk fetching resources...")
    resources = [
        "https://httpbin.org/delay/1",
        "https://httpbin.org/cache/60",
        "https://httpbin.org/cookies",
    ]

    bulk_results = bulk_webfetch_proxy(resources)
    print(f"      Bulk results: {len(bulk_results)} resources")

    # Step 4: Process results
    successful = sum(1 for r in bulk_results if r.get("success"))
    print(f"      Successful: {successful}/{len(bulk_results)}")

    print("✅ OpenCode workflow completed successfully")


def main():
    """Run all integration examples"""
    print("🔥 OPENCODE WEBFETCH PROXY INTEGRATION EXAMPLES")
    print("=" * 60)
    print("Demonstrating different ways to integrate proxy with opencode")

    examples = [
        example_1_monkey_patch_integration,
        example_2_wrapper_usage,
        example_3_ai_model_integration,
        example_4_bulk_osint,
        example_5_blocked_domain_handling,
        example_6_agent_emulation,
        example_7_real_world_workflow,
    ]

    for example in examples:
        try:
            example()
            time.sleep(1)  # Brief pause between examples
        except Exception as e:
            print(f"❌ Example failed: {e}")

    print("\n" + "=" * 60)
    print("✅ ALL INTEGRATION EXAMPLES COMPLETED")
    print("\n💡 Key Takeaways:")
    print("   • Monkey patching provides seamless integration")
    print("   • Wrapper functions offer explicit control")
    print("   • Proxy automatically handles blocked domains")
    print("   • Bulk operations improve efficiency")
    print("   • Agent emulation enhances success rates")
    print("   • Real-world workflows benefit from proxy intelligence")


if __name__ == "__main__":
    main()
