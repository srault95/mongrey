# -*- coding: utf-8 -*-

import unittest

import sys
from mongrey import cache

try:
    import redis
    HAVE_REDIS = True
except ImportError:
    HAVE_REDIS = False
    pass

REDIS_TEST = HAVE_REDIS
if sys.platform.startswith("win32"):
    REDIS_TEST = False
    

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

    @unittest.skipUnless(REDIS_TEST, "Skip redis tests")    
    def test_redis_cache(self):

        self.assertIsNone(cache.cache)
        
        cache.configure_cache(cache_url='redis://localhost', cache_timeout=10)
        
        self.assertIsNotNone(cache.cache)
        
        cache.cache.set('key', 'value')
        
        value = cache.cache.get('key')
        
        self.assertIsNotNone(value)
        
        cache.remove_cache()
        
        self.assertIsNone(cache.cache)
