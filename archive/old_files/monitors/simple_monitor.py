#!/usr/bin/env python3
"""
🔥 SIMPLE REAL-TIME PROXY MONITOR
Simple real-time monitoring of proxied requests
"""

import requests
import time
import json
from datetime import datetime


def monitor_requests():
    """Monitor proxied requests in real-time"""
    print("🔥 REAL-TIME PROXY MONITORING")
    print("=" * 60)
    print("Monitoring all proxied requests...")
    print("Press Ctrl+C to stop\n")

    # Track seen URLs
    seen_urls = set()
    request_count = 0

    try:
        while True:
            try:
                # Get latest intelligence
                response = requests.get(
                    "http://localhost:8081/intelligence/list?limit=20", timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])

                    # Find new requests
                    new_requests = []
                    for record in records:
                        url = record.get("url", "")
                        if url and url not in seen_urls:
                            seen_urls.add(url)
                            new_requests.append(record)

                    # Show new requests
                    if new_requests:
                        for record in reversed(new_requests):
                            url = record.get("url", "")
                            tags = record.get("tags", [])
                            timestamp = record.get("timestamp", "")
                            size = record.get("metadata", {}).get("size", 0)

                            # Domain
                            domain = url.split("/")[2] if "://" in url else "Unknown"

                            # Format timestamp
                            if "T" in timestamp:
                                time_part = timestamp.split("T")[1].split(".")[0]
                            else:
                                time_part = (
                                    timestamp.split(" ")[1]
                                    if " " in timestamp
                                    else timestamp
                                )

                            request_count += 1

                            print(f"🕐 {time_part} | #{request_count}")
                            print(f"   🌐 {domain}")
                            print(f"   📋 {url}")
                            print(f"   🏷️  {' '.join(tags) if tags else 'No tags'}")
                            print(f"   📏 {size} bytes")
                            print()

                    # Show summary line
                    total = data.get("total_records", 0)
                    print(
                        f"\r📊 Total: {total} | New: {len(new_requests)} | {datetime.now().strftime('%H:%M:%S')}",
                        end="",
                        flush=True,
                    )

                time.sleep(2)

            except requests.exceptions.RequestException as e:
                print(f"\n❌ Connection error: {e}")
                print("Trying again in 5 seconds...")
                time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n\n⏹️  Monitoring stopped. Total requests: {request_count}")


def make_test_request():
    """Make a test request to demonstrate monitoring"""
    print("🧪 Making test request...")

    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        print(f"✅ Test request completed: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"🌐 Request details:")
            print(f"   URL: {data.get('url', 'Unknown')}")
            print(f"   Headers: {len(data.get('headers', {}))} headers")
            print(f"   IP: {data.get('origin', 'Unknown')}")

    except Exception as e:
        print(f"❌ Test request failed: {e}")


def show_proxy_status():
    """Show current proxy status"""
    print("❤️  PROXY STATUS")
    print("=" * 60)

    try:
        # Health check
        health_response = requests.get("http://localhost:8081/health", timeout=5)

        if health_response.status_code == 200:
            health = health_response.json()
            status = health.get("status", "unknown")

            print(f"🟢 Proxy Status: {status.upper()}")
            print(f"⏰ Check Time: {health.get('timestamp', 'Unknown')}")

            components = health.get("components", {})
            print(f"💾 Cache: {components.get('cache', 'Unknown')}")
            print(f"🧠 Intelligence: {components.get('intelligence', 'Unknown')}")

        else:
            print(f"🔴 Proxy Health: HTTP {health_response.status_code}")

        # Intelligence stats
        intel_response = requests.get(
            "http://localhost:8081/intelligence/list?limit=1", timeout=5
        )

        if intel_response.status_code == 200:
            intel_data = intel_response.json()
            total_records = intel_data.get("total_records", 0)
            print(f"📊 Intelligence Records: {total_records}")

            if total_records > 0:
                latest_record = intel_data.get("records", [{}])[0]
                latest_url = latest_record.get("url", "Unknown")
                latest_timestamp = latest_record.get("timestamp", "Unknown")

                print(f"🕐 Latest Request: {latest_timestamp}")
                print(f"🌐 Latest URL: {latest_url}")

        else:
            print(f"🔴 Intelligence API: HTTP {intel_response.status_code}")

    except Exception as e:
        print(f"❌ Status check failed: {e}")


def main():
    """Main function with menu"""
    print("🔥 SHADOW PROXY REAL-TIME MONITOR")
    print("=" * 60)

    # Show current status
    show_proxy_status()
    print()

    # Make test request
    make_test_request()
    print()

    # Start monitoring
    monitor_requests()


if __name__ == "__main__":
    main()
