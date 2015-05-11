# -*- coding: utf-8 -*-

import logging
import datetime

import arrow

from mongoengine import Document, Q, fields
from mongoengine import ValidationError

from ... import utils
from ... import validators
from ... import constants
from ...policy import generic_search, search_mynetwork

logger = logging.getLogger(__name__)

class Domain(Document):
    
    name = fields.StringField(unique=True, required=True)

    def clean(self):
        Document.clean(self)
        validators.clean_domain(self.name, field_name="name", error_class=ValidationError)

    def __unicode__(self):
        return self.name
    
    @classmethod
    def search(cls, protocol):
        
        sender = protocol.get('sender', None)
        sender_domain = utils.parse_domain(sender)
        recipient = protocol.get('recipient')
        recipient_domain = utils.parse_domain(recipient)

        if sender_domain:
            if cls.objects(name__iexact=sender_domain).first():
                return constants.DOMAIN_SENDER_FOUND 

        if recipient_domain:
            if cls.objects(name__iexact=recipient_domain).first():
                return constants.DOMAIN_RECIPIENT_FOUND 
        
        return constants.DOMAIN_NOT_FOUND
        
    meta = {
        'collection': 'domain',
        'ordering': ['name'],        
        'indexes': ['name'],
    }

class Mynetwork(Document):
    
    value = fields.StringField(unique=True, required=True)

    def clean(self):
        Document.clean(self)
        validators.clean_ip_address_or_network(self.value, field_name="value", error_class=ValidationError)

    @classmethod
    def search(cls, protocol):
        client_address = protocol['client_address']
        return search_mynetwork(client_address=client_address, 
                              objects=cls.objects)

    def __unicode__(self):
        return self.value    

    meta = {
        'collection': 'mynetwork',
        'ordering': ['value'],        
        'indexes': ['value'],
    }


class BaseSearchField(Document):

    _valid_fields = []
    _cache_key = None

    value = fields.StringField(unique=True, required=True, max_length=255)

    @classmethod
    def search(cls, protocol, cache_enable=True, return_instance=False):
        return generic_search(protocol=protocol, 
                              objects=cls.objects.order_by('field_name'), 
                              valid_fields=cls._valid_fields, 
                              cache_key=cls._cache_key, cache_enable=cache_enable, 
                              return_instance=return_instance)

    def _clean(self):

        #TODO: helo_name and country validators

        if self.field_name == "client_address":
            validators.clean_ip_address_or_network(self.value, field_name="value", error_class=ValidationError)

        elif self.field_name == "client_name" and not "*" in self.value:
            validators.clean_hostname(self.value, field_name="value", error_class=ValidationError)
        
        elif self.field_name in ["sender", "recipient"]:
            if not "*" in self.value:
                validators.clean_email_or_domain(self.value, field_name="value", error_class=ValidationError)
            pass

        """
        TODO: .*@        
        """

    def clean(self):
        Document.clean(self)
        self._clean()

    meta = {
        'abstract': True,
    }

class Policy(BaseSearchField):
    
    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'greypolicy'
    
    name = fields.StringField(unique=True, required=True, max_length=20)
    
    field_name = fields.StringField(required=True, choices=constants.POLICY_FIELDS, default='client_address')
    
    mynetwork_vrfy = fields.BooleanField(default=True)

    domain_vrfy = fields.BooleanField(default=True)

    spoofing_enable = fields.BooleanField(default=True)

    greylist_enable = fields.BooleanField(default=True)
    
    greylist_key = fields.IntField(required=True, choices=constants.GREY_KEY, default=constants.GREY_KEY_MED)
    
    greylist_remaining = fields.IntField(default=10, min_value=1)

    greylist_expire = fields.IntField(default=35*86400, min_value=1)
    
    comments = fields.StringField(max_length=100)

    @classmethod
    def search(cls, protocol, cache_enable=True):
        return super(Policy, cls).search(protocol, cache_enable=cache_enable, return_instance=True)

    def __unicode__(self):
        return u"%s - %s (%s)" % (self.name, self.value, self.get_field_name_display())    

    meta = {
        'collection': 'policy',
        'ordering': ['name'],        
        'indexes': ['name', 'value', 'field_name'],
    }


class GreylistEntry(Document):

    key = fields.StringField(required=True)

    timestamp = fields.DateTimeField(default=utils.utcnow)

    expire_time = fields.DateTimeField()

    rejects = fields.IntField(default=0)

    accepts = fields.IntField(default=0)

    last_state = fields.DateTimeField()

    delay = fields.FloatField(default=0.0)

    protocol = fields.DictField()

    policy = fields.StringField()

    def __unicode__(self):
        return self.key

    def accept(self, now=None, expire=35 * 86400):
        now = now or utils.utcnow()
        self.accepts += 1
        self.last_state = now

        if self.accepts == 1:
            value = now - self.timestamp 
            self.delay = round(value.total_seconds(), 2)

        if not self.expire_time:
            self.expire_time = now + datetime.timedelta(seconds=expire)

        self.save()

    def reject(self, now=None):
        now = now or utils.utcnow()
        self.rejects += 1
        self.last_state = now
        self.save()

    def expire(self, delta=60, now=None):
        now = now or utils.utcnow()
        expire_date = self.timestamp + datetime.timedelta(seconds=delta)
        value =  expire_date-now
        return round(value.total_seconds(), 2)

    @classmethod
    def create_entry(cls, key=None, protocol=None, policy=None, timestamp=None, last_state=None, now=None, **kwargs):
        now = now or utils.utcnow()
        return cls(key=key, 
                   rejects=1,
                   timestamp=timestamp or now,
                   last_state=last_state or now,
                   policy=policy,
                   protocol=protocol,
                   **kwargs).save()
    
    @classmethod
    def search_entry(cls, key=None, now=None):
        """
        expire_time is None or greater than or equal to now AND key == key
        """
        now = now or utils.utcnow()
        
        query = (
            (Q(expire_time=None) | Q(expire_time__gt=now)) & Q(key=key)
        )
        #pp(query.to_query(GreylistEntry))
        return cls.objects(query).first()
    
    @classmethod
    def last_metrics(cls):
        last_24_hours = arrow.utcnow().replace(hours=-24).datetime
        objects = cls.objects(timestamp__gte=last_24_hours)

        last_1_hour = arrow.utcnow().replace(hours=-1).datetime
        
        metrics = {
            'count': objects.count(),
            'accepted': int(objects.sum('accepts')),
            'rejected': int(objects.sum('rejects')),
            'delay': objects.filter(accepts__gt=0, delay__gt=0).average('delay'),
            'abandoned': objects.filter(accepts=0, timestamp__lte=last_1_hour).count(),
            #'count_accepts': objects.filter(accepts__gte=1).count(),
        }
        
        metrics['requests'] = metrics['accepted'] + metrics['rejected']
        
        return metrics
    

    meta = {            
        'collection': 'greylist_entry',
        'ordering': ['-timestamp'],        
        'indexes': ['key', '-timestamp'],
    }


class GreylistMetric(Document):

    timestamp = fields.DateTimeField(default=utils.utcnow)
    
    count = fields.IntField(default=0)

    accepted = fields.IntField(default=0)

    rejected = fields.IntField(default=0)

    requests = fields.IntField(default=0)

    abandoned = fields.IntField(default=0)

    delay = fields.FloatField(default=0.0)

    meta = {
        'collection': 'greylist_metric',
        'ordering': ['-timestamp'],
        'indexes': ['-timestamp']
    }


class WhiteList(BaseSearchField):

    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'wlist'

    field_name = fields.StringField(required=True, choices=constants.WL_FIELDS, default='client_address')
    
    comments = fields.StringField(max_length=100)

    def __unicode__(self):
        return u"%s (%s)" % (self.value, self.get_field_name_display())

    meta = {
        'collection': 'whitelist',
        'indexes': ['value', 'field_name'],
    }
    
class BlackList(BaseSearchField):

    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'blist'

    field_name = fields.StringField(required=True, choices=constants.BL_FIELDS, default='client_address')
    
    comments = fields.StringField(max_length=100)

    def __unicode__(self):
        return u"%s (%s)" % (self.value, self.get_field_name_display())

    meta = {
        'collection': 'blacklist',
        'indexes': ['value', 'field_name'],
    }

        
def query_for_purge():
    
    query = (Q(expire_time__ne=None) & Q(expire_time__lt=utils.utcnow()))

    # now:  10/10/2015 10h00
    # last: 09/10/2015 10h00    
    last_24_hours = arrow.utcnow().replace(hours=-24).datetime
    query |= (Q(expire_time=None) & Q(timestamp__lte=last_24_hours))
    
    #pp(query.to_query(GreylistEntry))
    
    return GreylistEntry.objects(query)
        

