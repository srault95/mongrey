# -*- coding: utf-8 -*-

from gevent.monkey import patch_all
patch_all()

import time
import platform
import re
from pprint import pprint as pp
import urlparse
import itertools
import uuid
import types
import hashlib
import logging
import argparse
import sys
import os
import atexit

import six
import json

import gevent
from gevent.server import StreamServer
from gevent import socket

from decouple import config as env_config

from .. import version
from .. import constants
from .. import utils
from ..exceptions import *

try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False
    
logger = logging.getLogger(__name__)


DEFAULT_CONFIG = {
    
    'storage': env_config('MONGREY_STORAGE', 'mongo'),             
                      
    'host': env_config('MONGREY_HOST', '127.0.0.1', cast=str),
    
    'port': env_config('MONGREY_PORT', 9999, cast=int),
    
    'allow_hosts': env_config('MONGREY_ALLOW_HOSTS', '', cast=utils.to_list),
    
    'security_by_host': env_config('MONGREY_SECURITY_BY_HOST', False, cast=bool),
    
    'spawn': env_config('MONGREY_SPAWN', 50, cast=int),
    
    'backlog': env_config('MONGREY_BACKLOG', 256, cast=int),
    
    'connection_timeout': env_config('MONGREY_CONNECTION_TIMEOUT', 10.0, cast=float),
    
    #'default_action': env_config('MONGREY_DEFAULT_ACTION', 'DUNNO', cast=str),
    
    'error_action': env_config('MONGREY_ERROR_ACTION', 'DUNNO'),
    
    'close_socket': env_config('MONGREY_CLOSE_SOCKET', False, cast=bool),
    
    'no_stress': env_config('MONGREY_NO_STRESS', False, cast=bool),
    
    'stats_enable': env_config('MONGREY_STATS_ENABLE', True, cast=bool),
    
    'stats_interval': env_config('MONGREY_STATS_INTERVAL', 30.0, cast=float),

    'purge_enable': env_config('MONGREY_PURGE_ENABLE', True, cast=bool),
    
    'purge_interval': env_config('MONGREY_PURGE_INTERVAL', 60, cast=float),

    'metrics_enable': env_config('MONGREY_METRICS_ENABLE', True, cast=bool),
    
    'metrics_interval': env_config('MONGREY_METRICS_INTERVAL', 60.0 * 5, cast=float),
    
    'debug': env_config('MONGREY_DEBUG', False, cast=bool),
    
    'verbose': env_config('MONGREY_VERBOSE', 1, cast=int),
    
    'no_verify_protocol': env_config('MONGREY_NO_VERIFY_PROTOCOL', False, cast=bool),
    
    'mongodb_settings': {
        'host': env_config('MONGREY_DB', 'mongodb://localhost/mongrey'),
        'use_greenlets': True,
        'tz_aware': True,    
    },
                  
    'peewee_settings': {
        'db_name': env_config('MONGREY_DB', 'sqlite:///mongrey.db'),
        'db_options': {
            'threadlocals': True    #pour use with gevent patch
        }
    },        

    'cache_settings': {
        'cache_url': env_config('MONGREY_CACHE', 'simple'),
        'cache_timeout': env_config('MONGREY_CACHE_TIMEOUT', 300, cast=int),    
    },
                                       
    'country_ipv4': env_config('MONGREY_GEOIP_COUNTRY_V4', None),
    
    'country_ipv6': env_config('MONGREY_GEOIP_COUNTRY_V6', None),

    'greylist_settings': {
        'greylist_key': env_config('MONGREY_POLICY', constants.GREY_KEY_MED, cast=int),       
        'greylist_remaining': env_config('MONGREY_REMAINING', 20, cast=int),    # 60 second
        'greylist_expire': env_config('MONGREY_EXPIRE', 35*86400, cast=int), # 35 days
        'greylist_excludes': env_config('MONGREY_EXCLUDES', '', cast=utils.to_list),
        'greylist_private_bypass': env_config('MONGREY_PRIVATE_BYPASS', True, cast=bool),
    }
                  
}


def stats(interval=60):
    
    if not HAVE_PSUTIL:
        logger.warning("psutil is not installed")
        return

    logger.info("Start Stats...")
    
    pid = os.getpid()
    process = psutil.Process(pid)

    while True:
        gevent.sleep(interval)
        
        try:
            mem = process.memory_info()
            
            stat = {
                #'mem': float(process.memory_info()[0]) / (1024 ** 2),
                'mem_rss': utils.do_filesizeformat(mem.rss),
                'mem_vms': utils.do_filesizeformat(mem.vms),
                'mem_percent': process.memory_percent(),
                'cpu_percent': process.cpu_percent(None),
                'load_avg': os.getloadavg() if hasattr(os, 'getloadavg') else None,
                'connections': len(process.connections()),
            }
            logger.info(json.dumps(stat))
            
        except Exception, err:
            logger.error(str(err))
            
class PolicyServer(StreamServer):
    
    def __init__(self, host='0.0.0.0', port=9998, 
                 backlog=256, 
                 spawn=50,
                 security_by_host=False,
                 allow_hosts=[],
                 error_action=None,
                 connection_timeout=None,
                 no_stress=False,
                 no_verify_protocol=False,
                 close_socket=False,
                 policy=None,
                 debug=False,
                 verbose=1,
                 **kwargs
                 ):
        
        StreamServer.__init__(self, (host, port), handle=self.handler, backlog=backlog, spawn=spawn)
        
        self._host = host

        self._port = port
        
        self._concurency = spawn
        
        self._max_clients = backlog
        
        self._security_by_host = security_by_host
        
        self._allow_hosts = allow_hosts
        
        self._action_error = error_action
        
        self._connection_timeout = connection_timeout
        
        self._no_stress = no_stress
        
        self._no_verify_protocol = no_verify_protocol
        
        self._close_socket = close_socket
        
        self._policy = policy
                
        self._debug = debug
        
        self._verbose = verbose
        
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

            if not host in self._allow_hosts:
                logger.critical("reject host [%s]" % host)
                return False
            
            return True
            
        except Exception, err:
            logger.error(str(err))
        
        return False
        
    def handler(self, sock, address):
        """
        #('::1', 56483, 0, 0) <type 'tuple'>
        #Valable en ipv4 et v6
        host = address[0] 
        """
        
        if self._security_by_host and not self._security_check(address):                
            sock.close()
            return

        timeout = None
        
        fileobj = None
        instance_id = None
        
        try:
            if self._connection_timeout:        
                timeout = gevent.Timeout(self._connection_timeout, TimeoutError(
                            'Handler request exceeded maximum timeout value (%s seconds).' % self._connection_timeout
                            ))
                timeout.start()
            
            fileobj = sock.makefile()
                        
            protocol = utils.parse_postfix_protocol(fileobj, self._verbose > 2)
            
            if self._no_stress and 'stress' in protocol:
                if protocol['stress']:
                    raise BypassProtocolError("stress bypass")
            
            if not self._no_verify_protocol:
                utils.verify_protocol(protocol)
            
            actions = self._policy.check_actions(protocol)
            
            for action in actions:
                fileobj.write("action=%s\n" % action)
            fileobj.write("\n\n")
            
            gevent.sleep(0)

        except TimeoutError, err:
            if fileobj and not fileobj.closed:
                fileobj.write("action=%s\n\n" % self._action_error)
            logger.error(str(err))

        except BypassProtocolError, err:
            if fileobj and not fileobj.closed:
                fileobj.write("action=DUNNO\n\n")
            logger.warn(str(err))
                    
        except Exception, err:
            if fileobj and not fileobj.closed:
                fileobj.write("action=%s\n\n" % self._action_error)
            logger.error(str(err))
            
        finally:
            if timeout:
                timeout.cancel()
            
            try:
                if fileobj and not fileobj.closed:
                    fileobj.flush()
                    fileobj.close()
                    
                if self._close_socket:
                    sock.close()
            except Exception, err:
                msg = 'close socket error: %s' % str(err)
                logger.error(msg, exc_info=False)

    def _start_msg(self):
        logger.info("Start Policy Server on %s:%s" % (self._host, self._port))
        
        logger.info("OPTION error_action[%s]" % self._action_error)
        
        if self._security_by_host:
            logger.info("OPTION Security by ip ON. allows[%s]" % ",".join(self._allow_hosts))
        else:
            logger.info("OPTION Security by ip OFF")
        
        debug = "OFF"
        if self._debug:
            debug = "ON"
            
        logger.info("OPTION verbosity[%s] - debug[%s]" % (self._verbose, debug))
        
        logger.info("OPTION timeout[%s] - concurency[%s] - max-clients[%s]" % (self._connection_timeout,
                                                                               self._concurency, 
                                                                               self._max_clients))

                    
    def start(self):
        self._start_msg()
        StreamServer.start(self)
        
    def stop(self, timeout=None):
        logger.info("Stopping server...")
        
        StreamServer.stop(self, timeout=timeout)



def write_pid(pid_file):
    with open(pid_file, 'w') as fp:
        fp.write(str(os.getpid()))

def options():

    parser = argparse.ArgumentParser(description='Postfix Greylist Server',
                                     prog=os.path.basename(sys.argv[0]),
                                     version="mongo-greylist-%s" % (version.__VERSION__), 
                                     add_help=True)
    
    parser.add_argument('-D', '--debug', action="store_true")
    
    parser.add_argument('--console', 
                        action="store_true",
                        help="Enable logs console (stdout)")

    parser.add_argument('--syslog', 
                        action="store_true",
                        help="Enable syslog")

    parser.add_argument('--log-config',
                        dest="log_config", 
                        help='Log config from file')

    parser.add_argument('--pid', 
                        dest='pid_file',
                        help='Enable write pid file')
    
    parser.add_argument(choices=['start',                                  
                                 #'stop', 
                                 #'reload',
                                 #'status',
                                 'showconfig',
                                 ],
                        dest='command',
                        help="Run command.")
    
    args = parser.parse_args()
    return dict(args._get_kwargs())

def start_command(pid_file=None, **config):

    storage = config.pop('storage')
    
    stats_enable = config.pop('stats_enable')
    stats_interval = config.pop('stats_interval')
    
    purge_enable = config.pop('purge_enable')
    purge_interval = config.pop('purge_interval')
    
    metrics_enable = config.pop('metrics_enable')
    metrics_interval = config.pop('metrics_interval')
    
    cache_settings = config.pop('cache_settings')
    greylist_settings = config.pop('greylist_settings')
    
    from .. import cache
    cache.cache = cache.Cache(**cache_settings)

    policy_klass = None

    kwargs = greylist_settings.copy()
    kwargs['purge_interval'] = purge_interval
    kwargs['metrics_interval'] = metrics_interval

    if storage == "mongo":
        from mongrey.storage.mongo.policy import MongoPolicy
        policy_klass = MongoPolicy

    elif storage == "sql":
        from mongrey.storage.sql.policy import SqlPolicy
        policy_klass = SqlPolicy
    
    policy = policy_klass(**kwargs)
    
    if pid_file:
        write_pid(pid_file)     

    server = PolicyServer(policy=policy, **config)
    try:
        if purge_enable and purge_interval > 0:
            green_purge = gevent.spawn(policy.task_purge_expire)
            atexit.register(gevent.kill, green_purge)
            
        if metrics_enable and metrics_interval > 0:
            green_metrics = gevent.spawn(policy.task_metrics)
            atexit.register(gevent.kill, green_metrics)
            
        if stats_enable and stats_interval > 0:
            green_stats = gevent.spawn(stats, interval=stats_interval)
            atexit.register(gevent.kill, green_stats)
            
        server.serve_forever()
    except KeyboardInterrupt:
        sys.exit(0)

def main():
    opts = options()

    config = DEFAULT_CONFIG.copy()
        
    debug = opts.get('debug')
    command = opts.get('command')
    pid_file = opts.get('pid_file')
    
    config['debug'] = debug
    
    storage = config.get('storage', 'mongo')
    
    utils.configure_logging(debug=debug, 
                            stdout_enable=opts.get('console'), 
                            syslog_enable=opts.get('syslog'), 
                            prog_name="mongrey", 
                            config_file=opts.get('log_config'))
    
    if command == 'start':
        utils.configure_geoip(country_ipv4=config['country_ipv4'], country_ipv6=config['country_ipv6'])
        if storage == 'mongo':
            from mongrey.storage.mongo.utils import create_mongo_connection
            create_mongo_connection(config['mongodb_settings'])
        elif storage == "sql":
            from mongrey.storage.sql.models import configure_peewee
            configure_peewee(**config['peewee_settings'])
            
        start_command(pid_file=pid_file, **config)
        sys.exit(0)
    elif command == 'showconfig':
        pp(config)
        sys.exit(0)

    
if __name__ == "__main__":
    """
    python -m mongrey.server start
    """
    main()
