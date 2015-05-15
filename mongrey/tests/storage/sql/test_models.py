# -*- coding: utf-8 -*-

import arrow

from peewee import IntegrityError

from mongrey import constants
from mongrey import utils
from mongrey.storage.sql import models
from mongrey.exceptions import ValidationError

from .base import MongreyBaseTestCase
from ...test_models import TestModelsMixin

class ModelsTestCase(TestModelsMixin, MongreyBaseTestCase):

    def _drop_model(self, model):
        return model.delete().execute()
    
    def test_mynetwork(self):
        self._test_mynetwork(models, ValidationError, IntegrityError)
            
    def test_domain(self):
        self._test_domain(models, ValidationError, IntegrityError)
    
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
        
    def test_import_fixtures(self):
        self._test_import_fixtures(models)
        
    def test_export_fixtures(self):
        self._test_export_fixtures(models)
    
        