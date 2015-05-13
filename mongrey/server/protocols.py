# -*- coding: utf-8 -*-

import logging
import re

from .. import constants
from ..exceptions import InvalidProtocolError 

line_regex = re.compile(r'^\s*([^=\s]+)\s*=(.*)$')

logger = logging.getLogger(__name__)

def parse_policy_protocol(fileobj, debug=False):
    """
    @see: http://www.postfix.org/SMTPD_POLICY_README.html
    """

    protocol = {}

    while True:
        line = fileobj.readline()
        
        if line:
            line = line.strip()
            if debug:
                logger.debug(line)
            
        if not line:
            break
        else:
            m = line_regex.match(line)
            if not m:
                break
             
            key = m.group(1)        
            value = m.group(2)
            
            if len(protocol) == 0:
                '''First line'''
                if key != 'request':
                    raise InvalidProtocolError("Invalid Protocol")
                if not value or value != 'smtpd_access_policy':
                    raise InvalidProtocolError("Invalid Protocol")
            elif key == 'request':
                '''request=smtpd_access_policy already parsing'''
                raise InvalidProtocolError("Invalid Protocol")

            if key in protocol:
                logger.warn("key is already in protocol : %s" % key)
            else:
                value = value.decode('utf-8', 'ignore')
                value = value.encode('us-ascii', 'ignore')
                protocol[key] = value.lower()
    
    request = protocol.get('request', None)
    if not request:
        raise InvalidProtocolError("Invalid Protocol")
    else:
        if request != 'smtpd_access_policy':
            raise InvalidProtocolError("Invalid Protocol")
    
    return protocol

def verify_protocol(protocol):

    if not 'protocol_state' in protocol:
        raise InvalidProtocolError("protocol_state field not in protocol")
    
    protocol_state = protocol.get('protocol_state')
    if not protocol_state.lower() in constants.ACCEPT_PROTOCOL_STATES:
        raise InvalidProtocolError("this protocol_state is not supported: %s" % protocol_state)
    
    for key in protocol.keys():
        if not key.lower() in constants.POSTFIX_PROTOCOL['valid_fields']:
            raise InvalidProtocolError("invalid field in protocol: %s" % key)




def tcp_table_protocol(fileobj, debug=False):
    """
    @see: http://www.postfix.org/tcp_table.5.html
    """
    
    protocol = {}

    while True:
        line = fileobj.readline()
        
        if line:
            line = line.strip()
            if debug:
                logger.debug(line)
        
        if not line:
            break
        else:
            """
            get SPACE key NEWLINE
                Look up data under the specified key.
                
            REPLY:
                500 SPACE text NEWLINE
                400 SPACE text NEWLINE
                200 SPACE text NEWLINE
            """
            return line

    return protocol


def tcp_table_test():
    """
    postconf -e "smtpd_client_restrictions = check_client_access tcp:127.0.0.0:15005"
    postconf -e "smtpd_sender_restrictions = check_sender_access tcp:127.0.0.0:15005"
    postconf -e "smtpd_recipient_restrictions = check_recipient_access tcp:127.0.0.0:15005, reject"
    run("swaks --server policy.mail-analytics.io:25 --quit-after RCPT --timeout 5 --protocol ESMTP --to contact@mail-analytics.net --from contact@radicalspam.org")
    """
    
    from gevent.server import StreamServer
    
    def handle(sock, address):
        fileobj = sock.makefile()
        key_search = tcp_table_protocol(fileobj, debug=True)
        print "key_search : ", key_search
        fileobj.write("200 TEST\n")
        fileobj.close()
        #sock.close()
    
    server = StreamServer(listener=('127.0.0.0', 15005), handle=handle)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    
if __name__ == "__main__":
     tcp_table_test()    