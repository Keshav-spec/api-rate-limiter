import time
import threading

from .base import StorageBackend


class InMemoryStorage(StorageBackend):

    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.lock = threading.Lock()

    def _cleanup_if_expired(self, key):

        if key in self.expiry:

            if time.time() > self.expiry[key]:

                self.data.pop(key, None)
                self.expiry.pop(key, None)

    def get(self, key):

        with self.lock:

            self._cleanup_if_expired(key)

            return self.data.get(key)

    def set(self, key, value, ttl=None):

        with self.lock:

            self.data[key] = value

            if ttl is not None:
                self.expiry[key] = time.time() + ttl

    def increment(self, key, ttl=None):

        with self.lock:

            self._cleanup_if_expired(key)

            current = self.data.get(key, 0)

            current += 1

            self.data[key] = current

            if ttl is not None and key not in self.expiry:
                self.expiry[key] = time.time() + ttl

            return current

    def delete(self, key):

        with self.lock:

            self.data.pop(key, None)
            self.expiry.pop(key, None)