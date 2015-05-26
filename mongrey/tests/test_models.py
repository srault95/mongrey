# -*- coding: utf-8 -*-

import arrow

from mongrey import constants

class TestModelsMixin:
    
    def _drop_model(self, model):
        raise NotImplementedError()

    def _model_count(self, model):
        raise NotImplementedError()

    def _get_id(self, model):
        raise NotImplementedError()

    def _test_model_api(self, models, validation_klass, unique_error_klass):
        
        #api_create        
        doc = models.Domain.api_create(name="example.org")
        self.assertIsNotNone(doc)
        self.assertIsInstance(doc, models.Domain)

        #api_find        
        docs = models.Domain.api_find(name="example.org")
        self.assertIsNotNone(docs)
        self.assertEquals(self._model_count(models.Domain), 1)

        #api_find_one        
        doc = models.Domain.api_find_one(name="example.org")
        self.assertIsNotNone(doc)
        self.assertIsInstance(doc, models.Domain)
        
        #api_update        
        doc = models.Domain.api_find_one(name="example.org")
        result = models.Domain.api_update(doc=doc, name="example2.org")
        self.assertEquals(result, 1)

        #api_delete        
        doc = models.Domain.api_find_one(name="example2.org")
        models.Domain.api_delete(doc=doc)
        self.assertEquals(self._model_count(models.Domain), 0)
        
        self._drop_model(models.Domain)


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
        self.assertEquals(search, constants.NOT_FOUND)
        
        models.Domain(name="example.net").save()
        search = models.Domain.search(protocol)
        self.assertEquals(search, constants.SENDER_FOUND)
        self._drop_model(models.Domain)
            
        models.Domain(name="example.org").save()
        search = models.Domain.search(protocol)
        self.assertEquals(search, constants.RECIPIENT_FOUND)
        self._drop_model(models.Domain)

    def _test_mailbox(self, models, validation_klass, unique_error_klass):
        
        models.Mailbox(name="email@example.org").save()
        
        with self.assertRaises(validation_klass) as ex:
            models.Mailbox(name="badvalue").save()
            
        with self.assertRaises(unique_error_klass) as ex:
            models.Mailbox(name="email@example.org").save()

        self._drop_model(models.Mailbox)
            
        protocol = {
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
        }
        search = models.Mailbox.search(protocol)
        self.assertEquals(search, constants.NOT_FOUND)
        
        models.Mailbox(name="sender@example.net").save()
        search = models.Mailbox.search(protocol)
        self.assertEquals(search, constants.SENDER_FOUND)
        self._drop_model(models.Mailbox)
            
        models.Mailbox(name="rcpt@example.org").save()
        search = models.Mailbox.search(protocol)
        self.assertEquals(search, constants.RECIPIENT_FOUND)
        self._drop_model(models.Mailbox)

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

    def _test_domain_slug(self, models):
        d = models.Domain(name="example.org").save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "example-org")

        self._drop_model(models.Domain)

    def _test_mailbox_slug(self, models):
        d = models.Mailbox(name="email@example.org").save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "email-example-org")

        self._drop_model(models.Mailbox)
    
    def _test_mynetwork_slug(self, models):
        
        d1 = models.Mynetwork(value="1.1.1.1").save()
        self.assertIsNotNone(d1.slug)
        self.assertEquals(d1.slug, "1-1-1-1")

        d2 = models.Mynetwork(value="1.1.1.0/24").save()
        self.assertIsNotNone(d2.slug)
        self.assertEquals(d2.slug, "1-1-1-0-24")

        self._drop_model(models.Mynetwork)
        
    def _test_policy_slug(self, models):
        
        d = models.Policy(name="policytest", field_name='client_address', value='1.1.1.1').save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "policytest")

        self._drop_model(models.Policy)

    def _test_wblist_slug(self, model):

        d = model(field_name="client_address", value='1.1.1.1').save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "1-1-1-1")
        self._drop_model(model)

        d = model(field_name="client_address", value="1.1.1.0/24").save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "1-1-1-0-24")
        self._drop_model(model)

        d = model(field_name="client_name", value=".*\.example.net").save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "example-net")
        self._drop_model(model)

        d = model(field_name="sender", value=".*@example.net").save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "example-net")
        self._drop_model(model)

        d = model(field_name="sender", value="sender@.*").save()
        self.assertIsNotNone(d.slug)
        self.assertEquals(d.slug, "sender")
        self._drop_model(model)

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

        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'mx1.example.net',
            'helo_name': 'example.net',
            'sender': 'sender@example.net',
            'recipient': 'rcpt@example.org',
            'country': 'fr'
        }

        doc = models.GreylistEntry.create_entry(key='key2', protocol=protocol)
        self.assertDictEqual(doc.protocol, protocol)
        
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

        metrics = models.GreylistEntry.last_metrics()
        self.assertIsNone(metrics)
        """
        self.assertEquals(metrics['count'], 0)
        self.assertEquals(metrics['rejected'], 0)
        self.assertEquals(metrics['accepted'], 0)
        self.assertEquals(metrics['requests'], 0)
        self.assertEquals(metrics['delay'], 0)
        self.assertEquals(metrics['abandoned'], 0)
        models.GreylistMetric(**metrics).save()
        """
        
        metric = models.GreylistMetric.api_find_one()
        self.assertIsNotNone(metric)
        self.assertEquals(metric.accepted, 0)
                
        self._drop_model(models.GreylistEntry)
        
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
        
    def _test_import_fixtures(self, models):
        self.maxDiff = None

        fixtures = {
            'domain': [{
                'name': 'example.org',
            }],
            'mailbox': [{
                'name': 'email@example.org',
            }],
            'mynetwork': [{
                'value': '1.1.1.1',
            }],
            'whitelist': [{
                'value': '1.1.1.0/24',
                'field_name': 'client_address',
            }],
            'blacklist': [{
                'value': '2.2.2.2',
                'field_name': 'client_address',
            }],
            'policy': [{
                'name': 'policytest',
                'value': '1.1.1.0/24',
                'field_name': 'client_address',
            }],
        }
        
        result = models.import_fixtures(fixtures)
        
        result_attempt = {
            'entries': 6,
            'success': 6,
            'warn_error': 0,
            'fatal_error': 0,
            'errors': []
        }
        
        self.assertDictEqual(result, result_attempt)

        fixtures = {
            'mynetwork': [{
                'value': '1.1.1.1',
            }],
        }
        result = models.import_fixtures(fixtures)
        
        result_attempt = {
            'entries': 1,
            'success': 0,
            'warn_error': 1,
            'fatal_error': 0,
            'errors': []
        }
        self.assertDictEqual(result, result_attempt)
        
        fixtures = {
            'mynetwork': [{
                'value': 'badvalue',
            }],
        }
        result = models.import_fixtures(fixtures)
        self.assertEquals(result['fatal_error'], 1)
        self.assertEquals(len(result['errors']), 1)
        
    def _test_export_fixtures(self, models):
        self.maxDiff = None

        fixtures = {
            'domain': [{
                'name': 'example.org',
            }],
            'mailbox': [{
                'name': 'email@example.org',
            }],
            'mynetwork': [{
                'value': '1.1.1.1',
                'comments': None
            }],
            'whitelist': [{
                'value': '1.1.1.0/24',
                'field_name': 'client_address',
                'comments': None
            }],
            'blacklist': [{
                'value': '2.2.2.2',
                'field_name': 'client_address',
                'comments': None
            }],
            'policy': [{
                'name': 'policytest',
                'value': '1.1.1.0/24',
                'field_name': 'client_address',
                'domain_vrfy': True,
                'mynetwork_vrfy': True,
                'spoofing_enable': True,
                'rbl_enable': False,
                'rbl_hosts': [],
                'rwl_enable': False,
                'rwl_hosts': [],
                'rwbl_timeout': 30,
                'rwbl_cache_timeout': 3600,                
                'spf_enable': False,
                'greylist_enable': True,
                'greylist_expire': 100,
                'greylist_key': 'med',
                'greylist_remaining': 20,
                'comments': None
            }],
        }
        
        models.import_fixtures(fixtures)
        
        export_fixtures = models.export_fixtures()
        
        self.assertDictEqual(export_fixtures, fixtures)
            