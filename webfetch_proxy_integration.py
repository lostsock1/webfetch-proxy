#!/usr/bin/env python3
"""
🔥 OpenCode WebFetch Proxy Integration - VIBECODE
Comprehensive proxy integration for all webfetch operations
"""

import sys
import os
import requests
import json
import logging
import subprocess
import time
from typing import Dict, Any, List, Optional

# Add VIBECODE proxy to Python path
VIBECODE_PROXY_PATH = "/Users/djesys/#VIBECODE/webfetch-prxy"
if VIBECODE_PROXY_PATH not in sys.path:
    sys.path.insert(0, VIBECODE_PROXY_PATH)

logger = logging.getLogger("OpenCodeProxyIntegration")


class ProxyIntegration:
    """Main proxy integration class for OpenCode"""

    def __init__(self):
        self.enabled = False
        self.proxy_active = False
        self.original_requests = {}
        self.config = {}
        self._initialize_proxy()

    def _initialize_proxy(self):
        """Initialize the proxy integration"""
        try:
            # Try to import and initialize proxy plugins from VIBECODE
            from opencode_proxy_plugins import initialize_proxy_plugins

            # Configure proxy with authentication
            self.config = {
                "proxy_url": "http://localhost:8082",
                "api_key": "test-key",
                "enabled": True,
            }

            # Initialize plugins
            plugin_status = initialize_proxy_plugins()
            if plugin_status:
                self.enabled = True
                self.proxy_active = True
                logger.info(f"✅ Proxy integration active: {plugin_status}")
                return True
            else:
                logger.warning("⚠️  Proxy integration failed to initialize")
                return False

        except Exception as e:
            logger.error(f"❌ Proxy integration error: {e}")
            self.enabled = False
            self.proxy_active = False
            return False

    def ensure_proxy_running(self):
        """Ensure the proxy service is running"""
        if not self.proxy_active:
            return False

        try:
            import subprocess
            import time

            # Check if proxy is running
            response = requests.get("http://localhost:8082/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass

        # Start proxy if not running
        try:
            logger.info("🚀 Starting proxy service...")
            proxy_script = f"{VIBECODE_PROXY_PATH}/webfetch_proxy.py"
            subprocess.Popen(
                ["python3", proxy_script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            time.sleep(3)  # Wait for startup
            return True
        except Exception as e:
            logger.error(f"Failed to start proxy: {e}")
            return False

    def get_session(self):
        """Get a requests session with proxy support"""
        if self.proxy_active and self.enabled:
            # Use proxy-capable session
            from opencode_proxy_plugins import proxy_manager

            session = requests.Session()

            # Patch the session to use proxy
            original_get = session.get
            original_post = session.post

            def proxy_get(*args, **kwargs):
                try:
                    return proxy_manager.request("GET", *args, **kwargs)
                except:
                    return original_get(*args, **kwargs)

            def proxy_post(*args, **kwargs):
                try:
                    return proxy_manager.request("POST", *args, **kwargs)
                except:
                    return original_post(*args, **kwargs)

            session.get = proxy_get
            session.post = proxy_post

            return session
        else:
            # Use regular session
            return requests.Session()

    def fetch_url(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Fetch URL through proxy if available"""
        if self.proxy_active and self.enabled:
            try:
                from opencode_proxy_plugins import proxy_manager

                return proxy_manager.request(method.upper(), url, **kwargs)
            except Exception as e:
                logger.warning(f"Proxy request failed: {e}, falling back to direct")

        # Fallback to direct request
        if method.upper() == "GET":
            return requests.get(url, **kwargs)
        else:
            return requests.post(url, **kwargs)

    def bulk_fetch(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Bulk fetch URLs through proxy"""
        if self.proxy_active and self.enabled:
            try:
                from opencode_proxy_plugins import bulk_webfetch_proxy

                return bulk_webfetch_proxy(urls, **kwargs)
            except Exception as e:
                logger.warning(f"Proxy bulk fetch failed: {e}")

        # Fallback to individual requests
        results = []
        session = requests.Session()
        for url in urls:
            try:
                response = session.get(url, timeout=10, **kwargs)
                results.append(
                    {
                        "success": response.status_code < 400,
                        "status_code": response.status_code,
                        "content": response.text,
                        "headers": dict(response.headers),
                        "url": url,
                    }
                )
            except Exception as e:
                results.append({"success": False, "error": str(e), "url": url})

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get proxy integration status"""
        return {
            "enabled": self.enabled,
            "proxy_active": self.proxy_active,
            "config": self.config,
            "proxy_path": VIBECODE_PROXY_PATH,
        }


# Global proxy integration instance
proxy_integration = ProxyIntegration()


# Convenience functions for easy importing
def get_proxy_session():
    """Get a requests session with proxy support"""
    return proxy_integration.get_session()


def fetch_through_proxy(url: str, method: str = "GET", **kwargs):
    """Fetch URL through proxy"""
    return proxy_integration.fetch_url(url, method, **kwargs)


def bulk_fetch_proxy(urls: List[str], **kwargs):
    """Bulk fetch through proxy"""
    return proxy_integration.bulk_fetch(urls, **kwargs)


def ensure_proxy_running():
    """Ensure proxy service is running"""
    return proxy_integration.ensure_proxy_running()


def get_proxy_status():
    """Get proxy integration status"""
    return proxy_integration.get_status()


# Auto-initialize on import
if __name__ != "__main__":
    logger.info("🔥 OpenCode proxy integration loaded (VIBECODE)")
    status = get_proxy_status()
    if status["enabled"]:
        logger.info("✅ Proxy integration ready")
    else:
        logger.warning("⚠️  Using direct requests (proxy not available)")

if __name__ == "__main__":
    # Test the integration
    print("🔥 OpenCode WebFetch Proxy Integration Test (VIBECODE)")
    print("=" * 50)

    status = get_proxy_status()
    print(f"Enabled: {status['enabled']}")
    print(f"Proxy Active: {status['proxy_active']}")
    print(f"Config: {status['config']}")

    # Test basic fetch
    print("\n[1] Testing basic fetch...")
    try:
        result = fetch_through_proxy("https://httpbin.org/get")
        print(f"   Status: {result.status_code}")
        print(f"   Success: {result.status_code < 400}")
    except Exception as e:
        print(f"   Error: {e}")

    # Test bulk fetch
    print("\n[2] Testing bulk fetch...")
    try:
        urls = ["https://httpbin.org/get", "https://httpbin.org/json"]
        results = bulk_fetch_proxy(urls)
        print(f"   URLs processed: {len(results)}")
        successful = sum(1 for r in results if r.get("success", False))
        print(f"   Successful: {successful}/{len(results)}")
    except Exception as e:
        print(f"   Error: {e}")

    print("\n✅ Integration test completed")
