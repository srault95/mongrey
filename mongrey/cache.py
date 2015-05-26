# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

cache = None

class Cache(object):
    """
    Pour cache Redis:
        global cache
        cache = Cache('redis', default_timeout=300, host='192.168.0.188')
    
    Pour cache simple:
        global cache
        cache = Cache('simple', default_timeout=300)
    
    Pour désactiver le cache:
        global cache
        cache = Cache()
    
    """
    DEFAULT_KEY_PREFIX = 'mongrey-cache'
    
    def __init__(self, 
                 cache_url='simple', 
                 cache_timeout=300,
                 cache_prefix=None, 
                 ):
        
        self.cache_timeout = cache_timeout

        self.cache = None
        
        self.cache_prefix = cache_prefix or self.DEFAULT_KEY_PREFIX 
        
        if cache_url == 'simple':
            self._configure_cache_simple()
        elif cache_url.startswith('redis'):
            self._configure_cache_redis(cache_url)
        else:
            self._configure_null_cache()        
            
    def _configure_null_cache(self):
        from werkzeug.contrib.cache import NullCache
        self.cache = NullCache(default_timeout=self.cache_timeout)
        
    def _configure_cache_simple(self):
        from werkzeug.contrib.cache import SimpleCache
        #threshold=500, cache_timeout=300
        #threshold : the maximum number of items the cache stores before
        self.cache = SimpleCache(default_timeout=self.cache_timeout)
        
    def _configure_cache_redis(self, url):
        from werkzeug.contrib.cache import RedisCache
        from redis import from_url

        #'cache_url': 'redis://localhost:6379',
        
        client = from_url(url)
        
        self.cache = RedisCache(host=client, 
                                default_timeout=self.cache_timeout, 
                                key_prefix=self.cache_prefix
                                )
    
    
    def get(self, *args, **kwargs):
        "Proxy function for internal cache object."
        return self.cache.get(*args, **kwargs)

    def set(self, key, value, timeout=None):
        "Proxy function for internal cache object."
        if not key:
            raise Exception("Not valid key")
        
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("set cache key[%s]" % key)
        self.cache.set(key, value, timeout=timeout)

    def add(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.add(*args, **kwargs)

    def delete(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.delete(*args, **kwargs)

    def delete_many(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.delete_many(*args, **kwargs)

    def clear(self):
        "Proxy function for internal cache object."
        self.cache.clear()

    def get_many(self, *args, **kwargs):
        "Proxy function for internal cache object."
        return self.cache.get_many(*args, **kwargs)

    def set_many(self, *args, **kwargs):
        "Proxy function for internal cache object."
        self.cache.set_many(*args, **kwargs)

    


def configure_cache(**kwargs):
    global cache
    cache = Cache(**kwargs)
    return cache

def remove_cache():
    global cache
    cache = None