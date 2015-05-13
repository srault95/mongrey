# -*- coding: utf-8 -*-

import re

__dyn_host = re.compile('(\.bb\.|broadband|cable|dial|dip|dsl|dyn|gprs|pool|ppp|umts|wimax|wwan|[0-9]{1,3}[.-][0-9]{1,3}[.-][0-9]{1,3}[.-][0-9]{1,3})', re.I)
__static_host = re.compile('(colo|dedi|hosting|mail|mx[^$]|smtp|static)', re.I)

def check_dyn_host(host):
    '''Check the host for being a dynamic/dialup one.

    @type  host: string
    @param host: the host to check
    @rtype:      int
    @return:     0 if host is not dynamic, 1 if it is
    '''
    if __static_host.search(host):
        return 0
    if __dyn_host.search(host):
        return 1
    return 0
