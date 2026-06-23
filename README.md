# ratelimiter-keshav

![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![PyPI](https://img.shields.io/pypi/v/ratelimiter-keshav)
![License](https://img.shields.io/badge/license-MIT-green)

A pluggable Python rate-limiting library for modern web applications. Implements multiple rate-limiting algorithms with thread-safe storage backends and seamless middleware integration for Flask and FastAPI.

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Algorithms](#algorithms)
- [Storage Backends](#storage-backends)
- [Middleware Integration](#middleware-integration)
- [Response Headers](#response-headers)
- [Project Architecture](#project-architecture)
- [Testing](#testing)
- [Continuous Integration](#continuous-integration)
- [Performance](#performance)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

---

## Overview

`ratelimiter-keshav` provides a clean abstraction over rate-limiting logic, decoupling algorithm selection from storage and transport layers. It is designed to be dropped into existing Flask or FastAPI applications with minimal configuration while remaining extensible for custom use cases.

### Key Capabilities

- Five rate-limiting algorithms covering accuracy, memory efficiency, and burst tolerance trade-offs
- Thread-safe in-memory storage for development and testing
- Redis-backed storage for distributed, production environments
- Flask and FastAPI middleware with RFC-compliant response headers
- Configurable key extraction by IP address, API key, user ID, or any custom function
- 30 automated tests including concurrency, middleware, integration, and storage validation
- Published on PyPI and installable via pip

---

## Installation

### Core Package

```bash
pip install ratelimiter-keshav
```

### With Flask Support

```bash
pip install ratelimiter-keshav[flask]
```

### With FastAPI Support

```bash
pip install ratelimiter-keshav[fastapi]
```

### Development Dependencies

```bash
pip install ratelimiter-keshav[dev]
```

---

## Quick Start

```python
from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage

limiter = FixedWindow(
    limit=100,
    window_seconds=60
)

store = InMemoryStorage()

allowed, metadata = limiter.is_allowed(
    "user_123",
    store
)

print(allowed)
print(metadata)
```

---

# Algorithms

## Fixed Window

Counts requests within discrete, non-overlapping time intervals.

| Property | Detail |
|----------|---------|
| Memory per key | O(1) |
| Allows bursts | Yes |
| Boundary burst issue | Yes |
| Typical use case | Simple throttling |

**Trade-off:** Can allow burst traffic at window boundaries.

---

## Sliding Window Log

Maintains a timestamped log of all requests within the active window.

| Property | Detail |
|----------|---------|
| Memory per key | O(n) |
| Allows bursts | No |
| Boundary burst issue | No |
| Typical use case | Strict rate enforcement |

**Trade-off:** Most accurate but memory grows with request volume.

---

## Sliding Window Counter

Combines the current window count with a weighted portion of the previous window.

| Property | Detail |
|----------|---------|
| Memory per key | O(1) |
| Allows bursts | Partial |
| Boundary burst issue | No |
| Typical use case | Production APIs |

**Trade-off:** Small approximation error in exchange for constant memory.

---

## Token Bucket

Tokens refill at a constant rate. Requests consume tokens.

| Property | Detail |
|----------|---------|
| Memory per key | O(1) |
| Allows bursts | Yes |
| Boundary burst issue | No |
| Typical use case | Burst-friendly APIs |

**Trade-off:** Allows controlled bursts while enforcing long-term limits.

---

## Leaky Bucket

Requests are treated as water entering a bucket that leaks at a fixed rate.

| Property | Detail |
|----------|---------|
| Memory per key | O(1) |
| Allows bursts | No |
| Boundary burst issue | No |
| Typical use case | Traffic shaping and smooth request flow |

**Trade-off:** Produces a predictable request rate and prevents sudden bursts.

---

## Algorithm Comparison

| Algorithm | Memory Per Key | Allows Bursts | Boundary Burst Issue | Typical Use Case |
|------------|---------------|---------------|---------------------|------------------|
| Fixed Window | O(1) | Yes | Yes | Simple throttling |
| Sliding Window Log | O(n) | No | No | Strict enforcement |
| Sliding Window Counter | O(1) | Partial | No | Production APIs |
| Token Bucket | O(1) | Yes (capped) | No | APIs with burst traffic |
| Leaky Bucket | O(1) | No | No | Traffic shaping |

---

# Storage Backends

## InMemoryStorage

Thread-safe dictionary-backed storage designed for:

- Local development
- Unit testing
- Single-process deployments

```python
from rate_limiter.storage import InMemoryStorage

store = InMemoryStorage()
```

---

## RedisStorage

Redis-backed storage for distributed deployments.

```python
from rate_limiter.storage import RedisStorage

store = RedisStorage(
    host="localhost",
    port=6379
)
```

Uses atomic operations and Lua scripting where required to ensure correctness under concurrent load.

---

# Middleware Integration

## Flask

```python
from flask import Flask

from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage
from rate_limiter.middleware import FlaskRateLimiter

app = Flask(__name__)

limiter = FlaskRateLimiter(
    algorithm=FixedWindow(
        limit=100,
        window_seconds=60
    ),
    storage=InMemoryStorage()
)

@app.route("/")
@limiter.limit()
def home():
    return {
        "message": "OK"
    }

if __name__ == "__main__":
    app.run()
```

---

## FastAPI

```python
from fastapi import FastAPI

from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage
from rate_limiter.middleware import FastAPIRateLimiter

app = FastAPI()

app.add_middleware(
    FastAPIRateLimiter,
    algorithm=FixedWindow(
        limit=100,
        window_seconds=60
    ),
    storage=InMemoryStorage()
)

@app.get("/")
def home():
    return {
        "message": "OK"
    }
```

Run with:

```bash
uvicorn app:app --reload
```

---

# Response Headers

Successful requests include:

```http
X-RateLimit-Limit
X-RateLimit-Remaining
X-RateLimit-Reset
```

Blocked requests include:

```http
Retry-After
```

Example:

```http
HTTP/1.1 429 Too Many Requests

Retry-After: 42
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1712345678
```

---

# Project Architecture

```text
rate_limiter/
├── algorithms/
│   ├── fixed_window.py
│   ├── sliding_window_log.py
│   ├── sliding_window_counter.py
│   ├── token_bucket.py
│   └── leaky_bucket.py
│
├── storage/
│   ├── in_memory.py
│   └── redis_backend.py
│
├── middleware/
│   ├── flask_middleware.py
│   └── fastapi_middleware.py
│
├── core/
│   └── limiter.py
│
├── tests/
│
└── examples/
```

---

# Testing

Run all tests:

```bash
pytest
```

Run coverage:

```bash
pytest --cov=rate_limiter
```

### Current Status

- 30 automated tests
- Concurrency testing
- Middleware testing
- Integration testing
- Storage backend testing
- Algorithm testing
- ~82% code coverage

---

# Continuous Integration

GitHub Actions automatically:

- Runs tests on every push
- Executes coverage checks
- Verifies package integrity

Workflow:

```text
.github/workflows/tests.yml
```

---

# Performance

| Component | Time Complexity | Space Complexity |
|------------|----------------|------------------|
| Fixed Window | O(1) | O(1) |
| Sliding Window Log | O(n) | O(n) |
| Sliding Window Counter | O(1) | O(1) |
| Token Bucket | O(1) | O(1) |
| Leaky Bucket | O(1) | O(1) |
| InMemoryStorage | O(1) | O(1) |

---

# Roadmap

## Version 0.2.0

- Async Redis backend
- Advanced Redis Lua scripting
- Custom exception hierarchy
- Benchmark suite

## Version 0.3.0

- Django middleware
- Starlette middleware
- Prometheus metrics integration
- Distributed rate-limiting examples

---

# Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

# License

This project is licensed under the MIT License.

---

# Author

**Keshav Sharma**  
Computer Science Engineering (Data Science)  
VIT Chennai

GitHub: https://github.com/Keshav-spec

PyPI: https://pypi.org/project/ratelimiter-keshav/