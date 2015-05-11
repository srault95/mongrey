# -*- coding: utf-8 -*-

from pprint import pprint as pp
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
#from gevent import socket
import socket

from decouple import config as env_config

import IPy

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
    
    'purge_interval': env_config('MONGREY_PURGE_INTERVAL', 60.0, cast=float),

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

    'policy_settings': {
        'blacklist_enable': env_config('MONGREY_BLACKLIST_ENABLE', True, cast=bool),       
        'domain_vrfy': env_config('MONGREY_DOMAIN_ENABLE', False, cast=bool),       
        'mynetwork_vrfy': env_config('MONGREY_MYNETWORK_ENABLE', False, cast=bool),       
        'spoofing_enable': env_config('MONGREY_SPOOFING_ENABLE', False, cast=bool),       
        'greylist_enable': env_config('MONGREY_GREYLIST_ENABLE', True, cast=bool),       
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
    
    def __init__(self, host='0.0.0.0', port=9999, 
                 backlog=256, 
                 spawn=50,
                 security_by_host=False,
                 allow_hosts=None,
                 error_action=None,
                 connection_timeout=None,
                 no_stress=False,
                 no_verify_protocol=False,
                 close_socket=False,
                 policy=None,
                 debug=False,
                 verbose=1
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

    def start(self):

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

        StreamServer.start(self)
        
    def stop(self, timeout=None):
        logger.info("Stopping server...")
        
        StreamServer.stop(self, timeout=timeout)


def options():

    parser = argparse.ArgumentParser(description='Mongrey Server',
                                     prog=os.path.basename(sys.argv[0]),
                                     version="mongrey-%s" % (version.__VERSION__), 
                                     add_help=True)

    parser.add_argument('--settings',
                        dest="yaml_settings_path", 
                        help='load settings from YAML file')
    
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

    parser.add_argument('--daemon', 
                        action="store_true",
                        help="Daemonize")

    parser.add_argument('--pid', 
                        dest='pid_file',
                        help='Enable write pid file')
    
    parser.add_argument(choices=['start',                                  
                                 'showconfig',
                                 ],
                        dest='command',
                        help="Run command.")
    
    args = parser.parse_args()
    return dict(args._get_kwargs())

def daemonize(pid_file, callback=None, **config):
    
    def stop(signal, frame):
        raise SystemExit('terminated by signal %d' % int(signal))    

    from .geventdaemon import GeventDaemonContext
    import signal
    """
            chroot_directory=None,
            working_directory="/",
            umask=0,
            uid=None,
            gid=None,
            prevent_core=True,
            detach_process=None,
            files_preserve=None,
            pidfile=None,
            stdin=None,
            stdout=None,
            stderr=None,
            signal_map=None,
    
    """
    context = GeventDaemonContext(pidfile=pid_file,
                                  signal_map={signal.SIGTERM: stop,
                                              signal.SIGINT: stop})
    
    with context:
        callback(**config)

def start_command(**config):
    
    storage = config.pop('storage')

    if not storage in ["mongo", "sql"]:
        raise ConfigurationError("storage not available: %s\n" % storage)
    
    if storage == "sql" and not "peewee_settings" in config:
        raise ConfigurationError("peewee_settings not found in configuration")

    if storage == "mongo" and not "mongodb_settings" in config:
        raise ConfigurationError("mongodb_settings not found in configuration")

    stats_enable = config.pop('stats_enable')
    stats_interval = config.pop('stats_interval')
    
    purge_enable = config.pop('purge_enable')
    purge_interval = config.pop('purge_interval')
    
    metrics_enable = config.pop('metrics_enable')
    metrics_interval = config.pop('metrics_interval')
    
    cache_settings = config.pop('cache_settings')
    policy_settings = config.pop('policy_settings')
    
    from .. import cache
    cache.cache = cache.Cache(**cache_settings)

    policy_klass = None

    kwargs = policy_settings.copy()
    kwargs['purge_interval'] = purge_interval
    kwargs['metrics_interval'] = metrics_interval

    db = None

    if storage == "mongo":
        from mongrey.storage.mongo.utils import create_mongo_connection
        from mongrey.storage.mongo.policy import MongoPolicy
        mongodb_settings = config.pop('mongodb_settings')
        create_mongo_connection(mongodb_settings)
        db = mongodb_settings['host']
        policy_klass = MongoPolicy
        config.pop('peewee_settings')

    elif storage == "sql":
        from mongrey.storage.sql.models import configure_peewee
        from mongrey.storage.sql.policy import SqlPolicy
        peewee_settings = config.pop('peewee_settings')
        configure_peewee(**peewee_settings)
        db = peewee_settings['db_name']
        policy_klass = SqlPolicy
        config.pop('mongodb_settings')
    
    policy = policy_klass(**kwargs)
    
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

        logger.info("STORAGE[%s] - DB[%s]" % (storage, db))
            
        server.serve_forever()
        
    except Exception, err:
        sys.stderr.write("%s\n" % str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

def main():
    opts = options()

    config = DEFAULT_CONFIG.copy()
    
    yaml_settings_path = opts.get('yaml_settings_path')
    if yaml_settings_path:
        try:
            config = utils.load_yaml_config(settings=yaml_settings_path, default_config=config)
        except Exception, err:
            sys.stderr.write("%s\n" % str(err))
            sys.exit(1)
        
    debug = opts.get('debug')
    command = opts.get('command')
    pid_file = opts.get('pid_file')
    daemon = opts.get('daemon')
    
    config['debug'] = debug
    
    utils.configure_logging(debug=debug, 
                            stdout_enable=opts.get('console'), 
                            syslog_enable=opts.get('syslog'), 
                            prog_name="mongrey", 
                            config_file=opts.get('log_config'))
    
    if command == 'start':
        utils.configure_geoip(country_ipv4=config.pop('country_ipv4'), country_ipv6=config.pop('country_ipv6'))
        try:
            if not sys.platform.startswith("win32") and daemon:
                daemonize(pid_file, callback=start_command, **config)
            else: 
                start_command(**config)
                
            sys.exit(0)
        except Exception, err:
            sys.stderr.write("%s\n" % str(err))
            sys.exit(1)
        
    elif command == 'showconfig':
        pp(config)
        sys.exit(0)

    
if __name__ == "__main__":
    """
    python -m mongrey.server start
    """
    main()
