#!/usr/bin/env python
# -*- coding: utf-8 -*-

from decouple import config as env_config
import nose
from nose.core import run

def main():
    argv = [
     '',
     '-s',
     '--verbose',
     '--logging-level=INFO'
    ]
    
    #run(module="mongrey", argv=argv)
    nose.runmodule(name='mongrey', 
                   argv=[
                     '',
                     '-s',
                     '--verbose',
                     '--logging-level=INFO',
                    ])

if __name__ == "__main__":
    main()    