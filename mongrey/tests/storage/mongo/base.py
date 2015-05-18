# -*- coding: utf-8 -*-

import unittest
import os

from mongoengine import connect

from mongrey.storage.mongo import models
from mongrey.utils import get_db_config
from mongrey import cache

from ...base import BaseTestCase

def drop_all():
    models.User.drop_collection()
    models.GreylistMetric.drop_collection()
    models.GreylistEntry.drop_collection()
    models.Policy.drop_collection()
    models.WhiteList.drop_collection()
    models.BlackList.drop_collection()
    models.Domain.drop_collection()
    models.Mynetwork.drop_collection()
    models.Mailbox.drop_collection()
    

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', 'mongo') != "mongo", "Skip no mongodb tests")
class MongreyBaseTestCase(BaseTestCase):

    db_settings = {
        'host': 'mongodb://localhost/mongrey_test',
    }
    
    def setUp(self):
        BaseTestCase.setUp(self)
        settings, storage = get_db_config(**self.db_settings)
        self._db = connect(**settings)
        self._cache = cache.configure_cache(cache_url='simple')
        drop_all()
    
    def tearDown(self):
        BaseTestCase.tearDown(self)
        if self._cache:
            self._cache.clear()
    
