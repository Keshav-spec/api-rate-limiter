import threading

from rate_limiter.algorithms import (
    FixedWindow,
    TokenBucket
)

from rate_limiter.storage import (
    InMemoryStorage
)


def test_fixed_window_concurrency():

    limiter = FixedWindow(
        limit=10,
        window_seconds=60
    )

    store = InMemoryStorage()

    results = []

    lock = threading.Lock()

    def worker():

        allowed, _ = limiter.is_allowed(
            "shared_user",
            store
        )

        with lock:
            results.append(allowed)

    threads = [
        threading.Thread(target=worker)
        for _ in range(50)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    allowed_count = sum(results)

    assert allowed_count <= 10


def test_token_bucket_concurrency():

    limiter = TokenBucket(
        capacity=10,
        refill_rate=0
    )

    store = InMemoryStorage()

    results = []

    lock = threading.Lock()

    def worker():

        allowed, _ = limiter.is_allowed(
            "shared_user",
            store
        )

        with lock:
            results.append(allowed)

    threads = [
        threading.Thread(target=worker)
        for _ in range(50)
    ]

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    allowed_count = sum(results)

    assert allowed_count <= 10


if __name__ == "__main__":

    test_fixed_window_concurrency()
    print("Fixed Window concurrency test passed")

    test_token_bucket_concurrency()
    print("Token Bucket concurrency test passed")

    print("All concurrency tests passed")