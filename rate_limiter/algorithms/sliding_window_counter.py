import time

from .base import RateLimitAlgorithm


class SlidingWindowCounter(RateLimitAlgorithm):

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

        current_window = int(
            now // self.window
        )

        current_key = (
            f"{key}:{current_window}"
        )

        previous_key = (
            f"{key}:{current_window - 1}"
        )

        current_count = (
            store.get(current_key)
            or 0
        )

        previous_count = (
            store.get(previous_key)
            or 0
        )

        elapsed = (
            now % self.window
        )

        weight = (
            self.window - elapsed
        ) / self.window

        estimated_count = (
            current_count +
            previous_count * weight
        )

        if estimated_count >= self.limit:

            return False, {
                "limit": self.limit,
                "remaining": 0,
                "reset":
                (
                    current_window + 1
                ) * self.window
            }

        current_count = store.increment(
            current_key,
            ttl=self.window * 2
        )

        return True, {
            "limit": self.limit,
            "remaining":
            max(
                0,
                int(
                    self.limit -
                    estimated_count -
                    1
                )
            ),
            "reset":
            (
                current_window + 1
            ) * self.window
        }