# -*- coding: utf-8 -*-

import os

from mongrey.migration import radicalspam

from ..base import RESOURCE_DIR

RS_MIGRATION_DIR = os.path.abspath(os.path.join(RESOURCE_DIR, 'rs-3.5.4-postfix-migration'))

def get_resource_path(filename):
    return os.path.abspath(os.path.join(RS_MIGRATION_DIR, filename))

class RSMigrationTestCaseMixin:
    
    def _test_import_domains(self, models):
        filepath = get_resource_path('local-relays.db')
        result = radicalspam.import_domains(filepath=filepath, model_klass=models.Domain)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))

    def _test_import_mailboxs(self, models):
        filepath = get_resource_path('local-directory.db')
        result = radicalspam.import_mailboxs(filepath=filepath, model_klass=models.Mailbox)
        self.assertEquals(result['success'], 2)
        self.assertEquals(result['error'], 1)
        self.assertEquals(len(result['error_messages']), 1)

        filepath = get_resource_path('local-exceptions-directory.db')
        result = radicalspam.import_mailboxs_exceptions(filepath=filepath, model_klass=models.Mailbox)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))

    def _test_import_mynetworks(self, models):
        filepath = get_resource_path('local-mynetworks-lan.db')
        result = radicalspam.import_mynetworks_lan(filepath=filepath, model_klass=models.Mynetwork)
        self.assertDictEqual(result, dict(success=2, error=0, error_messages=[]))

        filepath = get_resource_path('local-mynetworks-wan.db')
        result = radicalspam.import_mynetworks_wan(filepath=filepath, model_klass=models.Mynetwork)
        self.assertEquals(result['success'], 1)
        self.assertEquals(result['error'], 1)
        self.assertEquals(len(result['error_messages']), 1)

    def _test_import_blacklist_clients(self, models):
        filepath = get_resource_path('local-blacklist-clients.db')
        result = radicalspam.import_blacklist_clients(filepath=filepath, model_klass=models.BlackList)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))

    def _test_import_blacklist_senders(self, models):
        filepath = get_resource_path('local-blacklist-senders.db')
        result = radicalspam.import_blacklist_senders(filepath=filepath, model_klass=models.BlackList)
        self.assertDictEqual(result, dict(success=2, error=0, error_messages=[]))

    def _test_import_blacklist_recipients(self, models):
        filepath = get_resource_path('local-blacklist-recipients.db')
        result = radicalspam.import_blacklist_recipients(filepath=filepath, model_klass=models.BlackList)
        self.assertDictEqual(result, dict(success=1, error=0, error_messages=[]))
