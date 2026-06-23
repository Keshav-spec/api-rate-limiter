from rate_limiter.storage import InMemoryStorage

from rate_limiter.algorithms.sliding_window_counter import (
    SlidingWindowCounter
)


def test_counter_basic():

    store = InMemoryStorage()

    limiter = SlidingWindowCounter(
        limit=3,
        window_seconds=60
    )

    assert limiter.is_allowed(
        "user",
        store
    )[0]

    assert limiter.is_allowed(
        "user",
        store
    )[0]

    assert limiter.is_allowed(
        "user",
        store
    )[0]

    assert not limiter.is_allowed(
        "user",
        store
    )[0]

def test_counter_multi_user():

    store = InMemoryStorage()

    limiter = SlidingWindowCounter(
        limit=1,
        window_seconds=60
    )

    assert limiter.is_allowed(
        "user1",
        store
    )[0]

    assert limiter.is_allowed(
        "user2",
        store
    )[0]

def test_counter_metadata():

    store = InMemoryStorage()

    limiter = SlidingWindowCounter(
        limit=5,
        window_seconds=60
    )

    allowed, meta = limiter.is_allowed(
        "user",
        store
    )

    assert allowed

    assert meta["limit"] == 5

    assert "remaining" in meta

    assert "reset" in meta

if __name__ == "__main__":

    test_counter_basic()
    print("Basic test passed")

    test_counter_multi_user()
    print("Multi-user test passed")

    test_counter_metadata()
    print("Metadata test passed")

    print(
        "All Sliding Window Counter tests passed!"
    )