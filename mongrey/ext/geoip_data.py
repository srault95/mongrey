# -*- coding: utf-8 -*-
'''
Usage:

    >>> import os
    >>> from mongrey.ext.geoip_data import where_country_ipv4
    >>> country_v4 = where_country_ipv4()
    >>> os.path.exists(country_v4)
    True
'''

__all__ = [
    'where_country_ipv4',
    'where_country_ipv6',
    'where_country_both'
]

import os

def where_country_ipv4():
    f = os.path.split(__file__)[0]
    return os.path.join(f, 'GeoIP.dat')

def where_country_ipv6():
    f = os.path.split(__file__)[0]
    return os.path.join(f, 'GeoIPv6.dat')

def where_country_both():
    return [where_country_ipv4(), where_country_ipv6()]

if __name__ == '__main__':
    print(where_country_ipv4())
    print(where_country_ipv6())
