# -*- coding: utf-8 -*-

from .. import validators

def _check_fqdn_email(value):

    try:
        validators.clean_email(value)
        return True
    except Exception:
        return False

def _check_fqdn_hostname(hostname):

    if not hostname:
        return False
    
    try:
        validators.clean_hostname(hostname)
        return True
    except Exception:
        return False

def check_fqdn_client_name(protocol):
    client_name = protocol.get('client_name', None)
    return _check_fqdn_hostname(client_name)

def check_fqdn_helo_name(protocol):
    #TODO: split []
    helo_name = protocol.get('helo_name', None)
    return _check_fqdn_hostname(helo_name)

def check_fqdn_sender(protocol):

    value = protocol.get('recipient', None)
    
    if not value:
        return False
    
    if value in ["", "<>"]:
        return False
    
    return _check_fqdn_email(value)
        
def check_fqdn_recipient(protocol):

    value = protocol.get('recipient', None)
    
    if not value:
        return False
    
    return _check_fqdn_email(value)

