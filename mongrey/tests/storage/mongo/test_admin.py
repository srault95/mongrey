# -*- coding: utf-8 -*-

import unittest
import os

from flask import url_for, session

from ...base import BaseFlaskTestCase
from ...web.test_admin import AdminTestCaseMixin

from mongrey.storage.mongo import models
from mongrey import constants

"""
/change-lang                   admin.change_lang HEAD,OPTIONS,GET
/greylistentry/                greylistentry.index_view HEAD,OPTIONS,GET
/greylistentry/delete/         greylistentry.delete_view POST,OPTIONS
/greylistentry/edit/           greylistentry.edit_view HEAD,POST,OPTIONS,GET
/greylistentry/new/            greylistentry.create_view HEAD,POST,OPTIONS,GET
/greylistentry/show            greylistentry.show HEAD,OPTIONS,GET
/greylistmetric/               greylistmetric.index_view HEAD,OPTIONS,GET
/greylistmetric/delete/        greylistmetric.delete_view POST,OPTIONS
/greylistmetric/edit/          greylistmetric.edit_view HEAD,POST,OPTIONS,GET
/greylistmetric/new/           greylistmetric.create_view HEAD,POST,OPTIONS,GET
/greylistpolicy/               greylistpolicy.index_view HEAD,OPTIONS,GET
/greylistpolicy/delete/        greylistpolicy.delete_view POST,OPTIONS
/greylistpolicy/edit/          greylistpolicy.edit_view HEAD,POST,OPTIONS,GET
/greylistpolicy/new/           greylistpolicy.create_view HEAD,POST,OPTIONS,GET
/whitelist/                    whitelist.index_view HEAD,OPTIONS,GET
/whitelist/delete/             whitelist.delete_view POST,OPTIONS
/whitelist/edit/               whitelist.edit_view HEAD,POST,OPTIONS,GET
/whitelist/new/                whitelist.create_view HEAD,POST,OPTIONS,GET

"""

#http://127.0.0.1:8081/change-lang?locale=fr

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', "mongo") != "mongo", "Skip no mongodb tests")
class AdminTestCase(AdminTestCaseMixin, BaseFlaskTestCase):

    CONFIG = "mongrey.tests.storage.mongo.flask_settings.Test"
    
    def _create_app(self):
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG)
        return app
    
    def test_security(self):
        self._test_security(models)
        
    def test_change_lang(self):

        self.assertEquals(self.flask_app.config.get('BABEL_DEFAULT_LOCALE'), 'en')
        
        #self.assertTrue(constants.SESSION_LANG_KEY in session)
        
        headers_login = self.login_basic_headers("radicalspamtest", "radicalspamtest")
        
        url = "%s?locale=fr" % url_for('admin.change_lang')
        with self.client as c:
            response = c.get(url, headers=headers_login, follow_redirects=True)
            #print response
            current_lang = self.get_context_variable('current_lang')
            #print "current_lang : ", current_lang            
            
            #self.assertEquals(session.get(constants.SESSION_LANG_KEY, None), 'fr')
        
