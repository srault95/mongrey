# -*- coding: utf-8 -*-

import datetime
import json

from jinja2 import Markup
from flask import abort, redirect, url_for, request, session, current_app

from flask_admin import Admin, AdminIndexView as BaseAdminIndexView, expose
from flask_admin.contrib.mongoengine.view import ModelView as BaseModelView
from flask_admin.contrib.mongoengine.view import SORTABLE_FIELDS

from mongoengine import fields as mongoengine_fields
SORTABLE_FIELDS.add(mongoengine_fields.LongField)

from flask_babelex import format_date, format_datetime, format_number
import arrow

from ...extensions import auth
from ...extensions import gettext, lazy_gettext
from ... import constants
from . import models

def json_convert(obj):
    from bson import ObjectId
    
    if isinstance(obj, ObjectId):
        return str(obj)
    
    elif isinstance(obj, datetime.datetime):
        return arrow.get(obj).for_json()
    
    return obj

def jsonify(obj):
    content = json.dumps(obj, default=json_convert)
    return current_app.response_class(content, mimetype='application/json')

def moment_format(value):
    """
    moment('2015-06-06 07:19:41.746000+00:00').utc().format('LLL')
    """
    if not value:
        return
    
    return Markup('<span class="moment" data-format="LLL" data-value="%s"></span>' % value)
    #return Markup("moment('%s').utc().format('LLL')" % value)
    
def key_format(id, value):
    return Markup('<a href="%s" class="show">%s</a>' % (url_for('greylistentry.show', id=id), value))

class SecureView(object):

    def is_accessible(self):
        return auth.authenticate()
    
    def inaccessible_callback(self, name, **kwargs):
        if not auth.authenticate():
            return abort(401)
        
        return abort(403)

class ModelView(SecureView, BaseModelView):
    pass

class WhiteListView(ModelView):
    
    column_list = ('value', 'value_type', 'comments')

    column_formatters = {
        "value_type": lambda v, c, m, n: m.get_value_type_display(),
    }

    column_searchable_list = ('value', 'comments')

class GreylistPolicyView(ModelView):
    
    column_list = ('name', 'value', 'value_type', 'greylist_key', 'greylist_remaining', 'greylist_expire', 'comments')
    
    column_formatters = {
        "value_type": lambda v, c, m, n: m.get_value_type_display(),
    }
    
class GreylistMetricView(ModelView):
    
    can_edit = False

    can_create = False
    
    column_list = ('timestamp', 'count', 'accepted', 'rejected', 'requests', 'abandoned', 'delay')
    
    column_formatters = {
        "timestamp": lambda v, c, m, n: moment_format(m.timestamp),
    }

class GreylistEntryView(ModelView):
    """
    TODO: Actions
        add whitelist ip
        add whitelist sender email
        add whitelist sender domain
        add whitelist recipient email
        add whitelist recipient domain
    """
    
    list_template = "mongrey/greylistentry_list.html"
    
    column_list = ('key', 'timestamp', 'delay', 'expire_time', 'rejects', 'accepts', 'policy')

    can_edit = False
    can_create = False

    column_formatters = {
        "key": lambda v, c, m, n: key_format(m.id, m.key),
        "timestamp": lambda v, c, m, n: moment_format(m.timestamp),
        "expire_time": lambda v, c, m, n: moment_format(m.expire_time),
    }

    column_filters = ['key', 'timestamp', 'expire_time']
    
    column_searchable_list = ['key']
    
    @expose('/show')
    def show(self):
        id = request.args.get('id') 
        model = self.get_one(id)
        if not model:
            abort(404)
                    
        kwargs = model.to_mongo().to_dict()
        
        return self.render('mongrey/greylistentry_show.html', **kwargs)
        
        return jsonify(kwargs)

class AdminIndexView(SecureView, BaseAdminIndexView):
    
    @expose()
    def index(self):
        return redirect(url_for('greylistentry.index_view'))
    
    @expose('/logout')
    def logout(self):
        auth.logout()
        return redirect(url_for('admin.index'))
    
    @expose('/change-lang', methods=('GET',))
    def change_lang(self):
        """
        {{ url_for('user_menu.change_lang') }}?locale=fr
        """
        
        from flask_babelex import refresh
        locale = request.args.get("locale", None)
        current_lang  = session.get(constants.SESSION_LANG_KEY, None)

        if locale and current_lang and locale != current_lang and locale in dict(current_app.config.get('ACCEPT_LANGUAGES_CHOICES')).keys():
            session[constants.SESSION_LANG_KEY] = locale
            refresh()
        
        next = request.args.get("next") or request.referrer or request.url
        return redirect(next)
        
    

def init_admin(app, 
               admin_app=None, 
               url='/admin',
               name=u"Greylist",
               base_template='mongrey/layout.html',
               index_template=None,
               index_view=None,
               ):
    
    admin = admin_app or Admin(app,
                               url=url,
                               name=name,
                               index_view=index_view or AdminIndexView(template=index_template, 
                                                                       url=url,
                                                                       name="home"), 
                               base_template=base_template, 
                               template_mode='bootstrap3')


    admin.add_view(GreylistPolicyView(models.GreylistPolicy, name=gettext(u"Policies")))
    
    admin.add_view(GreylistEntryView(models.GreylistEntry, name=gettext(u"Greylists")))

    admin.add_view(WhiteListView(models.WhiteList, name=gettext(u"Whitelists")))
    
    admin.add_view(GreylistMetricView(models.GreylistMetric, name=gettext(u"Metrics")))