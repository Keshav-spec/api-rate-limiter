import time


class TokenBucket:

    def __init__(
        self,
        capacity: int,
        refill_rate: float
    ):
        self.capacity = capacity
        self.refill_rate = refill_rate

    def is_allowed(
        self,
        key: str,
        store
    ) -> tuple[bool, dict]:

        now = time.time()

        bucket = store.get(key)

        if bucket is None:
            bucket = {
                "tokens": self.capacity,
                "last": now
            }

        elapsed = now - bucket["last"]

        bucket["tokens"] = min(
            self.capacity,
            bucket["tokens"] +
            elapsed * self.refill_rate
        )

        bucket["last"] = now

        if bucket["tokens"] >= 1:

            bucket["tokens"] -= 1

            store.set(
                key,
                bucket
            )

            return True, {
                "remaining":
                int(bucket["tokens"])
            }

        store.set(
            key,
            bucket
        )

        retry_after = None

        if self.refill_rate > 0:

            retry_after = (
                (1 - bucket["tokens"])
                / self.refill_rate
            )

        return False, {
            "retry_after":
            retry_after
        }