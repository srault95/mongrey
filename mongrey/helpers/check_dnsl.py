# -*- coding: utf-8 -*-

import logging
import time

from gevent import Timeout
from gevent.socket import gethostbyname

from IPy import IP

from ..cache import cache

logger = logging.getLogger(__name__)

#ix.dnsbl.manitu.net, dnsbl.ahbl.org
DEFAULT_DNSBL = [
    'zen.spamhaus.org',
    'combined.njabl.org',
    'dnsbl.sorbs.net',
    'bl.spamcop.net',
]

DEFAULT_DNSWL = [
    'list.dnswl.org',
]

def reverse_ip(ip):
    """
    ip = ipaddr.IPAddress('2001:DB8:abc:123::42')
    ip.exploded
    '2001:0db8:0abc:0123:0000:0000:0000:0042'
    
    ex spamhaus:
        2001:DB8:abc:123::42
        2.4.0.0.0.0.0.0.0.0.0.0.0.0.0.0.3.2.1.0.c.b.a.0.8.b.d.0.1.0.0.2.zen.spamhaus.org
    """
    ip = IP(ip)
    
    if ip.version() == 4:
        return ip.reverseName().strip('.in-addr.arpa.')
    
    elif ip.version() == 6:
        return ip.reverseName().strip('.ip6.arpa.')

def _check_dns_wb_list(rip, bl, resolver=None):
    """
    Génère une exception quand l'entrée n'est pas trouvé
    result: '127.0.0.11' si found et selon réponse des RBL
    """
    resolver = resolver or gethostbyname
    try:
        
        key = '%s.%s' % (rip, bl)
        result = resolver(key)
        return bl, result
    except Exception:
        return bl, None

def check_dns_wb_lists(ip, rbls=None, timeout=30.0, cache_timeout=3600, resolver=None):
    """
    TODO: besoin d'un cache soit ici soit dans l'appel de la fonction !!!
    """
    
    rbls = rbls or DEFAULT_DNSBL
    resolver = resolver or gethostbyname

    if not ip:
        return None, None
    
    start = time.time()    
    try:
        if not IP(ip).iptype() == 'PUBLIC':
            return None, None
        
        with Timeout(timeout):
        
            ip_reverse = reverse_ip(ip)
            
            if cache:
                cache_key = "rbl-%s" % ip_reverse            
                _cache = cache.get(cache_key)
                if _cache:
                    return _cache[0], _cache[1]
            
            for bl in rbls:
                rbl, result = _check_dns_wb_list(ip_reverse, bl, resolver=resolver)
                
                if result:
                    
                    if cache:
                        cache.set(cache_key, (bl, result), timeout=cache_timeout)
                        
                    return bl, result
    
    except Timeout:
        logger.warn("timeout[%s] for ip[%s]" % (timeout, ip))
        
    except Exception, err:
        logger.error(str(err))
        
    finally:
        end = time.time() - start
        logger.debug("rbl time: %.3f" % end)
    
    return None, None

