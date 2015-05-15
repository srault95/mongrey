# -*- coding: utf-8 -*-

import logging

import IPy
from gevent.wsgi import WSGIServer

logger = logging.getLogger(__name__)

class SecureWSGIServer(WSGIServer):
    
    def __init__(self, listener, application=None,
                 security_by_host=False, allow_hosts=None,
                 **kwargs):
        WSGIServer.__init__(self, listener, application=application, **kwargs)
        self._security_by_host = security_by_host
        self._allow_hosts = allow_hosts
    
    def handle(self, socket, address):
        if self._security_by_host and not self._security_check(address):                
            socket.close()
            return
        
        WSGIServer.handle(self, socket, address)
        
    def _security_check(self, address):
        """
        fail2ban: 2015-02-21 09:57:05 [5972] [CRITICAL] reject host [127.0.0.1]
        """
                
        if not self._security_by_host:
            return True
        
        if not self._allow_hosts:
            return True
        
        try:
            host = address[0]
            host_ipy = IPy.IP(host)

            for ip in self._allow_hosts:
                
                allow = IPy.IP(ip)
                
                if allow.len() == 1:
                    if ip == host:
                        return True
                else:
                    if host_ipy in allow:
                        return True

            logger.critical("reject host [%s]" % host)
            return False
        
        except Exception, err:
            logger.error(str(err))
        
        return False
        
        
