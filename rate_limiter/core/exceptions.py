class RateLimitExceeded(Exception):

    def __init__(self, info):
        self.info = info
        super().__init__("Rate limit exceeded")