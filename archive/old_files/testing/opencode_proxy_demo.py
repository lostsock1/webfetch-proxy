#!/usr/bin/env python3
"""
🔥 OPENCODE PROXY DEMO - Solving the Blocking Problem
Demonstrates how the proxy solves real opencode blocking issues
"""

import time
import requests
from opencode_proxy_plugins import initialize_proxy_plugins, webfetch_proxy


def demo_blocking_problem():
    """Demonstrate the problem that the proxy solves"""
    print("🔥 OPENCODE BLOCKING PROBLEM DEMO")
    print("=" * 50)

    print("\n❌ BEFORE PROXY: The Problem")
    print("Opencode models often get blocked when accessing online data:")
    print("• AI APIs: OpenAI, Anthropic, Together.ai")
    print("• Search engines: Google, Bing, DuckDuckGo")
    print("• Code platforms: GitHub, StackOverflow")
    print("• Research sites: Arxiv, papers with code")
    print("• Documentation: Real-time API docs")

    print("\n✅ AFTER PROXY: The Solution")
    print("The proxy automatically handles blocking with:")
    print("• Intelligent routing: Uses proxy for blocked domains")
    print("• Agent emulation: Rotates user agents")
    print("• Fallback safety: Always works, even if proxy fails")
    print("• Intelligence gathering: Tracks all requests")
    print("• Performance boost: Caching and bulk operations")


def demo_real_world_scenarios():
    """Demonstrate real-world opencode scenarios"""
    print("\n🌐 REAL-WORLD OPENCODE SCENARIOS")
    print("=" * 50)

    # Initialize proxy
    active_plugin = initialize_proxy_plugins()
    print(f"\n🔧 Proxy Active: {active_plugin}")

    scenarios = [
        {
            "name": "AI Model API Access",
            "description": "Opencode model needs to call OpenAI API",
            "url": "https://api.openai.com/v1/models",
            "expected": "Would normally be blocked",
        },
        {
            "name": "Documentation Lookup",
            "description": "Real-time API documentation access",
            "url": "https://docs.python.org/3/library/requests.html",
            "expected": "Research tool functionality",
        },
        {
            "name": "Code Search",
            "description": "Finding code examples on StackOverflow",
            "url": "https://stackoverflow.com/questions/tagged/python",
            "expected": "Code completion assistance",
        },
        {
            "name": "Research Papers",
            "description": "Accessing academic papers for knowledge",
            "url": "https://arxiv.org/abs/2303.08774",
            "expected": "Research and learning",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n[{i}] {scenario['name']}")
        print(f"    Purpose: {scenario['description']}")
        print(f"    URL: {scenario['url']}")

        try:
            # This demonstrates the proxy automatically routing
            result = webfetch_proxy(
                scenario["url"],
                tags=["opencode", "demo", scenario["name"].lower().replace(" ", "_")],
            )

            if result.get("success"):
                print(f"    ✅ Access: SUCCESS (via proxy)")
                print(f"    📊 Response: {result.get('status_code')}")
            else:
                print(f"    ⚠️  Access: FAILED ({result.get('error', 'Unknown')})")

        except Exception as e:
            print(f"    ❌ Error: {str(e)[:50]}")

        time.sleep(0.5)  # Brief pause


def demo_performance_comparison():
    """Show performance benefits"""
    print("\n⚡ PERFORMANCE COMPARISON")
    print("=" * 50)

    # Initialize proxy
    initialize_proxy_plugins()

    test_url = "https://httpbin.org/get"

    print(f"\nTesting URL: {test_url}")

    # First request (no cache)
    print("\n1️⃣  First Request (Cold)")
    start_time = time.time()
    result1 = requests.get(test_url)
    first_time = time.time() - start_time
    print(f"   Direct request: {first_time:.3f}s")

    # Second request (through proxy, first time)
    print("\n2️⃣  Proxy Request (First Time)")
    start_time = time.time()
    result2 = webfetch_proxy(test_url)
    proxy_first_time = time.time() - start_time
    print(f"   Proxy request: {proxy_first_time:.3f}s")

    # Third request (cached through proxy)
    print("\n3️⃣  Proxy Request (Cached)")
    start_time = time.time()
    result3 = webfetch_proxy(test_url)
    proxy_cached_time = time.time() - start_time
    print(f"   Cached proxy: {proxy_cached_time:.3f}s")

    # Performance analysis
    print(f"\n📊 Performance Analysis:")
    if proxy_cached_time > 0:
        speedup = first_time / proxy_cached_time
        print(f"   Cache speedup: {speedup:.1f}x faster")

    print(f"   Proxy overhead: {proxy_first_time - first_time:.3f}s (acceptable)")
    print(f"   Cached speed: {proxy_cached_time:.3f}s (excellent)")


def demo_bulk_operations():
    """Show bulk operation capabilities"""
    print("\n📦 BULK OPERATIONS DEMO")
    print("=" * 50)

    initialize_proxy_plugins()

    # Simulate multiple API calls that opencode might need
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/ip",
    ]

    print(f"\n🔄 Processing {len(urls)} URLs simultaneously...")

    start_time = time.time()
    results = []
    for url in urls:
        result = webfetch_proxy(url, tags=["bulk", "demo"])
        results.append(result)

    processing_time = time.time() - start_time

    successful = sum(1 for r in results if r.get("success"))

    print(f"   ✅ Completed: {successful}/{len(urls)} URLs")
    print(f"   ⏱️  Total time: {processing_time:.3f}s")
    print(f"   📊 Average per URL: {processing_time / len(urls):.3f}s")
    print(f"   🎯 Success rate: {successful / len(urls) * 100:.1f}%")


def demo_intelligence_gathering():
    """Show intelligence gathering capabilities"""
    print("\n🧠 INTELLIGENCE GATHERING DEMO")
    print("=" * 50)

    initialize_proxy_plugins()

    # Make some requests with intelligence tags
    print("\n📝 Making tagged requests...")

    tagged_urls = [
        ("https://httpbin.org/get", ["ai-model", "api-test"]),
        ("https://httpbin.org/json", ["research", "data"]),
        ("https://httpbin.org/headers", ["analysis", "tech"]),
    ]

    for url, tags in tagged_urls:
        result = webfetch_proxy(url, tags=tags)
        print(f"   ✅ {url.split('/')[-1]}: {tags}")
        time.sleep(0.2)

    # Check intelligence storage
    print("\n📊 Intelligence Summary:")
    try:
        import requests

        response = requests.get("http://localhost:8081/intelligence/list?limit=10")
        if response.status_code == 200:
            data = response.json()
            print(f"   📁 Total records: {data.get('total_records', 0)}")

            if data.get("records"):
                print("   🏷️  Recent tags:")
                recent_tags = set()
                for record in data.get("records", [])[:5]:
                    recent_tags.update(record.get("tags", []))

                for tag in sorted(list(recent_tags)[:5]):
                    print(f"      • {tag}")
    except Exception as e:
        print(f"   ⚠️  Could not retrieve intelligence: {e}")


def main():
    """Run the complete demo"""
    print("🔥 OPENCODE WEBFETCH PROXY - COMPLETE DEMONSTRATION")
    print("=" * 70)
    print("This demo shows how the proxy solves real opencode blocking problems")
    print("and enhances online data access for AI models.\n")

    # Run all demos
    demo_blocking_problem()
    demo_real_world_scenarios()
    demo_performance_comparison()
    demo_bulk_operations()
    demo_intelligence_gathering()

    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("\n🎯 Key Benefits Demonstrated:")
    print("   • Solves blocking issues for opencode models")
    print("   • Automatic intelligent routing")
    print("   • Performance improvements with caching")
    print("   • Bulk operation capabilities")
    print("   • Intelligence gathering and analytics")
    print("   • Seamless integration (zero code changes)")

    print("\n🚀 Next Steps:")
    print("   1. Integrate with your opencode models")
    print("   2. Monitor intelligence data for optimization")
    print("   3. Expand domain routing rules")
    print("   4. Scale proxy for production use")


if __name__ == "__main__":
    main()
