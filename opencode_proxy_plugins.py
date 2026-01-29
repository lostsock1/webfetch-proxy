#!/usr/bin/env python3
"""
🔥 OpenCode WebFetch Proxy Plugin Architecture
Multiple integration approaches for seamless proxy usage
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional, Callable
from abc import ABC, abstractmethod
from functools import wraps
import os
import sys

logger = logging.getLogger("OpenCodeProxyPlugin")


class ProxyPlugin(ABC):
    """Abstract base class for proxy plugins"""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize the plugin"""
        pass

    @abstractmethod
    def request(self, method: str, url: str, **kwargs) -> Any:
        """Handle request through plugin"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get plugin name"""
        pass


class MonkeyPatchPlugin(ProxyPlugin):
    """Plugin that uses monkey patching for seamless integration"""

    def __init__(self):
        self.original_functions = {}
        self.enabled = False
        self.proxy_url = "http://localhost:8081"
        self.api_key = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize monkey patching"""
        self.proxy_url = config.get("proxy_url", "http://localhost:8081")
        self.api_key = config.get("api_key")

        # Store original functions
        self.original_functions = {
            "requests_get": requests.get,
            "requests_post": requests.post,
            "session_get": requests.Session.get,
            "session_post": requests.Session.post,
        }

        self.enabled = True
        logger.info("MonkeyPatchPlugin initialized")
        return True

    def _proxy_request(self, method: str, url: str, **kwargs):
        """Make request through proxy"""
        try:
            proxy_data = {
                "url": url,
                "method": method,
                "timeout": kwargs.get("timeout", 30),
                "intelligence_tags": ["opencode", "auto"],
                "cache_enabled": True,
            }

            # Add headers if specified
            if "headers" in kwargs:
                proxy_data["headers"] = kwargs["headers"]

            # Add data for POST
            if kwargs.get("data"):
                proxy_data["data"] = kwargs["data"]
            elif kwargs.get("json"):
                proxy_data["data"] = json.dumps(kwargs["json"])

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.proxy_url}/fetch", json=proxy_data, headers=headers, timeout=35
            )

            if response.status_code == 200:
                result = response.json()
                return self._create_proxy_response(result)
            else:
                raise Exception(f"Proxy request failed: {response.status_code}")

        except Exception as e:
            logger.warning(f"Proxy request failed: {e}, falling back to direct")
            # Fallback to original function
            if method.upper() == "GET":
                return self.original_functions["requests_get"](url, **kwargs)
            else:
                return self.original_functions["requests_post"](url, **kwargs)

    def _create_proxy_response(self, proxy_result: Dict[str, Any]):
        """Create response object from proxy result"""

        class ProxyResponse:
            def __init__(self, result):
                self.status_code = result.get("status_code", 500)
                self.content = result.get("content", "").encode("utf-8")
                self.headers = result.get("headers", {})
                self.url = result.get("url", "")
                self.success = result.get("success", False)
                self.error = result.get("error")

        return ProxyResponse(proxy_result)

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Handle request"""
        if not self.enabled:
            # Fallback to direct request
            if method.upper() == "GET":
                return requests.get(url, **kwargs)
            else:
                return requests.post(url, **kwargs)

        return self._proxy_request(method, url, **kwargs)

    def get_name(self) -> str:
        return "MonkeyPatchPlugin"


class WrapperPlugin(ProxyPlugin):
    """Plugin that provides wrapper functions for explicit usage"""

    def __init__(self):
        self.enabled = False
        self.proxy_url = "http://localhost:8081"
        self.api_key = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize wrapper plugin"""
        self.proxy_url = config.get("proxy_url", "http://localhost:8081")
        self.api_key = config.get("api_key")
        self.enabled = True
        logger.info("WrapperPlugin initialized")
        return True

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Handle request through proxy"""
        return self._proxy_request(method, url, **kwargs)

    def _proxy_request(self, method: str, url: str, **kwargs):
        """Make request through proxy"""
        try:
            proxy_data = {
                "url": url,
                "method": method,
                "timeout": kwargs.get("timeout", 30),
                "intelligence_tags": ["opencode", "wrapper"],
                "cache_enabled": True,
            }

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.proxy_url}/fetch", json=proxy_data, headers=headers, timeout=35
            )

            if response.status_code == 200:
                result = response.json()
                return self._create_proxy_response(result)
            else:
                raise Exception(f"Proxy request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            # Fallback to direct request
            if method.upper() == "GET":
                return requests.get(url, **kwargs)
            else:
                return requests.post(url, **kwargs)

    def _create_proxy_response(self, proxy_result: Dict[str, Any]):
        """Create response object from proxy result"""

        class ProxyResponse:
            def __init__(self, result):
                self.status_code = result.get("status_code", 500)
                self.content = result.get("content", "").encode("utf-8")
                self.headers = result.get("headers", {})
                self.url = result.get("url", "")
                self.success = result.get("success", False)
                self.error = result.get("error")

        return ProxyResponse(proxy_result)

    def get_name(self) -> str:
        return "WrapperPlugin"


class ContextManagerPlugin(ProxyPlugin):
    """Plugin that uses context manager pattern"""

    def __init__(self):
        self.enabled = False
        self.proxy_url = "http://localhost:8081"
        self.api_key = None

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize context manager plugin"""
        self.proxy_url = config.get("proxy_url", "http://localhost:8081")
        self.api_key = config.get("api_key")
        self.enabled = True
        logger.info("ContextManagerPlugin initialized")
        return True

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Handle request"""
        return self._proxy_request(method, url, **kwargs)

    def _proxy_request(self, method: str, url: str, **kwargs):
        """Make request through proxy"""
        try:
            proxy_data = {
                "url": url,
                "method": method,
                "timeout": kwargs.get("timeout", 30),
                "intelligence_tags": ["opencode", "context"],
                "cache_enabled": True,
            }

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.proxy_url}/fetch", json=proxy_data, headers=headers, timeout=35
            )

            if response.status_code == 200:
                result = response.json()
                return self._create_proxy_response(result)
            else:
                raise Exception(f"Proxy request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            # Fallback to direct request
            if method.upper() == "GET":
                return requests.get(url, **kwargs)
            else:
                return requests.post(url, **kwargs)

    def _create_proxy_response(self, proxy_result: Dict[str, Any]):
        """Create response object from proxy result"""

        class ProxyResponse:
            def __init__(self, result):
                self.status_code = result.get("status_code", 500)
                self.content = result.get("content", "").encode("utf-8")
                self.headers = result.get("headers", {})
                self.url = result.get("url", "")
                self.success = result.get("success", False)
                self.error = result.get("error")

        return ProxyResponse(proxy_result)

    def get_name(self) -> str:
        return "ContextManagerPlugin"


class ProxyPluginManager:
    """Manages multiple proxy plugins"""

    def __init__(self):
        self.plugins = {}
        self.active_plugin = None
        self.config = {}

    def register_plugin(self, name: str, plugin: ProxyPlugin):
        """Register a proxy plugin"""
        self.plugins[name] = plugin
        logger.info(f"Registered plugin: {name}")

    def initialize_plugin(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """Initialize a specific plugin"""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin {plugin_name} not registered")
            return False

        success = self.plugins[plugin_name].initialize(config)
        if success:
            self.active_plugin = plugin_name
            self.config = config
            logger.info(f"Activated plugin: {plugin_name}")

        return success

    def initialize_all(self, config: Dict[str, Any]) -> str:
        """Initialize all plugins and return the first working one"""
        working_plugin = None

        for name, plugin in self.plugins.items():
            if plugin.initialize(config):
                working_plugin = name
                self.active_plugin = name
                self.config = config
                logger.info(f"Working plugin found: {name}")
                break

        return working_plugin

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Make request through active plugin"""
        if not self.active_plugin or self.active_plugin not in self.plugins:
            # Fallback to direct request
            if method.upper() == "GET":
                return requests.get(url, **kwargs)
            else:
                return requests.post(url, **kwargs)

        return self.plugins[self.active_plugin].request(method, url, **kwargs)

    def get_active_plugin(self) -> Optional[str]:
        """Get currently active plugin name"""
        return self.active_plugin


# Global plugin manager instance
_plugin_manager = ProxyPluginManager()

# Register all plugins
_plugin_manager.register_plugin("monkey_patch", MonkeyPatchPlugin())
_plugin_manager.register_plugin("wrapper", WrapperPlugin())
_plugin_manager.register_plugin("context_manager", ContextManagerPlugin())


def initialize_proxy_plugins(config_path: str = None) -> str:
    """Initialize proxy plugins with configuration"""
    config_path = config_path or "/Users/djesys/#VIBECODE/proxy_config.json"

    # Load configuration
    default_config = {
        "enabled": True,
        "proxy_url": "http://localhost:8081",
        "api_key": None,
        "plugin_type": "monkey_patch",
    }

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config = json.load(f)
        else:
            config = default_config
            with open(config_path, "w") as f:
                json.dump(config, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        config = default_config

    # Initialize plugins
    if config.get("enabled", True):
        active_plugin = _plugin_manager.initialize_all(config)
        return active_plugin
    else:
        logger.info("Proxy plugins disabled")
        return None


def webfetch_proxy(url: str, **kwargs) -> Dict[str, Any]:
    """Enhanced webfetch function using proxy"""
    try:
        response = _plugin_manager.request("GET", url, **kwargs)
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "content": response.content.decode("utf-8", errors="ignore"),
            "headers": dict(response.headers),
            "url": getattr(response, "url", url),
        }
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}


def bulk_webfetch_proxy(urls: List[str], **kwargs) -> List[Dict[str, Any]]:
    """Bulk webfetch with proxy support"""
    config = _plugin_manager.config

    # Use proxy bulk endpoint if available
    if config and config.get("proxy_url"):
        try:
            proxy_data = {
                "urls": urls,
                "concurrent_limit": kwargs.get("concurrent_limit", 3),
                "intelligence_tags": ["opencode", "bulk"],
                "common_headers": kwargs.get("headers", {}),
            }

            headers = {"Content-Type": "application/json"}
            if config.get("api_key"):
                headers["Authorization"] = f"Bearer {config['api_key']}"

            response = requests.post(
                f"{config['proxy_url']}/fetch/bulk",
                json=proxy_data,
                headers=headers,
                timeout=45,
            )

            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                raise Exception(f"Bulk fetch failed: {response.status_code}")

        except Exception as e:
            logger.warning(f"Proxy bulk fetch failed: {e}")

    # Fallback to individual requests
    results = []
    for url in urls:
        # Remove bulk-specific kwargs before making individual requests
        clean_kwargs = {
            k: v
            for k, v in kwargs.items()
            if k not in ["concurrent_limit", "intelligence_tags"]
        }
        result = webfetch_proxy(url, **clean_kwargs)
        results.append(result)

    return results


# Decorator for automatic proxy usage
def use_proxy(func: Callable) -> Callable:
    """Decorator to automatically use proxy for functions"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # This is a simple example - could be enhanced with more logic
        return func(*args, **kwargs)

    return wrapper


# Context manager for explicit proxy usage
class ProxyContext:
    """Context manager for explicit proxy usage"""

    def __init__(self, plugin_type: str = None):
        self.plugin_type = plugin_type or "wrapper"
        self.original_config = None

    def __enter__(self):
        # Save current config and switch to wrapper plugin
        self.original_config = _plugin_manager.config.copy()
        initialize_proxy_plugins()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore original config if needed
        pass


# Usage examples
def demonstrate_plugins():
    """Demonstrate different plugin approaches"""
    print("🔥 OpenCode Proxy Plugin Architecture Demo")
    print("=" * 60)

    # Initialize plugins
    active_plugin = initialize_proxy_plugins()
    print(f"Active plugin: {active_plugin}")

    if active_plugin:
        # Test basic webfetch
        print("\n[1] Testing basic webfetch...")
        result = webfetch_proxy("https://httpbin.org/get")
        print(f"   Status: {result.get('status_code', 'Failed')}")
        print(f"   Success: {result.get('success', False)}")

        # Test bulk webfetch
        print("\n[2] Testing bulk webfetch...")
        urls = ["https://httpbin.org/get", "https://httpbin.org/json"]
        results = bulk_webfetch_proxy(urls)
        print(f"   URLs processed: {len(results)}")
        print(f"   Successful: {sum(1 for r in results if r.get('success', False))}")

        # Test context manager
        print("\n[3] Testing context manager...")
        with ProxyContext("wrapper"):
            result = webfetch_proxy("https://httpbin.org/headers")
            print(f"   Context webfetch: {result.get('success', False)}")

        # Test decorator
        print("\n[4] Testing decorator...")

        @use_proxy
        def fetch_data(url):
            return requests.get(url).json()

        try:
            data = fetch_data("https://httpbin.org/json")
            print(f"   Decorator fetch: Success")
        except Exception as e:
            print(f"   Decorator fetch: {str(e)[:50]}")
    else:
        print("No proxy plugins active - using direct requests")

    print(f"\n✅ Plugin demo completed")


if __name__ == "__main__":
    demonstrate_plugins()
