# -*- coding: utf-8 -*-

import arrow

from .base import MongoGreylistBaseTestCase
from ...test_models import TestModelsMixin

from mongrey.storage.mongo import models
from mongrey import constants
from mongrey import utils

class ModelsTestCase(TestModelsMixin, MongoGreylistBaseTestCase):
    
    def _drop_model(self, model):
        model.drop_collection()
    
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
        
        
        
        
        