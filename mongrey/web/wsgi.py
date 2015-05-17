# -*- coding: utf-8 -*-

from flask import Flask, session
from werkzeug.contrib.fixers import ProxyFix
from decouple import config as config_from_env

from .. import constants
from .. import utils
from .extensions import auth, babel, session_store

def _configure_sentry(app):
    try:
        from raven.contrib.flask import Sentry
        if app.config.get('SENTRY_DSN', None):
            sentry = Sentry(app, logging=True, level=app.logger.level)
    except ImportError:
        app.logger.warning("Raven client for sentry is not installed")

def _configure_session(app):
    """
    SESSION_SET_TTL
    
    simplekv.fs.FilesystemStore(root, perm=None, **kwargs)
    file://
    simplekv.db.mongo.MongoStore(db, collection)
    """
    store = None
    
    SESSION_BACKEND = app.config.get('SESSION_BACKEND', 'memory://')
    from simplekv.memory import DictStore

    if SESSION_BACKEND.startswith('memory'):
        store = DictStore()
    
    elif SESSION_BACKEND.startswith('mongodb'):
        
        if not app.config.get('DB_SETTINGS', {}).get('host', '').startswith("mongodb://"):
            raise Exception("Use mongodb for session storage only if app STORAGE is mongodb")
        
        from ..storage.mongo.models import Domain
        from simplekv.db.mongo import MongoStore
        db = Domain._get_db()
        store = MongoStore(db, 'session')
    
    elif SESSION_BACKEND.startswith('redis://'):
        from simplekv.memory.redisstore import RedisStore
        from simplekv.decorator import PrefixDecorator
        from redis import from_url
        redis_cli = from_url(SESSION_BACKEND)
        store = PrefixDecorator('mongrey', RedisStore(redis_cli))

    else:
        store = DictStore()
    
    """
    TODO: CacheDecorator
    from simplekv.cache import CacheDecorator
    store = CacheDecorator(
      cache=MemcacheStore(mc),
      store=FilesystemStore('.')
    )
    """
    
    session_store.init_app(app, store)    

def _configure_i18n(app):

    babel.init_app(app)
    
    @app.before_request
    def set_locales():
        current_lang  = session.get(constants.SESSION_LANG_KEY, None)
        if not current_lang:
            session[constants.SESSION_LANG_KEY] = app.config.get('BABEL_DEFAULT_LOCALE')

        current_tz  = session.get(constants.SESSION_TIMEZONE_KEY, None)
        if not current_tz:
            session[constants.SESSION_TIMEZONE_KEY] = app.config.get('BABEL_DEFAULT_TIMEZONE')
    
    if babel.locale_selector_func is None:
        @babel.localeselector
        def get_locale():
            current_lang  = session.get(constants.SESSION_LANG_KEY, app.config.get('BABEL_DEFAULT_LOCALE'))
            return current_lang
    
    if babel.timezone_selector_func is None:
        @babel.timezoneselector
        def get_timezone():
            return session.get(constants.SESSION_TIMEZONE_KEY, app.config.get('BABEL_DEFAULT_TIMEZONE'))
    
def _configure_storage_mongo(app):    
    from flask_mongoengine import MongoEngine
    from mongrey.storage.mongo.admin import init_admin
    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))
    app.config['MONGODB_SETTINGS'] = settings
    db = MongoEngine(app)
    init_admin(app=app, url='/')

def _configure_storage_sql(app):
    from mongrey.storage.sql import models
    from mongrey.storage.sql.admin import init_admin
    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))
    models.configure_peewee(**settings)
    init_admin(app=app, url='/')
    
    @app.before_request
    def _db_connect():
        models.database_proxy.connect()
        
    @app.teardown_request
    def _db_close(exc):
        if not models.database_proxy.is_closed():
            models.database_proxy.close()            

def create_app(config='mongrey.web.settings.Prod'):

    env_config = config_from_env('MONGREY_SETTINGS', config)
    
    app = Flask(__name__)
    app.config.from_object(env_config)

    if not app.config.get('TESTING', False):
        app.config['LOGGER_NAME'] = 'mongrey'
        app._logger = utils.configure_logging(debug=app.debug, 
                                              prog_name='mongrey')    
    
    auth.init_app(app)
    _configure_i18n(app)
    
    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))

    if storage == "mongo":
        _configure_storage_mongo(app)
        if 'DEBUG_TB_PANELS' in app.config:
            app.config['DEBUG_TB_PANELS'].append('flask.ext.mongoengine.panels.MongoDebugPanel')
    
    elif storage == "sql":
        _configure_storage_sql(app)
        
    _configure_session(app)
    
    if app.debug:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except ImportError:
            pass
        
    _configure_sentry(app)
    
    @app.context_processor
    def all_processors():
        return dict(current_theme=app.config.get('DEFAULT_THEME', 'slate'),
                    current_user=auth.current_user(),
                    current_lang=app.config.get('BABEL_DEFAULT_LOCALE'),
                    langs=app.config.get('ACCEPT_LANGUAGES_CHOICES'))
    
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    return app
