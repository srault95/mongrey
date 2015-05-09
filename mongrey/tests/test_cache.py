# -*- coding: utf-8 -*-

import unittest

from mongrey import cache

try:
    import redis
    HAVE_REDIS = True
except ImportError:
    HAVE_REDIS = False
    pass    

class CacheTestCase(unittest.TestCase):
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        cache.cache = None
    
    def test_simple_cache(self):
        
        self.assertIsNone(cache.cache)
        
        cache.configure_cache(cache_url='simple', cache_timeout=10)
        
        self.assertIsNotNone(cache.cache)
        
        cache.cache.set('key', 'value')
        
        value = cache.cache.get('key')
        
        self.assertIsNotNone(value)
        
        cache.remove_cache()
        
        self.assertIsNone(cache.cache)

    @unittest.skipUnless(HAVE_REDIS, "Skip redis tests")    
    def test_redis_cache(self):

        self.assertIsNone(cache.cache)
        
        cache.configure_cache(cache_url='redis://localhost', cache_timeout=10)
        
        self.assertIsNotNone(cache.cache)
        
        cache.cache.set('key', 'value')
        
        value = cache.cache.get('key')
        
        self.assertIsNotNone(value)
        
        cache.remove_cache()
        
        self.assertIsNone(cache.cache)
