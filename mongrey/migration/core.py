# -*- coding: utf-8 -*-

import os
import sys
import argparse

from .. import version

def radicalspam_migration(basepath=None, dry_run=False):
    """
    1. Parcourir répertoire - rechercher les fichiers gérés (en .db)
    2. 
    """

def options():
    
    #TODO: source / destination libre par fichier: local-directory/mailbox, ...

    parser = argparse.ArgumentParser(description='Mongrey Migration',
                                     prog=os.path.basename(sys.argv[0]),
                                     version="mongrey-%s" % (version.__VERSION__), 
                                     add_help=True)

    parser.add_argument('-P', '--basepath',
                        dest="basepath", 
                        help='Base Path for search file')
    
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
    
    #TODO: config DB !!!

    debug = opts.get('debug')
    basepath = opts.get('basepath')
    dry_run = opts.get('dry_run')
    command = opts.get('command')
    
    if command == 'radicalspam':
        pass

    elif command == 'postgrey':
        pass
        
    

if __name__ == "__main__":
    main()
