# -*- coding: utf-8 -*-

from flask import Flask, session, request
from werkzeug.contrib.fixers import ProxyFix
from decouple import config as config_from_env

from .. import constants
from .. import utils
from .extensions import session_store, login_manager
from .login import UserLogin
from . import forms

def _create_default_user(app=None, update_if_exist=False):
    storage = app.config.get('STORAGE')
    username = app.config.get('DEFAULT_AUTH_USERNAME')
    password = app.config.get('DEFAULT_AUTH_PASSWORD')
    
    if storage == "mongo":
        from mongrey.storage.mongo.models import User
        User.create_user(username=username, password=password, 
                         update_if_exist=update_if_exist)
    elif storage == "sql":
        from mongrey.storage.sql.models import User
        User.create_user(username=username, password=password, 
                         update_if_exist=update_if_exist)

def _configure_sentry(app):
    try:
        if app.config.get('SENTRY_DSN', None):
            from raven.contrib.flask import Sentry
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
    
    import os
    from flask_babelex import Domain
    from flask_babelex import Babel
    from .. import translations
    TRANSLATIONS_DIR = os.path.abspath(os.path.dirname(translations.__file__))
    domain = Domain(dirname=TRANSLATIONS_DIR)#, domain="mongrey")
    babel = Babel(app, default_domain=domain, 
          default_locale=app.config.get('BABEL_DEFAULT_LOCALE'))
    
    @app.before_request
    def set_locales():
        current_lang  = session.get(constants.SESSION_LANG_KEY, None)
        if not current_lang:
            session[constants.SESSION_LANG_KEY] = app.config.get('BABEL_DEFAULT_LOCALE')

        current_tz  = session.get(constants.SESSION_TIMEZONE_KEY, None)
        if not current_tz:
            session[constants.SESSION_TIMEZONE_KEY] = app.config.get('BABEL_DEFAULT_TIMEZONE')
    
    if not babel.locale_selector_func:
        @babel.localeselector
        def get_locale():
            default_lang = request.accept_languages.best_match(dict(app.config.get('ACCEPT_LANGUAGES_CHOICES')).keys())
            return session.get(constants.SESSION_LANG_KEY, default_lang)

    if babel.timezone_selector_func is None:
        @babel.timezoneselector
        def get_timezone():
            return session.get(constants.SESSION_TIMEZONE_KEY, app.config.get('BABEL_DEFAULT_TIMEZONE'))
    
def _configure_storage_mongo(app):    
    from flask_mongoengine import MongoEngine
    from mongrey.storage.mongo.admin import init_admin
    from mongrey.storage.mongo.models import User
    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))
    app.config['MONGODB_SETTINGS'] = settings
    db = MongoEngine(app)
    init_admin(app=app, url='/')
    
    def load_user(userid):
        return User.objects(pk=userid).first()
    
    app.login_app = UserLogin(model=User, 
                              app=app, 
                              load_user_func=load_user)
    
def _configure_storage_sql(app):
    from mongrey.storage.sql import models
    from mongrey.storage.sql.admin import init_admin
    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))
    models.configure_peewee(**settings)
    init_admin(app=app, url='/')

    def load_user(userid):
        try:
            return models.User.get(id=userid)
        except Exception, err:
            app.logger.warning(str(err))            

    app.login_app = UserLogin(model=models.User, 
                              app=app, 
                              load_user_func=load_user)
    
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

    utils.SECRET_KEY = app.config.get('SECRET_KEY')

    _configure_i18n(app)
    
    login_manager.init_app(app)

    settings, storage = utils.get_db_config(**app.config.get('DB_SETTINGS'))

    if storage == "mongo":
        _configure_storage_mongo(app)
        app.config['STORAGE'] = "mongo"
        if 'DEBUG_TB_PANELS' in app.config:
            app.config['DEBUG_TB_PANELS'].append('flask.ext.mongoengine.panels.MongoDebugPanel')
    
    elif storage == "sql":
        _configure_storage_sql(app)
        app.config['STORAGE'] = "sql"
        
    _configure_session(app)

    _configure_sentry(app)
    
    if app.debug:
        try:
            from flask_debugtoolbar import DebugToolbarExtension
            DebugToolbarExtension(app)
        except ImportError:
            pass
    
    @app.context_processor
    def all_processors():
        current_lang = session.get(constants.SESSION_LANG_KEY, app.config.get('BABEL_DEFAULT_LOCALE'))
        return dict(current_theme=app.config.get('DEFAULT_THEME', 'slate'),
                    current_lang=current_lang,
                    langs=app.config.get('ACCEPT_LANGUAGES_CHOICES'),
                    url_for_security=app.login_app.url_for_security,
                    is_hidden=forms._is_hidden, 
                    is_required=forms._is_required,
                    )

    @app.before_first_request
    def create_default_user():
        _create_default_user(app=app)
    
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    return app
