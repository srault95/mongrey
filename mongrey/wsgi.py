# -*- coding: utf-8 -*-

from flask import Flask, session
from werkzeug.contrib.fixers import ProxyFix
from decouple import config as config_from_env

from .extensions import auth, babel
from . import constants
from . import utils

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
    db = MongoEngine(app)
    #db.init_app(app)
    init_admin(app=app, url='/')

def _configure_storage_sql(app):
    from mongrey.storage.sql import models
    from mongrey.storage.sql.admin import init_admin
    models.configure_peewee(**app.config.get('PEEWEE_SETTINGS'))
    init_admin(app=app, url='/')
    
    @app.before_request
    def _db_connect():
        models.database_proxy.connect()
        
    @app.teardown_request
    def _db_close(exc):
        if not models.database_proxy.is_closed():
            models.database_proxy.close()            

def create_app(config='mongrey.settings.Prod', force_storage=None):

    env_config = config_from_env('MONGREY_SETTINGS', config)
    
    app = Flask(__name__)
    app.config.from_object(env_config)

    if not app.config.get('TESTING', False):
        app.config['LOGGER_NAME'] = 'mongrey'
        app._logger = utils.configure_logging(debug=app.debug, 
                                              prog_name='mongrey')    
    
    auth.init_app(app)
    _configure_i18n(app)
    
    if force_storage:
        app.config['STORAGE'] = force_storage
    
    if app.config.get('STORAGE') == "mongo":
        _configure_storage_mongo(app)
    elif app.config.get('STORAGE') == "sql":
        _configure_storage_sql(app)
    
    @app.context_processor
    def all_processors():
        return dict(current_theme=app.config.get('DEFAULT_THEME', 'slate'),
                    current_user=auth.current_user(),
                    current_lang=app.config.get('BABEL_DEFAULT_LOCALE'),
                    langs=app.config.get('ACCEPT_LANGUAGES_CHOICES'))
    
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    return app
