from abc import ABC, abstractmethod
from typing import Any


class RateLimitAlgorithm(ABC):

    @abstractmethod
    def is_allowed(
        self,
        key: str,
        store: Any
    ) -> tuple[bool, dict[str, Any]]:
        pass