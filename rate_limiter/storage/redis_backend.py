"""
TODO Phase 3:

Token Bucket updates must use
a Redis Lua script to guarantee
atomic read-modify-write operations.

Without Lua scripts concurrent
requests can exceed limits due
to race conditions.
"""
import redis

from .base import StorageBackend


class RedisStorage(StorageBackend):

    def __init__(self, redis_url):

        self.client = redis.from_url(redis_url)

    def get(self, key):

        return self.client.get(key)

    def set(self, key, value, ttl=None):

        if ttl:
            self.client.setex(
                key,
                ttl,
                value
            )
        else:
            self.client.set(
                key,
                value
            )

    def increment(self, key, ttl=None):

        value = self.client.incr(key)

        if ttl:
            self.client.expire(
                key,
                ttl
            )

        return value

    def delete(self, key):

        self.client.delete(key)