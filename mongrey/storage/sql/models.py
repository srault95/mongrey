# -*- coding: utf-8 -*-

import logging
import datetime

import arrow

from peewee import (Proxy, 
                    Model,
                    CharField, 
                    DateTimeField, 
                    IntegerField, 
                    FloatField, 
                    TextField, 
                    BooleanField,
                    fn,
                    IntegrityError)

from playhouse.kv import KeyStore

try:
    from peewee import PostgresqlDatabase
    import psycopg2 # noqa
    HAVE_PSYCOPG2 = True
except ImportError:
    HAVE_PSYCOPG2 = False

try:
    from peewee import MySQLDatabase
    import MySQLdb as mysql   # noqa
    HAVE_MYSQL = True
except ImportError:
    try:
        import pymysql as mysql # noqa
    except ImportError:
        HAVE_MYSQL = False

from ...exceptions import ValidationError
from ... import utils
from ... import validators
from ... import constants
from ...policy import generic_search, search_mynetwork

database_proxy = Proxy()

logger = logging.getLogger(__name__)

class DateTimeFieldExtend(DateTimeField):

    def python_value(self, value):
        return arrow.get(value).datetime


class Domain(Model):
    
    name = CharField(unique=True, index=True)

    def _clean(self):
        validators.clean_domain(self.name, field_name="name", error_class=ValidationError)
    
    def save(self, force_insert=False, only=None, validate=True):
        if validate:
            self._clean()
        return Model.save(self, force_insert=force_insert, only=only)

    @classmethod
    def search(cls, protocol):
        
        sender = protocol.get('sender', None)
        sender_domain = utils.parse_domain(sender)
        recipient = protocol.get('recipient')
        recipient_domain = utils.parse_domain(recipient)

        if sender_domain:
            if cls.select().where(fn.Lower(cls.name)==sender_domain).first():
                return constants.DOMAIN_SENDER_FOUND 

        if recipient_domain:
            if cls.select().where(fn.Lower(cls.name)==recipient_domain).first():
                return constants.DOMAIN_RECIPIENT_FOUND 
        
        return constants.DOMAIN_NOT_FOUND


    def __unicode__(self):
        return self.name
    
    class Meta: # noqa
        database = database_proxy
        order_by = ('name',)
        
class Mynetwork(Model):
    
    value = CharField(unique=True, index=True)

    def _clean(self):
        validators.clean_ip_address_or_network(self.value, field_name="value", error_class=ValidationError)
    
    def save(self, force_insert=False, only=None, validate=True):
        if validate:
            self._clean()
        return Model.save(self, force_insert=force_insert, only=only)
    
    @classmethod
    def search(cls, protocol):
        client_address = protocol['client_address']
        return search_mynetwork(client_address, 
                              objects=cls.select())

    def __unicode__(self):
        return self.value    

    class Meta: # noqa
        database = database_proxy
        order_by = ('value',)


class BaseSearchField(Model):
    
    _valid_fields = []
    _cache_key = None

    value = CharField(unique=True, max_length=255, index=True)

    @classmethod
    def search(cls, protocol, cache_enable=True, return_instance=False):

        return generic_search(protocol=protocol, 
                              objects=cls.select().order_by('field_name'), 
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
            pass
        
    def save(self, force_insert=False, only=None, validate=True):
        if validate:
            self._clean()
        return Model.save(self, force_insert=force_insert, only=only)

    class Meta: # noqa
        database = database_proxy

class Policy(BaseSearchField):

    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'greypolicy'
    
    name = CharField(unique=True, max_length=20)
    
    field_name = CharField(choices=constants.POLICY_FIELDS, default='client_address')
    
    mynetwork_vrfy = BooleanField(default=True)

    domain_vrfy = BooleanField(default=True)

    spoofing_enable = BooleanField(default=True)

    greylist_enable = BooleanField(default=True)
    
    greylist_key = CharField(choices=constants.GREY_KEY, 
                             default=constants.GREY_KEY_MED)
    
    greylist_remaining = IntegerField(default=10)#, min_value=1)

    greylist_expire = IntegerField(default=35*86400)#s, min_value=1)
    
    comments = CharField(max_length=100, null=True)
    
    @classmethod
    def search(cls, protocol, cache_enable=True, return_instance=True): # noqa
        return super(Policy, cls).search(protocol, cache_enable=cache_enable, return_instance=return_instance)

    class Meta: # noqa
        order_by = ('name',)

    def __unicode__(self):
        return self.name    

class GreylistEntry(Model):
    
    key = CharField(index=True)
    
    timestamp = DateTimeFieldExtend(default=utils.utcnow)
    
    expire_time = DateTimeFieldExtend(null=True)
    
    rejects = IntegerField(default=0)
    
    accepts = IntegerField(default=0)
    
    last_state = DateTimeFieldExtend(null=True)
    
    delay = FloatField(default=0.0)
    
    protocol = KeyStore(TextField())
    
    policy = CharField(max_length=20, default='policy')

    def accept(self, now=None, expire=35*86400):
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
        value = expire_date - now 
        return round(value.total_seconds(), 2)

    @classmethod
    def create_entry(cls, key=None, protocol=None, policy='default', timestamp=None, last_state=None, now=None, **kwargs):        
        now = now or utils.utcnow()

        with database_proxy.transaction():
            return cls.create(key=key, 
                              rejects=1,
                              timestamp=timestamp or now,
                              last_state=last_state or now,
                              policy=policy,
                              protocol=protocol,
                              **kwargs)

    @classmethod
    def search_entry(cls, key=None, now=None):
        """
        expire_time is None or greater than or equal to now AND key == key
        """
        now = now or utils.utcnow()
        
        try:
            return cls.select().where(
                    ((cls.expire_time==None) | (cls.expire_time>now)) & (cls.key==key)).get()
        except:
            pass
        
    @classmethod
    def last_metrics(cls):
        last_24_hours = arrow.utcnow().replace(hours=-24).datetime
        
        objects = cls.select().where(cls.timestamp >= last_24_hours)

        last_1_hour = arrow.utcnow().replace(hours=-1).datetime
        
        metrics = {
            'count': objects.count(),
            'accepted': cls.select(fn.Sum(cls.accepts)).where(cls.timestamp >= last_24_hours),
            'rejected': cls.select(fn.Sum(cls.rejects)).where(cls.timestamp >= last_24_hours),
            'delay': cls.select(fn.Avg(cls.delay)).where(cls.timestamp >= last_24_hours, cls.accepts>=0, cls.delay>=0),
            'abandoned': objects.filter(cls.accepts==0, cls.timestamp<=last_1_hour).count(),
            #'count_accepts': objects.filter(accepts__gte=1).count(),
        }
        
        metrics['requests'] = metrics['accepted'] + metrics['rejected']
        
        return metrics
    
    def __unicode__(self):
        return self.key

    class Meta: # noqa
        database = database_proxy
        order_by = ('-timestamp',)

class GreylistMetric(Model):

    timestamp = DateTimeFieldExtend(default=utils.utcnow)
    
    count = IntegerField(default=0)

    accepted = IntegerField(default=0)

    rejected = IntegerField(default=0)

    requests = IntegerField(default=0)

    abandoned = IntegerField(default=0)

    delay = FloatField(default=0.0)

    class Meta: # noqa
        database = database_proxy
        order_by = ('-timestamp',)


class WhiteList(BaseSearchField):

    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'wlist'

    field_name = CharField(choices=constants.WL_FIELDS, default='client_address')
    
    comments = CharField(max_length=100, null=True)

    class Meta:
        order_by = ('value',)

class BlackList(BaseSearchField):

    _valid_fields = ['country', 'client_address', 'client_name', 'sender', 'recipient', 'helo_name']
    _cache_key = 'blist'

    field_name = CharField(choices=constants.BL_FIELDS, default='client_address')
    
    comments = CharField(max_length=100, null=True)

    class Meta:
        order_by = ('value',)

        
def query_for_purge():
    
    cls = GreylistEntry
    
    last_24_hours = arrow.utcnow().replace(hours=-24).datetime
    
    #pp(query.to_query(GreylistEntry))
    query = (((cls.expire_time!=None) & (cls.expire_time<utils.utcnow())) | ((cls.expire_time==None) & (cls.timestamp<=last_24_hours)))
    
    return GreylistEntry.delete().where(query)
        


def connect(url, **options):

    """
    sqlite:///:memory:
    sqlite:////this/is/absolute.path
    
    TODO: postgresql://localhost/db1?option=..
    TODO: mysql://localhost/db1?option=..
    
    """
    
    from peewee import SqliteDatabase
    
    schemes = {
        #'apsw': APSWDatabase,
        #'berkeleydb': BerkeleyDatabase,
        #'mysql': MySQLDatabase,
        #'postgres': PostgresqlDatabase,
        #'postgresql': PostgresqlDatabase,
        #'postgresext': PostgresqlExtDatabase,
        #'postgresqlext': PostgresqlExtDatabase,
        'sqlite': SqliteDatabase,
        #'sqliteext': SqliteExtDatabase,
    }
    if HAVE_PSYCOPG2:
        schemes['postgres'] = PostgresqlDatabase
        schemes['postgresql'] = PostgresqlDatabase

    if HAVE_MYSQL:
        schemes['mysql'] = MySQLDatabase
    
    from urlparse import urlparse
    parsed = urlparse(url)
    database_class = schemes.get(parsed.scheme)
    
    if database_class is None:
        if database_class in schemes:
            raise RuntimeError('Attempted to use "%s" but a required library '
                               'could not be imported.' % parsed.scheme)
        else:
            raise RuntimeError('Unrecognized or unsupported scheme: "%s".' %
                               parsed.scheme)

    options['database'] = parsed.path[1:]
    if parsed.username:
        options['user'] = parsed.username
    if parsed.password:
        options['password'] = parsed.password
    if parsed.hostname:
        options['host'] = parsed.hostname
    if parsed.port:
        options['port'] = parsed.port

    try:
    # Adjust parameters for MySQL.
        if database_class is MySQLDatabase and 'password' in options:
            options['passwd'] = options.pop('password')
    except:
        pass

    return database_class(**options)

def configure_peewee(db_name='sqlite:///:memory:', db_options=None, drop_before=False):
    
    from peewee import create_model_tables, drop_model_tables
    
    db_options = db_options or {}

    database = connect(db_name, **db_options)
    database_proxy.initialize(database)

    tables = [Domain,
              Mynetwork,
              Policy, 
              GreylistEntry, 
              GreylistMetric, 
              WhiteList, 
              BlackList]
    if drop_before:
        drop_model_tables(tables, fail_silently=True)

    create_model_tables(tables, fail_silently=True)

def import_fixtures(fixtures):

    #TODO: supp id/_id field if exist ?
    
    entries = 0    
    success = 0
    warn_error = 0
    fatal_error = 0
    errors = []
    
    fixtures_klass = (
        ('domain', Domain),
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
            except IntegrityError:
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
        ('mynetwork', Mynetwork),
        ('whitelist', WhiteList),
        ('blacklist', BlackList),
        ('policy', Policy),
    )
    
    fixtures = {}
    
    for key, klass in fixtures_klass:
        fixtures[key] = []
        for d in list(klass.select().dicts()):
            d.pop('id', None)
            fixtures[key].append(d)
    
    return fixtures
