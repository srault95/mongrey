# -*- coding: utf-8 -*-

import unittest
import os

from flask import url_for

from ...base import BaseFlaskTestCase

from mongrey import constants
from mongrey import utils
from mongrey.web.extensions import auth
from mongrey.storage.mongo import models

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', "mongo") != "mongo", "Skip no mongodb tests")
class AdminTestCase(BaseFlaskTestCase):

    def _create_app(self):
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG, force_storage="mongo")
        return app
    
    def test_security(self):
        
        url = url_for('greylistentry.index_view')
        #url = url_for('admin.index')
        self.assertIsNone(auth.current_user())
        
        response = self.client.get(url, follow_redirects=False)
        self.assert_401(response)
        
        headers_login = self.login_basic_headers("radicalspamtest", "radicalspamtest")
        with self.client as c:
            response = c.get(url, headers=headers_login, follow_redirects=True)
            self.assertOk(response)
            self.assertEquals(auth.current_user(), "radicalspamtest")

            response = c.get(url_for('admin.logout'), 
                             headers=headers_login, follow_redirects=False)
            self.assertRedirects(response, url_for('admin.index'))
        
            self.assertIsNone(auth.current_user())
    
