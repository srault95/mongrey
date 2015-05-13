# -*- coding: utf-8 -*-

import time
import unittest

from mongrey.helpers import check_dnsl

class MockResolver(object):
    
    def __init__(self, value_attempt, sleep=None):
        self.value_attempt = value_attempt
        self.sleep = sleep
        
    def gethostbyname(self, ip):
        if self.sleep:
           time.sleep(self.sleep)
        if not self.value_attempt:
            raise Exception("not in BL")
            
        return self.value_attempt

class RBLTest(unittest.TestCase):
    
    #TODO: test_cached

    def test_reverse_ip(self):

        reverse = check_dnsl.reverse_ip("1.2.3.4")
        self.assertEquals(reverse, '4.3.2.1')

    def test_check_rbl(self):

        #Private IP        
        resolver = MockResolver(None) 
        rbl_host, rbl_txt = check_dnsl.check_dns_wb_lists("192.168.1.1", rbls=['rbl.example.net'], resolver=resolver.gethostbyname)
        self.assertIsNone(rbl_host)
        self.assertIsNone(rbl_txt)
        
        #Found in RBL
        resolver = MockResolver('127.0.0.11') 
        rbl_host, rbl_txt = check_dnsl.check_dns_wb_lists("5.1.10.10", rbls=['rbl.example.net'], resolver=resolver.gethostbyname)
        self.assertEquals(rbl_host, 'rbl.example.net')
        self.assertEquals(rbl_txt, '127.0.0.11')
        
        #Not found in RBL
        resolver = MockResolver(None) 
        rbl_host, rbl_txt = check_dnsl.check_dns_wb_lists("5.1.10.10", rbls=['rbl.example.net'], resolver=resolver.gethostbyname)
        self.assertIsNone(rbl_host)
        self.assertIsNone(rbl_txt)
        
    def test_check_rbl_real(self):
        
        rbl_host, rbl_txt = check_dnsl.check_dns_wb_lists("83.221.194.7", rbls=['zen.spamhaus.org'])
        self.assertEquals(rbl_host, 'zen.spamhaus.org')
        self.assertEquals(rbl_txt, '127.0.0.11')

    def test_check_rbl_timeouted(self):

        resolver = MockResolver('127.0.0.11', sleep=0.5) 
        rbl_host, rbl_txt = check_dnsl.check_dns_wb_lists("5.1.10.10", 
                                                rbls=['rbl.example.net'], 
                                                resolver=resolver.gethostbyname,
                                                timeout=0.1)
        self.assertIsNone(rbl_host)
        self.assertIsNone(rbl_txt)
