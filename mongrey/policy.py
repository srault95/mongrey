# -*- coding: utf-8 -*-

import logging
import time
import regex
import IPy

from . import cache
from . import utils
from . import constants
from .helpers.check_dnsl import check_dns_wb_lists

logger = logging.getLogger(__name__)

def search_mynetwork(client_address=None, objects=None):

    for obj in objects:
        try:
            ip = IPy.IP(obj.value)
            
            if client_address in ip:
                return True
    
        except Exception, err:
            logger.warning(str(err))
    
    return False

#TODO: test case
def generic_search(protocol=None, objects=None, valid_fields=None, 
                   cache_key=None, cache_enable=True, 
                   return_instance=False):

    start = time.time()

    values = []
    for field in valid_fields:
        value = protocol.get(field, None)
        if value and not value in ['unknow', '<>', '']:
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
                cache.cache.set(cache_key, return_value)

        logger.debug("search time[%.3f]" % (time.time() - start))

    return return_value


class PolicySession(object):
    
    def __init__(self, 
                 protocol,
                 policy_name='default',
                 domain_vrfy=False,
                 mynetwork_vrfy=False,
                 spoofing_enable=False,
                 rbl_enable=False,
                 rbl_hosts=None,
                 rwl_enable=False,
                 rwl_hosts=None,                 
                 rwbl_timeout=30,
                 rwbl_cache_timeout=3600,
                 spf_enable=False,
                 greylist_enable=True,
                 greylist_key=constants.GREY_KEY_MED, 
                 greylist_remaining=20,
                 greylist_expire=35*86400):

        self.protocol = protocol
        self.policy_name = policy_name
        
        self.greylist_enable = greylist_enable
        self.domain_vrfy = domain_vrfy
        self.mynetwork_vrfy = mynetwork_vrfy
        self.spoofing_enable = spoofing_enable
        
        self.rbl_enable = rbl_enable
        self.rbl_hosts = rbl_hosts
        self.rwl_enable = rwl_enable
        self.rwl_hosts = rwl_hosts
        self.rwbl_timeout = rwbl_timeout
        self.rwbl_cache_timeout = rwbl_cache_timeout
        
        self.spf_enable = spf_enable
        
        self.greylist_key = greylist_key 
        self.greylist_remaining = greylist_remaining
        self.greylist_expire = greylist_expire
        
        self.uid = utils.get_uid(self.protocol)
        
        self.is_domain_found = None
        self.is_mynetwork_found = False
        self.is_outgoing = False
        
        
    def get_field(self, name, default=None):
        return self.protocol.get(name, default)
    
    def is_spoofing_sender(self):
        return self.domain_vrfy and self.mynetwork_vrfy and \
            self.spoofing_enable and not self.is_outgoing and \
            self.is_domain_found == constants.SENDER_FOUND
            
    def is_denied_relay(self):
        return self.domain_vrfy and self.mynetwork_vrfy and \
            not self.is_mynetwork_found and \
            self.is_domain_found == constants.NOT_FOUND
            
    def is_enable_rbl(self):
        return self.mynetwork_vrfy and self.rbl_enable and self.rbl_hosts        

class Policy(object):
    
    def __init__(self, 
                 blacklist_enable=True,
                 domain_vrfy=False,
                 mynetwork_vrfy=False,
                 spoofing_enable=False,
                 rbl_enable=False,
                 rbl_hosts=None,
                 rwl_enable=False,
                 rwl_hosts=None,
                 rwbl_timeout=30,
                 rwbl_cache_timeout=3600,
                 spf_enable=False,
                 greylist_enable=True,
                 greylist_key=constants.GREY_KEY_MED, 
                 greylist_remaining=20,        # 20 seconds
                 greylist_expire=35*86400,     # 35 days
                 private_bypass=True,
                 outgoing_bypass=True,
                 ip_excludes=None,
                 purge_interval=60,
                 metrics_interval=60*5):

        self.blacklist_enable = blacklist_enable
        self.greylist_enable = greylist_enable
        self.domain_vrfy = domain_vrfy
        self.mynetwork_vrfy = mynetwork_vrfy
        self.spoofing_enable = spoofing_enable
        
        self.rbl_enable = rbl_enable
        self.rbl_hosts = rbl_hosts
        self.rwl_enable = rwl_enable
        self.rwl_hosts = rwl_hosts
        self.rwbl_timeout = rwbl_timeout
        self.rwbl_cache_timeout = rwbl_cache_timeout
        
        self.spf_enable = spf_enable
        
        self.greylist_key = greylist_key 
        self.greylist_remaining = greylist_remaining
        self.greylist_expire = greylist_expire
        self.private_bypass = private_bypass
        self.outgoing_bypass = outgoing_bypass
        self.ip_excludes = ip_excludes
        self.purge_interval = purge_interval
        self.metrics_interval = metrics_interval

    def debug(self, msg):
        if logger.isEnabledFor(logging.DEBUG):
           logger.debug(msg)

    def cached_action(self, 
                      uid=None, 
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

    def get_cache(self, uid):

        if cache.cache:
            cache_value = cache.cache.get(uid)
            if cache_value:
                cache_msg = cache_value['msg']
                cache_action = cache_value['action']
                for c in ['is_relay_denied', 'is_blacklist', 'is_whitelist',
                          'is_outgoing', 'is_spoofing', 'is_rbl']:
                    if cache_value.get(c, False) is True:
                        return cache_action, cache_msg

        return None, None

    def whitelisted(self, protocol=None, uid=None, policy_name='default'):
        '''
        Check if white listed

        :param protocol: Complete protocol from policy request
        :type protocol: dict
        :param uid: hash id from protocol fields
        :type uid: str
        :param policy_name: Policy name
        :type policy_name: str
        :return: Policy actions or None if not found
        :rtype: list or None
        '''        
        
        wl = self.search_whitelist(protocol)
        if wl:
            msg = self.get_msg(action="pass", reason="whitelisted", protocol=protocol, policy_name=policy_name)
            action = "DUNNO whitelisted [%s]" % wl
            return self.cached_action(uid=uid, action=action, msg=msg, is_whitelist=True)
    
    def blacklisted(self, protocol=None, uid=None, policy_name='default'):
        '''
        Check if black listed

        :param protocol: Complete protocol from policy request
        :type protocol: dict
        :param uid: hash id from protocol fields
        :type uid: str
        :param policy_name: Policy name
        :type policy_name: str
        :return: Policy actions or None if not found
        :rtype: list or None
        '''        

        bl = self.search_blacklist(protocol)
        if bl:
            msg = self.get_msg(action="reject", reason="blacklisted", protocol=protocol, policy_name=policy_name)
            action = "554 5.7.1 blacklisted [%s] - %s#554" % (bl, constants.ERRORS_URL_BASE)
            return self.cached_action(uid=uid, action=action, msg=msg, is_blacklist=True)

    def identify(self, session=None):
        if session.mynetwork_vrfy:
            session.is_mynetwork_found = self.search_mynetwork(session.protocol)
            if session.is_mynetwork_found:
                session.is_outgoing = True
        
        if not session.is_mynetwork_found and session.domain_vrfy:
            session.is_domain_found = self.search_domain(session.protocol)        

    def get_private_bypass(self, session=None, private_bypass=False):

        if private_bypass and utils.is_private_address(session.protocol['client_address']):
            msg = self.get_msg(action="pass", reason="private", 
                               protocol=session.protocol, policy_name=session.policy_name)
            action = "DUNNO private address [%(client_address)s]" % session.protocol
            return self.cached_action(uid=session.uid, action=action, msg=msg, setcache=False)

    def get_ip_excludes(self, session=None, ip_excludes=None):
        
        if ip_excludes:

            client_address = session.protocol['client_address']
            
            for exclude in ip_excludes:
                
                ip = IPy.IP(exclude)
                
                if client_address in ip:
                    msg = self.get_msg(action="pass", reason="exclude", 
                                       protocol=session.protocol, policy_name=session.policy_name)
                    action = "DUNNO exclude filtering [%(client_address)s]" % session.protocol    
                    return self.cached_action(uid=session.uid, action=action, msg=msg, setcache=False)
    
    def get_rbl(self, session=None):
        
        rbl_host, rbl_result = check_dns_wb_lists(session.protocol['client_address'], 
                                               rbls=session.rbl_hosts, 
                                               timeout=session.rwbl_timeout, 
                                               cache_timeout=session.rwbl_cache_timeout)
        if rbl_result:
            msg = self.get_msg(action="reject", reason="rbl-%s" % rbl_host, 
                               protocol=session.protocol, policy_name=session.policy_name)
            action = "554 5.7.1 relay denied - %s#554" % constants.ERRORS_URL_BASE
            return self.cached_action(uid=session.uid, action=action, msg=msg, is_relay_denied=True)            
        
            
    def get_greylisted(self, 
                       protocol=None, 
                       greylist_key=None, greylist_remaining=None, greylist_expire=None, 
                       policy_name='default'):

        key = utils.build_key(protocol, greylist_key=greylist_key)
        doc = self.search_greylist(key)
        
        if doc:
            delta = doc.expire(delta=greylist_remaining)
            if delta > 0:
                msg = self.get_msg(action="greylist", reason="retry", protocol=protocol, policy_name=policy_name)
                logger.info(msg)
                doc.reject()
                return ["450 4.2.0 Greylisted for %s seconds. policy[%s] - %s#greylisted" % (delta, policy_name, constants.ERRORS_URL_BASE)]
            else:
                msg = self.get_msg(action="pass", reason="delay", protocol=protocol, policy_name=policy_name)
                logger.info(msg)
                doc.accept(expire=greylist_expire)
                return ["DUNNO policy[%s]" % policy_name]
    
        else:
            doc = self.create_greylist(key=key, protocol=protocol, policy=policy_name)
            msg = self.get_msg(action="greylist", reason="new", protocol=protocol, policy_name=policy_name)
            logger.info(msg)
            return ["450 4.2.0 Greylisted for %s seconds. policy[%s] - %s#greylisted" % (doc.expire(delta=greylist_remaining), policy_name, constants.ERRORS_URL_BASE)]
        
    def check_actions_one_request(self, request):        
        '''
        Check policy from command line

        :param request: Partial protocol request. ex: 'client_name=unknow client_address=1.1.1.1'
        :type request: str
        :return: Policy actions
        :rtype: list
        '''        
        fields = dict(constants.ALL_FIELDS).keys()
        
        protocol = dict([a.strip(',').split('=') for a in request.split()])
        
        for key in fields:
            if not key in protocol:
                protocol[key] = None 
        
        return self.check_actions(protocol, one_request=True)

    def update_settings(self, policy=None, session=None):
        session.policy_name = policy.name
        session.mynetwork_vrfy = policy.mynetwork_vrfy
        session.domain_vrfy = policy.domain_vrfy
        session.rbl_enable = policy.rbl_enable
        session.rbl_hosts = policy.get_rbl_hosts()
        session.rwl_enable = policy.rwl_enable
        session.rwl_hosts = policy.get_rwl_hosts()
        session.rwbl_timeout = policy.rwbl_timeout
        session.rwbl_cache_timeout = policy.rwbl_cache_timeout
        session.spf_enable = policy.spf_enable
        session.spoofing_enable = policy.spoofing_enable
        session.greylist_enable = policy.greylist_enable
        session.greylist_remaining = policy.greylist_remaining
        session.greylist_expire = policy.greylist_expire
        session.greylist_key = policy.greylist_key

    def check_actions(self, protocol, one_request=False):
        
        '''
        TODO: Séparer chaque check et utiliser Exception spécifique pour arrêter la procédure et renvoyer l'action
        
        TODO: Gérer un score pour certains actions et déterminer si score > Max: rejet 4xx ou rejet5xx
            - Policy pour décider action
        
        TODO: message rbl:  $rbl_code Service unavailable; $rbl_class [$rbl_what] blocked using $rbl_domain${rbl_reason?; $rbl_reason}
        - il faut dict pour utiliser %(field)s dans le template
        - ex postfix: May 13 08:15:15 ns339295 postfix/smtpd[16495]: NOQUEUE: reject: RCPT from ip-79-111-119-78.bb.netbynet.ru[79.111.119.78]: 554 5.7.1 Service unavailable; Client host [79.111.119.78] blocked using zen.spamhaus.org; http://www.spamhaus.org/sbl/query/SBLCSS / http://www.spamhaus.org/query/bl?ip=79.111.119.78; from=<5C4B728D-D2EB-4290-ACC9-73DBAC6BB00C@ghkaaakaahkgjbfg.notifycenter63.net> to=<rcpt@example.org> proto=SMTP helo=<ghkaaakaahkgjbfg.notifycenter63.net>
        '''

        policy_name = "default"
        
        session = PolicySession(protocol,
                                policy_name=policy_name,
                                domain_vrfy=self.domain_vrfy, 
                                mynetwork_vrfy=self.mynetwork_vrfy, 
                                spoofing_enable=self.spoofing_enable, 
                                rbl_enable=self.rbl_enable, 
                                rbl_hosts=self.rbl_hosts, 
                                rwl_enable=self.rwl_enable, 
                                rwl_hosts=self.rwl_hosts, 
                                rwbl_timeout=self.rwbl_timeout, 
                                rwbl_cache_timeout=self.rwbl_cache_timeout, 
                                spf_enable=self.spf_enable, 
                                greylist_enable=self.greylist_enable, 
                                greylist_key=self.greylist_key, 
                                greylist_remaining=self.greylist_remaining, 
                                greylist_expire=self.greylist_expire)
        
        uid = utils.get_uid(session.protocol)

        #---bypass filtering - private address
        private_bypass = self.get_private_bypass(session=session, private_bypass=self.private_bypass)
        if private_bypass:
            return private_bypass

        #---bypass filtering - ip or cidr        
        exclude = self.get_ip_excludes(session=session, ip_excludes=self.ip_excludes)
        if exclude:
            return exclude
        
        #---Cache actions
        if cache.cache:
            cache_action, cache_msg = self.get_cache(uid)
            if cache_action:
                self.cached_action(action=cache_action, msg=cache_msg, setcache=False)
    
        #---Add datas
        if not 'country' in session.protocol:
            session.protocol['country'] = utils.get_country(session.get_field('client_address'))
            
        #---Plugin Blacklist
        blacklisted = self.blacklisted(protocol=session.protocol, uid=session.uid)
        if blacklisted:
            return blacklisted
        
        #TODO: renvoyer une policy par défaut
        policy = self.search_policy(protocol)
        if policy:
            self.update_settings(policy=policy, session=session)

        #---Identify mynetwork / domain
        self.identify(session)
            
        if session.is_denied_relay():
            msg = self.get_msg(action="reject", reason="relay-denied", protocol=session.protocol, policy_name=session.policy_name)
            action = "554 5.7.1 relay denied - %s#554" % constants.ERRORS_URL_BASE
            return self.cached_action(uid=session.uid, action=action, msg=msg, is_relay_denied=True)            

        #TODO: add unique id in header si queue_id: car dernier recipient
        if self.outgoing_bypass and session.is_outgoing:
            msg = self.get_msg(action="pass", reason="outgoing", protocol=session.protocol, policy_name=session.policy_name)
            action = "DUNNO outgoing bypass"
            return self.cached_action(uid=session.uid, action=action, msg=msg, is_outgoing=True)            

        #---Plugin whitelist
        whitelisted = self.whitelisted(protocol=session.protocol, uid=session.uid, policy_name=session.policy_name)
        if whitelisted:
            return whitelisted

        #---Spoofing - not is_outgoing and sender is internal domain
        #TODO: spoofing helo
        #---Plugin spoofing sender
        if session.is_spoofing_sender():
            msg = self.get_msg(action="reject", reason="spoofing", 
                               protocol=session.protocol, policy_name=session.policy_name)
            action = "554 5.7.1 spoofing [%s] - %s#554" % (session.protocol['sender'], constants.ERRORS_URL_BASE)
            return self.cached_action(uid=session.uid, action=action, msg=msg, is_spoofing=True)

        #---Plugin rbl
        if session.is_enable_rbl():
            rbl = self.get_rbl(session)
            if rbl:
                return rbl

        #TODO: spf, ... ?
        #TODO: DDOS
        #TODO: rwl
        #TODO: plugins ?
        
        if not session.greylist_enable:
            msg = self.get_msg(action="pass", reason="disable-greylisting", 
                               protocol=session.protocol, policy_name=session.policy_name)
            logger.info(msg)
            return ["DUNNO"]

        #---Plugin greylist
        return self.get_greylisted(protocol=session.protocol, 
                                   greylist_key=session.greylist_key, 
                                   greylist_remaining=session.greylist_remaining, 
                                   greylist_expire=session.greylist_expire, 
                                   policy_name=session.policy_name)
                          
                          
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
        