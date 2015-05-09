# -*- coding: utf-8 -*-

from mongrey import utils
from mongrey import constants
from mongrey.exceptions import InvalidProtocolError

from .base import BaseTestCase
from .utils import protocol_yaml_TO_dict

class UtilsTestCase(BaseTestCase):
    
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

    def test_verify_protocol(self):

        with self.assertRaises(InvalidProtocolError) as ex:
            utils.verify_protocol({})
            self.assertEquals(str(ex), "protocol_state field not in protocol")

        with self.assertRaises(InvalidProtocolError) as ex:
            utils.verify_protocol({'protocol_state': 'DATA'})
            self.assertEquals(str(ex), "this protocol_state is not supported: DATA")
        
        with self.assertRaises(InvalidProtocolError) as ex:
            utils.verify_protocol({'protocol_state': 'RCPT', 'BADFIELD': 'value'})
            self.assertEquals(str(ex), "invalid field in protocol: BADFIELD")

        protocol = protocol_yaml_TO_dict()
        result = utils.verify_protocol(protocol)
        self.assertIsNone(result)
        

