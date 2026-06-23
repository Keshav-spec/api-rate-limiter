from rate_limiter.storage import InMemoryStorage
from rate_limiter.algorithms.sliding_window_log import SlidingWindowLog


def test_sliding_window_log():

    store = InMemoryStorage()

    limiter = SlidingWindowLog(
        limit=3,
        window_seconds=60
    )

    assert limiter.is_allowed("user", store)[0]
    assert limiter.is_allowed("user", store)[0]
    assert limiter.is_allowed("user", store)[0]

    assert not limiter.is_allowed("user", store)[0]

import time

def test_sliding_window_expiry():

    store = InMemoryStorage()

    limiter = SlidingWindowLog(
        limit=1,
        window_seconds=1
    )

    assert limiter.is_allowed("user", store)[0]

    assert not limiter.is_allowed("user", store)[0]

    time.sleep(1.1)

    assert limiter.is_allowed("user", store)[0]

def test_sliding_window_multiple_users():

    store = InMemoryStorage()

    limiter = SlidingWindowLog(
        limit=1,
        window_seconds=60
    )

    assert limiter.is_allowed("user1", store)[0]
    assert limiter.is_allowed("user2", store)[0]

if __name__ == "__main__":

    test_sliding_window_log()
    print("Basic test passed")

    test_sliding_window_expiry()
    print("Expiry test passed")

    test_sliding_window_multiple_users()
    print("Multi-user test passed")

    print("All Sliding Window Log tests passed!")