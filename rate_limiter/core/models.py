from dataclasses import dataclass

@dataclass
class RateLimitInfo:
    allowed: bool
    limit: int
    remaining: int
    reset: int | None = None
    retry_after: float | None = None