# -*- coding: utf-8 -*-

import os
import sys
import argparse

import jinja2
import envoy

from .. import version

def options():
    
    parser = argparse.ArgumentParser(description='Mongrey Install',
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

    parser.add_argument('--type-init',
                        choices=[
                            'system5',                
                            'supervisord',
                        ],
                        dest='type_init')

    parser.add_argument('-D', '--debug', action="store_true")

    parser.add_argument('-n', '--dry-run',
                        dest="dry_run", 
                        action="store_true")
        
    return dict(parser.parse_args()._get_kwargs())

def systemv_uninstall():
    raise NotImplementedError()

    """
    sudo /etc/init.d/mongrey-server stop
    sudo update-rc.d -f mongrey-server remove
    sudo rm -f /etc/init.d/mongrey-server
    sudo rm /usr/local/bin/mongrey-server    
    """

def systemv_install(server_path=None):
    raise NotImplementedError()

    """
    chmod +x /etc/init.d/mongrey-server
    sudo update-rc.d mongrey-server defaults 99
    sudo service mongrey-server start
    sudo service mongrey-server status
    sudo service mongrey-server stop
    """
    from .resources.initd import system5
    tmpl_path = os.path.abspath(os.path.join(system5.__path__[0], "mongrey-server.j2"))
    

def main():
    opts = options()
    
    debug = opts.get('debug')
    server_path = opts.get('server_path')
    dry_run = opts.get('dry_run')
    command = opts.get('command')
    type_init = opts.get('type_init')
    
    if command == 'install-service':
        raise NotImplementedError()

    elif command == 'uninstall-service':
        raise NotImplementedError()
        
if __name__ == "__main__":
    """
    python -m mongrey.install.core --type-init system5 install-service    
    """
    main()
