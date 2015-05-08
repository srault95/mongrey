# -*- coding: utf-8 -*-

import arrow

from .base import MongoGreylistBaseTestCase
from ...test_models import TestModelsMixin

from mongrey.storage.sql import models
from mongrey import constants
from mongrey import utils

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
        
        #doc.update_expire(expire=86400, now=doc.timestamp)
        doc.accept(expire=86400, now=doc.timestamp)
        value = doc.expire_time - doc.timestamp
        self.assertEquals(value.total_seconds(), 86400)
        
    def Xtest_policy_search(self):

        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'mx1.example.net',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr'
        }
        
        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_IP, value='1.1.1.1').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")

        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_COUNTRY, value='fr').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")

        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_HOSTNAME, value='mx1.example.net').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")
        
        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_DOMAIN_SENDER, value='example.net').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")
        
        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_EMAIL_SENDER, value='sender@example.net').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")

        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_DOMAIN_RECIPIENT, value='example.org').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")

        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest", value_type=constants.POLICY_TYPE_EMAIL_RECIPIENT, value='rcpt@example.org').save()
        policy = models.query_for_policy(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.GreylistPolicy))
        self.assertEquals(policy.name, "policytest")

        models.GreylistPolicy.delete().execute()

        models.GreylistPolicy(name="policytest1", value_type=constants.POLICY_TYPE_IP, value='1.1.1.1').save()
        models.GreylistPolicy(name="policytest2", value_type=constants.POLICY_TYPE_COUNTRY, value='fr').save()
        models.GreylistPolicy(name="policytest3", value_type=constants.POLICY_TYPE_HOSTNAME, value='mx1.example.net').save()
        models.GreylistPolicy(name="policytest4", value_type=constants.POLICY_TYPE_DOMAIN_SENDER, value='example.net').save()
        models.GreylistPolicy(name="policytest5", value_type=constants.POLICY_TYPE_EMAIL_SENDER, value='sender@example.net').save()
        models.GreylistPolicy(name="policytest6", value_type=constants.POLICY_TYPE_DOMAIN_RECIPIENT, value='example.org').save()
        models.GreylistPolicy(name="policytest7", value_type=constants.POLICY_TYPE_EMAIL_RECIPIENT, value='rcpt@example.org').save()
        policies = models.query_for_policy(protocol, first_only=False)
        self.assertEquals(len(policies), 7)
        
        models.GreylistPolicy.delete().execute()
        
    def Xtest_query_for_wl_search(self):
        
        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'mx1.example.net',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr'
        }
        
        models.WhiteList(value_type=constants.WL_TYPE_IP, value='1.1.1.1').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))

        models.WhiteList.delete().execute()
        
        models.WhiteList(value_type=constants.WL_TYPE_DOMAIN, value='example.net').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))
        
        models.WhiteList.delete().execute()
        
        models.WhiteList(value_type=constants.WL_TYPE_EMAIL, value='sender@example.net').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))

        models.WhiteList.delete().execute()
        
        models.WhiteList(value_type=constants.WL_TYPE_DOMAIN, value='example.org').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))
        
        models.WhiteList.delete().execute()
        
        models.WhiteList(value_type=constants.WL_TYPE_EMAIL, value='rcpt@example.org').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))

        models.WhiteList.delete().execute()
        
        models.WhiteList(value_type=constants.WL_TYPE_HOSTNAME, value='mx1.example.net').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))
        
        models.WhiteList.delete().execute()
    
        models.WhiteList(value_type=constants.WL_TYPE_IP, value='1.1.1.1').save()
        models.WhiteList(value_type=constants.WL_TYPE_DOMAIN, value='example.net').save()
        models.WhiteList(value_type=constants.WL_TYPE_EMAIL, value='sender@example.net').save()
        models.WhiteList(value_type=constants.WL_TYPE_DOMAIN, value='example.org').save()
        models.WhiteList(value_type=constants.WL_TYPE_EMAIL, value='rcpt@example.org').save()
        models.WhiteList(value_type=constants.WL_TYPE_HOSTNAME, value='mx1.example.net').save()
        wls = models.query_for_wl_search(protocol, first_only=False)
        self.assertEquals(len(wls), 6)

        models.WhiteList.delete().execute()
        
        protocol = {
            'client_address': '1.1.1.1',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@subdomain.example.org',
        }
        
        models.WhiteList(value_type=constants.WL_TYPE_DOMAIN, value='subdomain.example.org').save()
        wl = models.query_for_wl_search(protocol)
        self.assertIsNotNone(wl)
        self.assertTrue(isinstance(wl, models.WhiteList))
        
        models.WhiteList.delete().execute()
        
        
    def Xtest_greylist_metrics(self):
        
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        metrics = models.GreylistEntry.last_metrics()
        self.assertEquals(metrics['count'], 1)
        self.assertEquals(metrics['rejected'], 1)
        self.assertEquals(metrics['accepted'], 0)
        self.assertEquals(metrics['requests'], 1)
        self.assertEquals(metrics['delay'], 0)
        self.assertEquals(metrics['abandoned'], 0)
        models.GreylistMetric(**metrics).save()        
                
        models.GreylistEntry.delete().execute()
        
        backtime = arrow.utcnow().replace(hours=-2).datetime
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        doc.timestamp=backtime
        doc.save()
        metrics = models.GreylistEntry.last_metrics()
        self.assertEquals(metrics['abandoned'], 1)
        models.GreylistMetric(**metrics).save()
        
        models.GreylistEntry.delete().execute()
                
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        doc.timestamp=backtime
        doc.accept()
        metrics = models.GreylistEntry.last_metrics()
        self.assertEquals(metrics['count'], 1)
        self.assertEquals(metrics['rejected'], 1)
        self.assertEquals(metrics['accepted'], 1)
        self.assertEquals(metrics['requests'], 2)
        self.assertTrue(metrics['delay'] > 0)
        models.GreylistMetric(**metrics).save()
        
        models.GreylistEntry.delete().execute()
        
        
        
        
        