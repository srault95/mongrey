# -*- coding: utf-8 -*-

import time
import pprint
import os

from flask import current_app

from flask_script import Command, Option, Manager
from flask_script import prompt_bool

from werkzeug.debug import DebuggedApplication
from flask_script.commands import Shell, Server
from decouple import config as config_from_env

from mongrey.utils import GeventAccessLogger, read_whitelist
from mongrey.web.utils import SecureWSGIServer

def _import_postgrey_whitelist(filepath):
    whitelist, whitelist_ip = read_whitelist(filepath)
    
    for w in whitelist:
        print w
        
    for w in whitelist_ip:
        print "IP : ", w
    
def _show_config(app=None):

    if not app:
        app = current_app
    print "-------------------------------------------------------"
    app.config.keys().sort()
    pprint.pprint(dict(app.config))

    if app.config.get('STORAGE') == "mongo":
        print "---------------------------------"
        print "Reals Settings in mongoengine :"
        print "---------------------------------"
        from mongoengine.connection import _connection_settings, DEFAULT_CONNECTION_NAME        
        for key, val in _connection_settings.get(DEFAULT_CONNECTION_NAME).items():
            print "%s = %s" % (key, val)
    elif app.config.get('STORAGE') == "sql":
        import peewee
        print "---------------------------------"
        print "peewee                 : ", peewee.__version__        

    print "-------------------------------------------------------"
    print "app.root_path          : ", app.root_path
    print "app.config.root_path   : ", app.config.root_path
    print "app.instance_path      : ", app.instance_path
    print "app.static_folder      : ", app.static_folder
    print "app.template_folder    : ", app.template_folder
    print "-------------Extensions--------------------------------"
    extensions = app.extensions.keys()
    extensions.sort()
    for e in extensions:
        print e
    print "-------------------------------------------------------"

def _show_urls():
    order = 'rule'
    rules = sorted(current_app.url_map.iter_rules(), key=lambda rule: getattr(rule, order))
    for rule in rules:
        methods = ",".join(list(rule.methods))
        #rule.rule = str passé au début de route()
        print "%-30s" % rule.rule, rule.endpoint, methods


class ImportWhiteList(Command):
    u"""Import whitelist file"""
    
    option_list = (

        Option('-f', '--filepath',
               dest='filepath',
               required=True,
               ),

    )
    
    def run(self, filepath=None, **kwargs):
        if not os.path.exists(filepath):
            print "File not found : %s" % filepath
            return
        
        _import_postgrey_whitelist(filepath)
    

class ShowUrlsCommand(Command):
    u"""Display urls"""

    def run(self, **kwargs):
        _show_urls()

class ShowConfigCommand(Command):
    u"""Display configuration"""
    
    def run(self, **kwargs):
        _show_config()        

class CreateDefaultUserCommand(Command):
    u"""Create or reinit default User"""

    option_list = (
        Option('--reset', 
               action="store_true", 
               dest='update_if_exist', 
               default=False),
    )
    
    def run(self, update_if_exist=False, **kwargs):
        from mongrey.web.wsgi import _create_default_user
        _create_default_user(app=current_app, update_if_exist=False)  

def main(create_app_func=None):
    
    if not create_app_func:
        from mongrey.web.wsgi import create_app
        create_app_func = create_app
    
    class ServerWithGevent(Server):
        help = description = 'Runs the Flask server with Gevent WSGI'
    
        def __call__(self, app, host=None, port=None, use_debugger=None, use_reloader=None,
                   threaded=False, processes=1, passthrough_errors=False):
            
            config = app.config
            logger = app.logger
            
            if use_debugger:
                app = DebuggedApplication(app, evalex=True)
    
            host = config.get('WEB_HOST', host)
            port = config.get('WEB_PORT', port)
            security_by_host = config.get('SECURITY_BY_HOST', False)
            allow_hosts = config.get('ALLOW_HOSTS', [])
    
            server = SecureWSGIServer((host, port), application=app,
                                      security_by_host=security_by_host,
                                      allow_hosts=allow_hosts,
                                      #log=GeventAccessLogger(logger)
                                      )
            try:
                logger.info('Listening on http://%s:%s' % (host, port))
                server.serve_forever()
            except KeyboardInterrupt:
                pass
    
    env_config = config_from_env('MONGREY_SETTINGS', 'mongrey.web.settings.Prod')
    
    manager = Manager(create_app_func, with_default_commands=False)
    manager.add_option('-c', '--config',
                       dest="config",
                       default=env_config)

    manager.add_command("shell", Shell())

    manager.add_command("server", ServerWithGevent())

    manager.add_command("config", ShowConfigCommand())
    manager.add_command("urls", ShowUrlsCommand())
    
    manager.add_command("default-user", CreateDefaultUserCommand())    
    
    manager.add_command("import-whitelist", ImportWhiteList())
    
    manager.run()
    

if __name__ == "__main__":
    """
    python -m mongrey.web.manager run -p 8081 -d -R
    
    python -m mongrey.web.manager -c mongrey.web.settings.Dev server -p 8081 -d
    
    python -m mongrey.web.manager urls
    
    """
    main()

