# -*- coding: utf-8 -*-

import unittest
import os

from ...base import BaseFlaskTestCase
from ...web.test_admin import AdminTestCaseMixin

from mongrey.storage.sql import models

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', 'sql') != "sql", "Skip no sql tests")
class AdminTestCase(AdminTestCaseMixin, BaseFlaskTestCase):

    def _create_app(self):
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG, force_storage="sql")
        return app

    def test_security(self):
        self._test_security(models)

    """    
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
    """
