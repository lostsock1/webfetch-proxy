#!/usr/bin/env python3
"""
🔥 OpenCode WebFetch Proxy Integration Plugin
Seamlessly integrates webfetch proxy with opencode models
Handles blocking, agent emulation, and enhanced request capabilities
"""

import requests
import json
import time
import random
import logging
from typing import Dict, Any, Optional, Union, List
from urllib.parse import urljoin, urlparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path
import asyncio
import threading
from functools import wraps

# Configure logging
logger = logging.getLogger("OpenCodeProxy")


@dataclass
class ProxyConfig:
    """Configuration for proxy integration"""

    enabled: bool = True
    proxy_url: str = "http://localhost:8081"
    api_key: Optional[str] = None
    fallback_to_direct: bool = True
    max_retries: int = 3
    agent_rotation: bool = True
    intelligence_tags: List[str] = None
    timeout: int = 30


class OpenCodeProxySession:
    """
    Enhanced requests session with proxy integration
    Provides seamless proxy usage with fallback and agent emulation
    """

    def __init__(self, config: ProxyConfig = None):
        self.config = config or ProxyConfig()
        self.proxy_url = self.config.proxy_url
        self.api_key = self.config.api_key
        self.session = requests.Session()
        self.intelligence_tags = self.config.intelligence_tags or ["opencode", "auto"]

        # Agent rotation
        self.user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "SHADOW-OSINT-Bot/1.0 (Reconnaissance)",
            "SHADOW-Intelligence/2.0 (Cybersecurity)",
            "OpenCode-AI-Agent/1.0 (Language Model)",
            "Mozilla/5.0 (compatible; OpenCode-Crawler/1.0)",
        ]

        # Blocked domains that benefit from proxy
        self.blocked_domains = {
            "openai.com",
            "api.openai.com",
            "anthropic.com",
            "claude.ai",
            "google.com",
            "googleapis.com",
            "bing.com",
            "duckduckgo.com",
            "stackoverflow.com",
            "github.com",
            "api.github.com",
            "reddit.com",
            "api.reddit.com",
            "twitter.com",
            "api.twitter.com",
        }

        # Track proxy availability
        self.proxy_available = None
        self._check_proxy_availability()

        logger.info(f"OpenCode Proxy Session initialized: proxy={self.proxy_available}")

    def _check_proxy_availability(self):
        """Check if proxy is available"""
        try:
            response = requests.get(f"{self.proxy_url}/health", timeout=5)
            self.proxy_available = response.status_code == 200
            if self.proxy_available:
                logger.info("Proxy server is available")
            else:
                logger.warning("Proxy server not responding properly")
        except Exception as e:
            self.proxy_available = False
            logger.warning(f"Proxy server unavailable: {e}")

    def _get_random_user_agent(self) -> str:
        """Get random user agent for rotation"""
        return random.choice(self.user_agents)

    def _should_use_proxy(self, url: str) -> bool:
        """
        Determine if URL should use proxy
        Returns True for domains that often block AI/automated requests
        """
        try:
            domain = urlparse(url).netloc.lower()

            # Always use proxy for known blocked domains
            for blocked in self.blocked_domains:
                if blocked in domain:
                    return True

            # Use proxy for API endpoints
            if "/api/" in url or "api." in domain:
                return True

            # Use proxy for authenticated requests
            return True

        except Exception:
            return True  # Default to proxy for safety

    def _make_proxy_request(self, url: str, **kwargs) -> requests.Response:
        """Make request through proxy"""
        try:
            # Prepare proxy request
            proxy_data = {
                "url": url,
                "method": kwargs.get("method", "GET"),
                "timeout": kwargs.get("timeout", self.config.timeout),
                "follow_redirects": kwargs.get("allow_redirects", True),
                "verify_ssl": kwargs.get("verify", True),
                "intelligence_tags": self.intelligence_tags,
                "cache_enabled": True,
            }

            # Add headers
            if "headers" in kwargs:
                proxy_data["headers"] = kwargs["headers"]
            elif self.config.agent_rotation:
                proxy_data["user_agent"] = self._get_random_user_agent()

            # Add data for POST requests
            if kwargs.get("data"):
                proxy_data["data"] = kwargs["data"]
            elif kwargs.get("json"):
                proxy_data["data"] = json.dumps(kwargs["json"])

            # Make request through proxy
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.proxy_url}/fetch",
                json=proxy_data,
                headers=headers,
                timeout=self.config.timeout + 10,
            )

            # Convert proxy response to requests Response
            if response.status_code == 200:
                proxy_result = response.json()

                # Create fake response object
                class ProxyResponse:
                    def __init__(self, result):
                        self.status_code = result.get("status_code", 500)
                        self.content = result.get("content", "").encode("utf-8")
                        self.headers = result.get("headers", {})
                        self.url = result.get("url", url)
                        self.final_url = result.get("final_url", url)
                        self.success = result.get("success", False)
                        self.error = result.get("error")

                return ProxyResponse(proxy_result)
            else:
                raise Exception(f"Proxy request failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Proxy request failed: {e}")
            raise

    def request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Enhanced request method with proxy integration
        Automatically chooses between proxy and direct requests
        """
        # Check if we should use proxy
        use_proxy = self._should_use_proxy(url) and self.config.enabled

        if use_proxy and self.proxy_available:
            try:
                logger.debug(f"Using proxy for: {url}")
                return self._make_proxy_request(url, method=method, **kwargs)
            except Exception as e:
                logger.warning(f"Proxy request failed, falling back to direct: {e}")

                if not self.config.fallback_to_direct:
                    raise
        else:
            logger.debug(f"Using direct request for: {url}")

        # Add user agent for direct requests
        if self.config.agent_rotation:
            kwargs.setdefault("headers", {})
            if "User-Agent" not in kwargs["headers"]:
                kwargs["headers"]["User-Agent"] = self._get_random_user_agent()

        # Make direct request
        return self.session.request(method, url, **kwargs)

    def get(self, url: str, **kwargs) -> requests.Response:
        """Enhanced GET request"""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Enhanced POST request"""
        return self.request("POST", url, **kwargs)

    def bulk_fetch(self, urls: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Bulk fetch multiple URLs through proxy"""
        if not self.proxy_available or not self.config.enabled:
            # Fallback to individual requests
            results = []
            for url in urls:
                try:
                    response = self.get(url, **kwargs)
                    results.append(
                        {
                            "url": url,
                            "success": response.status_code < 400,
                            "status_code": response.status_code,
                            "content": response.content.decode(
                                "utf-8", errors="ignore"
                            ),
                            "headers": dict(response.headers),
                        }
                    )
                except Exception as e:
                    results.append({"url": url, "success": False, "error": str(e)})
            return results

        try:
            # Use proxy bulk endpoint
            proxy_data = {
                "urls": urls,
                "concurrent_limit": kwargs.get("concurrent_limit", 3),
                "intelligence_tags": self.intelligence_tags,
                "common_headers": kwargs.get("headers", {}),
            }

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            response = requests.post(
                f"{self.proxy_url}/fetch/bulk",
                json=proxy_data,
                headers=headers,
                timeout=self.config.timeout + 20,
            )

            if response.status_code == 200:
                return response.json().get("results", [])
            else:
                raise Exception(f"Bulk fetch failed: {response.status_code}")

        except Exception as e:
            logger.error(f"Bulk fetch failed: {e}")
            # Fallback to individual requests
            return self.bulk_fetch(urls, **{**kwargs, **{"concurrent_limit": 1}})


# Global proxy session instance
_global_proxy_session = None


def get_proxy_session(config: ProxyConfig = None) -> OpenCodeProxySession:
    """Get global proxy session instance"""
    global _global_proxy_session
    if _global_proxy_session is None:
        _global_proxy_session = OpenCodeProxySession(config)
    return _global_proxy_session


# Monkey patch for seamless integration
def patch_requests():
    """
    Monkey patch requests module for seamless proxy integration
    This allows existing opencode code to use proxy without modifications
    """
    global requests

    original_get = requests.get
    original_post = requests.post
    original_session_get = requests.Session.get
    original_session_post = requests.Session.post

    def proxy_get(url: str, **kwargs):
        session = get_proxy_session()
        return session.get(url, **kwargs)

    def proxy_post(url: str, **kwargs):
        session = get_proxy_session()
        return session.post(url, **kwargs)

    def proxy_session_get(self, url: str, **kwargs):
        session = get_proxy_session()
        return session.get(url, **kwargs)

    def proxy_session_post(self, url: str, **kwargs):
        session = get_proxy_session()
        return session.post(url, **kwargs)

    # Apply patches
    requests.get = proxy_get
    requests.post = proxy_post
    requests.Session.get = proxy_session_get
    requests.Session.post = proxy_session_post

    logger.info("Requests module patched for proxy integration")


# Convenience functions
def webfetch_with_proxy(url: str, tags: List[str] = None, **kwargs) -> Dict[str, Any]:
    """
    Enhanced webfetch function that uses proxy
    Drop-in replacement for direct webfetch operations
    """
    session = get_proxy_session()

    if tags:
        session.intelligence_tags = tags

    try:
        response = session.get(url, **kwargs)
        return {
            "success": response.status_code < 400,
            "status_code": response.status_code,
            "content": response.content.decode("utf-8", errors="ignore"),
            "headers": dict(response.headers),
            "url": response.url,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "url": url}


def bulk_webfetch(
    urls: List[str], tags: List[str] = None, **kwargs
) -> List[Dict[str, Any]]:
    """
    Bulk webfetch with proxy support
    """
    session = get_proxy_session()

    if tags:
        session.intelligence_tags = tags

    return session.bulk_fetch(urls, **kwargs)


# Configuration management
def load_proxy_config(config_path: str = None) -> ProxyConfig:
    """
    Load proxy configuration from file or environment
    """
    config_path = config_path or "/Users/djesys/#VIBECODE/proxy_config.json"

    default_config = ProxyConfig()

    try:
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                config_data = json.load(f)
                return ProxyConfig(**config_data)
        else:
            # Create default config file
            with open(config_path, "w") as f:
                json.dump(
                    {
                        "enabled": default_config.enabled,
                        "proxy_url": default_config.proxy_url,
                        "api_key": default_config.api_key,
                        "fallback_to_direct": default_config.fallback_to_direct,
                        "max_retries": default_config.max_retries,
                        "agent_rotation": default_config.agent_rotation,
                        "intelligence_tags": default_config.intelligence_tags,
                        "timeout": default_config.timeout,
                    },
                    f,
                    indent=2,
                )
            return default_config
    except Exception as e:
        logger.warning(f"Failed to load config: {e}, using defaults")
        return default_config


# Auto-initialization
def initialize_proxy_integration():
    """Initialize proxy integration for opencode"""
    config = load_proxy_config()

    if config.enabled:
        patch_requests()
        logger.info("OpenCode proxy integration initialized")
    else:
        logger.info("OpenCode proxy integration disabled")


# Usage examples and testing
def demonstrate_integration():
    """Demonstrate proxy integration functionality"""
    print("🔥 OpenCode Proxy Integration Demo")
    print("=" * 50)

    # Initialize integration
    config = ProxyConfig(
        enabled=True, agent_rotation=True, intelligence_tags=["demo", "integration"]
    )

    session = OpenCodeProxySession(config)

    print(f"Proxy available: {session.proxy_available}")
    print(f"Configuration: enabled={config.enabled}")

    # Test direct request
    print("\n[1] Testing direct webfetch...")
    result = webfetch_with_proxy("https://httpbin.org/get", tags=["test"])
    print(f"   Status: {result['status_code'] if result['success'] else 'Failed'}")

    # Test bulk fetch
    print("\n[2] Testing bulk fetch...")
    urls = ["https://httpbin.org/get", "https://httpbin.org/json"]
    results = bulk_webfetch(urls, tags=["bulk_test"])
    print(f"   Processed: {len(results)} URLs")
    print(f"   Successful: {sum(1 for r in results if r.get('success'))}")

    # Test proxy decision making
    print("\n[3] Testing proxy decision logic...")
    test_urls = [
        "https://api.openai.com/v1/models",
        "https://google.com",
        "https://example.com",
    ]

    for url in test_urls:
        should_proxy = session._should_use_proxy(url)
        print(f"   {url}: {'Proxy' if should_proxy else 'Direct'}")


if __name__ == "__main__":
    demonstrate_integration()
