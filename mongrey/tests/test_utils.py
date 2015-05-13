# -*- coding: utf-8 -*-

import unittest

from mongrey import utils
from mongrey import constants
from mongrey.exceptions import InvalidProtocolError

from .base import BaseTestCase
from .utils import protocol_yaml_TO_dict

class UtilsTestCase(BaseTestCase):
    
    @unittest.skip("NotImplemented")
    def test_read_whitelist(self):
        self.fail("NotImplemented")
        #utils.read_whitelist(whitelist_filename)

    @unittest.skip("NotImplemented")
    def test_read_postgrey_logs(self):
        self.fail("NotImplemented")
        #utils.read_postgrey_logs(filepath)
    
    def test_build_key(self):

        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': 'test@example.net',
            'recipient': 'test@example.org',
        }
        
        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_VERY_LOW)
        self.assertEquals(key, '1.1.1.1')

        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_LOW)
        self.assertEquals(key, '1.1.1.1-example.org')

        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_MED)
        self.assertEquals(key, '1.1.1.1-test@example.org')

        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_HIGH)
        self.assertEquals(key, '1.1.1.1-test@example.net-test@example.org')

        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_SPECIAL)
        self.assertEquals(key, 'test@example.net-test@example.org')
        
        protocol = {
            'client_address': '1.1.1.1',
            'client_name': 'unknow',
            'sender': '<>',
            'recipient': 'test@example.org',
        }
        
        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_HIGH)
        self.assertEquals(key, '1.1.1.1-<>-test@example.org')

        key = utils.build_key(protocol, greylist_key=constants.GREY_KEY_SPECIAL)
        self.assertEquals(key, '<>-test@example.org')

