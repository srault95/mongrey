# -*- coding: utf-8 -*-

import uuid
from gevent import socket
import gevent

protocol_yaml="""
request: smtpd_access_policy
protocol_state: RCPT
protocol_name: SMTP
helo_name: some.domain.tld
queue_id: 8045F2AB23
sender: foo@bar.tld
recipient: bar@foo.tld
recipient_count: 0
client_address: 1.2.3.4
client_name: another.domain.tld
reverse_client_name: another.domain.tld
instance: 123.456.7
#Postfix version 2.2 and later:
sasl_method: plain
sasl_username: you
sasl_sender:
size: 12345
ccert_subject: solaris9.porcupine.org
ccert_issuer: Wietse+20Venema
ccert_fingerprint: C2:9D:F4:87:71:73:73:D9:18:E7:C2:F3:C1:DA:6E:04
#Postfix version 2.3 and later:
encryption_protocol: TLSv1/SSLv3
encryption_cipher: DHE-RSA-AES256-SHA
encryption_keysize: 256
etrn_domain: 
#Postfix version 2.5 and later:
stress:
#Postfix version 2.9 and later:
ccert_pubkey_fingerprint: 68:B3:29:DA:98:93:E3:40:99:C7:D8:AD:5C:B9:C9:40
#Postfix version 3.0 and later:
client_port: 1234
"""

def policy_template(**kwargs):
    kwargs.setdefault('firstline', 'request=smtpd_access_policy')
    kwargs.setdefault('sender', '<>')
    kwargs.setdefault('recipient', 'contact@domain.com')
    kwargs.setdefault('client_address', '127.0.0.1')
    kwargs.setdefault('instance', str(uuid.uuid1()))
    kwargs.setdefault('queue_id', str(uuid.uuid1()))
    kwargs.setdefault('size', 0)
    kwargs.setdefault('helo_name', '127.0.0.1')
    kwargs.setdefault('stress', '')
    
    return '''%(firstline)s
protocol_state=RCPT
protocol_name=ESMTP
helo_name=%(helo_name)s
queue_id=%(queue_id)s
sender=%(sender)s
recipient=%(recipient)s
recipient_count=0
client_address=%(client_address)s
client_name=unknown
reverse_client_name=unknown
instance=%(instance)s
sasl_method=
sasl_username=
sasl_sender=
size=%(size)s
ccert_subject=
ccert_issuer=
ccert_fingerprint=
encryption_protocol=
encryption_cipher=
encryption_keysize=0
etrn_domain=
stress=%(stress)s
ccert_pubkey_fingerprint=
client_port=1234
''' % kwargs


def protocol_yaml_TO_dict(**kwargs):
    import yaml
    from StringIO import StringIO
    config = yaml.load(StringIO(protocol_yaml))
    config.update(kwargs)
    return config

def get_free_port():
    u"""Récupère un port libre pour les tests et ferme la socket std"""
    tempsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tempsock.bind(('localhost', 0))
    host, unused_port = tempsock.getsockname()
    tempsock.close()
    return host, unused_port

def tcp_policy_client(address, postfix_protocol, force_sleep=None, timeout=None):
    u""" Simule l'action client de Postfix
    
    Client TCP pour envoyer au serveur RS-Policy le protocol et recevoir le résultat
    dans un tableau qui seront les actions renvoyés à Postfix
    
    :param address: (host, port)
    :param postfix_protocol: str
    """
    
    if not postfix_protocol.endswith('\n\n'):
        """
        POUR ne pas bloquer la transaction, il faut que protocol se termine par un \n ou 2 ?
        """
        postfix_protocol = "%s\n\n" % postfix_protocol
    
    if timeout:
        conn = socket.create_connection(address, timeout=timeout)
    else:
        conn = socket.create_connection(address)
    fileobj = conn.makefile()
    
    fileobj.write(postfix_protocol)
    fileobj.flush()
    result = []
    while True:
        if force_sleep:
            gevent.sleep(force_sleep)
        
        line = fileobj.readline()
        
        if not line: break
        
        elif '=' in line:
            line = iter(line.strip().split('='))
            key = line.next()
            result.append(line.next())
        
        else:
            fileobj.flush()
            break
    
    return result

def send_policy(protocol_dict, host='127.0.0.1', port=9999, error_only=False):
    protocol_str = policy_template(**protocol_dict)
    actions = tcp_policy_client((host, port), protocol_str)
    return actions
        
