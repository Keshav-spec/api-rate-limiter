# ratelimiter-keshav

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

**Key capabilities:**

- Four rate-limiting algorithms covering accuracy, memory, and burst-tolerance trade-offs
- Thread-safe in-memory storage for development and testing
- Redis-backed storage for distributed, production environments
- Flask and FastAPI middleware with RFC-compliant response headers
- Configurable key extraction by IP address, API key, user ID, or any custom function
- 26+ automated tests including concurrency safety, middleware, integration, and storage layers

---

## Installation

**Core package:**

```bash
pip install ratelimiter-keshav
```

**With Flask support:**

```bash
pip install ratelimiter-keshav[flask]
```

**With FastAPI support:**

```bash
pip install ratelimiter-keshav[fastapi]
```

**Development dependencies:**

```bash
pip install ratelimiter-keshav[dev]
```

---

## Quick Start

```python
from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage

limiter = FixedWindow(limit=100, window_seconds=60)
store = InMemoryStorage()

allowed, metadata = limiter.is_allowed("user_123", store)

print(allowed)   # True or False
print(metadata)  # {"limit": 100, "remaining": 99, "reset": 1712345678}
```

---

## Algorithms

### Fixed Window

Counts requests within discrete, non-overlapping time intervals. Each window resets independently at the end of its period.

| Property | Detail |
|---|---|
| Memory per key | O(1) |
| Allows bursts | Yes |
| Boundary burst issue | Yes |
| Typical use case | Simple throttling |

**Trade-off:** A client can exhaust the limit at the tail end of one window and immediately exhaust the next, effectively doubling the permitted request rate at window boundaries.

---

### Sliding Window Log

Maintains a timestamped log of all requests within the active window. On each request, entries older than the window duration are pruned before evaluating the count.

| Property | Detail |
|---|---|
| Memory per key | O(n) — grows with request volume |
| Allows bursts | No |
| Boundary burst issue | No |
| Typical use case | Strict rate enforcement |

**Trade-off:** The most accurate algorithm, but memory usage scales with the number of requests per key within the window.

---

### Sliding Window Counter

Blends the request count from the current window with a time-weighted fraction of the previous window's count. Produces near-sliding-window accuracy at O(1) memory.

| Property | Detail |
|---|---|
| Memory per key | O(1) |
| Allows bursts | Partial |
| Boundary burst issue | No |
| Typical use case | Production APIs |

**Trade-off:** Introduces a small approximation error due to the weighted interpolation, negligible for most applications.

---

### Token Bucket

Each key holds a bucket with a maximum token capacity. Tokens are added at a constant refill rate. Each request consumes one token. Requests are rejected when the bucket is empty.

| Property | Detail |
|---|---|
| Memory per key | O(1) |
| Allows bursts | Yes, up to capacity |
| Boundary burst issue | No |
| Typical use case | APIs with variable burst traffic |

**Trade-off:** Permits short bursts up to the bucket capacity while enforcing a long-run average rate. Requires atomic storage operations (Lua scripts on Redis) to prevent race conditions.

---

### Algorithm Comparison

| Algorithm | Memory Per Key | Allows Bursts | Boundary Burst Issue | Typical Use Case |
|---|---|---|---|---|
| Fixed Window | O(1) | Yes | Yes | Simple throttling |
| Sliding Window Log | O(n) | No | No | Strict enforcement |
| Sliding Window Counter | O(1) | Partial | No | Production APIs |
| Token Bucket | O(1) | Yes (capped) | No | APIs with burst traffic |

---

## Storage Backends

### InMemoryStorage

A thread-safe, dictionary-backed storage layer intended for local development, unit testing, and single-process deployments. All read-modify-write operations are protected by a `threading.Lock`.

```python
from rate_limiter.storage import InMemoryStorage

store = InMemoryStorage()
```

### RedisStorage

A Redis-backed storage layer for distributed deployments. Uses atomic Lua scripts for algorithms that require compare-and-set semantics (e.g., Token Bucket) to eliminate race conditions under concurrent load.

```python
from rate_limiter.storage import RedisStorage

store = RedisStorage(host="localhost", port=6379)
```

**When to use Redis:** Any deployment with more than one application process or server instance. The in-memory backend does not share state across processes.

---

## Middleware Integration

### Flask

```python
from flask import Flask
from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage
from rate_limiter.middleware import FlaskRateLimiter

app = Flask(__name__)

limiter = FlaskRateLimiter(
    algorithm=FixedWindow(limit=100, window_seconds=60),
    storage=InMemoryStorage()
)

@app.route("/api/resource")
@limiter.limit()
def resource():
    return {"message": "OK"}

if __name__ == "__main__":
    app.run()
```

The `key_func` parameter defaults to `request.remote_addr`. Pass a custom callable to key by API token, user ID, or any other attribute:

```python
limiter = FlaskRateLimiter(
    algorithm=FixedWindow(limit=100, window_seconds=60),
    storage=InMemoryStorage(),
    key_func=lambda: request.headers.get("X-API-Key", request.remote_addr)
)
```

---

### FastAPI

```python
from fastapi import FastAPI
from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage
from rate_limiter.middleware import FastAPIRateLimiter

app = FastAPI()

app.add_middleware(
    FastAPIRateLimiter,
    algorithm=FixedWindow(limit=100, window_seconds=60),
    storage=InMemoryStorage()
)

@app.get("/api/resource")
def resource():
    return {"message": "OK"}
```

Run with:

```bash
uvicorn app:app --reload
```

---

## Response Headers

Both middleware implementations automatically attach standard rate-limit headers to every response, as specified in RFC 6585.

**On successful requests (2xx):**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 74
X-RateLimit-Reset: 1712345678
```

**On blocked requests (429 Too Many Requests):**

```
HTTP/1.1 429 Too Many Requests
Retry-After: 42
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1712345678
```

| Header | Description |
|---|---|
| `X-RateLimit-Limit` | Maximum requests allowed in the current window |
| `X-RateLimit-Remaining` | Requests remaining in the current window |
| `X-RateLimit-Reset` | Unix timestamp at which the window resets |
| `Retry-After` | Seconds until the client may retry (429 only) |

---

## Project Architecture

```
rate_limiter/
├── algorithms/
│   ├── fixed_window.py
│   ├── sliding_window_log.py
│   ├── sliding_window_counter.py
│   └── token_bucket.py
├── storage/
│   ├── in_memory.py
│   └── redis_backend.py
├── middleware/
│   ├── flask_middleware.py
│   └── fastapi_middleware.py
├── core/
│   └── limiter.py
├── tests/
└── examples/
    ├── flask_demo.py
    └── fastapi_demo.py
```

The storage layer is abstracted behind a `StorageBackend` interface. Algorithms call `store.get()`, `store.set()`, and `store.increment()` without any knowledge of the underlying implementation. This separation makes it straightforward to add new backends (e.g., Memcached, DynamoDB) without modifying algorithm code.

---

## Testing

Run the full test suite:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=rate_limiter
```

**Test coverage includes:**

- Unit tests for all four algorithms in isolation
- Edge cases: exactly at the limit, one over the limit, post-window-reset behaviour
- Concurrency tests: 50 simultaneous threads asserting the allowed count never exceeds the configured limit
- Middleware tests for both Flask and FastAPI (correct 429 responses, header values, per-key isolation)
- Integration tests across algorithm and storage combinations
- Storage backend tests for both InMemory and Redis

**Current status:** 26 automated tests passing.

---

## Continuous Integration

A GitHub Actions workflow runs automatically on every push to the repository.

**Pipeline steps:**

1. Install dependencies
2. Run the full pytest suite
3. Generate coverage report
4. Verify package build integrity

Workflow configuration: `.github/workflows/tests.yml`

---

## Performance

| Component | Time Complexity | Space Complexity |
|---|---|---|
| Fixed Window | O(1) | O(1) |
| Sliding Window Log | O(n) | O(n) |
| Sliding Window Counter | O(1) | O(1) |
| Token Bucket | O(1) | O(1) |
| InMemoryStorage access | O(1) | — |

---

## Roadmap

**Version 0.2.0**

- Leaky Bucket algorithm
- Atomic Redis operations via Lua scripts for all algorithms
- Async Redis backend (`aioredis`)
- Custom exception hierarchy

**Version 0.3.0**

- Django middleware
- Starlette middleware
- Benchmark suite with reproducible results
- Prometheus metrics integration

---

## Contributing

Contributions are welcome. To contribute:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Add tests covering any new or modified behaviour.
4. Ensure all existing tests pass (`pytest`).
5. Submit a pull request with a clear description of the change.

All pull requests must maintain or improve current test coverage.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Author

**Keshav Sharma**  
Computer Science Engineering (Data Science), VIT Chennai  
GitHub: [github.com/Keshav-spec](https://github.com/Keshav-spec)  
PyPI: [pypi.org/project/ratelimiter-keshav](https://pypi.org/project/ratelimiter-keshav/0.1.0/)