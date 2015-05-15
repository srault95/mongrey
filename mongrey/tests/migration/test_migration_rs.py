# -*- coding: utf-8 -*-

import os

from mongrey.migration import radicalspam

from ..base import RESOURCE_DIR

RS_MIGRATION_DIR = os.path.abspath(os.path.join(RESOURCE_DIR, 'rs-3.5.4-postfix-migration'))

def get_resource_path(filename):
    return os.path.abspath(os.path.join(RS_MIGRATION_DIR, filename))

class RSMigrationTestCaseMixin:
    
    def _check_resources(self):

        resources = [
            'local-relays.dbhash',
            'local-directory.dbhash',
            'local-exceptions-directory.dbhash',
            'local-mynetworks-lan.dbhash',
            'local-mynetworks-wan.dbhash',
            'local-blacklist-clients.dbhash',
            'local-blacklist-senders.dbhash',
            'local-blacklist-recipients.dbhash',
        ]
        
        for r in resources:
            filepath = get_resource_path(r)
            if not os.path.exists(filepath):
                self.fail("resource not found in tests : %s" % filepath)
    
    def _test_import_domains(self, models):
        filepath = get_resource_path('local-relays.dbhash')
        result = radicalspam.import_domains(filepath=filepath, model_klass=models.Domain)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))

    def _test_import_mailboxs(self, models):
        filepath = get_resource_path('local-directory.dbhash')
        result = radicalspam.import_mailboxs(filepath=filepath, model_klass=models.Mailbox)
        self.assertEquals(result['success'], 2)
        self.assertEquals(result['error'], 1)
        self.assertEquals(len(result['error_messages']), 1)

        filepath = get_resource_path('local-exceptions-directory.dbhash')
        result = radicalspam.import_mailboxs_exceptions(filepath=filepath, model_klass=models.Mailbox)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))

    def _test_import_mynetworks(self, models):
        filepath = get_resource_path('local-mynetworks-lan.dbhash')
        result = radicalspam.import_mynetworks_lan(filepath=filepath, model_klass=models.Mynetwork)
        self.assertDictEqual(result, dict(success=2, error=0, error_messages=[]))

        filepath = get_resource_path('local-mynetworks-wan.dbhash')
        result = radicalspam.import_mynetworks_wan(filepath=filepath, model_klass=models.Mynetwork)
        self.assertEquals(result['success'], 1)
        self.assertEquals(result['error'], 1)
        self.assertEquals(len(result['error_messages']), 1)

    def _test_import_blacklist_clients(self, models):
        filepath = get_resource_path('local-blacklist-clients.dbhash')
        result = radicalspam.import_blacklist_clients(filepath=filepath, model_klass=models.BlackList)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))

    def _test_import_blacklist_senders(self, models):
        filepath = get_resource_path('local-blacklist-senders.dbhash')
        result = radicalspam.import_blacklist_senders(filepath=filepath, model_klass=models.BlackList)
        self.assertDictEqual(result, dict(success=2, error=0, error_messages=[]))

    def _test_import_blacklist_recipients(self, models):
        filepath = get_resource_path('local-blacklist-recipients.dbhash')
        result = radicalspam.import_blacklist_recipients(filepath=filepath, model_klass=models.BlackList)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))
