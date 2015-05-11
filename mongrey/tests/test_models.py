# -*- coding: utf-8 -*-

import arrow

from mongrey import constants

class TestModelsMixin:
    
    def _drop_model(self, model):
        raise NotImplementedError()

    def _test_domain(self, models, validation_klass, unique_error_klass):
        
        models.Domain(name="example.org").save()
        
        with self.assertRaises(validation_klass) as ex:
            models.Domain(name="badvalue").save()
            
        with self.assertRaises(unique_error_klass) as ex:
            models.Domain(name="example.org").save()

        self._drop_model(models.Domain)
            
        protocol = {
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        search = models.Domain.search(protocol)
        self.assertEquals(search, constants.DOMAIN_NOT_FOUND)
        
        models.Domain(name="example.net").save()
        search = models.Domain.search(protocol)
        self.assertEquals(search, constants.DOMAIN_SENDER_FOUND)
        self._drop_model(models.Domain)
            
        models.Domain(name="example.org").save()
        search = models.Domain.search(protocol)
        self.assertEquals(search, constants.DOMAIN_RECIPIENT_FOUND)
        self._drop_model(models.Domain)

    def _test_mynetwork(self, models, validation_klass, unique_error_klass):
        
        models.Mynetwork(value="1.1.1.1").save()

        models.Mynetwork(value="1.1.1.0/24").save()

        models.Mynetwork(value="::1").save()
        
        with self.assertRaises(validation_klass) as ex:
            models.Mynetwork(value="xxx").save()
            
        with self.assertRaises(unique_error_klass) as ex:
            models.Mynetwork(value="1.1.1.1").save()

        with self.assertRaises(unique_error_klass) as ex:
            models.Mynetwork(value="1.1.1.0/24").save()

        self._drop_model(models.Mynetwork)
        
        protocol = {
            'client_address': '1.1.1.1',
        }
        
        search = models.Mynetwork.search(protocol)
        self.assertFalse(search)
        
        models.Mynetwork(value="1.1.1.1").save()
        search = models.Mynetwork.search(protocol)
        self.assertTrue(search)

        self._drop_model(models.Mynetwork)
        
        models.Mynetwork(value="1.1.1.0/24").save()
        search = models.Mynetwork.search(protocol)
        self.assertTrue(search)
            
        self._drop_model(models.Mynetwork)
    
    def _test_create_greylist_entry(self, models):
        
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        self.assertEquals(doc.rejects, 1)
        self.assertIsNone(doc.expire_time)
        
        search = models.GreylistEntry.search_entry(key='key1')
        self.assertIsNotNone(search)
        
        expire = search.expire(delta=60, now=doc.timestamp)
        self.assertEquals(expire, 60)

        now = arrow.utcnow().replace(hours=+1)
        expire = search.expire(delta=60, now=now.datetime)
        self.assertTrue(expire < 0)
        
        doc.accept(expire=86400, now=doc.timestamp)
        value = doc.expire_time - doc.timestamp
        self.assertEquals(value.total_seconds(), 86400)
        
    def _test_search_policy(self, models):

        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'mx1.example.net',
            'helo_name': 'example.net',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr'
        }
        
        models.Policy(name="policytest", 
                              field_name='client_address', 
                              value='1.1.1.1').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

        models.Policy(name="policytest", 
                              field_name='client_address', 
                              value='1.1.1.0/24').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)
        
        models.Policy(name="policytest", 
                              field_name='country', value='fr').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

        models.Policy(name="policytest", 
                              field_name='client_name', 
                              value='.*\.example.net').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

        models.Policy(name="policytest", 
                              field_name='sender', 
                              value='.*@example.net').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

        models.Policy(name="policytest", 
                              field_name='sender', 
                              value='sender@example.net').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

        models.Policy(name="policytest", 
                              field_name='recipient', 
                              value='.*@example.org').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

        models.Policy(name="policytest", field_name='recipient', value='rcpt@example.org').save()
        policy = models.Policy.search(protocol)
        self.assertIsNotNone(policy)
        self.assertTrue(isinstance(policy, models.Policy))
        self.assertEquals(policy.name, "policytest")

        self._drop_model(models.Policy)

    def _test_search_wblist(self, model):
        
        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'mx1.example.net',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr'
        }

        model(field_name="client_address", value='1.1.1.1').save()
        search = model.search(protocol, cache_enable=False)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['client_address'])

        self._drop_model(model)

        model(field_name="client_address", value="1.1.1.0/24").save()
        search = model.search(protocol, cache_enable=False)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['client_address'])
        
        self._drop_model(model)

        model(field_name="client_name", value=".*\.example.net").save()
        search = model.search(protocol, cache_enable=False)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['client_name'])

        self._drop_model(model)

        model(field_name="client_name", value=".*\.example.net").save()
        _protocol = protocol.copy()
        _protocol['client_name'] = "unknow" 
        search = model.search(_protocol, cache_enable=False)
        self.assertIsNone(search)

        self._drop_model(model)

        model(field_name="sender", value=".*@example.net").save()
        search = model.search(protocol, cache_enable=False)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['sender'])

        self._drop_model(model)

        model(field_name="sender", value="sender@.*").save()
        search = model.search(protocol, cache_enable=False)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['sender'])

        self._drop_model(model)

        model(field_name="recipient", value=".*@example.org").save()
        search = model.search(protocol, cache_enable=False)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['recipient'])

        self._drop_model(model)

        model(field_name="sender", value="sender@.*").save()
        _protocol = protocol.copy()
        _protocol['sender'] = '<>'
        search = model.search(_protocol, cache_enable=False)
        self.assertIsNone(search)
    
    def _test_search_whitelist_cache(self, models):

        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'mx1.example.net',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr'
        }

        models.WhiteList(field_name="client_address", value='1.1.1.1').save()
        search = models.WhiteList.search(protocol)
        self.assertIsNotNone(search)
        self.assertEquals(search, protocol['client_address'])

        self._drop_model(models.WhiteList)
        
        cache_key = "%s-1.1.1.1" % (models.WhiteList._cache_key)
        self.assertIsNotNone(self._cache.get(cache_key))
        
    def _test_greylist_metrics(self, models):
        
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        metrics = models.GreylistEntry.last_metrics()
        self.assertEquals(metrics['count'], 1)
        self.assertEquals(metrics['rejected'], 1)
        self.assertEquals(metrics['accepted'], 0)
        self.assertEquals(metrics['requests'], 1)
        self.assertEquals(metrics['delay'], 0)
        self.assertEquals(metrics['abandoned'], 0)
        models.GreylistMetric(**metrics).save()        
        self._drop_model(models.GreylistEntry)
        
        backtime = arrow.utcnow().replace(hours=-2).datetime
        doc = models.GreylistEntry.create_entry(key='key1', protocol={})
        doc.timestamp=backtime
        doc.save()
        metrics = models.GreylistEntry.last_metrics()
        self.assertEquals(metrics['abandoned'], 1)
        models.GreylistMetric(**metrics).save()
        self._drop_model(models.GreylistEntry)
                
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
        self._drop_model(models.GreylistEntry)
        
    