from .in_memory import InMemoryStorage

try:
    from .redis_backend import RedisStorage
except ImportError:
    RedisStorage = None