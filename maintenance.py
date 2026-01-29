#!/usr/bin/env python3
'''
Housekeeping script for SHADOW Proxy
'''
import requests
import json
import subprocess
import time

def run_housekeeping():
    print("🧹 Running proxy housekeeping...")
    
    try:
        # Clean up obsolete files
        response = requests.post("http://localhost:8081/housekeeping/cleanup", timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Housekeeping complete")
            print(f"   Intelligence files deleted: {result.get('intelligence_cleanup', {}).get('deleted', 0)}")
            print(f"   Log files rotated: {result.get('log_rotation', {}).get('rotated', 0)}")
        else:
            print(f"❌ Housekeeping failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Housekeeping error: {e}")

def check_blocked_requests():
    print("🔍 Checking blocked requests...")
    
    try:
        response = requests.get("http://localhost:8081/blocked/requests?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total', 0)
            recent = data.get('recent_count', 0)
            
            print(f"📊 Blocked requests summary:")
            print(f"   Total: {total}")
            print(f"   Recent: {recent}")
            
            if recent > 0:
                print("   Recent blocked:")
                for req in data.get('blocked_requests', [])[-3:]:
                    print(f"      {req.get('reason', 'Unknown')}: {req.get('url', 'Unknown')[:50]}")
        else:
            print(f"❌ Blocked requests check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Blocked requests error: {e}")

if __name__ == "__main__":
    run_housekeeping()
    check_blocked_requests()
