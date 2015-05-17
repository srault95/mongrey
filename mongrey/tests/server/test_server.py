# -*- coding: utf-8 -*-

import json
import logging
import unittest
import os
from StringIO import StringIO

import yaml

import gevent
import arrow

from mongrey import constants
from mongrey.server.core import PolicyServer, logger as server_logger
from mongrey.server.core import DEFAULT_CONFIG as SERVER_CONFIG
from mongrey.server.core import options, main
from mongrey.server.core import command_start
from mongrey import utils
from mongrey.exceptions import ConfigurationError

from ..utils import protocol_yaml_TO_dict, send_policy, get_free_port
from ..base import BaseTestCase

_DEFAULT_CONFIG = {
    'settings_path': None,
    'fixtures_path': None,
    'host': '127.0.0.1',
    'port': 9999,
    'allow_hosts': ['127.0.0.1', '::1'],
    'security_by_host': True,
    'spawn': 50,
    'backlog': 256,
    'connection_timeout': 10.0,
    'error_action': 'DUNNO',
    'close_socket': False,    
    'no_stress': False,
    'stats_enable': True,    
    'stats_interval': 30.0,
    'purge_enable': True,
    'purge_interval': 60.0,
    'metrics_enable': True,
    'metrics_interval': 60.0 * 5,
    'debug': False,
    'verbose': 1,
    'no_verify_protocol': False,
    
    'db_settings': {
        'host': 'sqlite:///mongrey.db',
    },

    'cache_settings': {
        'cache_url': 'simple',
        'cache_timeout': 300,    
    },
                                       
    'country_ipv4': None,
    'country_ipv6': None,

    'policy_settings': {
        'blacklist_enable': True,
        'domain_vrfy': False,       
        'mynetwork_vrfy': False,       
        'spoofing_enable': False,       
        'greylist_enable': True,                        
        'greylist_key': constants.GREY_KEY_MED,
        'greylist_remaining': 20,
        'greylist_expire': 35*86400,
        'greylist_excludes': [],
        'greylist_private_bypass': True
        
    }
                  
}


class NoRunServerTestCase(BaseTestCase):
    
    #TODO: command_fixtures_import
    #TODO: command_fixtures_export
    #TODO: command_load_settings
    
    
    @unittest.skipIf('TRAVIS' in os.environ, "Skip Travis")        
    def test_default_config(self):
        self.maxDiff = None
        
        _default_config = _DEFAULT_CONFIG.copy()
        _default_config['db_settings'] = SERVER_CONFIG['db_settings']
        _default_config['cache_settings'] = SERVER_CONFIG['cache_settings']        
        self.assertDictEqual(_default_config, SERVER_CONFIG)

    def test_configuration_from_yaml(self):
        
        change_config = """
        allow_hosts: ['1.1.1.1']
        db_settings:
          host: mongodb://host/db
        """
        
        config = utils.load_yaml_config(settings=StringIO(change_config), default_config=_DEFAULT_CONFIG.copy())
        
        self.assertEquals(config['allow_hosts'], ['1.1.1.1'])
        self.assertEquals(config['db_settings']['host'], 'mongodb://host/db')
        self.assertEquals(config['port'], 9999)
                
    def test_security_disable(self):
        u"""Disable security by ip"""
        
        server = PolicyServer(host="127.0.0.1", port=9999, security_by_host=False)
        self.assertTrue(server._security_check(("2.2.2.2",)))
    
    def test_allow_deny(self):
        u"""Allow/Deny tests"""

        server_logger.handlers = [logging.StreamHandler(self.log)]
        
        server = PolicyServer(host="127.0.0.1", port=9999,
                              security_by_host=True,
                              allow_hosts=['1.1.1.1', '10.10.1.0/24'])

        self.assertTrue(server._security_check(("1.1.1.1",)))
        
        self.assertFalse(server._security_check(("2.2.2.2",)))
        self.assertInLog("reject host [2.2.2.2]")

        self.assertTrue(server._security_check(("10.10.1.1",)))
        
    
class NoRunServerMixin:
    
    def _drop_model(self, model):
        raise NotImplementedError()
    
    def _model_count(self, model):
        raise NotImplementedError()
    
    def _get_policy(self, **kwargs):
        raise NotImplementedError()

    def _test_purge_expire(self, models):

        policy = self._get_policy(purge_interval=0.1)
        
        back_datetime = arrow.utcnow().replace(hours=-1).datetime
        models.GreylistEntry.create_entry(key='1.1.1.1', expire_time=back_datetime)
        
        green = gevent.spawn(policy.task_purge_expire, run_once=True)
        gevent.joinall([green], timeout=1.1)
        #gevent.kill(green)
        self.assertEquals(self._model_count(models.GreylistEntry), 0)
        
        back_datetime = arrow.utcnow().replace(hours=-25).datetime
        models.GreylistEntry.create_entry(key='1.1.1.1', timestamp=back_datetime)
        green = gevent.spawn(policy.task_purge_expire, run_once=True)
        gevent.joinall([green], timeout=1.1)
        #gevent.kill(green)
        self.assertEquals(self._model_count(models.GreylistEntry), 0)
        
        back_datetime = arrow.utcnow().replace(hours=-10).datetime
        #models.GreylistEntry(key='1.1.1.1', timestamp=back_datetime, protocol="").save()
        models.GreylistEntry.create_entry(key='1.1.1.1', timestamp=back_datetime)
        green = gevent.spawn(policy.task_purge_expire, run_once=True)
        gevent.joinall([green], timeout=1.1)
        #gevent.kill(green)
        self.assertEquals(self._model_count(models.GreylistEntry), 1)

    def _test_action_excludes(self):
        
        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        policy = self._get_policy(greylist_excludes=['1.1.1.1'])
        
        actions = policy.check_actions(protocol)
        
        self.assertEquals(actions[0], "DUNNO exclude filtering [1.1.1.1]")

    def _test_action_private_bypass(self):

        protocol = {
            'instance': '123',
            'client_address': '192.168.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }

        policy = self._get_policy(greylist_private_bypass=True)
        
        actions = policy.check_actions(protocol)
        
        self.assertEquals(actions[0], "DUNNO private address [192.168.1.1]")
        
    def _test_action_whitelisted(self, models):

        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr',
            'helo_name': "mx1.example.net",
        }

        policy = self._get_policy()
        
        models.WhiteList(field_name='client_address', value='1.1.1.1').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [1.1.1.1]")

        self._drop_model(models.WhiteList)

        models.WhiteList(field_name='helo_name', value='mx1.example.net').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [mx1.example.net]")

        self._drop_model(models.WhiteList)

        models.WhiteList(field_name='country', value='fr').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [fr]")

        self._drop_model(models.WhiteList)
        
        models.WhiteList(field_name='sender', value='.*@example.net').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [sender@example.net]")
        
        self._drop_model(models.WhiteList)
        
        models.WhiteList(field_name='sender', value='sender@example.net').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [sender@example.net]")

        self._drop_model(models.WhiteList)
        
        models.WhiteList(field_name='recipient', value='.*@example.org').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [rcpt@example.org]")
        
        self._drop_model(models.WhiteList)
        
        models.WhiteList(field_name='recipient', value='rcpt@example.org').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [rcpt@example.org]")

    def _test_action_blacklisted(self, models):
        
        #TODO: test avec blacklist disable
        
        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr',
            'helo_name': "mx1.example.net",
        }

        policy = self._get_policy(blacklist_enable=True)
        
        models.BlackList(field_name='client_address', value='1.1.1.1').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [1.1.1.1] - %s#554" % constants.ERRORS_URL_BASE)

        self._drop_model(models.BlackList)

        models.BlackList(field_name='helo_name', value='mx1.example.net').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [mx1.example.net] - %s#554" % constants.ERRORS_URL_BASE)

        self._drop_model(models.BlackList)

        models.BlackList(field_name='country', value='fr').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [fr] - %s#554" % constants.ERRORS_URL_BASE)

        self._drop_model(models.BlackList)
        
        models.BlackList(field_name='sender', value='.*@example.net').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [sender@example.net] - %s#554" % constants.ERRORS_URL_BASE)
        
        self._drop_model(models.BlackList)
        
        models.BlackList(field_name='sender', value='sender@example.net').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [sender@example.net] - %s#554" % constants.ERRORS_URL_BASE)

        self._drop_model(models.BlackList)
        
        models.BlackList(field_name='recipient', value='.*@example.org').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [rcpt@example.org] - %s#554" % constants.ERRORS_URL_BASE)
        
        self._drop_model(models.BlackList)
        
        models.BlackList(field_name='recipient', value='rcpt@example.org').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [rcpt@example.org] - %s#554" % constants.ERRORS_URL_BASE)
        
        self._drop_model(models.BlackList)

    def _test_action_relay_denied(self, models):

        policy = self._get_policy(blacklist_enable=False,
                                  domain_vrfy=True,
                                  mynetwork_vrfy=True,
                                  spoofing_enable=False,
                                  greylist_enable=False)

        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 relay denied - %s#554" % constants.ERRORS_URL_BASE)
        
        models.Mynetwork(value="1.1.1.1").save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO outgoing bypass")
        
        self._drop_model(models.Mynetwork)
        
        models.Mynetwork(value="1.1.1.0/24").save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO outgoing bypass")
        
        self._drop_model(models.Mynetwork)

        models.Domain(name="example.org").save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO")
        
        self._drop_model(models.Domain)

    def _test_action_spoofing(self, models):

        policy = self._get_policy(blacklist_enable=False,
                                  domain_vrfy=True,
                                  mynetwork_vrfy=True,
                                  spoofing_enable=True,
                                  greylist_enable=False)

        protocol = {
            'instance': '123',
            'client_address': '2.2.2.2',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        models.Domain(name="example.net").save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 spoofing [sender@example.net] - %s#554" % constants.ERRORS_URL_BASE)
        
        self._drop_model(models.Domain)

    def _test_action_policy(self, models):

        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'helo_name': "unknow",
            'country': 'fr',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        models.Policy(name="country-fr",
                      mynetwork_vrfy=False,
                      domain_vrfy=False,
                      spoofing_enable=False,
                      greylist_enable=True,
                      greylist_key=constants.GREY_KEY_VERY_LOW,
                      field_name='country', 
                      value='FR').save()
        
        policy = self._get_policy()

        actions = policy.check_actions(protocol)
        self.assertTrue(actions[0].startswith('450 4.2.0 Greylisted for'))
        self.assertTrue(actions[0].endswith("policy[country-fr] - %s#greylisted" % constants.ERRORS_URL_BASE))
        
        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_VERY_LOW)
        greylist_entry = models.GreylistEntry.search_entry(key=key)
        self.assertIsNotNone(greylist_entry)
        
        self._drop_model(models.GreylistEntry)
        self._drop_model(models.Policy)
        
        models.Policy(name="cloud-partner",
                      mynetwork_vrfy=False,
                      domain_vrfy=False,
                      spoofing_enable=False,
                      greylist_enable=True,
                      greylist_key=constants.GREY_KEY_SPECIAL,
                      field_name='recipient', 
                      value='.*@example.org').save()
        
        actions = policy.check_actions(protocol)
        self.assertTrue(actions[0].startswith('450 4.2.0 Greylisted for'))
        self.assertTrue(actions[0].endswith("policy[cloud-partner] - %s#greylisted" % constants.ERRORS_URL_BASE))
        
        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_SPECIAL)
        greylist_entry = models.GreylistEntry.search_entry(key=key)
        self.assertIsNotNone(greylist_entry)


class NoRunServerWithCacheMixin:

    def _test_cache_action_blacklisted(self, models):
        
        self.assertIsNotNone(self._cache)
        self._cache.clear()
        
        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr',
            'helo_name': "mx1.example.net",
        }

        policy = self._get_policy(blacklist_enable=True)
        
        models.BlackList(field_name='client_address', value='1.1.1.1').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 blacklisted [1.1.1.1] - %s#554" % constants.ERRORS_URL_BASE)
        
        uid = utils.get_uid(protocol)
        cache_value = self._cache.get(uid)
        self.assertIsNotNone(cache_value)
        self.assertTrue(cache_value['is_blacklist'])
        self.assertEquals(cache_value['action'], "554 5.7.1 blacklisted [1.1.1.1] - %s#554" % constants.ERRORS_URL_BASE)

    def _test_cache_action_whitelisted(self, models):
        
        self.assertIsNotNone(self._cache)
        self._cache.clear()
        
        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr',
            'helo_name': "mx1.example.net",
        }

        policy = self._get_policy()
        
        models.WhiteList(field_name='client_address', value='1.1.1.1').save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO whitelisted [1.1.1.1]")

        self._drop_model(models.WhiteList)
        
        uid = utils.get_uid(protocol)
        cache_value = self._cache.get(uid)
        self.assertIsNotNone(cache_value)
        self.assertTrue(cache_value['is_whitelist'])
        self.assertEquals(cache_value['action'], "DUNNO whitelisted [1.1.1.1]")
        
    def _test_cache_action_relay_denied(self, models):

        self.assertIsNotNone(self._cache)
        self._cache.clear()

        policy = self._get_policy(blacklist_enable=False,
                                  domain_vrfy=True,
                                  mynetwork_vrfy=True,
                                  spoofing_enable=False,
                                  greylist_enable=False)

        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 relay denied - %s#554" % constants.ERRORS_URL_BASE)
        
        uid = utils.get_uid(protocol)
        cache_value = self._cache.get(uid)
        self.assertIsNotNone(cache_value)
        self.assertTrue(cache_value['is_relay_denied'])
        self.assertEquals(cache_value['action'], "554 5.7.1 relay denied - %s#554" % constants.ERRORS_URL_BASE)

    def _test_cache_action_outgoing(self, models):

        self.assertIsNotNone(self._cache)
        self._cache.clear()

        policy = self._get_policy(blacklist_enable=False,
                                  domain_vrfy=True,
                                  mynetwork_vrfy=True,
                                  spoofing_enable=False,
                                  greylist_enable=False)

        protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        models.Mynetwork(value="1.1.1.1").save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "DUNNO outgoing bypass")

        self._drop_model(models.Mynetwork)
        
        uid = utils.get_uid(protocol)
        cache_value = self._cache.get(uid)
        self.assertIsNotNone(cache_value)
        self.assertTrue(cache_value['is_outgoing'])
        self.assertEquals(cache_value['action'], "DUNNO outgoing bypass")
        
    def _test_cache_action_spoofing(self, models):

        self.assertIsNotNone(self._cache)
        self._cache.clear()

        policy = self._get_policy(blacklist_enable=False,
                                  domain_vrfy=True,
                                  mynetwork_vrfy=True,
                                  spoofing_enable=True,
                                  greylist_enable=False)

        protocol = {
            'instance': '123',
            'client_address': '2.2.2.2',
            'client_name': 'unknow',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        
        models.Domain(name="example.net").save()
        actions = policy.check_actions(protocol)
        self.assertEquals(actions[0], "554 5.7.1 spoofing [sender@example.net] - %s#554" % constants.ERRORS_URL_BASE)
        
        self._drop_model(models.Domain)
        
        uid = utils.get_uid(protocol)
        cache_value = self._cache.get(uid)
        self.assertIsNotNone(cache_value)
        self.assertTrue(cache_value['is_spoofing'])
        self.assertEquals(cache_value['action'], "554 5.7.1 spoofing [sender@example.net] - %s#554" % constants.ERRORS_URL_BASE)




class BaseRunServerMixin:

    def _get_policy(self, **kwargs):
        raise NotImplementedError()

    def _get_config(self):
        policy_settings={
            'greylist_key': constants.GREY_KEY_MED,       
            'greylist_remaining': 1,
            'greylist_expire': 3600,
            'greylist_excludes': [],
            'greylist_private_bypass': False,                         
        }

        policy = self._get_policy(**policy_settings)
        
        return dict(policy=policy, 
                    error_action="DUNNO ERROR[%s]" % os.getpid())
            
    def _get_server(self):
        self.host, self.port = get_free_port()
        server_logger.handlers = [logging.StreamHandler(self.log)]
        self.server = PolicyServer(host=self.host, port=self.port, **self._get_config())
    
        
class ServerRequestMixin:
    
    def _test_sent_request(self, models):
        
        _protocol = {
            'instance': '123',
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'test@example.net',
            'recipient': 'test@example.org',
            'country': 'fr'
        }
        
        protocol = protocol_yaml_TO_dict(**_protocol)
        actions = send_policy(protocol, host=self.host, port=self.port)
        self.assertEquals(len(actions), 1)
        self.assertTrue(actions[0].startswith('450 4.2.0 Greylisted for'))
        self.assertTrue(actions[0].endswith("policy[default] - %s#greylisted" % constants.ERRORS_URL_BASE))

        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_MED)        
        entry = models.GreylistEntry.search_entry(key=key)
        self.assertIsNotNone(entry)
        self.assertEquals(entry.rejects, 1)
        self.assertEquals(entry.accepts, 0)
        
        gevent.sleep(1.1)
        
        actions = send_policy(protocol, host=self.host, port=self.port)
        self.assertEquals(len(actions), 1)
        self.assertFalse("ERROR" in actions[0])
        self.assertEquals(actions[0], 'DUNNO policy[default]')
    