# -*- coding: utf-8 -*-

import logging
import anydbm

logger = logging.getLogger(__name__)

def read_db_file(filepath):
    
    values = {}
    
    try:
        db = anydbm.open(filepath, flag='r')
        
        for key, value in db.iteritems():
            values[key.strip('\x00').strip()] = value.strip('\x00').strip()
                        
        db.close()
    except Exception, err:
        logger.error(err)
    
    return values