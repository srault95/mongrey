# -*- coding: utf-8 -*-

import unittest
import arrow

from mongoengine import ValidationError, NotUniqueError

from mongrey.storage.mongo import models
from mongrey import constants
from mongrey import utils

from .base import MongreyBaseTestCase
from ...test_models import TestModelsMixin

class ModelsTestCase(TestModelsMixin, MongreyBaseTestCase):
    
    def _drop_model(self, model):
        model.drop_collection()

    def _model_count(self, model):
        return model.objects.count()
    
    def _get_id(self, model):
        return model.pk

    def test_model_api(self):
        self._test_model_api(models, ValidationError, NotUniqueError)

    def test_domain(self):
        self._test_domain(models, ValidationError, NotUniqueError)
        
    def test_mailbox(self):
        self._test_mailbox(models, ValidationError, NotUniqueError)

    def test_mynetwork(self):
        self._test_mynetwork(models, ValidationError, NotUniqueError)
            
    def test_domain_slug(self):
        self._test_domain_slug(models)

    def test_mailbox_slug(self):
        self._test_mailbox_slug(models)
        
    def test_mynetwork_slug(self):
        self._test_mynetwork_slug(models)
        
    def test_policy_slug(self):
        self._test_policy_slug(models)
        
    def test_whitelist_slug(self):
        self._test_wblist_slug(models.WhiteList)

    def test_whitelist_slug(self):
        self._test_wblist_slug(models.BlackList)
        
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
        
    @unittest.skip("TODO")
    def test_greylist_metrics(self):
        self._test_greylist_metrics(models)
        
    def test_import_fixtures(self):
        self._test_import_fixtures(models)
        
    def test_export_fixtures(self):
        self._test_export_fixtures(models)
        
    @unittest.skip("TODO")
    def test_create_fixtures(self):
        from ...fixtures import fixtures
        self._drop_model(models.GreylistEntry)
        results = fixtures(models)
        count = self._model_count(models.GreylistEntry)
        print "results : ", results
        print "count : ", count
                