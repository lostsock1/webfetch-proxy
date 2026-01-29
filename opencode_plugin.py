#!/usr/bin/env python3
"""
OpenCode WebFetch Proxy Plugin
Implements a proper OpenCode plugin that intercepts webfetch operations.
"""

import sys
import os
import json
import time
import logging
import threading
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/opencode-webfetch-plugin.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("OpenCodeWebFetchPlugin")


class OpenCodeWebFetchPlugin:
    """
    OpenCode Plugin for webfetch proxy integration.

    This plugin provides:
    1. Automatic interception of webfetch operations
    2. Proxy routing for all web requests
    3. Intelligence gathering and logging
    4. Cache optimization
    5. Graceful fallback to direct requests
    """

    PLUGIN_NAME = "webfetch-proxy"
    PLUGIN_VERSION = "1.0.0"

    def __init__(self, config_path: str = None):
        """Initialize the OpenCode webfetch proxy plugin"""
        self.config_path = (
            config_path or "/Users/djesys/#VIBECODE/webfetch-prxy/config.yaml"
        )
        self.config = self._load_config()

        # Plugin state
        self.enabled = False
        self.proxy_url = "http://localhost:8082"
        self.api_key = None
        self.fallback_enabled = True

        # Request tracking
        self.request_count = 0
        self.cache_hits = 0
        self.blocked_requests = []
        self.lock = threading.Lock()

        # Original webfetch function reference
        self._original_webfetch = None

        logger.info("OpenCode WebFetch Plugin initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load plugin configuration"""
        default_config = {
            "enabled": True,
            "proxy_url": "http://localhost:8082",
            "api_key": None,
            "fallback_enabled": True,
            "intelligence": {
                "enabled": True,
                "storage_path": "intelligence",
                "auto_tagging": True,
            },
            "caching": {
                "enabled": True,
                "ttl": 3600,
                "redis_url": "redis://localhost:6379/0",
            },
            "security": {"blocked_domains": [], "allowed_domains": []},
        }

        try:
            if os.path.exists(self.config_path):
                import yaml

                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f) or default_config
                return config
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")

        return default_config

    def enable(self) -> bool:
        """Enable the plugin and start intercepting webfetch operations"""
        try:
            self.enabled = True
            self.proxy_url = self.config.get("proxy_url", "http://localhost:8082")
            # Use config API key or fall back to default "test-key"
            self.api_key = self.config.get("api_key") or "test-key"
            self.fallback_enabled = self.config.get("fallback_enabled", True)

            # Register as OpenCode plugin
            self._register_plugin()

            logger.info(
                f"OpenCode WebFetch Plugin enabled with proxy: {self.proxy_url}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to enable plugin: {e}")
            return False

    def disable(self) -> bool:
        """Disable the plugin and stop intercepting"""
        try:
            self.enabled = False
            self._unregister_plugin()
            logger.info("OpenCode WebFetch Plugin disabled")
            return True
        except Exception as e:
            logger.error(f"Failed to disable plugin: {e}")
            return False

    def _register_plugin(self):
        """Register plugin with OpenCode system"""
        # Store original webfetch if not already stored
        if self._original_webfetch is None:
            try:
                # Try to get OpenCode's webfetch function
                import builtins

                if hasattr(builtins, "webfetch"):
                    self._original_webfetch = builtins.webfetch
                    logger.info("Captured original webfetch function")
            except Exception as e:
                logger.warning(f"Could not capture original webfetch: {e}")

    def _unregister_plugin(self):
        """Unregister plugin from OpenCode system"""
        if self._original_webfetch is not None:
            try:
                import builtins

                builtins.webfetch = self._original_webfetch
                logger.info("Restored original webfetch function")
            except Exception as e:
                logger.warning(f"Could not restore original webfetch: {e}")

    def webfetch(self, url: str, **kwargs) -> Dict[str, Any]:
        """
        Main webfetch function that routes requests through the proxy.

        Args:
            url: URL to fetch
            **kwargs: Additional arguments (headers, timeout, method, etc.)

        Returns:
            Dict with success, content, headers, etc.
        """
        if not self.enabled:
            return self._direct_fetch(url, **kwargs)

        with self.lock:
            self.request_count += 1

        # Check if proxy is available
        if not self._is_proxy_available():
            if self.fallback_enabled:
                logger.info(f"Proxy unavailable, using direct fetch for {url}")
                return self._direct_fetch(url, **kwargs)
            else:
                return {
                    "success": False,
                    "error": "Proxy unavailable and fallback disabled",
                    "url": url,
                }

        # Check domain restrictions
        if not self._is_domain_allowed(url):
            self._log_blocked_request(url, kwargs, "Domain not allowed")
            return {
                "success": False,
                "error": "Domain blocked by security policy",
                "url": url,
                "blocked": True,
            }

        # Check cache
        cache_key = self._generate_cache_key(url, kwargs)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            with self.lock:
                self.cache_hits += 1
            logger.info(f"Cache hit for {url}")
            return cached_result

        # Make request through proxy
        return self._proxy_fetch(url, cache_key, **kwargs)

    def _is_proxy_available(self) -> bool:
        """Check if proxy server is available"""
        try:
            health_url = f"{self.proxy_url}/health"
            response = requests.get(health_url, timeout=2)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Proxy health check failed: {e}")
            return False

    def _is_domain_allowed(self, url: str) -> bool:
        """Check if domain is allowed by security policy"""
        try:
            from urllib.parse import urlparse

            domain = urlparse(url).netloc.lower()

            # Check blocked domains
            blocked = self.config.get("security", {}).get("blocked_domains", [])
            if any(b in domain for b in blocked):
                return False

            # Check allowed domains
            allowed = self.config.get("security", {}).get("allowed_domains", [])
            if allowed and not any(a in domain for a in allowed):
                return False

            return True
        except Exception:
            return True  # Allow by default if check fails

    def _generate_cache_key(self, url: str, kwargs: Dict) -> str:
        """Generate cache key for request"""
        import hashlib

        content = f"{url}:{str(sorted(kwargs.items()))}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        if not self.config.get("caching", {}).get("enabled", True):
            return None

        try:
            import redis

            redis_url = self.config.get("caching", {}).get(
                "redis_url", "redis://localhost:6379/0"
            )
            r = redis.Redis.from_url(redis_url)
            cached = r.get(f"webfetch:{cache_key}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")

        return None

    def _cache_result(self, cache_key: str, result: Dict[str, Any], ttl: int = 3600):
        """Cache the result"""
        if not self.config.get("caching", {}).get("enabled", True):
            return

        try:
            import redis
            import json

            redis_url = self.config.get("caching", {}).get(
                "redis_url", "redis://localhost:6379/0"
            )
            r = redis.Redis.from_url(redis_url)
            r.setex(f"webfetch:{cache_key}", ttl, json.dumps(result))
        except Exception as e:
            logger.debug(f"Cache storage failed: {e}")

    def _log_blocked_request(self, url: str, kwargs: Dict, reason: str):
        """Log blocked request for intelligence"""
        with self.lock:
            self.blocked_requests.append(
                {
                    "timestamp": time.time(),
                    "url": url,
                    "reason": reason,
                    "kwargs": kwargs,
                }
            )

        # Log to file
        try:
            intelligence_dir = Path(
                self.config.get("intelligence", {}).get("storage_path", "intelligence")
            )
            blocked_file = intelligence_dir / "blocked_opencode_requests.json"

            blocked_data = []
            if blocked_file.exists():
                with open(blocked_file, "r") as f:
                    blocked_data = json.load(f)

            blocked_data.append(
                {
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "url": url,
                    "reason": reason,
                    "kwargs": kwargs,
                }
            )

            # Keep last 1000
            blocked_data = blocked_data[-1000:]

            with open(blocked_file, "w") as f:
                json.dump(blocked_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to log blocked request: {e}")

    def _proxy_fetch(self, url: str, cache_key: str, **kwargs) -> Dict[str, Any]:
        """Fetch URL through proxy"""
        try:
            # Prepare proxy request
            proxy_data = {
                "url": url,
                "method": kwargs.get("method", "GET"),
                "timeout": kwargs.get("timeout", 30),
                "cache_enabled": True,
                "intelligence_tags": ["opencode", "plugin"],
            }

            # Add headers
            if "headers" in kwargs:
                proxy_data["headers"] = kwargs["headers"]

            # Add data for POST
            if "data" in kwargs:
                proxy_data["data"] = kwargs["data"]
            elif "json" in kwargs:
                proxy_data["data"] = json.dumps(kwargs["json"])

            # Prepare headers
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            # Make proxy request
            response = requests.post(
                f"{self.proxy_url}/fetch",
                json=proxy_data,
                headers=headers,
                timeout=kwargs.get("timeout", 30) + 5,
            )

            if response.status_code == 200:
                result = response.json()

                # Cache successful response
                if result.get("success"):
                    self._cache_result(cache_key, result)

                return result
            else:
                error_msg = f"Proxy request failed: {response.status_code}"
                logger.warning(error_msg)

                if self.fallback_enabled:
                    return self._direct_fetch(url, **kwargs)
                else:
                    return {"success": False, "error": error_msg, "url": url}

        except Exception as e:
            error_msg = f"Proxy fetch error: {str(e)}"
            logger.warning(f"{error_msg} for {url}")

            if self.fallback_enabled:
                return self._direct_fetch(url, **kwargs)
            else:
                return {"success": False, "error": error_msg, "url": url}

    def _direct_fetch(self, url: str, **kwargs) -> Dict[str, Any]:
        """Direct fetch without proxy"""
        try:
            start_time = time.time()

            # Prepare request
            timeout = kwargs.get("timeout", 30)
            headers = kwargs.get("headers", {})
            method = kwargs.get("method", "GET")
            data = kwargs.get("data")
            json_data = kwargs.get("json")

            # Make direct request
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=timeout, **kwargs)
            else:
                if json_data:
                    response = requests.post(
                        url, json=json_data, headers=headers, timeout=timeout, **kwargs
                    )
                else:
                    response = requests.request(
                        method,
                        url,
                        data=data,
                        headers=headers,
                        timeout=timeout,
                        **kwargs,
                    )

            result = {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "content": response.text,
                "headers": dict(response.headers),
                "url": url,
                "execution_time": time.time() - start_time,
                "cached": False,
                "direct": True,
            }

            return result

        except Exception as e:
            return {"success": False, "error": str(e), "url": url, "direct": True}

    def bulk_webfetch(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Bulk webfetch through proxy"""
        results = []
        concurrent_limit = kwargs.get("concurrent_limit", 3)

        import asyncio

        async def fetch_url(url: str) -> Dict[str, Any]:
            return self.webfetch(url, **kwargs)

        # Process URLs with semaphore for concurrency control
        async def process_urls():
            semaphore = asyncio.Semaphore(concurrent_limit)

            async def fetch_with_limit(url: str):
                async with semaphore:
                    return await fetch_url(url)

            tasks = [fetch_with_limit(url) for url in urls]
            return await asyncio.gather(*tasks)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(process_urls())
            loop.close()
        except Exception as e:
            logger.error(f"Bulk fetch error: {e}")
            # Fallback to sequential
            for url in urls:
                results.append(self.webfetch(url, **kwargs))

        return results

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status"""
        return {
            "plugin": self.PLUGIN_NAME,
            "version": self.PLUGIN_VERSION,
            "enabled": self.enabled,
            "proxy_url": self.proxy_url,
            "request_count": self.request_count,
            "cache_hits": self.cache_hits,
            "fallback_enabled": self.fallback_enabled,
            "cache_hit_rate": (self.cache_hits / self.request_count * 100)
            if self.request_count > 0
            else 0,
        }

    def get_blocked_requests(self, limit: int = 50) -> List[Dict]:
        """Get blocked requests"""
        with self.lock:
            return self.blocked_requests[-limit:]


# Global plugin instance
_plugin_instance = None


def get_plugin() -> OpenCodeWebFetchPlugin:
    """Get the global plugin instance"""
    global _plugin_instance
    if _plugin_instance is None:
        _plugin_instance = OpenCodeWebFetchPlugin()
    return _plugin_instance


def initialize_plugin(config_path: str = None) -> bool:
    """Initialize the OpenCode webfetch proxy plugin"""
    plugin = get_plugin()
    return plugin.enable()


def webfetch(url: str, **kwargs) -> Dict[str, Any]:
    """OpenCode-compatible webfetch function with proxy support"""
    plugin = get_plugin()
    return plugin.webfetch(url, **kwargs)


def bulk_webfetch(urls: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Bulk webfetch through proxy"""
    plugin = get_plugin()
    return plugin.bulk_webfetch(urls, **kwargs)


def get_plugin_status() -> Dict[str, Any]:
    """Get plugin status"""
    plugin = get_plugin()
    return plugin.get_status()


def enable_plugin() -> bool:
    """Enable the plugin"""
    plugin = get_plugin()
    return plugin.enable()


def disable_plugin() -> bool:
    """Disable the plugin"""
    plugin = get_plugin()
    return plugin.disable()


# Example usage and testing
if __name__ == "__main__":
    print("OpenCode WebFetch Plugin - Test")
    print("=" * 50)

    # Initialize plugin
    success = initialize_plugin()
    print(f"Plugin initialized: {success}")

    # Get status
    status = get_plugin_status()
    print(f"Status: {json.dumps(status, indent=2)}")

    # Test single fetch
    print("\n[1] Testing single fetch...")
    result = webfetch("https://httpbin.org/get")
    print(f"   Success: {result.get('success')}")
    print(f"   Status: {result.get('status_code')}")

    # Test bulk fetch
    print("\n[2] Testing bulk fetch...")
    urls = [
        "https://httpbin.org/get",
        "https://httpbin.org/json",
        "https://httpbin.org/html",
    ]
    results = bulk_webfetch(urls)
    successful = sum(1 for r in results if r.get("success"))
    print(f"   Successful: {successful}/{len(results)}")

    # Final status
    status = get_plugin_status()
    print(f"\nFinal Status: {json.dumps(status, indent=2)}")

    print("\n✅ Plugin test completed")
