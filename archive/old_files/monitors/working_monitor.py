#!/usr/bin/env python3
"""
🔥 WORKING REAL-TIME PROXY MONITOR
Monitor proxied requests with working intelligence tracking
"""

import requests
import sys
import time
from datetime import datetime

# Initialize proxy
sys.path.insert(0, "/Users/djesys/#VIBECODE")
from opencode_proxy_plugins import initialize_proxy_plugins

initialize_proxy_plugins()


def monitor_intelligence():
    """Monitor intelligence records in real-time"""
    print("🔥 REAL-TIME PROXY MONITOR")
    print("=" * 60)
    print("Monitoring proxied requests...")
    print("Press Ctrl+C to stop\n")

    seen_records = set()
    request_count = 0

    try:
        while True:
            try:
                # Get intelligence records
                response = requests.get(
                    "http://localhost:8081/intelligence/list?limit=10", timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])

                    # Find new records
                    new_records = []
                    for record in records:
                        record_id = (
                            f"{record.get('timestamp', '')}-{record.get('url', '')}"
                        )
                        if record_id not in seen_records:
                            seen_records.add(record_id)
                            new_records.append(record)

                    # Show new records
                    if new_records:
                        print(
                            f"🕐 {datetime.now().strftime('%H:%M:%S')} - NEW REQUESTS:"
                        )

                        for record in reversed(new_records):
                            url = record.get("url", "")
                            tags = record.get("tags", [])
                            timestamp = record.get("timestamp", "")
                            size = record.get("metadata", {}).get("size", 0)

                            # Extract domain
                            domain = url.split("/")[2] if "://" in url else "Unknown"

                            request_count += 1

                            print(f"   #{request_count} 🌐 {domain}")
                            print(f"      📋 {url}")
                            print(f"      🏷️  {' '.join(tags) if tags else 'No tags'}")
                            print(f"      📏 {size} bytes")
                            print(f"      🕐 {timestamp}")
                            print()

                    # Show summary
                    total = data.get("total_records", 0)
                    print(
                        f"\r📊 Total: {total} | New: {len(new_records)} | Requests: {request_count}",
                        end="",
                        flush=True,
                    )

                time.sleep(2)

            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\n⏹️  Monitoring stopped. Total requests: {request_count}")


def test_proxy():
    """Test proxy and show current status"""
    print("🧪 PROXY STATUS")
    print("=" * 40)

    try:
        # Health check
        health = requests.get("http://localhost:8081/health", timeout=5)
        if health.status_code == 200:
            health_data = health.json()
            print(f"🟢 Proxy: {health_data['status']}")
            print(f"💾 Cache: {health_data['components']['cache']}")
            print(f"🧠 Intelligence: {health_data['components']['intelligence']}")
        else:
            print(f"🔴 Proxy health: {health.status_code}")

        # Intelligence check
        intel = requests.get(
            "http://localhost:8081/intelligence/list?limit=3", timeout=5
        )
        if intel.status_code == 200:
            intel_data = intel.json()
            print(f"📊 Intelligence records: {intel_data['total_records']}")

            if intel_data.get("records"):
                latest = intel_data["records"][0]
                print(f"🕐 Latest: {latest.get('timestamp', 'Unknown')}")
                print(f"🌐 Latest URL: {latest.get('url', 'Unknown')}")
                print(f"🏷️  Tags: {latest.get('tags', [])}")

    except Exception as e:
        print(f"❌ Status check failed: {e}")


def make_sample_requests():
    """Make sample requests to demonstrate monitoring"""
    print("\n🧪 MAKING SAMPLE REQUESTS")
    print("=" * 40)

    import requests

    test_urls = [
        ("https://httpbin.org/get", "Basic GET request"),
        ("https://httpbin.org/json", "JSON response"),
        ("https://httpbin.org/headers", "Headers test"),
    ]

    for i, (url, description) in enumerate(test_urls, 1):
        print(f"[{i}/3] {description}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"      ✅ Status: {response.status_code}")
            else:
                print(f"      ⚠️  Status: {response.status_code}")
        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}")

        time.sleep(1)

    print("\n✅ Sample requests complete!")
    print("💡 Monitor will show these requests in real-time...")


if __name__ == "__main__":
    # Show status
    test_proxy()

    # Make sample requests
    make_sample_requests()

    print("\n" + "=" * 60)

    # Start monitoring
    monitor_intelligence()
