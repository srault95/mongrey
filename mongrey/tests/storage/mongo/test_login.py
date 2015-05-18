# -*- coding: utf-8 -*-

import unittest
import os

from ...base import BaseFlaskTestCase
from ...web.test_login import LoginTestCaseMixin
from .base import drop_all

from mongrey.storage.mongo import models

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', "mongo") != "mongo", "Skip no mongodb tests")
class LoginTestCase(LoginTestCaseMixin, BaseFlaskTestCase):

    CONFIG = "mongrey.tests.storage.mongo.flask_settings.Test"
    
    def _create_app(self):
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG)
        return app
    
    def setUp(self):
        BaseFlaskTestCase.setUp(self)
        drop_all()
        self._views(self.flask_app)
        
    def test_user_password(self):
        user = models.User.create_user("test", "password")
        self.assertTrue(user.check_password("password"))

    def test_login_with_basic_auth(self):
        self._test_login_with_basic_auth(models)

    def test_login_api_key(self):
        self._test_login_api_key(models)

    def test_login_with_form(self):
        self._test_login_with_form(models)
    
