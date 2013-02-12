from pyrts.core.cache.backends.redis.client import Redis, StrictRedis
from pyrts.core.cache.backends.redis.connection import (
    ConnectionPool,
    Connection,
    UnixDomainSocketConnection
)
from pyrts.core.cache.backends.redis.utils import from_url
from pyrts.core.cache.backends.redis.exceptions import (
    AuthenticationError,
    ConnectionError,
    DataError,
    InvalidResponse,
    PubSubError,
    RedisError,
    ResponseError,
    WatchError,
)

__version__ = '2.7.1'
VERSION = tuple(map(int, __version__.split('.')))

__all__ = [
    'Redis', 'StrictRedis', 'ConnectionPool',
    'Connection', 'UnixDomainSocketConnection',
    'RedisError', 'ConnectionError', 'ResponseError', 'AuthenticationError',
    'InvalidResponse', 'DataError', 'PubSubError', 'WatchError', 'from_url',
]
