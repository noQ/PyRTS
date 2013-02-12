'''
Created on Jun 18, 2012

@author: Adrian Costia
'''

import time
import importlib
from pyrts.core.cache.memory import *
from pyrts.core.restexception import ServerParametersNotFound

def get_cache(backend, **kwargs):
    """
    Function to load a cache backend dynamically. This is flexible by design
    to allow different use cases:

    To load a backend that is pre-defined in the settings::
        cache = get_cache('default')
        
    To load a backend with its dotted import path,
    including arbitrary options::

        - REDIS -
        cache = get_cache('pyrts.core.utils.cache.redis.RedisCache', **{
            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 30,
        })
        
        - MEMCAHCED -
        cache = get_cache('pyrts.core.utils.cache.memcached.MemcachedCache', **{
            'LOCATION': '127.0.0.1:11211', 'TIMEOUT': 30,
        })

    """
    try:
        mod_path, cls_name = backend.rsplit('.', 1)
        mod = importlib.import_module(mod_path)
        backend_cls = getattr(mod, cls_name)
    except (AttributeError, ImportError), e:
        raise Exception(
            "Could not find backend '%s': %s" % (backend, e))
    location = kwargs.pop('LOCATION', '')
    return backend_cls(location, kwargs)
