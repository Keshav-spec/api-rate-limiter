from functools import wraps
class RateLimiter:

    def __init__(
        self,
        algorithm,
        storage,
        key_func=None
    ):
        self.algorithm = algorithm
        self.storage = storage
        self.key_func = key_func

    def check(self, key):
        return self.algorithm.is_allowed(
            key,
            self.storage
        )


    def limit(self):

        def decorator(func):

            @wraps(func)
            def wrapper(*args, **kwargs):

                allowed, meta = self.check("global")

                if not allowed:
                    raise Exception(
                        "Rate limit exceeded"
                    )

                return func(*args, **kwargs)

            return wrapper

        return decorator