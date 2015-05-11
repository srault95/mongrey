# -*- coding: utf-8 -*-

import unittest
import os

from ...base import BaseFlaskTestCase
from ...web.test_admin import AdminTestCaseMixin

from mongrey.storage.mongo import models

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

@unittest.skipIf(os.environ.get('MONGREY_STORAGE', "mongo") != "mongo", "Skip no mongodb tests")
class AdminTestCase(AdminTestCaseMixin, BaseFlaskTestCase):
    
    def _create_app(self):
        from mongrey.web import create_app
        app = create_app(config=self.CONFIG, force_storage="mongo")
        return app
    
    def test_security(self):
        self._test_security(models)
