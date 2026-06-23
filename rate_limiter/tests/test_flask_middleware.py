from flask import Flask

from rate_limiter.storage import InMemoryStorage
from rate_limiter.algorithms import FixedWindow
from rate_limiter.middleware import FlaskRateLimiter


def create_app():

    app = Flask(__name__)

    limiter = FlaskRateLimiter(
        algorithm=FixedWindow(
            limit=2,
            window_seconds=60
        ),
        storage=InMemoryStorage()
    )

    @app.route("/")
    @limiter.limit()
    def home():
        return {"message": "ok"}

    return app


def test_flask_rate_limit():

    app = create_app()

    client = app.test_client()

    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 200
    assert client.get("/").status_code == 429


def test_flask_headers():

    app = create_app()

    client = app.test_client()

    response = client.get("/")

    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert "X-RateLimit-Reset" in response.headers


if __name__ == "__main__":

    test_flask_rate_limit()
    print("Rate limit test passed")

    test_flask_headers()
    print("Header test passed")

    print("All Flask middleware tests passed")