import time

from .base import RateLimitAlgorithm


class FixedWindow(RateLimitAlgorithm):

    def __init__(
        self,
        limit: int,
        window_seconds: int
    ):
        self.limit = limit
        self.window = window_seconds

    def is_allowed(
        self,
        key: str,
        store
    ) -> tuple[bool, dict]:
        now = int(time.time())
        window_key = f"{key}:{now // self.window}"
        count = store.increment(window_key, ttl=self.window)
        remaining = max(0, self.limit - count)
        return count <= self.limit, {
            "limit": self.limit,
            "remaining": remaining,
            "reset": (now // self.window + 1) * self.window
        }
    

