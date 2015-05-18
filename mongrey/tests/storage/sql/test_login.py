# -*- coding: utf-8 -*-

import unittest
import os

from mongrey.utils import get_db_config
from mongrey.storage.sql import models

from ...base import BaseFlaskTestCase
from ...web.test_login import LoginTestCaseMixin

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', "sql") != "sql", "Skip no sql tests")
class LoginTestCase(LoginTestCaseMixin, BaseFlaskTestCase):

    CONFIG = "mongrey.tests.storage.sql.flask_settings.Test"

    db_settings = {
        'host': 'sqlite:///../mongrey_test.db',
    } 

    def _create_app(self):
        settings, storage = get_db_config(**self.db_settings)        
        models.configure_peewee(drop_before=True, **settings)
        
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG)
        return app
    
    def setUp(self):
        BaseFlaskTestCase.setUp(self)
        self._views(self.flask_app)        

    def test_login_with_basic_auth(self):
        self._test_login_with_basic_auth(models)

    def test_login_api_key(self):
        self._test_login_api_key(models)

    def test_login_with_form(self):
        self._test_login_with_form(models)
    
