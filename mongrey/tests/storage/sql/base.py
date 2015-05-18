# -*- coding: utf-8 -*-

import unittest
import os

from mongrey.storage.sql import models
from mongrey.utils import get_db_config
from mongrey import cache

from ...base import BaseTestCase

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', 'sql') != "sql", "Skip no sql tests")
class MongreyBaseTestCase(BaseTestCase):
    
    db_settings = {
        'host': 'sqlite:///../mongrey_test.db',
    } 
    
    def setUp(self):
        BaseTestCase.setUp(self)
        settings, storage = get_db_config(**self.db_settings)        
        models.configure_peewee(drop_before=True, **settings)
        self._cache = cache.configure_cache(cache_url='simple')                

    def tearDown(self):
        BaseTestCase.tearDown(self)
        if self._cache:
            self._cache.clear()

    
