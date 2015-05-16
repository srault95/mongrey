# -*- coding: utf-8 -*-

import logging

logger = logging.getLogger(__name__)

from .utils import read_db_file

def import_domains(filepath="/var/rs/addons/postfix/etc/local-relays.db", model_klass=None):
    
    values = read_db_file(filepath)
    
    result = dict(success=0, error=0, error_messages=[])
    
    for value, comments in values.items():
        try:
            model_klass(name=value.lower()).save()
            result['success'] += 1
        except Exception, err:
            result['error'] += 1
            result['error_messages'].append(str(err))
    
    return result

def _import_mailboxs(filepath=None, model_klass=None):
    
    values = read_db_file(filepath)
    
    result = dict(success=0, error=0, error_messages=[])
    
    for value, comments in values.items():
        try:
            model_klass(name=value.lower()).save()
            result['success'] += 1
        except Exception, err:
            result['error'] += 1
            result['error_messages'].append(str(err))
    
    return result

def import_mailboxs(filepath="/var/rs/addons/postfix/etc/local-directory.db", model_klass=None):
    return _import_mailboxs(filepath=filepath, model_klass=model_klass)

def import_mailboxs_exceptions(filepath="/var/rs/addons/postfix/etc/local-exceptions-directory.db", model_klass=None):
    return _import_mailboxs(filepath=filepath, model_klass=model_klass)

def _import_mynetworks(filepath=None, model_klass=None):
    
    values = read_db_file(filepath)
    
    result = dict(success=0, error=0, error_messages=[])
    
    for value, comments in values.items():
        try:
            model_klass(value=value.lower(),
                        comments=comments.replace('#', '').strip()).save()
            result['success'] += 1
        except Exception, err:
            result['error'] += 1
            result['error_messages'].append(str(err))
    
    return result

def import_mynetworks_lan(filepath="/var/rs/addons/postfix/etc/local-mynetworks-lan.db", model_klass=None):
    return _import_mynetworks(filepath=filepath, model_klass=model_klass)

def import_mynetworks_wan(filepath="/var/rs/addons/postfix/etc/local-mynetworks-wan.db", model_klass=None):
    return _import_mynetworks(filepath=filepath, model_klass=model_klass)

def _import_blacklist(filepath=None, field_name=None, model_klass=None):
    
    values = read_db_file(filepath)
    
    result = dict(success=0, error=0, error_messages=[])
    
    for value, comments in values.items():
        try:
            model_klass(value=value.lower(),
                        field_name=field_name,
                        comments=comments.strip()).save()
            result['success'] += 1
        except Exception, err:
            result['error'] += 1
            result['error_messages'].append(str(err))
    
    return result

def import_blacklist_clients(filepath="/var/rs/addons/postfix/etc/local-blacklist-clients.db", model_klass=None):
    return _import_blacklist(filepath=filepath, field_name="client_address", model_klass=model_klass)

def import_blacklist_senders(filepath="/var/rs/addons/postfix/etc/local-blacklist-senders.db", model_klass=None):
    return _import_blacklist(filepath=filepath, field_name="sender", model_klass=model_klass)
    
def import_blacklist_recipients(filepath="/var/rs/addons/postfix/etc/local-blacklist-recipients.db", model_klass=None):
    return _import_blacklist(filepath=filepath, field_name="recipient", model_klass=model_klass)
    
RS_FILES = {
    'local-relays.db': ('domain', import_domains),
    'local-directory.db': ('mailbox', import_mailboxs),
    'local-exceptions-directory.db': ('mailbox', import_mailboxs_exceptions),
    'local-mynetworks-lan.db': ('mynetwork', import_mynetworks_lan),
    'local-mynetworks-wan.db': ('mynetwork', import_mynetworks_wan),
    'local-blacklist-clients.db': ('blacklist', import_blacklist_clients),
    'local-blacklist-senders.db': ('blacklist', import_blacklist_senders),
    'local-blacklist-recipients.db': ('blacklist', import_blacklist_recipients)
}
