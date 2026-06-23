from fastapi import Request
from fastapi.responses import JSONResponse

from starlette.middleware.base import (
    BaseHTTPMiddleware
)

from rate_limiter.algorithms.base import (
    RateLimitAlgorithm
)

from rate_limiter.storage.base import (
    StorageBackend
)


class FastAPIRateLimiter(
    BaseHTTPMiddleware
):

    def __init__(
        self,
        app,
        algorithm: RateLimitAlgorithm,
        storage: StorageBackend,
        key_func=None
    ):

        super().__init__(app)

        self.algorithm = algorithm
        self.storage = storage

        self.key_func = (
            key_func
            or
            (
                lambda request:
                request.client.host
            )
        )

    async def dispatch(
        self,
        request: Request,
        call_next
    ):

        key = self.key_func(
            request
        )

        allowed, meta = (
            self.algorithm.is_allowed(
                key,
                self.storage
            )
        )

        if not allowed:

            return JSONResponse(
                status_code=429,
                content={
                    "error":
                    "rate limit exceeded"
                },
                headers={
                    "Retry-After":
                    str(
                        meta.get(
                            "retry_after",
                            60
                        )
                    ),
                    "X-RateLimit-Limit":
                    str(
                        meta.get(
                            "limit",
                            "?"
                        )
                    ),
                    "X-RateLimit-Remaining":
                    str(
                        meta.get(
                            "remaining",
                            0
                        )
                    ),
                    "X-RateLimit-Reset":
                    str(
                        meta.get(
                            "reset",
                            0
                        )
                    )
                }
            )

        response = await call_next(
            request
        )

        response.headers[
            "X-RateLimit-Limit"
        ] = str(
            meta.get(
                "limit",
                "?"
            )
        )

        response.headers[
            "X-RateLimit-Remaining"
        ] = str(
            meta.get(
                "remaining",
                0
            )
        )

        response.headers[
            "X-RateLimit-Reset"
        ] = str(
            meta.get(
                "reset",
                0
            )
        )

        return response