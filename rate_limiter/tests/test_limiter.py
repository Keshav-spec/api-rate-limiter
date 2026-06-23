from rate_limiter.core.limiter import RateLimiter
from rate_limiter.algorithms import FixedWindow
from rate_limiter.storage import InMemoryStorage


def test_check():

    limiter = RateLimiter(
        algorithm=FixedWindow(
            limit=1,
            window_seconds=60
        ),
        storage=InMemoryStorage()
    )

    allowed, _ = limiter.check("user")

    assert allowed

def test_limit_decorator():

    limiter = RateLimiter(
        algorithm=FixedWindow(
            limit=1,
            window_seconds=60
        ),
        storage=InMemoryStorage()
    )

    @limiter.limit()
    def hello():
        return "hello"

    assert hello() == "hello"

