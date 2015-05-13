# -*- coding: utf-8 -*-

import unittest
from StringIO import StringIO

from mongrey import constants
from mongrey.exceptions import InvalidProtocolError

from ..base import BaseTestCase
from ..utils import protocol_yaml_TO_dict, policy_template

from mongrey.server import protocols

class PolicyProtocolTestCase(BaseTestCase):

    def test_parse_policy_protocol(self):
    
        values = dict(client_address="192.168.1.1", 
                      sender="sender@test.org", 
                      recipient="recipient@test.org")
        
        '''dict du protocol modifié'''
        postfix_protocol = protocol_yaml_TO_dict(**values)
        
        '''résultat str du dict protocol'''
        protocol_str = policy_template(**postfix_protocol)
        
        '''parse du protocol str - doit renvoyer un dict'''
        protocol = protocols.parse_policy_protocol(StringIO(protocol_str))
        
        self.assertIsNotNone(protocol)
        
        self.assertEquals(protocol['client_address'], values['client_address'])
        self.assertEquals(protocol['sender'], values['sender'])
        self.assertEquals(protocol['recipient'],  values['recipient'])

    def test_verify_protocol(self):

        with self.assertRaises(InvalidProtocolError) as ex:
            protocols.verify_protocol({})
            self.assertEquals(str(ex), "protocol_state field not in protocol")

        with self.assertRaises(InvalidProtocolError) as ex:
            protocols.verify_protocol({'protocol_state': 'DATA'})
            self.assertEquals(str(ex), "this protocol_state is not supported: DATA")
        
        with self.assertRaises(InvalidProtocolError) as ex:
            protocols.verify_protocol({'protocol_state': 'RCPT', 'BADFIELD': 'value'})
            self.assertEquals(str(ex), "invalid field in protocol: BADFIELD")

        protocol = protocol_yaml_TO_dict()
        result = protocols.verify_protocol(protocol)
        self.assertIsNone(result)
        

