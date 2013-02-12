'''
Memcached cache backend

Created on Nov 1, 2012
@author: adrian.costia
'''

import time
from threading import local
from pyrts.core.cache.base import BaseCache
from pyrts.core.cache.backends.memcached.memcache import *
from pyrts.core.util import import_module
from pyrts.core.const import one_month_in_seconds

class BaseMemcachedCache(BaseCache):
    def __init__(self, server, params, value_not_found_exception):
        super(BaseMemcachedCache, self).__init__(params)
        if isinstance(server, basestring):
            self._servers = server.split(';')
        else:
            self._servers = server

        self.LibraryValueNotFoundException = value_not_found_exception
        self._options = params.get('OPTIONS', None)

    @property
    def _cache(self):
        """
        Implements transparent thread-safe access to a memcached client.
        """
        if getattr(self, '_client', None) is None:
            self._client = Client(self._servers)

        return self._client

    def _get_memcache_timeout(self, timeout):
        """
        Memcached deals with long (> 30 days) timeouts in a special
        way. Call this function to obtain a safe value for your timeout.
        """
        timeout = timeout or self.default_timeout
        if timeout > 2592000: # 60*60*24*30, 30 days
            # See http://code.google.com/p/memcached/wiki/FAQ
            # "You can set expire times up to 30 days in the future. After that
            # memcached interprets it as a date, and will expire the item after
            # said date. This is a simple (but obscure) mechanic."
            #
            # This means that we have to switch to absolute timestamps.
            timeout += int(time.time())
        return timeout

    def add(self, key, value, timeout=0, version=None):
        key = self.make_key(str(key), version=version)
        return self._cache.add(key, value, self._get_memcache_timeout(timeout))

    def get(self, key, default=None, version=None):
        key = self.make_key(str(key), version=version)
        val = self._cache.get(key)
        if val is None:
            return default
        return val

    def exists(self, key, default=None, version=None):
        return self.get(key, default, version)
        
    def set(self, key, value, timeout=0, version=None):
        key = self.make_key(str(key), version=version)
        self._cache.set(key, value, self._get_memcache_timeout(timeout))

    def set_json(self, key, value, **kwargs):
        timeout = one_month_in_seconds
        version = None
        if kwargs.has_key("ttl"):
            timeout = int(kwargs.get("ttl"))
        if kwargs.has_key("version"):
            version = int(kwargs.get("version"))
        key = self.make_key(str(key), version=version)
        self._cache.set(key, value, self._get_memcache_timeout(timeout))
    
    def get_json(self, key, default=None, version=None):
        return self.get(key, default, version)

    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self._cache.delete(key)

    def get_many(self, keys, version=None):
        new_keys = map(lambda x: self.make_key(x, version=version), keys)
        ret = self._cache.get_multi(new_keys)
        if ret:
            _ = {}
            m = dict(zip(new_keys, keys))
            for k, v in ret.items():
                _[m[k]] = v
            ret = _
        return ret

    def close(self, **kwargs):
        self._cache.disconnect_all()

    def incr(self, key, delta=1, version=None):
        key = self.make_key(key, version=version)
        try:
            val = self._cache.incr(key, delta)

        # python-memcache responds to incr on non-existent keys by
        # raising a ValueError, pylibmc by raising a pylibmc.NotFound
        # and Cmemcache returns None. In all cases,
        # we should raise a ValueError though.
        except self.LibraryValueNotFoundException:
            val = None
        if val is None:
            raise ValueError("Key '%s' not found" % key)
        return val

    def decr(self, key, delta=1, version=None):
        key = self.make_key(key, version=version)
        try:
            val = self._cache.decr(key, delta)

        # python-memcache responds to incr on non-existent keys by
        # raising a ValueError
        # we should raise a ValueError though.
        except self.LibraryValueNotFoundException:
            val = None
        if val is None:
            raise ValueError("Key '%s' not found" % key)
        return val

    def set_many(self, data, timeout=0, version=None):
        safe_data = {}
        for key, value in data.items():
            key = self.make_key(key, version=version)
            safe_data[key] = value
        self._cache.set_multi(safe_data, self._get_memcache_timeout(timeout))

    def delete_many(self, keys, version=None):
        l = lambda x: self.make_key(x, version=version)
        self._cache.delete_multi(map(l, keys))

    def clear(self):
        self._cache.flush_all()

class MemcachedCache(BaseMemcachedCache):
    "An implementation of a cache binding using python-memcached"
    def __init__(self, server, params):
        super(MemcachedCache, self).__init__(server, params, value_not_found_exception=ValueError)
