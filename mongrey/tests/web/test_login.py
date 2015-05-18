# -*- coding: utf-8 -*-

from flask import url_for

from mongrey import constants

class LoginTestCaseMixin:

    def _test_login_with_basic_auth(self, models):
        
        self.assertIsNotAuthenticated()
        
        user = models.User.create_user(username="test", password="password")
        headers_login = self.login_basic_headers("test", "password")
        
        url = "/test/require_login"
        
        with self.client as c:
            response = c.get(url, headers=headers_login, follow_redirects=True)
            self.assert_200(response)
            self.assertIsAuthenticated("test")
            
            self.logout(url_for(self.flask_app.config['LOGOUT_VIEW']))
            self.assertIsNotAuthenticated()
            
    def _test_login_api_key(self, models):

        self.assertIsNotAuthenticated()
        
        user = models.User.create_user(username="test", password="password", api_key="KHPSW13")
        
        url = "/test/require_login?%s=KHPSW13" % constants.API_KEY
        
        with self.client as c:
            response = c.get(url, follow_redirects=True)
            self.assert_200(response)
            self.assertIsAuthenticated("test")

            self.logout(url_for(self.flask_app.config['LOGOUT_VIEW']))
            self.assertIsNotAuthenticated()


    def _test_login_with_form(self, models):
        
        self.assertIsNotAuthenticated()
        
        user = models.User.create_user(username="test", password="password")
        
        login_url = url_for(self.flask_app.config['LOGIN_VIEW'])
        response = self.login(username="test", password="password", url=login_url)

        self.assertIsAuthenticated("test")

        self.assert_200(response)
        
        context_value = self.get_context_variable('current_user')
        
        self.logout(url_for(self.flask_app.config['LOGOUT_VIEW']))
        self.assertIsNotAuthenticated()

        url = "/test/require_login"

        with self.client as c:
            response = c.get(url, follow_redirects=True)
            self.assert_200(response)
        
