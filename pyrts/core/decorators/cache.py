'''
Created on Oct 30, 2012

@author: adrian.costia

'''
import time
import traceback
from functools import wraps, update_wrapper, WRAPPER_ASSIGNMENTS
from pyrts.settings import CACHE, DEBUG_LEVEL
from pyrts.core.cachemanipulator import get_from_cache, save_in_cache
from pyrts.core.const import five_minutes_in_seconds

def available_attrs(fn):
    """
    Return the list of functools-wrappable attributes on a callable.
    This is required as a workaround for http://bugs.python.org/issue3445.
    """
    return tuple(a for a in WRAPPER_ASSIGNMENTS if hasattr(fn, a))

def cache(**kwargs):
    TTL_KEY     ="ttl"
    CACHE_KEY   = "cache_key" 
    '''
        CACHE ANNOTATION
        
            - Example to use:
                
                @cache(cache_key='country')
                def get_cities(self, fields=['name','district'], **kwargs):
                    ...
                    ...
                    return response
    '''
    def make_request_key(key, kwargs):
        '''
            Generate cache key. Example cache key: country_ROM
            Return None if arg cache_key (or len) not found in the request
        '''
        if kwargs.has_key(key):
            _value = kwargs.get(key)
            if len(_value) > 0:
                return "%s_%s" % (key, _value)
        return None
    
    def get_cache_key(kwargs):
        '''
            Get value of arg 'cache_key'. 
        '''
        if kwargs.has_key(CACHE_KEY):
            _cache_key = kwargs.get(CACHE_KEY)
            if len(_cache_key) > 0:
                return _cache_key
        return None
        
    def get_key_ttl(kwargs):
        if kwargs.has_key(TTL_KEY):
            _ttl_key = kwargs.get(TTL_KEY)
            if isinstance(_ttl_key, int):
                if int(_ttl_key) > 0:
                    return _ttl_key
        return 0
    
    def _cache_controller(viewfunc):
        '''
            GET/SET value in cache based on 'cache_key'  
        '''
        def _cache_controlled(*args, **kw):
            _request_key = None
            ''' search for cache key in the @cache annotation. return  key value '''
            _cache_key = get_cache_key(kwargs)
            if _cache_key:
                ''' generate request key based on cache key. returns None if nil '''
                _request_key = make_request_key(_cache_key, kw)
                if _request_key:
                    start_execution_time = time.time()
                    ''' get value from cache '''
                    cache_response = get_from_cache(_request_key)
                    end_execution_time = time.time()
                    if cache_response:
                        ''' calculate execution time '''
                        if DEBUG_LEVEL:
                            dt = int((end_execution_time - start_execution_time)*1000)
                            if dt>2:
                                print "WARNING: To get value from cache took "+str(dt)+" msecs to execute"
                        return cache_response
            ''' return original function ''' 
            response = viewfunc(*args, **kw)
            ''' save key in cache if key is valid'''
            if _request_key:
                ttl = get_key_ttl(kwargs)
                if ttl == 0:
                    ttl = five_minutes_in_seconds
                save_in_cache(_request_key, response, ttl)
            return response
        _cache_controller.__doc__ = viewfunc.__doc__        
        return wraps(viewfunc, assigned=available_attrs(viewfunc))(_cache_controlled)
    return _cache_controller
