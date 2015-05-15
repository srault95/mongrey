# -*- coding: utf-8 -*-

from decouple import config
from ..utils import to_list

gettext = lambda s:s

class Config(object):
    
    SECURITY_BY_HOST = config('MONGREY_WEB_SECURITY_BY_HOST', True, cast=bool)

    ALLOW_HOSTS = config('MONGREY_WEB_ALLOW_HOSTS', ['127.0.0.1'], cast=to_list)
    
    STORAGE = config('MONGREY_STORAGE', 'sql')

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
        'host': config('MONGREY_DB', 'mongodb://localhost/mongrey'),
        'tz_aware': True,    
    }   
    
    PEEWEE_SETTINGS = {
        'db_name': config('MONGREY_DB', 'sqlite:///mongrey.db'),
        'db_options': {
            'threadlocals': True    #pour use with gevent patch
        }
    }        
    
    WEB_HOST = config('MONGREY_WEB_HOST', '127.0.0.1')
    
    WEB_PORT = config('MONGREY_WEB_PORT', 8081, cast=int)
    
    #---Flask-Kvsession
    SESSION_BACKEND = config('MONGREY_SESSION_BACKEND', 'memory://')
    SESSION_KEY_BITS = 64
    #TODO: PERMANENT_SESSION_LIFETIME
    
    #---sentry
    SENTRY_DSN = config('SENTRY_DSN', None)

class Prod(Config):
    pass

class Dev(Config):

    DEBUG = True

    SECRET_KEY = 'dev_key' # noqa
    
    MAIL_DEBUG = True

    #---debugtoolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_PANELS = [
        'flask_debugtoolbar.panels.versions.VersionDebugPanel',
        'flask_debugtoolbar.panels.timer.TimerDebugPanel',
        'flask_debugtoolbar.panels.headers.HeaderDebugPanel',
        'flask_debugtoolbar.panels.request_vars.RequestVarsDebugPanel',
        'flask_debugtoolbar.panels.template.TemplateDebugPanel',
        'flask_debugtoolbar.panels.logger.LoggingPanel',
        'flask_debugtoolbar.panels.profiler.ProfilerDebugPanel',
        #'flask.ext.mongoengine.panels.MongoDebugPanel',
    ]
    
    
class Test(Config):

    TESTING = True
    
    SECRET_KEY = 'test_key' # noqa
    
    WTF_CSRF_ENABLED = False
    
    PROPAGATE_EXCEPTIONS = True

    MAIL_SUPPRESS_SEND = True

    BASIC_AUTH_USERNAME = 'radicalspamtest'
    BASIC_AUTH_PASSWORD = 'radicalspamtest' # noqa

    MONGODB_SETTINGS = {
        'host': config('MONGREY_DB', 'mongodb://localhost/mongrey_test'),
        'tz_aware': True,    
    }   

    PEEWEE_SETTINGS = {
        'db_name': config('MONGREY_DB', 'sqlite:///../mongrey_test.db'),
        'db_options': {
            'threadlocals': True    #pour use with gevent patch
        }
    }        
