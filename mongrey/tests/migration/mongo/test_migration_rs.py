# -*- coding: utf-8 -*-

import os
import unittest

from mongrey.storage.mongo import models

from ...storage.mongo.base import MongreyBaseTestCase
from ..test_migration_rs import RSMigrationTestCaseMixin

@unittest.skipIf('TRAVIS' in os.environ, "Skip Travis - Bug: No module named _bsddb")
class MongoRSMigrationTestCase(RSMigrationTestCaseMixin, MongreyBaseTestCase):
    
    def setUp(self):
        MongreyBaseTestCase.setUp(self)
        self._check_resources()
    
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
