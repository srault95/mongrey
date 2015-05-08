# -*- coding: utf-8 -*-

import unittest
import os

from mongoengine import connect

from mongrey.storage.mongo import models
from mongrey import cache

from ...base import BaseTestCase

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', 'mongo') != "mongo", "Skip no mongodb tests")
class MongoGreylistBaseTestCase(BaseTestCase):
    
    mongodb_settings = {
        'host': 'mongodb://localhost/greylist_test',
        'use_greenlets': True,
        'tz_aware': True,    
    }
    
    def setUp(self):
        BaseTestCase.setUp(self)        
        self._db = connect(**self.mongodb_settings)
        self._cache = cache.configure_cache(cache_url='simple')
        models.GreylistMetric.drop_collection()
        models.GreylistEntry.drop_collection()
        models.GreylistPolicy.drop_collection()
        models.WhiteList.drop_collection()
        models.BlackList.drop_collection()
    
    def tearDown(self):
        BaseTestCase.tearDown(self)
        if self._cache:
            self._cache.clear()
