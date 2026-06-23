from rate_limiter.storage import InMemoryStorage
from rate_limiter.algorithms import (
    FixedWindow
)


def test_integration():

    store = InMemoryStorage()

    limiter = FixedWindow(
        limit=2,
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

    assert not limiter.is_allowed(
        "user",
        store
    )[0]


if __name__ == "__main__":

    test_integration()

    print(
        "Integration test passed"
    )