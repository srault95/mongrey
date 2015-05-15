# -*- coding: utf-8 -*-

import os
import sys
import logging
import re
import uuid
import hashlib

from six import string_types

try:    
    from yaml import load as yaml_load
    from yaml import dump as yaml_dump
    from yaml import safe_dump    
    HAVE_YAML = True
except ImportError, err:
    HAVE_YAML = False

import arrow
from IPy import IP

try:
    from .ext.geoip_data import where_country_ipv4, where_country_ipv6
    HAVE_GEOIP_DATA = True
except ImportError:
    HAVE_GEOIP_DATA = False

from . import constants

geoip_country_v4 = None
geoip_country_v6 = None

logger = logging.getLogger(__name__)

def get_uid(protocol):    
    u'''Return unique identity from client_address and instance field with hashlib.sha256 crypt'''
    client_address = protocol.get('client_address')
    instance = protocol.get('instance')    
    key = "-".join([client_address, instance])
    return hashlib.sha256(key).hexdigest()

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
        
    except Exception:
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
    values = []
    for v in value.split(','):
        values.append(v.strip())
    return values

def is_private_address(client_address):
    try:
        return IP(client_address).iptype() in ['PRIVATE', 'LOOPBACK']
    except Exception:
        pass
    return False

def parse_domain(email):
    u"""Return domain name in lower case from email address"""

    if email is None: 
        return

    if not "@" in email:
        return

    _email = email.strip().lower()

    try:
        values = _email.split("@")

        if len(values) != 2:
            return
        else:
            return values[-1].lower().strip()

    except Exception:
        return

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
    except Exception:
        return False

def check_ipv4(value):
    try:
        return IP(value).version() == 4 
    except Exception:
        return False

def check_ipv6(value):
    try:
        return IP(value).version() == 6 
    except Exception:
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
>>> result.groups()
>>> result.groupdict()
results = read_postgrey_logs('/tmp/greylist.csv')
>>> import pprint
>>> pprint.pprint(results[0])
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
    """
    python -m mongrey.web.manager import-whitelist -f contrib/postgrey/postgrey_whitelist_clients.txt
    
    TODO: record DB - choix field_name selon type
    - ip/cidr: field_name="client_address"
    - regexp: field_name="client_name" ou sender ou recipient !!!!
    Ou générer un yaml intermédiaire à finaliser manuellement pour import
    
    TODO: validité des regexp !
    """

    with open(whitelist_filename, 'r') as whitelist_fh:
    
        whitelist = list()
        whitelist_ip = list()
        
        for line in whitelist_fh:
            line = line.split('#', 1)[0]
            line = line.split(';', 1)[0]
            line = line.strip()
            
            if not line or line == "":
                continue
            
            if line.startswith('/') and line.endswith('/'):
                # line is regex
                try:
                    re.compile(line[1:-1])
                    whitelist.append(line[1:-1])
                except Exception, err:
                    logger.error("LINE[%s] ERROR[%s]" % (line, str(err)))
            else:
                try:
                    IP(line)
                    whitelist_ip.append(line)
                except ValueError:
                    whitelist.append(line)
                except Exception, err:
                    logger.error("LINE[%s] ERROR[%s]" % (line, str(err)))
                    
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
        'disable_existing_loggers': False,
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
        #LOGGING['loggers'][prog_name]['level'] = 'DEBUG'
        for handler in LOGGING['handlers'].keys():
            LOGGING['handlers'][handler]['formatter'] = 'debug'
            LOGGING['handlers'][handler]['level'] = 'DEBUG' 

    logging.config.dictConfig(LOGGING)
    #logger = logging.getLogger(prog_name)
    logger = logging.getLogger()
    
    return logger


def dump_dict_to_yaml_file(filepath, data={}, replace=False, createdir=True):
    """Enregistre le fichier de configuration au format YAML"""

    if not HAVE_YAML:
        raise Exception("PyYAML is not installed\n")
    
    filepath = os.path.abspath(os.path.expanduser(filepath))
    
    if os.path.exists(filepath) and not replace:
        raise Exception("file %s exist" % filepath)
    
    filedir = os.path.abspath(os.path.dirname(filepath))
    if not os.path.exists(filedir):
        if createdir:
            os.makedirs(filedir)
        else:
            raise Exception("directory %s not found" % filedir)
    
    stream = file(filepath, 'w')
    safe_dump(data, stream, explicit_start=False, default_flow_style=False)
    #yaml_dump(data, stream, explicit_start=False, default_flow_style=False)
    stream.close()
    
    return filepath
    
def load_yaml_config(settings=None, default_config=None):

    if not HAVE_YAML:
        raise Exception("PyYAML is not installed\n")
    
    default_config = default_config or {}
    
    if isinstance(settings, list):
        found = False
        for s in settings:
            if not s: 
                continue
            filepath = os.path.abspath(os.path.expanduser(s))
            
            logger.debug("search in %s" % filepath)
            
            if filepath and os.path.exists(filepath):
                logger.info("load from %s" % filepath)
                settings = filepath
                found = True
                break
        if not found:
            raise Exception("file not found in all paths")
        
    stream = settings
    
    if isinstance(settings, string_types):
    
        with open(settings) as fp:
            from StringIO import StringIO
            stream = StringIO(fp.read())
            
    yaml_config = yaml_load(stream)
    default_config.update(yaml_config)
        
    return default_config

def confirm_with_exist(install_path, **data):
    try:
        print("The file %s exist.\n" % install_path)
        
        while True:
            answer = raw_input("Are you sure you want to destroy it? [y/N] : ")
            answer = answer.strip().lower()

            if answer == 'y':
                return dump_dict_to_yaml_file(install_path, data=data, replace=True, createdir=True)
            
            elif answer == 'n':
                return False
    except EOFError:
        pass
    except KeyboardInterrupt:
        return False
    
    return False