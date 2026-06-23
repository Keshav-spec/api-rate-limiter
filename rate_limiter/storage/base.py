from abc import ABC, abstractmethod
from typing import Any


class StorageBackend(ABC):

    @abstractmethod
    def get(self, key: str) -> Any:
        pass

    @abstractmethod
    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None
    ) -> None:
        pass

    @abstractmethod
    def increment(
        self,
        key: str,
        ttl: int | None = None
    ) -> int:
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        pass