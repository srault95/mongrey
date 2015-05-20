# -*- coding: utf-8 -*-

import os
import sys
import argparse

import jinja2
import envoy

def options():
    
    parser = argparse.ArgumentParser(description='Mongrey Initd Install',
                                     prog=os.path.basename(sys.argv[0]),
                                     version="mongrey-%s" % (version.__VERSION__), 
                                     add_help=True)

    parser.add_argument('--server-path',
                        dest="server_path",
                        default="/usr/local/bin/mongrey-server",
                        help='Path of Mongrey Server binary: %(default)s')

    parser.add_argument(choices=[
                            'install-service',                
                            'uninstall-service',
                        ],
                        dest='command')

    parser.add_argument('-D', '--debug', action="store_true")

    parser.add_argument('-n', '--dry-run',
                        dest="dry_run", 
                        action="store_true")
        
    return dict(parser.parse_args()._get_kwargs())

def systemv_uninstall():
    """
    sudo /etc/init.d/mongrey-server stop
    sudo update-rc.d -f mongrey-server remove
    sudo rm -f /etc/init.d/mongrey-server
    sudo rm /usr/local/bin/mongrey-server    
    """

def systemv_install(server_path=None):
    """
    chmod +x /etc/init.d/mongrey-server
    
    sudo update-rc.d mongrey-server defaults 99
    sudo service mongrey-server start
    sudo service mongrey-server status
    sudo service mongrey-server stop

    """
    from .resources.initd import system5
    tmpl_path = os.path.abspath(os.path.join(system5.__path__[0], "mongrey-server.j2"))
    #TODO:
    

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
    python -m mongrey.migration.core -n -P C:/temp/postfix-abakus-db radicalspam    
    """
    main()
