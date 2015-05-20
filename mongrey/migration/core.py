# -*- coding: utf-8 -*-

import os
import sys
import argparse

from decouple import config as env_config

from .. import version
from .. import utils

DEFAULT_CONFIG = {
    
    'settings_path': env_config('MONGREY_SERVER_SETTINGS', None),             

    'db_settings': {
        'host': env_config('MONGREY_DB', 'sqlite:///mongrey.db'),
        'options': {
            'threadlocals': True
        }    
    },
                                       
}


def radicalspam_migration(basepath=None, models=None, dry_run=False):
    from . import radicalspam
    results = {}
    
    files_found = []
    files_not_found = []
    
    for f, settings in radicalspam.RS_FILES.iteritems():
        model_klass = models[settings[0]]
        func = settings[1]
        filepath = os.path.abspath(os.path.join(basepath, f))
        if os.path.exists(filepath):
            files_found.append(filepath)
            if not dry_run:
                results[f] = func(filepath=filepath, model_klass=model_klass)
        else:
            files_not_found.append(filepath)
        
    
    print "------------- RADICALSPAM MIGRATION -------------"
    for f in files_found:
        print("file found : %s" % f)
    for f in files_not_found:
        print("file not found : %s" % f)
            
    for key, result in results.iteritems():
        result['filename'] = key
        msg = "[%(filename)s] - success[%(success)s] - error[%(error)s]" % result
        print(msg)
        error_messages = result['error_messages']
        if len(error_messages) > 0:
            for e in error_messages:
                print("\t%s" % e) 
    print "-------------------------------------------------"

def get_models(**config):
    
    settings, storage = utils.get_db_config(config.get('db_settings', {}))
    
    if storage == "mongo":
        from mongrey.storage.mongo.utils import create_mongo_connection
        from mongrey.storage.mongo import models
        create_mongo_connection(**settings)
        _models = {
            'domain': models.Domain,
            'mynetwork': models.Mynetwork,
            'mailbox': models.Mailbox,
            'whitelist': models.WhiteList,
            'blacklist': models.BlackList,
        }        
        return _models

    elif storage == "sql":
        from mongrey.storage.sql.models import configure_peewee
        from mongrey.storage.sql import models
        configure_peewee(**settings)
        _models = {
            'domain': models.Domain,
            'mynetwork': models.Mynetwork,
            'mailbox': models.Mailbox,
            'whitelist': models.WhiteList,
            'blacklist': models.BlackList,
        }        
        return _models
    

def options():
    
    #TODO: source / destination libre par fichier: local-directory/mailbox, ...

    parser = argparse.ArgumentParser(description='Mongrey Migration',
                                     prog=os.path.basename(sys.argv[0]),
                                     version="mongrey-%s" % (version.__VERSION__), 
                                     add_help=True)

    parser.add_argument('-P', '--basepath',
                        dest="basepath",
                        default="/var/rs/addons/postfix/etc",
                        help='Base Path for search file. default: %(default)s')

    parser.add_argument('--settings',
                        dest="settings_path", 
                        default=DEFAULT_CONFIG['settings_path'], 
                        help='load settings from YAML file')

    parser.add_argument('--db',
                        dest="mongrey_db",
                        default=env_config('MONGREY_DB', 'sqlite:///mongrey.db'), 
                        help='Mongrey DB. default: %(default)s')
    
    parser.add_argument('-D', '--debug', action="store_true")

    parser.add_argument('-n', '--dry-run',
                        dest="dry_run", 
                        action="store_true")
    
    parser.add_argument(choices=[
                            'radicalspam',                                  
                            'postgrey',
                        ],
                        dest='command',
                        help="Migration From ?")
    
    return dict(parser.parse_args()._get_kwargs())

def main():
    opts = options()
    
    debug = opts.get('debug')
    basepath = opts.get('basepath')
    dry_run = opts.get('dry_run')
    command = opts.get('command')
    settings_path = opts.get('settings_path')
    
    config = DEFAULT_CONFIG.copy()

    if settings_path:
        filepath = os.path.expanduser(settings_path)
        if os.path.exists(filepath):
            config = utils.load_yaml_config(settings=filepath, 
                                            default_config=DEFAULT_CONFIG)
    
    models = get_models(**config)
    
    if not models:
        sys.stderr.write("not models loaded\n")
        sys.exit(1)
    
    if command == 'radicalspam':
        radicalspam_migration(basepath=basepath, 
                              models=models, 
                              dry_run=dry_run)

    elif command == 'postgrey':
        pass
        
if __name__ == "__main__":
    """
    python -m mongrey.migration.core -n -P C:/temp/postfix-db radicalspam    
    """
    main()
