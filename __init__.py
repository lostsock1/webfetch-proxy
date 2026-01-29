#!/usr/bin/env python3
"""
🔥 VIBECODE WebFetch Proxy Package
OpenCode-compatible webfetch proxy with intelligence gathering
"""

__version__ = "1.0.0"
__author__ = "SHADOWHacker-GOD"

from .webfetch_proxy import (
    ShadowWebfetchProxy,
    ProxyConfig,
    FetchRequest,
    BulkFetchRequest,
)
from .opencode_proxy_plugins import (
    initialize_proxy_plugins,
    webfetch_proxy,
    bulk_webfetch_proxy,
    ProxyPluginManager,
)

__all__ = [
    "ShadowWebfetchProxy",
    "ProxyConfig",
    "FetchRequest",
    "BulkFetchRequest",
    "initialize_proxy_plugins",
    "webfetch_proxy",
    "bulk_webfetch_proxy",
    "ProxyPluginManager",
]
