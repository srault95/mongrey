# -*- coding: utf-8 -*-

from decouple import config
from ..utils import to_list

#gettext = lambda s:s
from .extensions import gettext

class Config(object):
    
    STORAGE = None
    
    SECURITY_BY_HOST = config('MONGREY_WEB_SECURITY_BY_HOST', True, cast=bool)

    ALLOW_HOSTS = config('MONGREY_WEB_ALLOW_HOSTS', ['127.0.0.1'], cast=to_list)
    
    SECRET_KEY = config('MONGREY_SECRET_KEY', 'qwerty12345678')

    DEBUG = config('MONGREY_DEBUG', False, cast=bool)
    
    DEFAULT_THEME = config('MONGREY_WEB_THEME', 'slate')

    ACCEPT_LANGUAGES_CHOICES = (
        ('en', gettext(u'English')),
        ('fr', gettext(u'French')),
    )
    
    #---Flask-Babelex
    BABEL_DEFAULT_TIMEZONE = config('MONGREY_TIMEZONE', "UTC")
    BABEL_DEFAULT_LOCALE = config('MONGREY_LANG', "en")

    #---Login
    LOGIN_VIEW = "login"
    LOGOUT_VIEW = "admin.logout"
    DEFAULT_AUTH_USERNAME = config('MONGREY_WEB_USERNAME', 'admin')
    DEFAULT_AUTH_PASSWORD = config('MONGREY_WEB_PASSWORD', 'mongrey') # noqa
    AUTH_MAX_ATTEMPT = config('MONGREY_WEB_AUTH_MAX_ATTEMPT', 3, cast=int)
    
    DB_SETTINGS = {
        'host': config('MONGREY_DB', 'sqlite:////var/lib/mongrey/mongrey.db'),
    }        
    
    WEB_HOST = config('MONGREY_WEB_HOST', '127.0.0.1')
    
    WEB_PORT = config('MONGREY_WEB_PORT', 8081, cast=int)
    
    #---Flask-Kvsession
    SESSION_BACKEND = config('MONGREY_WEB_SESSION_BACKEND', 'memory://')
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

    DEFAULT_AUTH_USERNAME = 'radicalspamtest'
    DEFAULT_AUTH_PASSWORD = 'radicalspamtest' # noqa

    DB_SETTINGS = {
        'host': config('MONGREY_DB', 'sqlite:////tmp/mongrey_test.db'),
    }        

