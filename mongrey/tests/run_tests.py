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
    env = {
        'MONGREY_STORAGE': 'mongo'
    }
    
    #run(module="mongrey", argv=argv)
    #mongrey/tests/server/test_server.py
    run(defaultTest="mongrey.tests.storage.mongo.test_server", argv=argv, env=env)


if __name__ == "__main__":
    """
    > nok avec python -m
    python mongrey\tests\run_tests.py
    """
    main()    