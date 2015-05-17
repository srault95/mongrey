# -*- coding: utf-8 -*-

from decouple import config

from mongrey.web.settings import Test as BaseTest

class Test(BaseTest):

    DB_SETTINGS = {
        'host': config('MONGREY_DB', 'sqlite:///../mongrey_test.db'),
    }        

