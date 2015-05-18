# -*- coding: utf-8 -*-

from flask import request, session, url_for, flash, abort, redirect, render_template

from ..ext.flask_login import login_user

from .. import utils
from .. import constants

from .extensions import login_manager
from .forms import LoginForm
from .extensions import gettext

class UserLogin(object):
    """
    TODO: remember
    
    TODO: backports.pbkdf2==0.1 ?
    
    TODO: @login_manager.unauthorized_handler
    def unauthorized():
        # do stuff
        return a_response
        
    TODO: login_manager.refresh_view = "accounts.reauthenticate"
    
    TODO: @login_manager.needs_refresh_handler
    
    TODO: login_manager.session_protection = "strong" basic ou None (default: basic) : SESSION_PROTECTION    
    """
    
    def __init__(self, model=None, app=None, load_user_func=None, basic_auth=True, apikey_auth=True):
        self.model = model
        self.app = app
        self.basic_auth = basic_auth
        self.apikey_auth = apikey_auth
        self.load_user_func = load_user_func
        self.views()
        UserLogin.set_loaders(self)
        
    def is_valid_basic_auth(self):
        auth = request.authorization
        if not auth:
            return False
        try:
            if auth.username:
                return True
        except Exception:
            return False
        
    def url_for_security(self, endpoint):
        endpoints = {
            'login': 'LOGIN_VIEW',
            'logout': 'LOGOUT_VIEW',
        }
        url_view = self.app.config.get(endpoints[endpoint])
        return url_for(url_view) 

    def check_password(self, from_request=None, user=None):
        
        max = self.app.config.get('AUTH_MAX_ATTEMPT', 0)
        
        if max > 0:
            if not "login_count" in session:
                session['login_count'] = 0
                 
            session['login_count'] += 1
            
            if session['login_count'] >= max:                
                self.app.logger.error("reject host [%s]" % request.remote_addr)
                abort(403)
                
        #result = from_db == utils.encrypt_sign(from_request)
        result = user.check_password(from_request)
        if not result and user.username:
            self.app.logger.warning(gettext(u"bad password for [%(username)s]", username=user.username))
        
        return result

    @classmethod
    def set_loaders(cls, login_app):

        @login_manager.user_loader
        def load_user(userid):
            return login_app.load_user(userid)

        @login_manager.request_loader
        def load_user_from_request(request):
            return login_app.load_user_from_request(request)

    def load_user(self, userid):
        return self.load_user_func(userid)
        
    def load_user_from_request(self, request):
        
        if self.apikey_auth:        
            api_key = request.args.get(constants.API_KEY)
            if api_key:
                kwargs = {constants.API_KEY: api_key}
                user = self.model.api_find_one(api_key=api_key)
                if user:
                    login_user(user)#, remember=True)
                    return user

        if self.basic_auth and self.is_valid_basic_auth():
            auth = request.authorization
            user = self.model.api_find_one(username=auth.username)
            if user:
                if self.check_password(from_request=auth.password, 
                                       user=user):
                    login_user(user)#, remember=True)
                    return user
                
        return None
    
    def views(self):
        
        login_manager.login_view =  "login"
        
        @self.app.route('/login', methods=['GET', 'POST'], endpoint="login")
        def login():
            form = LoginForm()
            
            if form.validate_on_submit():
                
                username = form.username.data
                password = form.password.data

                user = self.model.api_find_one(username=username)
                if user:
                    if self.check_password(from_request=password, 
                                           user=user):
                        
                        login_user(user)#, remember=True)
                        flash(gettext(u'Logged in successfully.'))
                        next = request.args.get('next')
                        return redirect(next or '/')
                
                flash(gettext(u'login fail. bad password or username'))
            
            return render_template('mongrey/login_user.html', login_user_form=form)    

        @self.app.errorhandler(401)
        def unauthorized(error):
            return redirect(url_for('login', next=request.url))
            