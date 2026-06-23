from fastapi import FastAPI

from rate_limiter.storage import (
    InMemoryStorage
)

from rate_limiter.algorithms import (
    FixedWindow
)

from rate_limiter.middleware import (
    FastAPIRateLimiter
)


app = FastAPI()

app.add_middleware(
    FastAPIRateLimiter,
    algorithm=FixedWindow(
        limit=3,
        window_seconds=60
    ),
    storage=InMemoryStorage()
)


@app.get("/")
def home():

    return {
        "message":
        "hello fastapi"
    }