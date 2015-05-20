# -*- coding: utf-8 -*-

import datetime
import json

from flask import abort, request, current_app
from wtforms import fields

from flask_admin import Admin, expose
from flask_admin.model import filters
from flask_admin.contrib.peewee.filters import FilterConverter 
from flask_admin.contrib.peewee.view import ModelView as BaseModelView
from flask_admin.contrib.peewee.form import CustomModelConverter

from playhouse import shortcuts

import arrow

from ...web.extensions import gettext

from ...web import admin as share_admin
from . import models

class CustomFilterConverter(FilterConverter):

    @filters.convert('DateTimeFieldExtend')
    def conv_datetime(self, column, name):
        return [f(column, name) for f in self.datetime_filters]

    #@filters.convert('ListCharField')
    #def conv_datetime(self, column, name):
    #    return [f(column, name) for f in self.datetime_filters]

class ModelConverter(CustomModelConverter):

    def handle_list(self, model, field, **kwargs):
        return field.name, fields.FieldList(**kwargs)
    
    def __init__(self, view, additional=None):
        CustomModelConverter.__init__(self, view, additional=additional)
        self.converters[models.DateTimeFieldExtend] = self.handle_datetime        
        self.converters[models.ListCharField] = self.handle_list       

def json_convert(obj):
    
    if isinstance(obj, datetime.datetime):
        return arrow.get(obj).for_json()
    
    return obj

def jsonify(obj):
    content = json.dumps(obj, default=json_convert)
    return current_app.response_class(content, mimetype='application/json')


class ModelView(share_admin.SecureView, BaseModelView):
    
    model_form_converter = ModelConverter
    
    filter_converter = CustomFilterConverter()


class UserView(share_admin.UserViewMixin, ModelView):
    pass


class DomainView(share_admin.DomainViewMixin, ModelView):
    pass


class MailboxView(share_admin.MailboxViewMixin, ModelView):
    pass


class MynetworkView(share_admin.MynetworkViewMixin, ModelView):
    pass


class WhiteListView(share_admin.WhiteListViewMixin, ModelView):
    pass


class BlackListView(share_admin.BlackListViewMixin, ModelView):
    pass


class PolicyView(share_admin.PolicyViewMixin, ModelView):
    pass
    
    
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

        kwargs = shortcuts.model_to_dict(model, exclude=['protocol'])
        print "model.protocol : ", model.protocol, type(model.protocol), model.protocol.items()
        kwargs['protocol'] = model.protocol

        return self.render('mongrey/greylistentry_show.html', **kwargs)


def init_admin(app, 
               admin_app=None, 
               url='/admin',
               name=u"Greylist",               
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
                               template_mode='bootstrap3'
                               )
    
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
