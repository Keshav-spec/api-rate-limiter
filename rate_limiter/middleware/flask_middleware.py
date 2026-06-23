from flask import request, jsonify, make_response, Response
from functools import wraps
from typing import Callable, Any

from rate_limiter.algorithms.base import RateLimitAlgorithm
from rate_limiter.storage.base import StorageBackend


class FlaskRateLimiter:

    def __init__(
        self,
        algorithm: RateLimitAlgorithm,
        storage: StorageBackend,
        app=None,
        key_func: Callable | None = None
    ):
        self.algorithm = algorithm
        self.storage = storage

        self.key_func = (
            key_func
            or
            (lambda: request.remote_addr or "anonymous")
        )

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def limit(self, rule: str | None = None):
        """
        Future:
        Support rules like:
        - 100/minute
        - 10/second
        - 1000/hour
        """

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):

                key = self.key_func()

                allowed, meta = self.algorithm.is_allowed(
                    key,
                    self.storage
                )

                if not allowed:

                    response = jsonify({
                        "error": "rate limit exceeded"
                    })

                    response.status_code = 429

                    self._add_headers(
                        response,
                        meta
                    )

                    return response

                response = make_response(
                    func(*args, **kwargs)
                )

                self._add_headers(
                    response,
                    meta
                )

                return response

            return wrapper

        return decorator

    def _add_headers(
        self,
        response: Response,
        meta: dict[str, Any]
    ) -> Response:

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

        if "retry_after" in meta:

            response.headers[
                "Retry-After"
            ] = str(
                meta["retry_after"]
            )

        return response