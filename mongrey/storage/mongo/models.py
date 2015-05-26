# -*- coding: utf-8 -*-

import logging
import datetime

import arrow

from mongoengine import Document as BaseDocument
from mongoengine import Q, fields
from mongoengine import ValidationError, NotUniqueError

from ...ext.slugify import UniqueSlugify

from ... import utils
from ... import validators
from ... import constants
from ...policy import generic_search, search_mynetwork
from ..base import UserMixin

logger = logging.getLogger(__name__)

class ModelSlug(object):
    
    def __init__(self, model, slug_field='slug'):
        self.model = model
        self.slug_field = slug_field
        
    def __call__(self, text, uids):
        if text in uids:
            return False
        kwargs = {self.slug_field: text}
        return not self.model.objects(**kwargs).first()
    
    @classmethod
    def unique_slug(cls, model, slug_field='slug'):
        return UniqueSlugify(unique_check=ModelSlug(model, slug_field='slug'))

class Document(BaseDocument):

    @classmethod
    def api_find(cls, **kwargs):
        return cls.objects(**kwargs)

    @classmethod
    def api_find_one(cls, **kwargs):
        return cls.api_find(**kwargs).first()

    @classmethod
    def api_create(cls, **kwargs):
        return cls(**kwargs).save()

    @classmethod
    def api_update(cls, doc=None, **kwargs):
        return doc.update(**kwargs)
        #return doc

    @classmethod
    def api_delete(cls, doc=None):
        return doc.delete()

    meta = {
        'abstract': True,
    }

class User(UserMixin, Document):

    username = fields.StringField(unique=True, required=True)
    
    email = fields.EmailField(required=False)
    
    password = fields.StringField(required=True)
    
    api_key = fields.StringField()
    
    active = fields.BooleanField(default=True)

    slug = fields.StringField(unique=True, required=True)

    def _clean_api_key(self):
        if self.api_key:
            exist = User.objects(api_key=self.api_key, username__ne=self.username).first()
            if exist:
                message = _(u"Conflict with api_key[%s]. Already exist") % value
                raise NotUniqueError(message)        
    
    @classmethod    
    def create_user(cls, 
                    username=None, password=None,
                    api_key=None, 
                    update_if_exist=False):
        user = cls.objects(username__exact=username).first()

        if user:
            if not update_if_exist:
                return user

        user = user or cls(username=username)
        user.set_password(password)
        user.api_key = api_key
        return user.save()
    
    def clean(self):
        Document.clean(self)
        validators.clean_email_or_username(self.username, field_name="username", error_class=ValidationError)
        if self.api_key:
            self._clean_api_key()
    
    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(User)(self.username)        
        return Document.save(self, **kwargs)

    def __unicode__(self):
        return self.username

    meta = {
        'collection': 'user',
        'ordering': ['username'],        
        'indexes': ['username', 'slug'],
    }

class Domain(Document):
    
    name = fields.StringField(unique=True, required=True)

    slug = fields.StringField(unique=True, required=True)
    
    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(Domain)(self.name)        
        return Document.save(self, **kwargs)

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
                return constants.SENDER_FOUND 

        if recipient_domain:
            if cls.objects(name__iexact=recipient_domain).first():
                return constants.RECIPIENT_FOUND 
        
        return constants.NOT_FOUND
        
    meta = {
        'collection': 'domain',
        'ordering': ['name'],        
        'indexes': ['name', 'slug'],
    }

class Mailbox(Document):
    
    name = fields.StringField(unique=True, required=True)

    slug = fields.StringField(unique=True, required=True)
    
    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(Mailbox)(self.name)        
        return Document.save(self, **kwargs)

    def clean(self):
        Document.clean(self)
        validators.clean_email(self.name, field_name="name", error_class=ValidationError)

    @classmethod
    def search(cls, protocol):
        
        sender = protocol.get('sender', None)
        recipient = protocol.get('recipient')

        if sender and sender != '<>':
            if cls.objects(name__iexact=sender.lower()).first():
                return constants.SENDER_FOUND 

        if recipient:
            if cls.objects(name__iexact=recipient.lower()).first():
                return constants.RECIPIENT_FOUND 
        
        return constants.NOT_FOUND

    def __unicode__(self):
        return self.name
    
    meta = {
        'collection': 'mailbox',
        'ordering': ['name'],        
        'indexes': ['name', 'slug'],
    }

class Mynetwork(Document):
    
    value = fields.StringField(unique=True, required=True)

    slug = fields.StringField(unique=True, required=True)
    
    comments = fields.StringField(max_length=255)

    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(Mynetwork)(self.value)        
        return Document.save(self, **kwargs)

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
        'indexes': ['value', 'slug'],
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
                              cache_key=cls._cache_key, 
                              cache_enable=cache_enable, 
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

        #TODO: .*@        

    def clean(self):
        Document.clean(self)
        self._clean()

    meta = {
        'abstract': True,
    }

class Policy(BaseSearchField):
    
    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'cachepolicy'
    
    name = fields.StringField(unique=True, required=True, max_length=255)

    slug = fields.StringField(unique=True, required=True)
    
    field_name = fields.StringField(required=True, choices=constants.POLICY_FIELDS, default='client_address')
    
    mynetwork_vrfy = fields.BooleanField(default=True)

    domain_vrfy = fields.BooleanField(default=True)

    spoofing_enable = fields.BooleanField(default=True)
    
    rbl_enable = fields.BooleanField(default=False)
    
    rbl_hosts = fields.SortedListField(fields.StringField(), default=[])
    
    rwl_enable = fields.BooleanField(default=False)

    rwl_hosts = fields.SortedListField(fields.StringField(), default=[])

    rwbl_timeout = fields.IntField(default=30, min_value=5)

    rwbl_cache_timeout = fields.IntField(default=3600, min_value=30)
    
    spf_enable = fields.BooleanField(default=False)

    greylist_enable = fields.BooleanField(default=True)
    
    greylist_key = fields.StringField(required=True, 
                                      choices=constants.GREY_KEY, 
                                      default=constants.GREY_KEY_MED)
    
    greylist_remaining = fields.IntField(default=10, min_value=1)

    greylist_expire = fields.IntField(default=35*86400, min_value=1)
    
    comments = fields.StringField(max_length=255)

    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(Policy)(self.name)
        return Document.save(self, **kwargs)

    def get_rbl_hosts(self):
        return self.rbl_hosts

    def get_rwl_hosts(self):
        return self.rwl_hosts

    @classmethod
    def search(cls, protocol, cache_enable=True, return_instance=True): # noqa
        return super(Policy, cls).search(protocol, cache_enable=cache_enable, return_instance=return_instance)

    def __unicode__(self):
        return u"%s - %s (%s)" % (self.name, self.value, self.get_field_name_display())    

    meta = {
        'collection': 'policy',
        'ordering': ['name'],        
        'indexes': ['name', 'value', 'field_name', 'slug'],
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

    policy = fields.StringField(max_length=255)

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
        count = objects.count()
        if count == 0:
            return

        last_1_hour = arrow.utcnow().replace(hours=-1).datetime
        
        metrics = {
            'count': count,
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
    
    comments = fields.StringField(max_length=255)

    slug = fields.StringField(unique=True, required=True)
    
    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(WhiteList)(self.value)        
        return Document.save(self, **kwargs)

    def __unicode__(self):
        return u"%s (%s)" % (self.value, self.get_field_name_display())

    meta = {
        'collection': 'whitelist',
        'indexes': ['value', 'field_name', 'slug'],
    }
    
class BlackList(BaseSearchField):

    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'blist'

    field_name = fields.StringField(required=True, choices=constants.BL_FIELDS, default='client_address')
    
    slug = fields.StringField(unique=True, required=True)
    
    comments = fields.StringField(max_length=255)
    
    def save(self, **kwargs):
        self.slug = ModelSlug.unique_slug(BlackList)(self.value)        
        return Document.save(self, **kwargs)

    def __unicode__(self):
        return u"%s (%s)" % (self.value, self.get_field_name_display())

    meta = {
        'collection': 'blacklist',
        'indexes': ['value', 'field_name', 'slug'],
    }

        
def query_for_purge():
    
    query = (Q(expire_time__ne=None) & Q(expire_time__lt=utils.utcnow()))

    # now:  10/10/2015 10h00
    # last: 09/10/2015 10h00    
    last_24_hours = arrow.utcnow().replace(hours=-24).datetime
    query |= (Q(expire_time=None) & Q(timestamp__lte=last_24_hours))
    
    #pp(query.to_query(GreylistEntry))
    
    return GreylistEntry.objects(query)
        
def import_fixtures(fixtures):

    #TODO: supp id/_id field if exist ?

    entries = 0    
    success = 0
    warn_error = 0
    fatal_error = 0
    errors = []
    
    fixtures_klass = (
        ('domain', Domain),
        ('mailbox', Mailbox),
        ('mynetwork', Mynetwork),
        ('whitelist', WhiteList),
        ('blacklist', BlackList),
        ('policy', Policy),
    )
    
    for key, klass in fixtures_klass:
        values = fixtures.get(key, [])
        for value in values:
            entries += 1
            try:
                klass(**value).save()
                success +=1
            except NotUniqueError:
                warn_error += 1
            except Exception, err:
                logger.error(err)
                fatal_error += 1
                errors.append(str(err))

    return {
        'entries': entries,
        'success': success,
        'warn_error': warn_error,
        'fatal_error': fatal_error,
        'errors': errors
    }

def export_fixtures():

    fixtures_klass = (
        ('domain', Domain),
        ('mailbox', Mailbox),
        ('mynetwork', Mynetwork),
        ('whitelist', WhiteList),
        ('blacklist', BlackList),
        ('policy', Policy),
    )
    
    fixtures = {}
    
    for key, klass in fixtures_klass:
        fixtures[key] = []
        for d in klass.objects.as_pymongo():
            d.pop('_id', None)
            d.pop('slug', None)
            fixtures[key].append(d)
            
    #add comments fields beacause mongoengine not include empty field 
    for key, values in fixtures.iteritems():
        if key in ['whitelist', 'blacklist', 'policy', 'mynetwork']:
            for entry in values:
                if not 'comments' in entry:
                    entry['comments'] = None

    return fixtures
