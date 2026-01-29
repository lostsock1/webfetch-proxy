#!/usr/bin/env python3
"""
🔥 REAL-TIME PROXY MONITOR
Monitor proxied requests in real-time with various viewing options
"""

import requests
import json
import time
import subprocess
from datetime import datetime


def monitor_intelligence_api():
    """Monitor proxy intelligence API in real-time"""
    print("🔥 REAL-TIME PROXY INTELLIGENCE MONITOR")
    print("=" * 60)
    print("Watching for new proxied requests...")
    print("Press Ctrl+C to stop\n")

    seen_urls = set()

    try:
        while True:
            try:
                # Get latest intelligence records
                response = requests.get(
                    "http://localhost:8081/intelligence/list?limit=20"
                )
                if response.status_code == 200:
                    data = response.json()
                    records = data.get("records", [])

                    # Show new records
                    new_records = []
                    for record in records:
                        url = record.get("url", "")
                        if url not in seen_urls and url:
                            seen_urls.add(url)
                            new_records.append(record)

                    if new_records:
                        print(
                            f"🕐 {datetime.now().strftime('%H:%M:%S')} - NEW REQUESTS:"
                        )
                        for record in reversed(new_records[-5:]):  # Show last 5
                            url = record.get("url", "Unknown")
                            tags = record.get("tags", [])
                            timestamp = record.get("timestamp", "")
                            size = record.get("metadata", {}).get("size", 0)

                            # Show domain for quick reference
                            domain = url.split("/")[2] if "://" in url else "Unknown"

                            print(f"   🌐 {domain}")
                            print(f"      URL: {url}")
                            print(f"      Tags: {', '.join(tags) if tags else 'None'}")
                            print(f"      Size: {size} bytes")
                            print(f"      Time: {timestamp}")
                            print()

                    print(f"📊 Total records: {data.get('total_records', 0)}", end="\r")

                time.sleep(2)  # Check every 2 seconds

            except requests.exceptions.RequestException as e:
                print(f"❌ Connection error: {e}")
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")


def monitor_proxy_logs():
    """Monitor proxy logs in real-time"""
    print("🔥 REAL-TIME PROXY LOG MONITOR")
    print("=" * 60)
    print("Following proxy logs...")
    print("Press Ctrl+C to stop\n")

    try:
        # Follow the proxy log file
        subprocess.run(["tail", "-f", "/Users/djesys/#VIBECODE/logs/proxy.log"])
    except KeyboardInterrupt:
        print("\n\n⏹️  Log monitoring stopped")


def monitor_proxy_health():
    """Monitor proxy health and statistics"""
    print("🔥 PROXY HEALTH MONITOR")
    print("=" * 60)
    print("Monitoring proxy health...")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            try:
                # Check health
                response = requests.get("http://localhost:8081/health", timeout=3)

                if response.status_code == 200:
                    health = response.json()
                    status = health.get("status", "unknown")

                    # Get intelligence count
                    intel_response = requests.get(
                        "http://localhost:8081/intelligence/list?limit=1", timeout=3
                    )
                    intel_count = 0
                    if intel_response.status_code == 200:
                        intel_data = intel_response.json()
                        intel_count = intel_data.get("total_records", 0)

                    # Clear line and print status
                    print(
                        f"\r🟢 Proxy: {status.upper()} | Records: {intel_count} | Time: {datetime.now().strftime('%H:%M:%S')}",
                        end="",
                        flush=True,
                    )

                else:
                    print(
                        f"\r🔴 Proxy: ERROR {response.status_code} | Time: {datetime.now().strftime('%H:%M:%S')}",
                        end="",
                        flush=True,
                    )

                time.sleep(3)

            except requests.exceptions.RequestException as e:
                print(
                    f"\r🔴 Proxy: OFFLINE ({str(e)[:30]}...) | Time: {datetime.now().strftime('%H:%M:%S')}",
                    end="",
                    flush=True,
                )
                time.sleep(5)

    except KeyboardInterrupt:
        print("\n\n⏹️  Health monitoring stopped")


def show_recent_requests():
    """Show recent proxied requests in a formatted table"""
    print("🔥 RECENT PROXIED REQUESTS")
    print("=" * 80)

    try:
        response = requests.get("http://localhost:8081/intelligence/list?limit=15")
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])

            print(f"{'Time':<8} {'Domain':<25} {'Tags':<20} {'Size':<8} {'URL'}")
            print("-" * 80)

            for record in records:
                timestamp = record.get("timestamp", "")
                time_str = timestamp.split(" ")[1] if " " in timestamp else timestamp

                url = record.get("url", "")
                domain = url.split("/")[2] if "://" in url else "Unknown"
                if len(domain) > 25:
                    domain = domain[:22] + "..."

                tags = record.get("tags", [])
                tags_str = ",".join(tags) if tags else ""
                if len(tags_str) > 20:
                    tags_str = tags_str[:17] + "..."

                size = record.get("metadata", {}).get("size", 0)
                size_str = f"{size // 1024}KB" if size > 1024 else f"{size}B"

                # Truncate URL for display
                display_url = url
                if len(display_url) > 30:
                    display_url = display_url[:27] + "..."

                print(
                    f"{time_str:<8} {domain:<25} {tags_str:<20} {size_str:<8} {display_url}"
                )

            print(f"\n📊 Total intelligence records: {data.get('total_records', 0)}")

        else:
            print(f"❌ Failed to get intelligence data: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {e}")


def monitor_bulk_requests():
    """Monitor bulk request processing"""
    print("🔥 BULK REQUEST MONITOR")
    print("=" * 60)
    print("Simulating bulk requests to see real-time processing...\n")

    # Make several requests to see them appear in intelligence
    test_urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json",
        "https://httpbin.org/headers",
        "https://httpbin.org/user-agent",
        "https://httpbin.org/ip",
    ]

    for i, url in enumerate(test_urls, 1):
        print(f"[{i}/5] Making request to: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"      ✅ Status: {response.status_code}")

            # Check if it appears in intelligence immediately
            time.sleep(1)
            intel_response = requests.get(
                "http://localhost:8081/intelligence/list?limit=5"
            )
            if intel_response.status_code == 200:
                intel_data = intel_response.json()
                latest_url = intel_data.get("records", [{}])[0].get("url", "")
                if url in latest_url:
                    print(f"      🧠 Appeared in intelligence: ✅")
                else:
                    print(f"      🧠 Appeared in intelligence: ⏳")

        except Exception as e:
            print(f"      ❌ Error: {str(e)[:50]}")

        time.sleep(0.5)

    print(f"\n✅ Bulk monitoring complete!")
    print(f"📊 Check intelligence API for full results")


def main():
    """Main menu for real-time monitoring options"""
    print("🔥 SHADOW PROXY REAL-TIME MONITORING")
    print("=" * 60)
    print("Choose monitoring option:")
    print()
    print("1. 📊 Intelligence API Monitor (real-time)")
    print("2. 📋 Recent Requests Table")
    print("3. ❤️  Health Monitor")
    print("4. 📝 Log Monitor (follows proxy.log)")
    print("5. 🧪 Bulk Request Test")
    print("6. 🔄 Auto-refresh Intelligence (every 5s)")
    print()

    try:
        choice = input("Select option (1-6): ").strip()

        if choice == "1":
            monitor_intelligence_api()
        elif choice == "2":
            show_recent_requests()
        elif choice == "3":
            monitor_proxy_health()
        elif choice == "4":
            monitor_proxy_logs()
        elif choice == "5":
            monitor_bulk_requests()
        elif choice == "6":
            # Auto-refresh intelligence every 5 seconds
            print("\n🔄 Auto-refreshing intelligence every 5 seconds...")
            print("Press Ctrl+C to stop\n")

            try:
                while True:
                    # Clear screen
                    subprocess.run(["clear"], check=False)

                    show_recent_requests()
                    print(
                        f"\n🕐 Last updated: {datetime.now().strftime('%H:%M:%S')} | Press Ctrl+C to stop"
                    )
                    time.sleep(5)

            except KeyboardInterrupt:
                print("\n\n⏹️  Auto-refresh stopped")
        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n\n⏹️  Monitoring stopped")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
