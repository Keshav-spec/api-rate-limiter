from rate_limiter.algorithms import LeakyBucket
from rate_limiter.storage import InMemoryStorage


def test_leaky_bucket_capacity():

    bucket = LeakyBucket(
        capacity=5,
        leak_rate=1
    )

    store = InMemoryStorage()

    results = []

    for _ in range(5):

        allowed, _ = bucket.is_allowed(
            "user",
            store
        )

        results.append(allowed)

    assert all(results)

def test_leaky_bucket_blocks():

    bucket = LeakyBucket(
        capacity=5,
        leak_rate=1
    )

    store = InMemoryStorage()

    for _ in range(5):

        allowed, _ = bucket.is_allowed(
            "user",
            store
        )

        assert allowed

    allowed, meta = bucket.is_allowed(
        "user",
        store
    )
    

    assert not allowed
    assert "retry_after" in meta

import time


def test_leaky_bucket_leaks():

    bucket = LeakyBucket(
        capacity=2,
        leak_rate=2
    )

    store = InMemoryStorage()

    bucket.is_allowed(
        "user",
        store
    )

    bucket.is_allowed(
        "user",
        store
    )

    time.sleep(1)

    allowed, _ = bucket.is_allowed(
        "user",
        store
    )

    assert allowed

if __name__ == "__main__":

    test_leaky_bucket_capacity()
    print("Capacity test passed")

    test_leaky_bucket_blocks()
    print("Blocking test passed")

    test_leaky_bucket_leaks()
    print("Leak test passed")

    print("All Leaky Bucket tests passed")