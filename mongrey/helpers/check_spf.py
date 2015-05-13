# -*- coding: utf-8 -*-

"""
@ 10800 IN TXT "v=spf1 include:aspmx.googlemail.com ~all"

#Paramètrage du DNS default avant utilisation de SPF : (pydns)
import DNS
DNS.defaults['server'] = ['127.0.0.1']

>>> import spf
#client_address, sender, helo_name
>>> s = spf.query('83.145.101.135', 'postmaster@example.net', 'mx1.example.net')
>>> r = s.check()   #moment ou la requette est envoyé
>>> r
('temperror', 451, 'SPF Temporary Error: DNS Timeout')
>>> r = s.best_guess()
>>> r
>>> ('pass', 250, 'sender SPF authorized')

"""

import logging
import time

from gevent import Timeout
from gevent.socket import gethostbyname

import spf

from ..cache import cache

logger = logging.getLogger(__name__)

def check_spf(protocol, guess):
    '''Check the SPF record of the sending address.
    Try Best Guess when the domain has no SPF record.
    Returns 1 when the SPF result is in ['fail', 'softfail'],
    returns 0 else.

    @type  protocol: dict
    @param protocol: the params from Postfix
    @type  guess:    int
    @param guess:    1 if use 'best guess', 0 if not
    @rtype:          int
    @return:         1 if bad SPF, 0 else
    '''
    score = 0
    try:
        s = spf.query(protocol['client_address'], protocol['sender'], protocol['helo_name'])
        r = s.check()
        if r[0] in ['fail', 'softfail']:
            score = 1
        elif r[0] in ['pass']:
            score = 0
        elif guess > 0 and r[0] in ['none']:
            r = s.best_guess()
            if r[0] in ['fail', 'softfail']:
                score = 1
            elif r[0] in ['pass']:
                score = 0
    except:
        # DNS Errors, yay...
        print 'something went wrong in check_spf()'
    return score


