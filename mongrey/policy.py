# -*- coding: utf-8 -*-

import logging
import time
import regex
import IPy

from . import cache
from . import utils
from . import constants

logger = logging.getLogger(__name__)

def search_mynetwork(client_address=None, objects=None):

    for obj in objects:
        try:
            ip = IPy.IP(obj.value)
            
            if ip.len() == 1:
                if client_address == obj.value:
                    return True
                
            elif client_address in ip:
                #---Include in network
                return True
    
        except Exception, err:
            logger.warning(str(err))
    
    return False

def generic_search(protocol=None, objects=None, valid_fields=None, 
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
                        
                    elif client_address in ip:
                        #---Include network
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
                 blacklist_enable=True,
                 domain_vrfy=False,
                 mynetwork_vrfy=False,
                 spoofing_enable=False,
                 greylist_enable=True,
                 greylist_key=constants.GREY_KEY_MED, 
                 greylist_remaining=20,        # 20 seconds
                 greylist_expire=35*86400,     # 35 days
                 greylist_private_bypass=True,
                 greylist_excludes=None,
                 purge_interval=60,
                 metrics_interval=60*5):
        """
            Constructor

            :param greylist_key:
                Numeric value (@see constants.GREY_KEY_MED)
            :param greylist_remaining:
                Delay for attempt after the first greylist request
        """

        self.blacklist_enable = blacklist_enable
        self.greylist_enable = greylist_enable
        self.domain_vrfy = domain_vrfy
        self.mynetwork_vrfy = mynetwork_vrfy
        self.spoofing_enable = spoofing_enable
        
        self.greylist_key = greylist_key 
        self.greylist_remaining = greylist_remaining
        self.greylist_expire = greylist_expire
        self.greylist_private_bypass = greylist_private_bypass
        self.greylist_excludes = greylist_excludes
        self.purge_interval = purge_interval
        self.metrics_interval = metrics_interval

    def return_cache_action(self, uid=None, 
                      action=None, msg=None,
                      is_relay_denied=False,
                      is_whitelist=False,
                      is_blacklist=False,
                      is_outgoing=False,
                      is_spoofing=False, 
                      setcache=True):
        if cache.cache and setcache:
            #default timeout 300 seconds
            cache.cache.set(uid, dict(action=action,
                                      is_relay_denied=is_relay_denied,
                                      is_whitelist=is_whitelist,                                      
                                      is_blacklist=is_blacklist,
                                      is_outgoing=is_outgoing,
                                      is_spoofing=is_spoofing,
                                      msg=msg))
            
        logger.info(msg)
        return [action]

    def get_msg(self, action=None, reason=None, protocol=None, policy_name='default'):
        kwargs = {
            'action': action,
            'reason': reason,
            'policy_name': policy_name
        }
        kwargs.update(protocol)
        return "action=%(action)s, reason=%(reason)s, client_name=%(client_name)s, client_address=%(client_address)s, sender=%(sender)s, recipient=%(recipient)s policy=%(policy_name)s" % kwargs

    def check_actions(self, protocol):

        policy_name = "default"
        
        cache_action = None
        cache_msg = None
        cache_is_relay_denied = False
        cache_is_blacklist = False
        cache_is_whitelist = False
        cache_is_outgoing = False
        cache_is_spoofing = False
        
        uid = utils.get_uid(protocol)
        
        if cache.cache:
            cache_value = cache.cache.get(uid)
            if cache_value:
                cache_msg = cache_value['msg']
                cache_action = cache_value['action']
                cache_is_relay_denied = cache_value['is_relay_denied']
                cache_is_blacklist = cache_value['is_blacklist']
                cache_is_whitelist = cache_value['is_whitelist']
                cache_is_outgoing = cache_value['is_outgoing']
                cache_is_spoofing = cache_value['is_spoofing']

        #---Cache actions
        if cache_is_relay_denied or cache_is_outgoing or cache_is_spoofing or cache_is_blacklist or cache_is_whitelist:
            self.return_cache_action(action=cache_action, msg=cache_msg, setcache=False)
    
        if self.greylist_excludes and protocol['client_address'] in self.greylist_excludes:
            msg = self.get_msg(action="pass", reason="exclude", protocol=protocol, policy_name=policy_name)
            action = "DUNNO exclude filtering [%(client_address)s]" % protocol    
            return self.return_cache_action(uid=uid, action=action, msg=msg, setcache=False)
        
        if self.greylist_private_bypass and utils.is_private_address(protocol['client_address']):
            msg = self.get_msg(action="pass", reason="private", protocol=protocol, policy_name=policy_name)
            action = "DUNNO private address [%(client_address)s]" % protocol
            return self.return_cache_action(uid=uid, action=action, msg=msg, setcache=False)

    
        if not 'country' in protocol:
            protocol['country'] = utils.get_country(protocol['client_address'])
            
        #---Blacklist
        if self.blacklist_enable:
            bl = self.search_blacklist(protocol)
            if bl:
                msg = self.get_msg(action="reject", reason="blacklisted", protocol=protocol, policy_name=policy_name)
                action = "554 5.7.1 blacklisted [%s]" % bl
                return self.return_cache_action(uid=uid, action=action, msg=msg, is_blacklist=True)

        domain_found = None
        mynetwork_found = False
        is_outgoing = False
        
        mynetwork_vrfy = self.mynetwork_vrfy
        domain_vrfy = self.domain_vrfy
        spoofing_enable = self.spoofing_enable
        greylist_enable = self.greylist_enable
        greylist_remaining = self.greylist_remaining
        greylist_key = self.greylist_key
        greylist_expire = self.greylist_expire

        policy = self.search_policy(protocol)
        if policy:
            policy_name = policy.name
            mynetwork_vrfy = policy.mynetwork_vrfy
            domain_vrfy = policy.domain_vrfy
            spoofing_enable = policy.spoofing_enable
            greylist_enable = policy.greylist_enable
            greylist_remaining = policy.greylist_remaining
            greylist_expire = policy.greylist_expire
            greylist_key = policy.greylist_key

        if mynetwork_vrfy:
            mynetwork_found = self.search_mynetwork(protocol)
            if mynetwork_found:
                is_outgoing = True
        
        if not mynetwork_found and domain_vrfy:
            domain_found = self.search_domain(protocol)
            
        if domain_vrfy and mynetwork_vrfy and not mynetwork_found and domain_found == constants.DOMAIN_NOT_FOUND:
            msg = self.get_msg(action="reject", reason="relay-denied", protocol=protocol, policy_name=policy_name)
            action = "554 5.7.1 relay denied"
            return self.return_cache_action(uid=uid, action=action, msg=msg, is_relay_denied=True)            

        if is_outgoing:
            msg = self.get_msg(action="pass", reason="outgoing", protocol=protocol, policy_name=policy_name)
            action = "DUNNO outgoing bypass"
            return self.return_cache_action(uid=uid, action=action, msg=msg, is_outgoing=True)            

        #---Spoofing - not is_outgoing and sender is internal domain
        #TODO: spoofing helo
        if domain_vrfy and mynetwork_vrfy and spoofing_enable and not is_outgoing and domain_found == constants.DOMAIN_SENDER_FOUND:
            msg = self.get_msg(action="reject", reason="spoofing", protocol=protocol, policy_name=policy_name)
            action = "554 5.7.1 spoofing [%s]" % protocol['sender']
            return self.return_cache_action(uid=uid, action=action, msg=msg, is_spoofing=True)

        #---Whitelist
        wl = self.search_whitelist(protocol)
        if wl:
            msg = self.get_msg(action="pass", reason="whitelisted", protocol=protocol, policy_name=policy_name)
            action = "DUNNO whitelisted [%s]" % wl
            return self.return_cache_action(uid=uid, action=action, msg=msg, is_whitelist=True)

        #TODO: spf, rbl, ... ?
        #TODO: DDOS
        
        if not greylist_enable:
            msg = self.get_msg(action="pass", reason="disable-greylisting", protocol=protocol, policy_name=policy_name)
            logger.info(msg)
            return ["DUNNO"]
    
        key = utils.build_key(protocol, greylist_key=greylist_key)
        doc = self.search_greylist(key)
        
        if doc:
            delta = doc.expire(delta=greylist_remaining)
            if delta > 0:
                msg = self.get_msg(action="greylist", reason="retry", protocol=protocol, policy_name=policy_name)
                logger.info(msg)
                doc.reject()
                return ["450 4.2.0 Greylisted for %s seconds. policy[%s]" % (delta, policy_name)]
            else:
                msg = self.get_msg(action="pass", reason="delay", protocol=protocol, policy_name=policy_name)
                logger.info(msg)
                doc.accept(expire=greylist_expire)
                return ["DUNNO policy[%s]" % policy_name]
    
        else:
            doc = self.create_greylist(key=key, protocol=protocol, policy=policy_name)
            msg = self.get_msg(action="greylist", reason="new", protocol=protocol, policy_name=policy_name)
            logger.info(msg)
            return ["450 4.2.0 Greylisted for %s seconds. policy[%s]" % (doc.expire(delta=greylist_remaining), policy_name)]
                          
                          
    def search_domain(self, protocol):
        raise NotImplementedError()

    def search_mynetwork(self, protocol):
        raise NotImplementedError()

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
        