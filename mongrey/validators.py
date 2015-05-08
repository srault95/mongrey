# -*- coding: utf-8 -*-

import re

from . import utils
from .constants import _

EMAIL_REGEX = re.compile(
    # dot-atom
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
    # quoted-string
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"'
    # domain (max length of an ICAAN TLD is 22 characters)
    r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,253}[A-Z0-9])?\.)+[A-Z]{2,22}$', re.IGNORECASE
)

def clean_domain(value, field_name=None, error_class=None):
    
    new_value = "user@%s" % value

    if not EMAIL_REGEX.match(new_value):
        message = _(u"Invalid Domain: %s") % value
        raise error_class(message, field_name=field_name)

def clean_email(value, field_name=None, error_class=None):
    
    if not EMAIL_REGEX.match(value):
        message = _(u"Invalid Email: %s") % value
        raise error_class(message, field_name=field_name)
    
def clean_email_or_domain(value, field_name=None, error_class=None):
    
    valid_email = False
    valid_domain = False
    try:
        clean_email(value, field_name, error_class)
        valid_email = True
    except:
        pass
    
    if not valid_email:
        try:
            clean_domain(value, field_name, error_class)
            valid_domain = True
        except:
            pass
    
    if not valid_email and not valid_domain:
        message = _(u"Invalid Email or Domain: %s") % value
        raise error_class(message, field_name=field_name)

def clean_ip_address(value, field_name=None, error_class=None):

    valid = utils.check_ipv4(value) or utils.check_ipv6(value)

    if not valid:
        message = _(u"Invalid IP Address: %s") % value
        raise error_class(message, field_name=field_name)

def clean_ip_address_or_network(value, field_name=None, error_class=None):
    
    valid = utils.check_ipv4(value) or utils.check_ipv6(value) or utils.check_is_network(value)

    if not valid:
        message = _(u"Invalid IP Address: %s") % value
        raise error_class(message, field_name=field_name)
    
def clean_hostname(value, field_name=None, error_class=None):
    
    valid = True
    
    if value:
        vals = value.split(".")
        
        if value is None or len(value.strip()) == 0:
            valid = False
        elif len(value) > 255:
            valid = False
        elif len(vals) < 3:
            valid = False
        elif value.strip().lower() == "unknow":
            valid = False
        
        domain = ".".join(vals[(len(vals) - 2):(len(vals))])
        if len(domain) > 63:
            valid = False

    if not valid:
        message = _(u"Invalid Hostname: %s") % value
        raise error_class(message, field_name=field_name)    

