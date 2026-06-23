from flask import Flask

from rate_limiter.storage import (
    InMemoryStorage
)

from rate_limiter.algorithms import (
    FixedWindow
)

from rate_limiter.middleware import (
    FlaskRateLimiter
)


app = Flask(__name__)

limiter = FlaskRateLimiter(
    algorithm=FixedWindow(
        limit=3,
        window_seconds=60
    ),
    storage=InMemoryStorage()
)


@app.route("/")
@limiter.limit()
def home():

    return {
        "message":
        "hello world"
    }


if __name__ == "__main__":
    app.run(debug=True)