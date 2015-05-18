# -*- coding: utf-8 -*-

from flask import url_for

from mongrey import constants
from mongrey import utils
from mongrey.ext.flask_login import current_user

class AdminTestCaseMixin:
    pass

    def _test_security(self, models):
        
        url = url_for('greylistentry.index_view')
        #TODO: url = url_for('admin.index')
        self.assertFalse(current_user.is_authenticated)
        
        response = self.client.get(url, follow_redirects=False)
        self.assert_401(response)
        
        headers_login = self.login_basic_headers("radicalspamtest", "radicalspamtest")
        with self.client as c:
            response = c.get(url, headers=headers_login, follow_redirects=True)
            self.assertOk(response)
            self.assertEquals(current_user.username, "radicalspamtest")

            response = c.get(url_for('admin.logout'), 
                             headers=headers_login, follow_redirects=False)
            self.assertRedirects(response, url_for('admin.index'))
        
    
