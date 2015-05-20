# -*- coding: utf-8 -*-

import datetime
import json

from flask import abort, request, current_app

from flask_admin import Admin
from flask_admin import expose
from flask_admin.contrib.mongoengine.view import ModelView as BaseModelView
from flask_admin.contrib.mongoengine.view import SORTABLE_FIELDS

from mongoengine import fields as mongoengine_fields
SORTABLE_FIELDS.add(mongoengine_fields.LongField)

import arrow

from ...web import admin as share_admin
from ...web.extensions import gettext
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



class ModelView(share_admin.SecureView, BaseModelView):
    pass


class UserView(share_admin.UserViewMixin, ModelView):
    pass


class DomainView(share_admin.DomainViewMixin, ModelView):
    pass


class MailboxView(share_admin.MailboxViewMixin, ModelView):
    pass
    

class MynetworkView(share_admin.MynetworkViewMixin, ModelView):
    pass
    

class WhiteListView(share_admin.WhiteListViewMixin, ModelView):
    
    column_formatters = {
        "field_name": lambda v, c, m, n: m.get_field_name_display(),
    }


class BlackListView(share_admin.BlackListViewMixin, ModelView):

    column_formatters = {
        "field_name": lambda v, c, m, n: m.get_field_name_display(),
    }


class PolicyView(share_admin.PolicyViewMixin, ModelView):
    
    #column_list = ('name', 'value', 'mynetwork_vrfy', 'field_name', 'greylist_key', 'greylist_remaining', 'greylist_expire', 'comments')
    
    column_formatters = {
        "field_name": lambda v, c, m, n: m.get_field_name_display(),
    }
    
class GreylistMetricView(share_admin.GreylistMetricViewMixin, ModelView):
    pass
    
class GreylistEntryView(share_admin.GreylistEntryViewMixin, ModelView):
    """
    TODO: Actions
        add whitelist ip
        add whitelist sender email
        add whitelist sender domain
        add whitelist recipient email
        add whitelist recipient domain
    """
    
    @expose('/show')
    def show(self):
        _id = request.args.get('id') 
        model = self.get_one(_id)
        if not model:
            abort(404)
                    
        kwargs = model.to_mongo().to_dict()
        
        return self.render('mongrey/greylistentry_show.html', **kwargs)

def init_admin(app, 
               admin_app=None, 
               url='/admin',
               name=u"Mongrey Admin",
               base_template='mongrey/layout.html',
               index_template=None,
               index_view=None,
               ):

    index_view = index_view or share_admin.AdminIndexView(template=index_template, 
                                                          url=url,
                                                          name="home")
    
    admin = admin_app or Admin(app,
                               url=url,
                               name=name,
                               index_view=index_view, 
                               base_template=base_template, 
                               template_mode='bootstrap3')

    admin.add_view(UserView(models.User, 
                            name=gettext(u"Users")))

    admin.add_view(DomainView(models.Domain, 
                                 name=gettext(u"Domains")))
    
    admin.add_view(MailboxView(models.Mailbox, 
                                 name=gettext(u"Mailboxs")))
    
    admin.add_view(MynetworkView(models.Mynetwork, 
                                 name=gettext(u"Mynetworks")))

    admin.add_view(PolicyView(models.Policy, 
                                      name=gettext(u"Policies")))

    admin.add_view(GreylistEntryView(models.GreylistEntry, 
                                     name=gettext(u"Greylists")))

    admin.add_view(WhiteListView(models.WhiteList, 
                                 name=gettext(u"Whitelists")))

    admin.add_view(BlackListView(models.BlackList, 
                                 name=gettext(u"Blacklists")))
    
    admin.add_view(GreylistMetricView(models.GreylistMetric, 
                                      name=gettext(u"Metrics")))
    