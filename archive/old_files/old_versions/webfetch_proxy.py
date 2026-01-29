#!/usr/bin/env python3
"""
🔥 SHADOW WEBFETCH PROXY v1.0
Advanced webfetch proxy for opencode operations
Supports reconnaissance, OSINT, and secure web fetching
"""

import asyncio
import aiohttp
import json
import time
import logging
import hashlib
import os
import re
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urljoin, urlparse
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import redis.asyncio as redis
import yaml
from datetime import datetime, timedelta
import ssl
import certifi
import aiofiles
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/shadow-webfetch-proxy.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ShadowWebfetchProxy")

# Security scheme
security = HTTPBearer()


@dataclass
class ProxyRequest:
    """Represents a proxy request"""

    url: str
    method: str = "GET"
    headers: Optional[Dict[str, str]] = None
    data: Optional[str] = None
    timeout: int = 30
    follow_redirects: bool = True
    verify_ssl: bool = True
    user_agent: Optional[str] = None
    cookies: Optional[Dict[str, str]] = None
    allow_status_codes: Optional[List[int]] = None


@dataclass
class ProxyResponse:
    """Represents a proxy response"""

    status_code: int
    content: str
    headers: Dict[str, str]
    url: str
    final_url: str
    execution_time: float
    size: int
    success: bool
    error: Optional[str] = None


@dataclass
class IntelligenceRecord:
    """OSINT intelligence record"""

    url: str
    timestamp: datetime
    content: str
    metadata: Dict[str, Any]
    hash: str
    tags: List[str]


class FetchRequest(BaseModel):
    """Pydantic model for fetch requests"""

    url: str = Field(..., description="URL to fetch")
    method: str = Field("GET", description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    data: Optional[str] = Field(None, description="Request body data")
    timeout: int = Field(30, description="Request timeout in seconds")
    follow_redirects: bool = Field(True, description="Follow HTTP redirects")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    user_agent: Optional[str] = Field(None, description="Custom User-Agent")
    cookies: Optional[Dict[str, str]] = Field(None, description="Request cookies")
    allow_status_codes: Optional[List[int]] = Field(
        None, description="Allowed status codes"
    )
    cache_enabled: bool = Field(True, description="Enable response caching")
    intelligence_tags: Optional[List[str]] = Field(
        None, description="Intelligence tags"
    )


class BulkFetchRequest(BaseModel):
    """Pydantic model for bulk fetch requests"""

    urls: List[str] = Field(..., description="URLs to fetch")
    concurrent_limit: int = Field(5, description="Concurrent request limit")
    intelligence_tags: Optional[List[str]] = Field(
        None, description="Intelligence tags"
    )
    common_headers: Optional[Dict[str, str]] = Field(
        None, description="Common headers for all requests"
    )


class ProxyConfig:
    """Configuration management"""

    def __init__(self, config_path: str = "/tmp/shadow-proxy-config.yaml"):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        """Load proxy configuration"""
        default_config = {
            "proxy": {
                "host": "0.0.0.0",
                "port": 8081,
                "workers": 4,
                "timeout": 30,
                "max_concurrent": 100,
            },
            "caching": {
                "enabled": True,
                "ttl": 3600,
                "redis_url": "redis://localhost:6379/0",
                "max_size_mb": 100,
            },
            "security": {
                "api_key": None,
                "allowed_domains": [],
                "blocked_domains": [],
                "rate_limiting": {
                    "enabled": True,
                    "requests_per_minute": 60,
                    "requests_per_hour": 1000,
                },
            },
            "intelligence": {
                "enabled": True,
                "storage_path": "/tmp/shadow-intelligence",
                "auto_tagging": True,
                "content_analysis": True,
            },
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
                "SHADOW-OSINT-Bot/1.0 (Reconnaissance)",
                "SHADOW-Intelligence/2.0 (Cybersecurity)",
            ],
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = yaml.safe_load(f) or default_config
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self.config = default_config

    def save_config(self):
        """Save proxy configuration"""
        try:
            with open(self.config_path, "w") as f:
                yaml.dump(self.config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")


class ShadowWebfetchProxy:
    """Advanced webfetch proxy for SHADOW operations"""

    def __init__(self, config: ProxyConfig = None):
        self.config = config or ProxyConfig()
        self.redis_client = None
        self.session = None
        self.intelligence_dir = Path(
            self.config.config.get("intelligence", {}).get(
                "storage_path", "/tmp/shadow-intelligence"
            )
        )
        self.intelligence_dir.mkdir(exist_ok=True)

        # Request tracking
        self.request_counts = {}
        self.blocked_domains = set(
            self.config.config.get("security", {}).get("blocked_domains", [])
        )
        self.allowed_domains = set(
            self.config.config.get("security", {}).get("allowed_domains", [])
        )

        logger.info("SHADOW Webfetch Proxy initialized")

    async def initialize(self):
        """Initialize proxy components"""
        try:
            # Initialize Redis for caching
            if self.config.config.get("caching", {}).get("enabled"):
                redis_url = self.config.config.get("caching", {}).get(
                    "redis_url", "redis://localhost:6379/0"
                )
                self.redis_client = await redis.from_url(redis_url)
                logger.info("Redis cache initialized")

            # Initialize HTTP session
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=30,
                keepalive_timeout=30,
                enable_cleanup_closed=True,
            )

            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={
                    "User-Agent": "SHADOW-Intelligence/2.0 (Cybersecurity Reconnaissance)"
                },
            )

            logger.info("HTTP session initialized")

        except Exception as e:
            logger.error(f"Failed to initialize proxy: {e}")
            raise

    async def close(self):
        """Cleanup proxy resources"""
        if self.session:
            await self.session.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Proxy resources cleaned up")

    def _generate_cache_key(self, request: FetchRequest) -> str:
        """Generate cache key for request"""
        headers_str = ""
        if request.headers:
            headers_str = hashlib.md5(
                str(sorted(request.headers.items())).encode()
            ).hexdigest()
        content = f"{request.method}:{request.url}:{headers_str}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def _is_domain_allowed(self, url: str) -> bool:
        """Check if domain is allowed"""
        try:
            domain = urlparse(url).netloc.lower()

            # Check blocked domains
            if any(blocked in domain for blocked in self.blocked_domains):
                return False

            # Check allowed domains (if configured)
            if self.allowed_domains and not any(
                allowed in domain for allowed in self.allowed_domains
            ):
                return False

            return True
        except Exception:
            return False

    async def _check_rate_limit(self, api_key: str = None) -> bool:
        """Check rate limiting"""
        if (
            not self.config.config.get("security", {})
            .get("rate_limiting", {})
            .get("enabled")
        ):
            return True

        now = datetime.now()
        minute_key = f"rate_limit:{api_key or 'anonymous'}:{now.strftime('%Y%m%d%H%M')}"
        hour_key = f"rate_limit:{api_key or 'anonymous'}:{now.strftime('%Y%m%d%H')}"

        if self.redis_client:
            minute_count = await self.redis_client.get(minute_key) or 0
            hour_count = await self.redis_client.get(hour_key) or 0

            if int(minute_count) >= 60 or int(hour_count) >= 1000:
                return False

            # Increment counters
            pipe = self.redis_client.pipeline()
            pipe.incr(minute_key)
            pipe.expire(minute_key, 60)
            pipe.incr(hour_key)
            pipe.expire(hour_key, 3600)
            await pipe.execute()

        return True

    async def _get_cached_response(self, cache_key: str) -> Optional[ProxyResponse]:
        """Get cached response"""
        if not self.redis_client:
            return None

        try:
            cached_data = await self.redis_client.get(f"proxy_cache:{cache_key}")
            if cached_data:
                return ProxyResponse(**json.loads(cached_data))
        except Exception as e:
            logger.error(f"Cache retrieval failed: {e}")

        return None

    async def _cache_response(
        self, cache_key: str, response: ProxyResponse, ttl: int = 3600
    ):
        """Cache response"""
        if not self.redis_client:
            return

        try:
            await self.redis_client.setex(
                f"proxy_cache:{cache_key}", ttl, json.dumps(asdict(response))
            )
        except Exception as e:
            logger.error(f"Cache storage failed: {e}")

    async def _save_intelligence(self, record: IntelligenceRecord):
        """Save intelligence record"""
        try:
            intelligence_config = self.config.config.get("intelligence", {})
            if not intelligence_config.get("enabled"):
                return

            # Generate filename
            timestamp = record.timestamp.strftime("%Y%m%d_%H%M%S")
            url_hash = hashlib.md5(record.url.encode()).hexdigest()[:8]
            filename = f"webfetch_{timestamp}_{url_hash}.json"
            filepath = self.intelligence_dir / filename

            # Save record
            async with aiofiles.open(filepath, "w") as f:
                await f.write(json.dumps(asdict(record), default=str, indent=2))

            logger.info(f"Intelligence record saved: {filepath}")

        except Exception as e:
            logger.error(f"Failed to save intelligence: {e}")

    def _log_blocked_request(self, request: FetchRequest, reason: str, details: str):
        """Log blocked requests for analysis"""
        try:
            blocked_log = {
                "timestamp": datetime.now().isoformat(),
                "url": request.url,
                "method": request.method,
                "reason": reason,
                "details": details,
                "headers": request.headers or {},
                "user_agent": request.user_agent,
                "tags": request.intelligence_tags or [],
            }

            # Log to main logger
            logger.warning(f"BLOCKED REQUEST: {reason} - {request.url} - {details}")

            # Optionally save to blocked requests file
            blocked_file = self.intelligence_dir / "blocked_requests.json"

            # Read existing blocked requests
            blocked_requests = []
            if blocked_file.exists():
                try:
                    with open(blocked_file, "r") as f:
                        blocked_requests = json.load(f)
                except:
                    pass

            # Add new blocked request
            blocked_requests.append(blocked_log)

            # Keep only last 1000 blocked requests
            if len(blocked_requests) > 1000:
                blocked_requests = blocked_requests[-1000:]

            # Save updated list
            with open(blocked_file, "w") as f:
                json.dump(blocked_requests, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to log blocked request: {e}")

    async def fetch_url(
        self, request: FetchRequest, api_key: str = None
    ) -> ProxyResponse:
        """Fetch URL with proxy capabilities"""
        start_time = time.time()

        try:
            # Security checks
            if not self._is_domain_allowed(request.url):
                # Log blocked request
                logger.warning(f"BLOCKED: Domain not allowed - {request.url}")
                await self._log_blocked_request(
                    request, "DOMAIN_BLOCKED", "Domain blocked by security policy"
                )

                return ProxyResponse(
                    status_code=403,
                    content="Domain not allowed",
                    headers={},
                    url=request.url,
                    final_url=request.url,
                    execution_time=time.time() - start_time,
                    size=0,
                    success=False,
                    error="Domain blocked by security policy",
                )

            # Rate limiting
            if not await self._check_rate_limit(api_key):
                # Log rate limit block
                logger.warning(f"BLOCKED: Rate limit exceeded - {request.url}")
                await self._log_blocked_request(
                    request, "RATE_LIMIT", "Rate limit exceeded"
                )

                return ProxyResponse(
                    status_code=429,
                    content="Rate limit exceeded",
                    headers={},
                    url=request.url,
                    final_url=request.url,
                    execution_time=time.time() - start_time,
                    size=0,
                    success=False,
                    error="Rate limit exceeded",
                )

            # Check cache
            cache_key = self._generate_cache_key(request)
            if request.cache_enabled:
                cached_response = await self._get_cached_response(cache_key)
                if cached_response:
                    logger.info(f"Cache hit for {request.url}")
                    cached_response.execution_time = time.time() - start_time
                    return cached_response

            # Prepare headers
            headers = request.headers or {}
            if request.user_agent:
                headers["User-Agent"] = request.user_agent
            elif "User-Agent" not in headers:
                # Use random user agent
                user_agents = self.config.config.get("user_agents", [])
                if user_agents:
                    import random

                    headers["User-Agent"] = random.choice(user_agents)

            # Add intelligence headers
            headers["X-SHADOW-Proxy"] = "enabled"
            headers["X-Request-ID"] = hashlib.sha256(
                f"{request.url}{time.time()}".encode()
            ).hexdigest()[:8]

            # Prepare request
            kwargs = {
                "headers": headers,
                "allow_redirects": request.follow_redirects,
                "ssl": ssl.create_default_context(cafile=certifi.where())
                if request.verify_ssl
                else False,
            }

            if request.cookies:
                kwargs["cookies"] = request.cookies

            if request.data and request.method.upper() != "GET":
                kwargs["data"] = request.data

            # Execute request
            timeout = aiohttp.ClientTimeout(total=request.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.request(
                    request.method, request.url, **kwargs
                ) as response:
                    content = await response.text()

                    proxy_response = ProxyResponse(
                        status_code=int(response.status),
                        content=content,
                        headers=dict(response.headers),
                        url=request.url,
                        final_url=str(response.url),
                        execution_time=time.time() - start_time,
                        size=len(content.encode("utf-8")),
                        success=200 <= int(response.status) < 400
                        if not request.allow_status_codes
                        else int(response.status) in request.allow_status_codes,
                    )

                    # Cache successful responses
                    if proxy_response.success and request.cache_enabled:
                        await self._cache_response(cache_key, proxy_response)

                    # Save intelligence
                    if self.config.config.get("intelligence", {}).get("enabled"):
                        intelligence_record = IntelligenceRecord(
                            url=request.url,
                            timestamp=datetime.now(),
                            content=content[:10000],  # Limit content size
                            metadata={
                                "status_code": response.status,
                                "headers": dict(response.headers),
                                "execution_time": proxy_response.execution_time,
                                "size": proxy_response.size,
                                "method": request.method,
                                "tags": request.intelligence_tags or [],
                            },
                            hash=hashlib.sha256(content.encode()).hexdigest(),
                            tags=request.intelligence_tags or [],
                        )
                        await self._save_intelligence(intelligence_record)

                    return proxy_response

        except asyncio.TimeoutError:
            # Log timeout
            logger.warning(f"BLOCKED: Request timeout - {request.url}")
            await self._log_blocked_request(request, "TIMEOUT", "Request timeout")

            return ProxyResponse(
                status_code=408,
                content="Request timeout",
                headers={},
                url=request.url,
                final_url=request.url,
                execution_time=request.timeout,
                size=0,
                success=False,
                error="Request timeout",
            )
        except Exception as e:
            # Log general errors
            logger.warning(f"BLOCKED: General error - {request.url} - {str(e)}")
            await self._log_blocked_request(request, "ERROR", str(e))

            return ProxyResponse(
                status_code=500,
                content=str(e),
                headers={},
                url=request.url,
                final_url=request.url,
                execution_time=time.time() - start_time,
                size=0,
                success=False,
                error=str(e),
            )

    async def bulk_fetch(
        self, bulk_request: BulkFetchRequest, api_key: str = None
    ) -> List[ProxyResponse]:
        """Bulk fetch URLs concurrently"""
        semaphore = asyncio.Semaphore(bulk_request.concurrent_limit)

        async def fetch_with_semaphore(url: str) -> ProxyResponse:
            async with semaphore:
                request = FetchRequest(
                    url=url,
                    method="GET",
                    headers=bulk_request.common_headers or {},
                    intelligence_tags=bulk_request.intelligence_tags,
                )
                return await self.fetch_url(request, api_key)

        tasks = [fetch_with_semaphore(url) for url in bulk_request.urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ProxyResponse(
                        status_code=500,
                        content=str(result),
                        headers={},
                        url=bulk_request.urls[i],
                        final_url=bulk_request.urls[i],
                        execution_time=0,
                        size=0,
                        success=False,
                        error=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results


# FastAPI application
app = FastAPI(
    title="SHADOW Webfetch Proxy",
    description="Advanced webfetch proxy for opencode intelligence operations",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global proxy instance (will be initialized with proper config path)
proxy = None


@app.on_event("startup")
async def startup_event():
    global proxy
    # Initialize proxy with proper config path
    config = ProxyConfig("config.yaml")
    proxy = ShadowWebfetchProxy(config)
    await proxy.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    global proxy
    if proxy:
        await proxy.close()


async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract API key from authorization header"""
    # For production, implement proper API key validation
    return credentials.credentials


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "SHADOW Webfetch Proxy",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Webfetch proxy",
            "Caching",
            "Rate limiting",
            "Intelligence gathering",
            "CORS support",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        if proxy.redis_client:
            await proxy.redis_client.ping()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "cache": "enabled" if proxy.redis_client else "disabled",
                "intelligence": "enabled"
                if proxy.config.config.get("intelligence", {}).get("enabled")
                else "disabled",
            },
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {e}")


@app.post("/fetch")
async def fetch_url(request: FetchRequest, api_key: str = Depends(get_api_key)):
    """Fetch a single URL"""
    try:
        result = await proxy.fetch_url(request, api_key)

        if not result.success and result.error:
            raise HTTPException(status_code=result.status_code, detail=result.error)

        return {
            "success": result.success,
            "status_code": result.status_code,
            "url": result.url,
            "final_url": result.final_url,
            "execution_time": result.execution_time,
            "size": result.size,
            "content": result.content,
            "headers": result.headers,
            "error": result.error,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fetch request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fetch/bulk")
async def bulk_fetch_urls(
    request: BulkFetchRequest, api_key: str = Depends(get_api_key)
):
    """Bulk fetch multiple URLs"""
    try:
        results = await proxy.bulk_fetch(request, api_key)

        return {
            "total_urls": len(request.urls),
            "successful": sum(1 for r in results if r.success),
            "failed": sum(1 for r in results if not r.success),
            "results": [
                {
                    "url": r.url,
                    "success": r.success,
                    "status_code": r.status_code,
                    "execution_time": r.execution_time,
                    "size": r.size,
                    "error": r.error,
                }
                for r in results
            ],
        }

    except Exception as e:
        logger.error(f"Bulk fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/intelligence/list")
async def list_intelligence(limit: int = 50):
    """List intelligence records"""
    try:
        intelligence_files = list(proxy.intelligence_dir.glob("webfetch_*.json"))
        intelligence_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        records = []
        for filepath in intelligence_files[:limit]:
            try:
                async with aiofiles.open(filepath, "r") as f:
                    content = await f.read()
                    record = json.loads(content)
                    records.append(
                        {
                            "filename": filepath.name,
                            "timestamp": record.get("timestamp"),
                            "url": record.get("url"),
                            "tags": record.get("tags", []),
                            "size": record.get("metadata", {}).get("size", 0),
                        }
                    )
            except Exception as e:
                logger.error(f"Failed to read intelligence file {filepath}: {e}")

        return {"total_records": len(records), "records": records}

    except Exception as e:
        logger.error(f"Failed to list intelligence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get proxy configuration (sanitized)"""
    config = proxy.config.config.copy()

    # Remove sensitive information
    if "security" in config and "api_key" in config["security"]:
        config["security"]["api_key"] = "***REDACTED***"

    return config


@app.post("/config/reload")
async def reload_config():
    """Reload proxy configuration"""
    try:
        proxy.config.load_config()
        logger.info("Configuration reloaded")
        return {"status": "success", "message": "Configuration reloaded"}
    except Exception as e:
        logger.error(f"Failed to reload config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/blocked/requests")
async def get_blocked_requests(limit: int = 50):
    """Get list of blocked requests"""
    try:
        blocked_file = proxy.intelligence_dir / "blocked_requests.json"

        if not blocked_file.exists():
            return {"blocked_requests": [], "total": 0}

        with open(blocked_file, "r") as f:
            blocked_requests = json.load(f)

        # Return last 'limit' requests
        recent_requests = (
            blocked_requests[-limit:]
            if limit < len(blocked_requests)
            else blocked_requests
        )

        return {
            "blocked_requests": recent_requests,
            "total": len(blocked_requests),
            "recent_count": len(recent_requests),
        }
    except Exception as e:
        logger.error(f"Failed to get blocked requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/housekeeping/cleanup")
async def cleanup_obsolete_files():
    """Cleanup obsolete files and perform maintenance"""
    try:
        results = {
            "intelligence_cleanup": {"deleted": 0, "errors": []},
            "cache_cleanup": {"deleted": 0, "errors": []},
            "log_rotation": {"rotated": 0, "errors": []},
            "overall_status": "success",
        }

        # Cleanup intelligence files (keep last 1000)
        intelligence_dir = proxy.intelligence_dir
        if intelligence_dir.exists():
            intelligence_files = list(intelligence_dir.glob("webfetch_*.json"))
            intelligence_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # Remove old files
            for file_path in intelligence_files[1000:]:
                try:
                    file_path.unlink()
                    results["intelligence_cleanup"]["deleted"] += 1
                except Exception as e:
                    results["intelligence_cleanup"]["errors"].append(str(e))

        # Cleanup old log files (keep last 5)
        log_dir = Path("/Users/djesys/#VIBECODE/logs")
        if log_dir.exists():
            log_files = list(log_dir.glob("*.log*"))
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            for log_file in log_files[5:]:
                try:
                    log_file.unlink()
                    results["log_rotation"]["rotated"] += 1
                except Exception as e:
                    results["log_rotation"]["errors"].append(str(e))

        # Cleanup Redis cache if needed
        if proxy.redis_client:
            try:
                # Remove old cache entries (older than 24 hours)
                await proxy.redis_client.execute_command(
                    "EVAL",
                    """
                    local keys = redis.call('KEYS', 'proxy_cache:*')
                    local expired = 0
                    for i=1,#keys do
                        if redis.call('TTL', keys[i]) < 0 then
                            redis.call('DEL', keys[i])
                            expired = expired + 1
                        end
                    end
                    return expired
                """,
                    0,
                )
            except Exception as e:
                results["cache_cleanup"]["errors"].append(str(e))

        # Count remaining files
        remaining_intelligence = (
            len(list(intelligence_dir.glob("webfetch_*.json")))
            if intelligence_dir.exists()
            else 0
        )
        remaining_logs = len(list(log_dir.glob("*.log*"))) if log_dir.exists() else 0

        results["remaining"] = {
            "intelligence_files": remaining_intelligence,
            "log_files": remaining_logs,
        }

        logger.info(f"Housekeeping completed: {results}")
        return results

    except Exception as e:
        logger.error(f"Housekeeping failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    # Run the proxy server
    config = ProxyConfig("config.yaml")
    uvicorn.run(
        "webfetch_proxy:app",
        host=config.config.get("proxy", {}).get("host", "0.0.0.0"),
        port=config.config.get("proxy", {}).get("port", 8081),
        workers=config.config.get("proxy", {}).get("workers", 4),
        log_level="info",
        access_log=True,
    )
