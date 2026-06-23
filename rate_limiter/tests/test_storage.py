from rate_limiter.storage import InMemoryStorage


def test_set_get():

    store = InMemoryStorage()

    store.set(
        "user1",
        "hello"
    )

    assert store.get(
        "user1"
    ) == "hello"

import time

def test_expiry():

    store = InMemoryStorage()

    store.set(
        "user1",
        "hello",
        ttl=1
    )

    time.sleep(2)

    assert store.get(
        "user1"
    ) is None

def test_increment():

    store = InMemoryStorage()

    assert store.increment("user") == 1
    assert store.increment("user") == 2
    assert store.increment("user") == 3

def test_delete():

    store = InMemoryStorage()

    store.set("user", "hello")

    store.delete("user")

    assert store.get("user") is None

def test_increment_expiry():

    store = InMemoryStorage()

    store.increment("counter", ttl=1)

    time.sleep(2)

    assert store.get("counter") is None



if __name__ == "__main__":
    test_set_get()
    test_expiry()
    test_increment()
    test_increment_expiry()
    test_delete()

    print("All tests passed!")