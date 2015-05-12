# -*- coding: utf-8 -*-

from decouple import config

gettext = lambda s:s

class Config(object):
    
    STORAGE = config('MONGREY_STORAGE', 'mongo')

    SECRET_KEY = config('MONGREY_SECRET_KEY', 'qwerty12345678')

    DEBUG = config('MONGREY_DEBUG', False, cast=bool)
    
    DEFAULT_THEME = config('MONGREY_THEME', 'slate')

    ACCEPT_LANGUAGES_CHOICES = (
        ('en', gettext(u'English')),
        ('fr', gettext(u'French')),
    )
    
    #---Flask-Babelex
    BABEL_DEFAULT_TIMEZONE = config('MONGREY_TIMEZONE', "UTC")
    BABEL_DEFAULT_LOCALE = config('MONGREY_LANG', "en")

    #---Flask-Basic-Auth
    BASIC_AUTH_USERNAME = config('MONGREY_USERNAME', 'radicalspam')
    BASIC_AUTH_PASSWORD = config('MONGREY_PASSWORD', 'radicalspam') # noqa
    BASIC_AUTH_FORCE = True
    BASIC_AUTH_REALM = '/'
    BASIC_AUTH_MAX_ATTEMPT = config('MONGREY_AUTH_MAX_ATTEMPT', 3, cast=int)
    
    MONGODB_SETTINGS = {
        'host': config('MONGREY_DB', 'mongodb://localhost/greylist'),
        'use_greenlets': True,
        'tz_aware': True,    
    }   
    
    PEEWEE_SETTINGS = {
        'db_name': config('MONGREY_DB', 'sqlite:///mongrey.db'),
        'db_options': {
            'threadlocals': True    #pour use with gevent patch
        }
    }        
    
    WEB_HOST = config('MONGREY_WEB_HOST', '127.0.0.1', cast=str)
    
    WEB_PORT = config('MONGREY_WEB_PORT', 8081, cast=int)
    

class Prod(Config):
    pass

class Dev(Config):

    DEBUG = True

    SECRET_KEY = 'dev_key' # noqa
    
    MAIL_DEBUG = True
    
class Test(Config):

    TESTING = True
    
    SECRET_KEY = 'test_key' # noqa
    
    WTF_CSRF_ENABLED = False
    
    PROPAGATE_EXCEPTIONS = True

    MAIL_SUPPRESS_SEND = True

    BASIC_AUTH_USERNAME = 'radicalspamtest'
    BASIC_AUTH_PASSWORD = 'radicalspamtest'

    MONGODB_SETTINGS = {
        'host': config('MONGREY_DB', 'mongodb://localhost/greylist_test'),
        'use_greenlets': True,
        'tz_aware': True,    
    }   

    PEEWEE_SETTINGS = {
        'db_name': config('MONGREY_DB', 'sqlite:///../mongrey_test.db'),
        'db_options': {
            'threadlocals': True    #pour use with gevent patch
        }
    }        
