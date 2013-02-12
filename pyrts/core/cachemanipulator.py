'''
Created on Oct 31, 2012

@author: adrian.costia
'''
import traceback
from pyrts.settings import CACHE
from pyrts.core.util import dict2object
from pyrts.core.cache.base import CacheHandler
from pyrts.core.serializers.base import MongoEncoder, MongoObject
from pyrts.settings import DEBUG_LEVEL

def get_token_from_cache(token_key):
    ''' get user token from cache '''
    token = None
    token_is_in_cache = CacheHandler(CACHE).exists(str(token_key))
    if token_is_in_cache:
        ''' read token from cache '''
        token = CacheHandler(CACHE).get_object(token_key)
        ''' transform dict to object '''
        if isinstance(token, dict):
            try:
                if DEBUG_LEVEL:
                    print "Get token from cache - " + str(token)
                token = dict2object(token)
            except:
                traceback.print_exc()
    return token

def save_token_in_cache(key, value, **kwargs):
    ''' save user token in cache '''
    cache_obj = CacheHandler(CACHE)
    cache_obj.set_object(key, value, **kwargs)
    ''' set expiration time for token '''
    if isinstance(value, dict):
        if value.has_key("expire_at"):
            if hasattr(cache_obj.get_cache_object(), "expire"):
                _expire_at = value.get("expire_at")
                cache_obj.expire(ttl=_expire_at)

def delete_from_cache(key, **kwargs):
    cache_obj = CacheHandler(CACHE)
    key_exists = cache_obj.exists(str(key))
    if key_exists:
        cache_obj.delete(str(key))

def get_from_cache(key):
    return CacheHandler(CACHE).get(key)

def save_in_cache(key, value, ttl=500):
    return CacheHandler(CACHE).set(key, value, ttl)
