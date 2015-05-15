# -*- coding: utf-8 -*-

from mongrey.storage.sql import models
from mongrey.storage.sql.policy import SqlPolicy as Policy
from mongrey.cache import remove_cache

from .base import MongreyBaseTestCase
from ...server.test_server import (NoRunServerMixin, 
                                   NoRunServerWithCacheMixin, 
                                   BaseRunServerMixin, 
                                   ServerRequestMixin)

class NoRunServerTestCase(NoRunServerMixin, MongreyBaseTestCase):

    def setUp(self):
        MongreyBaseTestCase.setUp(self)
        remove_cache()

    def _drop_model(self, model):
        return model.delete().execute()
        
    def _model_count(self, model):
        return model.select().count()

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

    def test_action_relay_denied(self):
        self._test_action_relay_denied(models)

    def test_action_spoofing(self):
        self._test_action_spoofing(models)
        
    def test_action_policy(self):
        self._test_action_policy(models)

class NoRunServerWithCacheTestCase(NoRunServerWithCacheMixin, MongreyBaseTestCase):
    
    def setUp(self):
        MongreyBaseTestCase.setUp(self)

    def _drop_model(self, model):
        return model.delete().execute()
        
    def _get_policy(self, **kwargs):
        return Policy(**kwargs)

    def test_cache_action_spoofing(self):
        self._test_cache_action_spoofing(models)
        
    def test_cache_action_outgoing(self):
        self._test_cache_action_outgoing(models)
    
    def test_cache_action_blacklisted(self):
        self._test_cache_action_blacklisted(models)

    def test_cache_action_whitelisted(self):
        self._test_cache_action_whitelisted(models)
        
    def test_cache_action_relay_denied(self):
        self._test_cache_action_relay_denied(models)
        
        
class BaseRunServerTestCase(BaseRunServerMixin, MongreyBaseTestCase):

    def setUp(self):
        MongreyBaseTestCase.setUp(self)
        self._get_server()
        self.server.start()
        
    def tearDown(self):
        MongreyBaseTestCase.tearDown(self)
        self.server.stop()
        
    def _get_policy(self, **kwargs):
        return Policy(**kwargs)

    def _drop_model(self, model):
        return model.delete().execute()
            
class RequestsTestCase(ServerRequestMixin, BaseRunServerTestCase):

    def test_sent_request(self):
        self._test_sent_request(models)

