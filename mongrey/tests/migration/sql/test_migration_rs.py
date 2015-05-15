# -*- coding: utf-8 -*-

from mongrey.storage.sql import models

from ...storage.sql.base import MongreyBaseTestCase
from ..test_migration_rs import RSMigrationTestCaseMixin

class MongoRSMigrationTestCase(RSMigrationTestCaseMixin, MongreyBaseTestCase):
    
    def test_import_domains(self):
        self._test_import_domains(models)

    def test_import_mailboxs(self):
        self._test_import_mailboxs(models)

    def test_import_mynetworks(self):
        self._test_import_mynetworks(models)
    
    def test_import_blacklist_clients(self):
        self._test_import_blacklist_clients(models)

    def test_import_blacklist_senders(self):
        self._test_import_blacklist_senders(models)

    def test_import_blacklist_recipients(self):
        self._test_import_blacklist_recipients(models)
