from fastapi import FastAPI
from fastapi.testclient import TestClient

from rate_limiter.storage import InMemoryStorage
from rate_limiter.algorithms import FixedWindow
from rate_limiter.middleware import FastAPIRateLimiter


def create_app():

    app = FastAPI()

    app.add_middleware(
        FastAPIRateLimiter,
        algorithm=FixedWindow(
            limit=2,
            window_seconds=60
        ),
        storage=InMemoryStorage()
    )

    @app.get("/")
    def home():
        return {"message": "ok"}

    return app


def test_fastapi_rate_limit():

    app = create_app()

    client = TestClient(app)

    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 429


def test_fastapi_headers():

    app = create_app()

    client = TestClient(app)

    response = client.get("/")

    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


if __name__ == "__main__":

    test_fastapi_rate_limit()
    print("Rate limit test passed")

    test_fastapi_headers()
    print("Header test passed")

    print("All FastAPI middleware tests passed")