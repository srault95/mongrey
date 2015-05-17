# -*- coding: utf-8 -*-

from pprint import pprint as pp
import logging
import argparse
import sys
import os
import atexit
import six # noqa
import json

import gevent
from gevent.server import StreamServer

from decouple import config as env_config

import IPy

from .. import version
from .. import constants
from .. import utils
from ..exceptions import (BypassProtocolError, 
                          ConfigurationError, 
                          PolicyError, 
                          TimeoutError)
from . import protocols
try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False
    
logger = logging.getLogger(__name__)

DEFAULT_SETTINGS_PATH = [
    '~/mongrey/server.yml',
    '/etc/mongrey/server.yml',
]

#TODO: /var/lib/mongrey/fixtures.yml et/ou /opt/mongrey/fixtures.yml 
DEFAULT_FIXTURES_PATH = [
    '~/mongrey/server-fixtures.yml',
    '/etc/mongrey/server-fixtures.yml',
]

DEFAULT_CONFIG = {
                  
    'settings_path': env_config('MONGREY_SERVER_SETTINGS', None),             

    'fixtures_path': env_config('MONGREY_SERVER_FIXTURES', None),             
    
    'host': env_config('MONGREY_HOST', '127.0.0.1', cast=str),
    
    'port': env_config('MONGREY_PORT', 9999, cast=int),
    
    'allow_hosts': env_config('MONGREY_ALLOW_HOSTS', '127.0.0.1, ::1', cast=utils.to_list),
    
    'security_by_host': env_config('MONGREY_SECURITY_BY_HOST', True, cast=bool),
    
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

    'db_settings': {
        'host': env_config('MONGREY_DB', 'sqlite:///mongrey.db'),
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
        'greylist_key': env_config('MONGREY_POLICY', constants.GREY_KEY_MED),       
        'greylist_remaining': env_config('MONGREY_REMAINING', 20, cast=int),    # 60 second
        'greylist_expire': env_config('MONGREY_EXPIRE', 35*86400, cast=int), # 35 days
        'greylist_excludes': env_config('MONGREY_EXCLUDES', '', cast=utils.to_list),
        'greylist_private_bypass': env_config('MONGREY_PRIVATE_BYPASS', True, cast=bool),
    }
                  
}
"""
TODO: policy_settings
    rbl_enable=False,
    rbl_hosts=None,
    rwl_enable=False,
    rwl_hosts=None,
    rwbl_timeout=30,
    rwbl_cache_timeout=3600,
"""

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
        
        try:
            if self._connection_timeout:        
                timeout = gevent.Timeout(self._connection_timeout, TimeoutError(
                            'Handler request exceeded maximum timeout value (%s seconds).' % self._connection_timeout
                            ))
                timeout.start()
            
            fileobj = sock.makefile()
                        
            protocol = protocols.parse_policy_protocol(fileobj, self._verbose > 2)
            
            if self._no_stress and 'stress' in protocol:
                if protocol['stress']:
                    raise BypassProtocolError("stress bypass")
            
            if not self._no_verify_protocol:
                protocols.verify_protocol(protocol)
            
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
                        dest="settings_path", 
                        default=DEFAULT_CONFIG['settings_path'], 
                        help='load settings from YAML file')

    parser.add_argument('--fixtures', 
                        dest='fixtures_path',
                        help='load fixtures from YAML file')
    
    parser.add_argument('-D', '--debug', action="store_true")
    
    parser.add_argument('--console', 
                        action="store_true",
                        help="Enable logs console (stdout)")

    parser.add_argument('--syslog', 
                        action="store_true",
                        help="Enable syslog")

    parser.add_argument('--quiet', 
                        action="store_true",
                        help="Silent mode (config-install command only)")

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
                                 'check',
                                 'config',
                                 'config-install',
                                 'fixtures-import',
                                 'fixtures-export',
                                 ],
                        dest='command',
                        help="Run command.")

    parser.add_argument('--request',
                        dest="request", 
                        help='Request policy for check command')
    
    return dict(parser.parse_args()._get_kwargs())

def daemonize(pid_file, callback=None, **config):
    
    def stop(signal, frame): # noqa
        raise SystemExit('terminated by signal %d' % int(signal))    

    from .geventdaemon import GeventDaemonContext
    import signal

    context = GeventDaemonContext(pidfile=pid_file,
                                  signal_map={signal.SIGTERM: stop,
                                              signal.SIGINT: stop})
    
    with context:
        callback(**config)
        
def command_fixtures_import(option_fixtures_path=None, raise_error=False, **config):
    
    logger.info("start import fixtures...")

    fixtures_path = [
        option_fixtures_path,
        config.get('fixtures_path', None),
    ] + DEFAULT_FIXTURES_PATH
            
    try:
        fixtures = utils.load_yaml_config(settings=fixtures_path, default_config={})
        
        if fixtures and len(fixtures) > 0:
            policy_klass, models = get_store(**config)
            result = models.import_fixtures(fixtures)
            
            logger.info("IMPORT entries[%(entries)s] - success[%(success)s] - warn[%(warn_error)s] - error[%(fatal_error)s]" % result)
            
            for error in result['errors']:
                logger.error(error)
        
    except Exception, err:
        if raise_error:
            logger.error(str(err))
            raise
        logger.warning(str(err))
        
def command_fixtures_export(filepath=None, raise_error=False, **config):

    try:
        policy_klass, models = get_store(**config)

        fixtures = models.export_fixtures()
        return utils.dump_dict_to_yaml_file(filepath, data=fixtures, replace=True, createdir=True)
        
    except Exception, err:
        if raise_error:
            logger.error(str(err))
            raise
        logger.warning(str(err))
    
def command_load_settings(default_config=None, option_settings_path=None, raise_error=True):

    settings_path = [
        option_settings_path, 
        default_config.get('settings_path', None),
    ] + DEFAULT_SETTINGS_PATH
    
    try:
        return utils.load_yaml_config(settings=settings_path, default_config=default_config)
    except Exception, err:
        if raise_error:
            raise


def valid_allow_hosts(*allow_hosts):
    
    if not allow_hosts or len(allow_hosts) == 0:
        raise Exception("Empty allow_hosts")
    
    for ip in allow_hosts:
        try:        
            IPy.IP(ip)
        except Exception:
            return ip
    


def get_store(**config):

    settings, storage = utils.get_db_config(**config.get('db_settings', {}))    
    
    if storage == "mongo":
        from mongrey.storage.mongo.utils import create_mongo_connection
        from mongrey.storage.mongo.policy import MongoPolicy
        from mongrey.storage.mongo import models
        create_mongo_connection(settings)
        policy_klass = MongoPolicy
        return policy_klass, models

    elif storage == "sql":
        from mongrey.storage.sql.models import configure_peewee
        from mongrey.storage.sql.policy import SqlPolicy
        from mongrey.storage.sql import models
        configure_peewee(**settings)
        policy_klass = SqlPolicy
        return policy_klass, models
    
    return None, None

def command_check(request=None, request_file=None, **config):
    """
    > Le sender peut être absent
    cat /var/log/maillog-07052015.log | grep postgrey | grep ']: action' | awk -F ']: ' '{ print $2}'
    
    May 16 01:40:07 ns339295 postgrey[2429]: action=greylist, reason=new, client_name=unknown, client_address=177.125.127.151, recipient=carole.lemoing@csem.fr
    May 16 01:45:16 ns339295 postgrey[2429]: action=pass, reason=triplet found, delay=309, client_name=unknown, client_address=177.125.127.151, recipient=carole.lemoing@csem.fr
    """
    
    cache_settings = config.pop('cache_settings')
    policy_settings = config.pop('policy_settings')
    
    from .. import cache
    cache.configure_cache(**cache_settings)

    policy_klass, models = get_store(**config)

    kwargs = policy_settings.copy()
    kwargs['purge_interval'] = purge_interval
    kwargs['metrics_interval'] = metrics_interval

    policy = policy_klass(**kwargs)
    
    
    result = {}
    try:
        if request:
            policy.check_actions_one_request(request.strip())
        
        elif request_file:
            
            with open(request_file, 'r') as fp:
                for request in fp.readlines():
                    
                    if not request:
                        continue
                    
                    request = request.strip()
                    
                    policy.check_actions_one_request(request)
    except Exception, err:
        pass
    
def command_start(start_server=True, start_threads=True, **config):
    
    if config.get('security_by_host', False):
        ip_error = valid_allow_hosts(*config.get('allow_hosts'))
        if ip_error:
            sys.stderr.write("ip format error for [%s]" % ip)
            sys.exit(1) 

    stats_enable = config.pop('stats_enable')
    stats_interval = config.pop('stats_interval')
    
    purge_enable = config.pop('purge_enable')
    purge_interval = config.pop('purge_interval')
    
    metrics_enable = config.pop('metrics_enable')
    metrics_interval = config.pop('metrics_interval')
    
    cache_settings = config.pop('cache_settings')
    policy_settings = config.pop('policy_settings')
    
    from .. import cache
    cache.configure_cache(**cache_settings)

    policy_klass, models = get_store(**config)

    config.pop('db_settings', None)
    config.pop('settings_path', None)
    config.pop('fixtures_path', None)

    kwargs = policy_settings.copy()
    kwargs['purge_interval'] = purge_interval
    kwargs['metrics_interval'] = metrics_interval

    policy = policy_klass(**kwargs)
    
    server = PolicyServer(policy=policy, **config)
    
    try:
        if start_threads:
            
            if purge_enable and purge_interval > 0:
                green_purge = gevent.spawn(policy.task_purge_expire)
                atexit.register(gevent.kill, green_purge)
                
            if metrics_enable and metrics_interval > 0:
                green_metrics = gevent.spawn(policy.task_metrics)
                atexit.register(gevent.kill, green_metrics)
                
            if stats_enable and stats_interval > 0:
                green_stats = gevent.spawn(stats, interval=stats_interval)
                atexit.register(gevent.kill, green_stats)
    
        if start_server:            
            server.serve_forever()
        else:
            return server
        
    except Exception, err:
        sys.stderr.write("%s\n" % str(err))
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(0)

def main():
    opts = options()

    config = DEFAULT_CONFIG.copy()

    debug = opts.get('debug')
    command = opts.get('command')
    pid_file = opts.get('pid_file')
    daemon = opts.get('daemon')
    
    config['debug'] = debug
    
    utils.configure_logging(daemon=daemon,
                            debug=debug,                             
                            stdout_enable=opts.get('console'), 
                            syslog_enable=opts.get('syslog'), 
                            prog_name="mongrey", 
                            config_file=opts.get('log_config'))

    _config = command_load_settings(default_config=config, 
                                   option_settings_path=opts.get('settings_path', None),
                                   raise_error=False)
    if not _config:
        logger.warning("not setting file")
    else:
        config = _config

    if command == 'start':
        
        utils.configure_geoip(country_ipv4=config.pop('country_ipv4'), 
                              country_ipv6=config.pop('country_ipv6'))

        command_fixtures_import(option_fixtures_path=opts.get('fixtures_path', None),
                              raise_error=False,
                              **config)
        
        try:
            if sys.platform.startswith("win32"):
                command_start(**config)
            elif daemon:
                sys.stderr.write("Daemon mode is not implemented\n")
                sys.exit(1)
                #daemonize(pid_file, callback=command_start, **config)
            else:
                if pid_file:
                    utils.write_pid(pid_file) 
                command_start(**config)
                
            sys.exit(0)
        except Exception, err:
            sys.stderr.write("%s\n" % str(err))
            sys.exit(1)

    elif command == 'check':
        """
        
        """
        request = opts.get('request')
        utils.configure_geoip(country_ipv4=config.pop('country_ipv4'), 
                              country_ipv6=config.pop('country_ipv6'))
        command_check(request=request, **config)
        
    elif command == 'config-install':
        filepath = opts.get('settings_path', None) or config.get('settings_path', None) or DEFAULT_SETTINGS_PATH[0]
        
        filepath = os.path.abspath(os.path.expanduser(filepath))
        
        if os.path.exists(filepath) and not opts.get('quiet'):
            result = utils.confirm_with_exist(filepath, **DEFAULT_CONFIG.copy())
        else:
            try:
                result = utils.dump_dict_to_yaml_file(filepath, data=DEFAULT_CONFIG.copy(), replace=True, createdir=True)
                print("Success operation !. file writed: %s\n" % filepath)
            except Exception, err:
                print(str(err))
                sys.exit(1)
        if not result:
            sys.stdout.write("canceled operation\n")

    elif command == 'config':
        pp(config)

    elif command == 'fixtures-export':
        filepath = opts.get('fixtures_path', None) or config.get('fixtures_path', None) or DEFAULT_FIXTURES_PATH[0]
        try:
            result = command_fixtures_export(filepath=filepath, raise_error=True, **config)
            print("Success operation !. file writed: %s\n" % result)
        except Exception, err:
            print("ERROR: %s" % str(err))
            sys.exit(1)

    elif command == 'fixtures-import':
        try:
            command_fixtures_import(option_fixtures_path=opts.get('fixtures_path', None),
                                  raise_error=True, 
                                  **config)
        except Exception, err:
            print("ERROR: %s" % str(err))
            sys.exit(1)
            
        
    sys.exit(0)

    
if __name__ == "__main__":
    main()
