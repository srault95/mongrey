# -*- coding: utf-8 -*-

from mongrey.storage.mongo import models
from mongrey.storage.mongo.policy import MongoPolicy as Policy
from mongrey.cache import remove_cache

from .base import MongoGreylistBaseTestCase
from ...test_server import NoRunServerMixin, BaseRunServerMixin, ServerRequestMixin

class NoRunServerTestCase(NoRunServerMixin, MongoGreylistBaseTestCase):
    
    def setUp(self):
        MongoGreylistBaseTestCase.setUp(self)
        remove_cache()

    def _drop_model(self, model):
        model.drop_collection()
        
    def _model_count(self, model):
        return model.objects.count()
    
    def _get_policy(self, **kwargs):
        return Policy(**kwargs)
    
    def test_purge_expire(self):
        self._test_purge_expire(models)
    
    def test_action_excludes(self):
        self._test_action_excludes()
        
    def test_action_private_bypass(self):
        self._test_action_private_bypass()
        
    def test_action_whitelisted(self):
        self._test_action_whitelisted(models)

    def test_action_blacklisted(self):
        self._test_action_blacklisted(models)
        
    def test_action_policy(self):
        self._test_action_policy(models)
        

class BaseRunServerTestCase(BaseRunServerMixin, MongoGreylistBaseTestCase):

    def _get_policy(self, **kwargs):
        return Policy(**kwargs)
    
    def setUp(self):
        MongoGreylistBaseTestCase.setUp(self)
        self._get_server()
        self.server.start()
        
    def tearDown(self):
        MongoGreylistBaseTestCase.tearDown(self)
        self.server.stop()
        
class RequestsTestCase(ServerRequestMixin, BaseRunServerTestCase):


    def test_sent_request(self):
        self._test_sent_request(models)
