from rate_limiter.algorithms.fixed_window import FixedWindow
from rate_limiter.storage import InMemoryStorage


def test_fixed_window_metadata():

    store = InMemoryStorage()

    limiter = FixedWindow(
        limit=2,
        window_seconds=60
    )

    allowed, meta = limiter.is_allowed(
        "user1",
        store
    )

    assert allowed is True

    assert meta["limit"] == 2

    assert "remaining" in meta

    assert "reset" in meta

import time

from rate_limiter.algorithms.token_bucket import TokenBucket
from rate_limiter.storage import InMemoryStorage


def test_token_bucket():

    store = InMemoryStorage()

    limiter = TokenBucket(
        capacity=3,
        refill_rate=1
    )

    assert limiter.is_allowed("user1", store)[0] is True
    assert limiter.is_allowed("user1", store)[0] is True
    assert limiter.is_allowed("user1", store)[0] is True

    assert limiter.is_allowed("user1", store)[0] is False

    time.sleep(1.2)

    assert limiter.is_allowed("user1", store)[0] is True

def test_fixed_window_blocks_after_limit():

    store = InMemoryStorage()

    limiter = FixedWindow(
        limit=1,
        window_seconds=60
    )

    assert limiter.is_allowed("user", store)[0]

    assert not limiter.is_allowed("user", store)[0]

def test_fixed_window_multiple_users():

    store = InMemoryStorage()

    limiter = FixedWindow(
        limit=1,
        window_seconds=60
    )

    assert limiter.is_allowed("user1", store)[0]
    assert limiter.is_allowed("user2", store)[0]

def test_token_bucket_capacity():

    store = InMemoryStorage()

    limiter = TokenBucket(
        capacity=2,
        refill_rate=1
    )

    assert limiter.is_allowed("user", store)[0]
    assert limiter.is_allowed("user", store)[0]

    assert not limiter.is_allowed("user", store)[0]

def test_token_bucket_refill():

    store = InMemoryStorage()

    limiter = TokenBucket(
        capacity=1,
        refill_rate=1
    )

    assert limiter.is_allowed("user", store)[0]

    assert not limiter.is_allowed("user", store)[0]

    time.sleep(1.1)

    assert limiter.is_allowed("user", store)[0]

def test_token_bucket_multiple_users():

    store = InMemoryStorage()

    limiter = TokenBucket(
        capacity=1,
        refill_rate=1
    )

    assert limiter.is_allowed("user1", store)[0]
    assert limiter.is_allowed("user2", store)[0]

if __name__ == "__main__":

    test_fixed_window_metadata()
    print("Fixed Window passed")

    test_token_bucket()
    print("Token Bucket passed")

    test_fixed_window_blocks_after_limit()
    test_fixed_window_multiple_users()
    test_token_bucket_capacity()
    test_token_bucket_refill()
    test_token_bucket_multiple_users()

    print("All algorithm tests passed!")