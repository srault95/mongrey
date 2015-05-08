# -*- coding: utf-8 -*-

import os
import sys
import logging
import re

import arrow
from IPy import IP

try:
    from geoip_data import where_country_ipv4, where_country_ipv6
    HAVE_GEOIP_DATA = True
except ImportError:
    HAVE_GEOIP_DATA = False

from . import constants
from .exceptions import *    

geoip_country_v4 = None
geoip_country_v6 = None

line_regex = re.compile(r'^\s*([^=\s]+)\s*=(.*)$')

logger = logging.getLogger(__name__)

def get_country(client_address):

    try:
        ip = IP(client_address)
        
        if ip.iptype() != 'PUBLIC':
            return None
        
        if ip.version() == 4:
            if not geoip_country_v4:
                return None
            
            return geoip_country_v4.country_code_by_addr(client_address)

        if ip.version() == 6:
            if not geoip_country_v6:
                return None
            
            return geoip_country_v6.country_code_by_addr_v6(client_address)
        
    except:
        pass

def configure_geoip(country_ipv4=None, country_ipv6=None):
    
    import pygeoip
    global geoip_country_v4
    global geoip_country_v6
     
    if not geoip_country_v4:
        if country_ipv4 and os.path.exists(country_ipv4):
            geoip_country_v4 = pygeoip.GeoIP(country_ipv4, flags=pygeoip.MMAP_CACHE)            
        elif HAVE_GEOIP_DATA:
            geoip_country_v4 = pygeoip.GeoIP(where_country_ipv4(), flags=pygeoip.MMAP_CACHE)

    if not geoip_country_v6:
        if country_ipv6 and os.path.exists(country_ipv6):
            geoip_country_v6 = pygeoip.GeoIP(country_ipv6, flags=pygeoip.MMAP_CACHE)
        elif HAVE_GEOIP_DATA:
            geoip_country_v6 = pygeoip.GeoIP(where_country_ipv6(), flags=pygeoip.MMAP_CACHE)
    

def utcnow():
    return arrow.utcnow().datetime

def to_list(value):
    if not value:
        return []
    return value.split(',')

def is_private_address(client_address):
    try:
        return IP(client_address).iptype() == 'PRIVATE'
    except:
        pass
    return False

def parse_domain(email):
    u"""Renvoi en minuscule, la partie domaine d'une adresse email"""

    if email is None: return None

    if email.find('@') < 0: return None

    _email = email.strip().lower()

    try:

        values = _email.split("@")

        if len(values) != 2:
            return None
        else:
            return values[1].lower().strip()

    except Exception, err:
        return None

def do_filesizeformat(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    _bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and "KiB" or "kB"),
        (binary and "MiB" or "MB"),
        (binary and "GiB" or "GB"),
        (binary and "TiB" or "TB"),
        (binary and "PiB" or "PB"),
        (binary and "EiB" or "EB"),
        (binary and "ZiB" or "ZB"),
        (binary and "YiB" or "YB")
    ]
    if _bytes == 1:
        return "1 Byte"
    elif _bytes < base:
        return "%d Bytes" % _bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base * base ** (i + 1)
            if _bytes < unit:
                return "%.1f %s" % ((_bytes / unit), prefix)
        return "%.1f %s" % ((_bytes / unit), prefix)


def check_is_network(value):
    try:
        return IP(value).len() > 1
    except:
        return False

def check_ipv4(value):
    try:
        return IP(value).version() == 4 
    except:
        return False

def check_ipv6(value):
    try:
        return IP(value).version() == 6 
    except:
        return False
    
class GeventAccessLogger(object):
    
    def __init__(self, logger):
        self.logger = logger
        self.level = self.logger.level
    
    def write(self, value):
        if self.level == logging.INFO:
            self.logger.info(value)
        elif self.level == logging.WARN:
            self.logger.warn(value)
        elif self.level == logging.ERROR:
            self.logger.error(value)
        elif self.level == logging.DEBUG:
            self.logger.debug(value)
        else:
            self.logger.info(value)


"""
action=greylist, reason=new, client_name=qc206.internetdsl.tpnet.pl, client_address=80.55.28.206, sender=Jessica.fa@ataaksa.com, recipient=cias@ciasdublaisois.fr

>>> result.groups()
('pass', 'client whitelist', 'mx1.ville-blois.fr', '195.101.212.30', 'Sylvain.HEURTEBISE@blois.fr', 'mcsauve@ciasdublaisois.fr')

>>> result.groupdict()
{'sender': 'Sylvain.HEURTEBISE@blois.fr', 'client_name': 'mx1.ville-blois.fr', 'reason': 'client whitelist', 'action': 'pass', 'recipient': 'mcsauve@ciasdublaisois.fr', 'client_address': '195.101.212.30'}

results = read_postgrey_logs('/tmp/greylist.csv')

>>> import pprint
>>> pprint.pprint(results[0])
{'action': 'greylist',
 'client_address': '209.43.22.9, sender=bounce-2067564_HTML-87484678-1167334-10875875-0@bounce.vp-email.com',
 'client_name': 'mta9.vp-email.com',
 'reason': 'new',
 'recipient': 'lverdier@ciasdublaisois.fr',
 'sender': None}

"""

def read_postgrey_logs(filepath):
    line_re = re.compile("^action=(?P<action>.*),\sreason=(?P<reason>.*),\sclient_name=(?P<client_name>.*),\sclient_address=(?P<client_address>.*),\s(sender=(?P<sender>.*),\s)+recipient=(?P<recipient>.*)$", re.IGNORECASE)
    results = []
    with open(filepath, 'r') as fp:
        for line in fp.readlines():
            search = line_re.match(line.strip())
            if search:
                results.append(search.groupdict())
            else:
                print "not : ", line
    return results
    

def read_whitelist(whitelist_filename):
    raise NotImplementedError

    with open(whitelist_filename, 'r') as whitelist_fh:
    
        whitelist = list()
        whitelist_ip = list()
        
        for line in whitelist_fh:
            line = line.split('#', 1)[0]
            line = line.split(';', 1)[0]
            line = line.strip()
            if line == "":
                continue
            if line.startswith('/') and line.endswith('/'):
                # line is regex
                whitelist.append(re.compile(line[1:-1]))
                continue
            try:
                IP(line)
                whitelist_ip.append(line)
            except (ValueError):
                # Ordinary string (domain name or username)
                whitelist.append(line)
        return (whitelist, whitelist_ip)

def domain_from_hostname(host):
    try:
        d = host.split('.')
        if len(d) > 1:
            return '%s.%s' % (d[-2], d[-1])
        else:
            return host
    except:
        return host
    
def build_key(protocol, greylist_key=constants.GREY_KEY_MED):

    build_key = []

    client_address = protocol.get('client_address')
    sender = protocol.get('sender', '<>')
    recipient = protocol.get('recipient')
    recipient_domain = parse_domain(recipient)
    
    if greylist_key == constants.GREY_KEY_VERY_LOW:
        build_key.append(client_address)
    elif greylist_key == constants.GREY_KEY_LOW:
        build_key.append(client_address)
        if recipient_domain:
            build_key.append(recipient_domain)
    elif greylist_key == constants.GREY_KEY_MED:
        build_key.append(client_address)
        build_key.append(recipient)
    elif greylist_key == constants.GREY_KEY_HIGH:
        build_key.append(client_address)
        build_key.append(sender)
        build_key.append(recipient)
    elif greylist_key == constants.GREY_KEY_SPECIAL:
        build_key.append(sender)
        build_key.append(recipient)
    
    return "-".join(build_key)
    
    
def verify_protocol(protocol):

    if not 'protocol_state' in protocol:
        raise InvalidProtocolError("protocol_state field not in protocol")
    
    protocol_state = protocol.get('protocol_state')
    if not protocol_state.lower() in constants.ACCEPT_PROTOCOL_STATES:
        raise InvalidProtocolError("this protocol_state is not supported: %s" % protocol_state)
    
    for key in protocol.keys():
        if not key.lower() in constants.POSTFIX_PROTOCOL['valid_fields']:
            raise InvalidProtocolError("invalid field in protocol: %s" % key)

def parse_postfix_protocol(fileobj, debug=False):

    protocol = {}

    while True:
        line = fileobj.readline()
        
        if line:
            line = line.strip()
            if debug:
                print(line)
            
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
                protocol[key] = value.lower()
    
    request = protocol.get('request', None)
    if not request:
        raise InvalidProtocolError("Invalid Protocol")
    else:
        if request != 'smtpd_access_policy':
            raise InvalidProtocolError("Invalid Protocol")
    
    return protocol


def configure_logging(debug=False, 
                      stdout_enable=True, 
                      syslog_enable=False,
                      prog_name=None,
                      config_file=None
                      ):

    IS_WINDOWS = sys.platform.startswith("win32")
    
    import logging.config
    
    if config_file:
        logging.config.fileConfig(config_file, disable_existing_loggers=True)
        return logging.getLogger(prog_name)
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'debug': {
                'format': 'line:%(lineno)d - %(asctime)s %(name)s: [%(levelname)s] - [%(process)d] - [%(module)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
            'simple': {
                'format': '%(asctime)s %(name)s: [%(levelname)s] - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },    
        'handlers': {
            'null': {
                'level':'ERROR',
                'class':'logging.NullHandler',
            },
            'console':{
                'level':'INFO',
                'class':'logging.StreamHandler',
                'formatter': 'simple'
            },       
        },
        'loggers': {
            '': {
                'handlers': [],
                'level': 'INFO',
                'propagate': False,
            },
            prog_name: {
                'level': 'INFO',
                'propagate': True,
            },
        },
    }
    
    if IS_WINDOWS:
        LOGGING['loggers']['']['handlers'] = ['console']

    elif syslog_enable:
        LOGGING['handlers']['syslog'] = {
                'level':'INFO',
                'class':'logging.handlers.SysLogHandler',
                'address' : '/dev/log',
                'facility': 'daemon',
                'formatter': 'simple'    
        }       
        LOGGING['loggers']['']['handlers'].append('syslog')
        
    if 'SENTRY_DSN' in os.environ:
        LOGGING['handlers']['sentry'] = {
            'level': 'ERROR',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': os.environ.get('SENTRY_DSN'),
        }
        LOGGING['loggers']['']['handlers'].append('sentry')
    
    if stdout_enable:
        if not 'console' in LOGGING['loggers']['']['handlers']:
            LOGGING['loggers']['']['handlers'].append('console')

    '''if handlers is empty'''
    if not LOGGING['loggers']['']['handlers']:
        LOGGING['loggers']['']['handlers'] = ['console']
        
    if debug:
        LOGGING['loggers']['']['level'] = 'DEBUG'
        LOGGING['loggers'][prog_name]['level'] = 'DEBUG'
        for handler in LOGGING['handlers'].keys():
            LOGGING['handlers'][handler]['formatter'] = 'debug'
            LOGGING['handlers'][handler]['level'] = 'DEBUG' 

    logging.config.dictConfig(LOGGING)
    logger = logging.getLogger(prog_name)
    
    return logger

    