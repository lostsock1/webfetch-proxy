#!/usr/bin/env python3
"""
🚀 COMPLETE PROXY INTEGRATION FOR OPENCODE
Exact steps to add proxy to your opencode startup
"""

print("🔥 PROXY INTEGRATION FOR OPENCODE")
print("=" * 50)

print("\n📍 STEP 1: Add to Your Main OpenCode File")
print("=" * 50)

print("\nFind your main opencode file (like main.py, app.py, etc.)")
print("Add these 2 lines at the very TOP:")

print("""
# Example: /Users/djesys/opencode/main.py
#!/usr/bin/env python3

# 🔥 PROXY INTEGRATION - Add these 2 lines FIRST
from opencode_proxy_plugins import initialize_proxy_plugins
proxy_status = initialize_proxy_plugins()

# Your existing imports below...
import requests
import json
# ... rest of your imports

def main():
    # Your existing opencode code...
    print("Starting opencode with proxy...")
    
    # Optional: Check if proxy is active
    if proxy_status:
        print(f"✅ Proxy active: {proxy_status}")
    else:
        print("⚠️ Using direct requests")
    
    # Your LLM code will now use proxy automatically!
    # No other changes needed
""")

print("\n📍 STEP 2: Start Proxy Automatically")
print("=" * 50)

print("\nMethod A: Manual Start (Recommended for testing)")
print("Run this command to start proxy:")
print("cd /Users/djesys/#VIBECODE/webfetch-prxy && ./start_proxy.sh")

print("\nMethod B: Auto-start via startup.py")
print("Create /Users/djesys/opencode/startup.py:")

print("""
# startup.py
def start_proxy_if_needed():
    try:
        import requests
        response = requests.get('http://localhost:8081/health', timeout=2)
        if response.status_code == 200:
            print('✅ Proxy already running')
            return True
    except:
        pass
    
    print('🚀 Starting proxy...')
    import subprocess
    import os
    
    proxy_path = '/Users/djesys/#VIBECODE/webfetch-prxy/webfetch_proxy.py'
    subprocess.Popen(['python3', proxy_path])
    
    # Wait a few seconds
    import time
    time.sleep(3)
    return True

if __name__ == '__main__':
    start_proxy_if_needed()
""")

print("\n📍 STEP 3: Modify Your Main OpenCode File")
print("=" * 50)

print("Modified main.py example:")
print("""
#!/usr/bin/env python3

# STEP 1: Auto-start proxy if needed
try:
    from startup import start_proxy_if_needed
    start_proxy_if_needed()
except:
    pass

# STEP 2: Initialize proxy integration  
from opencode_proxy_plugins import initialize_proxy_plugins
proxy_status = initialize_proxy_plugins()

# Your existing imports and code below...
import requests
# ... rest of your opencode code
""")

print("\n📍 STEP 4: Test Integration")
print("=" * 50)

print("Add this test code to verify it works:")
print("""
def test_proxy():
    # This will use proxy automatically
    try:
        response = requests.get('https://api.github.com/repos/python/cpython')
        print(f'✅ Proxy working: {response.status_code}')
        return True
    except Exception as e:
        print(f'❌ Proxy test failed: {e}')
        return False

# Call test_proxy() in your main function
""")

print("\n📍 STEP 5: Complete Integration Example")
print("=" * 50)

print("Full example of /Users/djesys/opencode/main.py:")
print("""
#!/usr/bin/env python3
'''
Main OpenCode Application
'''

# STEP 1: Auto-start proxy if needed
def ensure_proxy_running():
    try:
        import requests
        response = requests.get('http://localhost:8081/health', timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    
    # Start proxy
    import subprocess
    import os
    proxy_script = '/Users/djesys/#VIBECODE/webfetch-prxy/webfetch_proxy.py'
    subprocess.Popen(['python3', proxy_script])
    return True

# STEP 2: Initialize proxy
ensure_proxy_running()
from opencode_proxy_plugins import initialize_proxy_plugins
proxy_status = initialize_proxy_plugins()

# Your existing imports
import requests
import json

class OpenCodeLLM:
    def __init__(self):
        self.proxy_active = bool(proxy_status)
        print(f'OpenCode LLM ready (proxy: {self.proxy_active})')
    
    def web_query(self, query):
        '''This will automatically use proxy'''
        # LLM makes this request - proxy handles it automatically
        response = requests.get(f'https://api.github.com/search?q={query}')
        return response.json()
    
    def get_docs(self, topic):
        '''Documentation lookup - proxy handles automatically'''
        response = requests.get(f'https://docs.python.org/3/library/{topic}.html')
        return response.text

def main():
    print('🚀 Starting OpenCode with Proxy...')
    
    # Check proxy status
    if proxy_status:
        print(f'✅ Proxy integration active: {proxy_status}')
    else:
        print('⚠️ Using direct requests')
    
    # Initialize LLM
    llm = OpenCodeLLM()
    
    # Test web query
    print('🔍 Testing web query...')
    results = llm.web_query('python')
    print(f'Found {len(results.get("items", []))} results')
    
    # Test documentation
    print('📚 Testing documentation...')
    docs = llm.get_docs('asyncio')
    print(f'Documentation length: {len(docs)} chars')
    
    print('✅ OpenCode with proxy complete!')

if __name__ == '__main__':
    main()
""")

print("\n🎯 SUMMARY: Quick Integration")
print("=" * 50)
print("1. Add 2 lines to top of your main opencode file")
print("2. Optionally add auto-start function")
print("3. Test with a simple request")
print("4. Your LLM will use proxy automatically!")
print("\n🚀 That's it! Your opencode LLM now has unlimited online access!")
