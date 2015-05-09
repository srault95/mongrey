# -*- coding: utf-8 -*-

import arrow

from .base import MongoGreylistBaseTestCase
from ...test_models import TestModelsMixin

from mongrey import constants
from mongrey import utils
from mongrey.storage.sql import models

class ModelsTestCase(TestModelsMixin, MongoGreylistBaseTestCase):
    
    def _drop_model(self, model):
        model.delete().execute()

    def test_create_greylist_entry(self):
        self._test_create_greylist_entry(models)
        
    def test_search_policy(self):
        self._test_search_policy(models)

    def test_search_whitelist(self):
        self._test_search_wblist(models.WhiteList)

    def test_search_blacklist(self):
        self._test_search_wblist(models.BlackList)

    def test_search_whitelist_cache(self):
        self._test_search_whitelist_cache(models)
        
    def test_greylist_metrics(self):
        self._test_greylist_metrics(models)
        
    
    def Xtest_create_greylist_entry(self):
        
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        self.assertEquals(doc.rejects, 1)
        self.assertIsNone(doc.expire_time)
        
        search = models.GreylistEntry.search_entry(key='key1')
        self.assertIsNotNone(search)
        self.assertEquals(search.key, 'key1')

        expire = search.expire(delta=60, now=doc.timestamp)
        self.assertEquals(expire, 60)

        now = arrow.utcnow().replace(hours=+1)
        expire = search.expire(delta=60, now=now.datetime)
        self.assertTrue(expire < 0)
        
        doc.accept(expire=86400, now=doc.timestamp)
        value = doc.expire_time - doc.timestamp
        self.assertEquals(value.total_seconds(), 86400)
        
        