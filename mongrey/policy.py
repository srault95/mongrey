# -*- coding: utf-8 -*-

import logging
import time
import regex
import IPy

from . import cache
from . import utils
from . import constants

logger = logging.getLogger(__name__)

def generic_search(protocol=None, objects=[], valid_fields=[], 
                   cache_key=None, cache_enable=True, 
                   return_instance=False):

    start = time.time()

    values = []
    for field in valid_fields:
        value = protocol.get(field, None)
        if value and not value in ['unknow', '<>']:
            values.append(value)

    #FIXME: car prend tous les champs ?    
    if not return_instance and cache.cache and cache_enable and cache_key:
        for v in values:
            _cache_key = "%s-%s" % (cache_key, v)
            cache_value = cache.cache.get(_cache_key)
            if cache_value:
                logger.debug("found in cache : %s" % cache_value)
                return cache_value
    
    return_value = None

    client_address = protocol.get('client_address')
    client_name = protocol.get('client_name')
    sender = protocol.get('sender', None)
    recipient = protocol.get('recipient')
    country = protocol.get('country', None)
    helo_name = protocol.get('helo_name', None)

    try:

        for reg in objects:

            try:
                if 'country' in valid_fields and country and reg.field_name == "country":
                    if country.lower() == reg.value.lower():
                        return_value = country
                        if return_instance:
                            return_value = reg
                        break
                
                elif 'client_address' in valid_fields and reg.field_name == "client_address":
                    ip = IPy.IP(reg.value)
                    
                    if ip.len() == 1:
                        if client_address == reg.value:
                            return_value = client_address
                            if return_instance:
                                return_value = reg
                            break
                        
                    else:
                        '''Include network'''
                        if client_address in ip:
                            return_value = client_address
                            if return_instance:
                                return_value = reg
                            break
                
                elif 'client_name' in valid_fields and client_name != 'unknow' and reg.field_name == "client_name":
                    if regex.match(reg.value, client_name, regex.IGNORECASE):
                        return_value = client_name
                        if return_instance:
                            return_value = reg
                        break

                elif 'helo_name' in valid_fields and helo_name and reg.field_name == "helo_name":
                    if regex.match(reg.value, helo_name, regex.IGNORECASE):
                        return_value = helo_name
                        if return_instance:
                            return_value = reg
                        break

                elif 'sender' in valid_fields and sender and sender != '<>' and reg.field_name == "sender":
                    if regex.match(reg.value, sender, regex.IGNORECASE):
                        return_value = sender
                        if return_instance:
                            return_value = reg
                        break

                elif 'recipient' in valid_fields and reg.field_name == "recipient":
                    if regex.match(reg.value, recipient, regex.IGNORECASE):
                        return_value = recipient
                        if return_instance:
                            return_value = reg
                        break
                        
            except Exception, err:
                logger.warning(str(err))
    finally:
        
        if return_value and cache.cache and cache_enable and cache_key:
            if not return_instance:
                cache_key = "%s-%s" % (cache_key, return_value)
                logger.debug("set cache key[%s]" % cache_key)
                cache.cache.set(cache_key, return_value)

        logger.debug("search time[%.3f]" % (time.time() - start))

    return return_value


class Policy(object):
    
    _name = None

    def __init__(self, 
                 greylist_key=constants.GREY_KEY_MED, 
                 greylist_remaining=20,        # 20 seconds
                 greylist_expire=35*86400,     # 35 days
                 greylist_private_bypass=True,
                 greylist_excludes=[],
                 blacklist_enable=True,
                 purge_interval=60,
                 metrics_interval=60*5):
        """
            Constructor

            :param greylist_key:
                Numeric value (@see constants.GREY_KEY_MED)
            :param greylist_remaining:
                Delay for attempt after the first greylist request
        """

        self.greylist_key = greylist_key 
        self.greylist_remaining = greylist_remaining
        self.greylist_expire = greylist_expire
        self.greylist_private_bypass = greylist_private_bypass
        self.greylist_excludes = greylist_excludes
        self.blacklist_enable = blacklist_enable
        self.purge_interval = purge_interval
        self.metrics_interval = metrics_interval

    def check_actions(self, protocol):

        policy_name = "default"
    
        if self.greylist_excludes and protocol['client_address'] in self.greylist_excludes:
            msg = "action=pass, reason=exclude, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s" % protocol
            msg = "policy=%s %s" % (msg, policy_name)
            logger.info(msg)
            return ["DUNNO exclude filtering [%(client_address)s]" % protocol]    
        
        if self.greylist_private_bypass and utils.is_private_address(protocol['client_address']):
            msg = "action=pass, reason=private, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s" % protocol
            msg = "policy=%s %s" % (msg, policy_name)
            logger.info(msg)
            return ["DUNNO private address [%(client_address)s]" % protocol]    
    
        if not 'country' in protocol:
            protocol['country'] = utils.get_country(protocol['client_address'])
            
        if self.blacklist_enable:
            bl = self.search_blacklist(protocol)
            if bl:
                msg = "action=reject, reason=blacklisted, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s, policy=default" % protocol
                logger.info(msg)
                #TODO: custom code et message
                return ["554 5.7.1 blacklisted [%s]" % bl]    
        
        wl = self.search_whitelist(protocol)
        if wl:
            msg = "action=pass, reason=whitelisted, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s, policy=default" % protocol
            logger.info(msg)
            return ["DUNNO whitelisted [%s]" % wl]    
        
        greylist_remaining = self.greylist_remaining
        greylist_key = self.greylist_key
        greylist_expire = self.greylist_expire
        
        policy = self.search_policy(protocol)
        if policy:
            policy_name = policy.name
            greylist_remaining = policy.greylist_remaining
            greylist_expire = policy.greylist_expire
            greylist_key = policy.greylist_key
    
        key = utils.build_key(protocol, greylist_key=greylist_key)
        doc = self.search_greylist(key)
        
        if doc:
            delta = doc.expire(delta=greylist_remaining)
            if delta > 0:
                msg = "action=greylist, reason=retry, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s" % protocol
                msg = "policy=%s %s" % (msg, policy_name)
                logger.info(msg)
                doc.reject()
                return ["450 4.2.0 Greylisted for %s seconds. policy[%s]" % (delta, policy_name)]
            else:
                msg = "action=pass, reason=delay, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s" % protocol
                msg = "policy=%s %s" % (msg, policy_name)
                logger.info(msg)
                doc.accept(expire=greylist_expire)
                return ["DUNNO policy[%s]" % policy_name]
    
        else:
            doc = self.create_greylist(key=key, protocol=protocol, policy=policy_name)
            msg = "action=greylist, reason=new, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s" % protocol
            msg = "policy=%s %s" % (msg, policy_name)
            logger.info(msg)
            return ["450 4.2.0 Greylisted for %s seconds. policy[%s]" % (doc.expire(delta=greylist_remaining), policy_name)]
                          

    def search_policy(self, protocol):
        raise NotImplementedError()
    
    def search_whitelist(self, protocol):
        raise NotImplementedError()

    def search_blacklist(self, protocol):
        raise NotImplementedError()
    
    def search_greylist(self, key):
        raise NotImplementedError()
    
    def create_greylist(self, key=None, protocol=None, policy=None):
        raise NotImplementedError()

    def task_purge_expire(self, run_once=False):
        raise NotImplementedError()

    def task_metrics(self):
        raise NotImplementedError()
        