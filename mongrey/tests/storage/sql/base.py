# -*- coding: utf-8 -*-

import unittest
import os

from mongrey.storage.sql import models
from mongrey import cache

from ...base import BaseTestCase

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', 'sql') != "sql", "Skip no sql tests")
class MongoGreylistBaseTestCase(BaseTestCase):
    
    peewee_settings = {
        'db_name': 'sqlite:///../mongrey_test.db',
        'db_options': {
            'threadlocals': True    #pour use with gevent patch
        }
    } 
    
    def setUp(self):
        BaseTestCase.setUp(self)
        self._cache = cache.configure_cache(cache_url='simple')                
        models.configure_peewee(drop_before=True, **self.peewee_settings)

    def tearDown(self):
        BaseTestCase.tearDown(self)
        if self._cache:
            self._cache.clear()
