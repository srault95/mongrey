# -*- coding: utf-8 -*-

from flask import url_for

from mongrey import constants
from mongrey import utils
from mongrey.web.extensions import auth

class AdminTestCaseMixin:
    pass

    def _test_security(self, models):
        
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
    
