# -*- coding: utf-8 -*-

import unittest

from mongrey.storage.sql import models
from mongrey.storage.sql.policy import SqlPolicy as Policy
from mongrey.cache import remove_cache
from mongrey.server.core import command_start, get_store

from .base import MongreyBaseTestCase
from ...server.test_server import (NoRunServerMixin, 
                                   NoRunServerWithCacheMixin, 
                                   BaseRunServerMixin, 
                                   ServerRequestMixin,
                                   CheckOneRequestMixin,
                                   _DEFAULT_CONFIG)

class CheckOneRequestTestCase(CheckOneRequestMixin, MongreyBaseTestCase):
    
    def setUp(self):
        MongreyBaseTestCase.setUp(self)
        remove_cache()

    def _drop_model(self, model):
        return model.delete().execute()
        
    def _model_count(self, model):
        return model.select().count()

    def _get_policy(self, **kwargs):
        return Policy(**kwargs)

    def test_action_whitelisted(self):
        self._test_action_whitelisted(models)
    
    @unittest.skip("FIXME")
    def test_command_check(self):
        
        config = _DEFAULT_CONFIG.copy()
        config['db_settings']['host'] = 'sqlite:///mongrey_test.db'
        config.pop('country_ipv4')
        config.pop('country_ipv6')
        
        #---policy default with disabled greylisting        
        config['policy_settings']['greylist_enable'] = False
        self._test_command_check(models, **config)
    

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

    def test_get_store(self):
        config = _DEFAULT_CONFIG.copy()
        config['db_settings']['host'] = 'sqlite:///mongrey_test.db'
        policy_klass, _models = get_store(**config)
        self.assertTrue(issubclass(policy_klass, Policy))
        self.assertEquals(models, _models)

    def test_command_start(self):
        config = _DEFAULT_CONFIG.copy()
        config['db_settings']['host'] = 'sqlite:///mongrey_test.db'
        config.pop('country_ipv4')
        config.pop('country_ipv6')
        server = command_start(start_server=False, start_threads=False, **config)
        self.assertIsInstance(server._policy, Policy)

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

