# -*- coding: utf-8 -*-

import logging

import gevent

from ...policy import Policy
from . import models

logger = logging.getLogger(__name__)

class MongoPolicy(Policy):
    
    _name = "mongo"

    def search_domain(self, protocol):
        return models.Domain.search(protocol)

    def search_mynetwork(self, protocol):
        return models.Mynetwork.search(protocol)

    def search_policy(self, protocol):
        return models.Policy.search(protocol)

    def search_blacklist(self, protocol):
        return models.BlackList.search(protocol)
        
    def search_whitelist(self, protocol):
        return models.WhiteList.search(protocol)
        
    def search_greylist(self, key):
        return models.GreylistEntry.search_entry(key)
        
    def create_greylist(self, key=None, protocol=None, policy=None):
        return models.GreylistEntry.create_entry(key=key, protocol=protocol, policy=policy)

    def task_purge_expire(self, run_once=False):

        logger.info("Start Expired Purge...")
        
        while True:
            gevent.sleep(self.purge_interval)
            try:
                for_delete = models.query_for_purge()
                #for_delete = models.GreylistEntry.objects(expire_time__lt=utils.utcnow())
                count = for_delete.count()
                if count > 0:
                    logger.info("purge expire entries : %s" % count)
                    for_delete.delete()
                if run_once:
                    return
            except Exception, err:
                logger.error(str(err))

    def task_metrics(self):
    
        logger.info("Start Metrics...")
        
        while True:
            gevent.sleep(self.metrics_interval)
            try:
                metric = models.GreylistEntry.last_metrics()
                if metric:
                    models.GreylistMetric(**metric).save()
            except Exception, err:
                logger.error(str(err))
