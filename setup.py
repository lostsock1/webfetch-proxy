#!/usr/bin/env python3
"""
Setup script for WebFetch Proxy
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="webfetch-proxy",
    version="1.0.0",
    author="WebFetch Proxy Team",
    author_email="",
    description="Advanced web content fetching proxy service with intelligence gathering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lostsock1/webfetch-proxy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn[standard]>=0.24.0",
        "aiohttp>=3.9.1",
        "redis>=5.0.1",
        "PyYAML>=6.0.1",
        "pydantic>=2.5.0",
        "certifi>=2024.2.2",
        "aiofiles>=23.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "webfetch-proxy=webfetch_proxy:main",
        ],
    },
)
