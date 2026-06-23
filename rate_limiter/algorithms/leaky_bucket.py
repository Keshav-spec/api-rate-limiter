import time


class LeakyBucket:

    def __init__(
        self,
        capacity: int,
        leak_rate: float
    ):
        self.capacity = capacity
        self.leak_rate = leak_rate

    def is_allowed(
        self,
        key: str,
        store
    ) -> tuple[bool, dict]:

        now = time.time()

        bucket = store.get(key)

        if bucket is None:

            bucket = {
                "water": 0.0,
                "last": now
            }

        elapsed = now - bucket["last"]

        leaked = elapsed * self.leak_rate

        bucket["water"] = max(
            0.0,
            bucket["water"] - leaked
        )

        bucket["last"] = now

        projected_water = (
            bucket["water"] + 1
        )

        if projected_water > self.capacity:

            store.set(
                key,
                bucket
            )

            retry_after = None

            if self.leak_rate > 0:

                retry_after = (
                    projected_water
                    - self.capacity
                ) / self.leak_rate

            return False, {
                "retry_after":
                retry_after
            }

        bucket["water"] = projected_water

        store.set(
            key,
            bucket
        )

        return True, {
            "remaining":
            int(
                self.capacity
                - bucket["water"]
            )
        }