# -*- coding: utf-8 -*-

import unittest
import os

from ...base import BaseFlaskTestCase
from ...web.test_admin import AdminTestCaseMixin

from mongrey.storage.sql import models

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', 'sql') != "sql", "Skip no sql tests")
class AdminTestCase(AdminTestCaseMixin, BaseFlaskTestCase):

    CONFIG = "mongrey.tests.storage.sql.flask_settings.Test"

    def _create_app(self):
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG)
        return app

    @unittest.skip("TODO")    
    def test_security(self):
        self._test_security(models)

    @unittest.skip("TODO")    
    def test_change_lang(self):
        pass
