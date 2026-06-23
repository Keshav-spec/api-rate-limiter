import time

from .base import RateLimitAlgorithm


class SlidingWindowLog(RateLimitAlgorithm):

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

        now = time.time()

        timestamps = store.get(key)

        if timestamps is None:
            timestamps = []

        timestamps = [
            ts
            for ts in timestamps
            if now - ts < self.window
        ]

        if len(timestamps) >= self.limit:

            store.set(
                key,
                timestamps,
                ttl=self.window
            )

            return False, {
                "limit": self.limit,
                "remaining": 0,
                "reset": int(
                    timestamps[0] +
                    self.window
                )
            }

        timestamps.append(now)

        store.set(
            key,
            timestamps,
            ttl=self.window
        )

        return True, {
            "limit": self.limit,
            "remaining":
                self.limit -
                len(timestamps),
            "reset":
                int(now + self.window)
        }