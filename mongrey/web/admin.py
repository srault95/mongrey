# -*- coding: utf-8 -*-

from jinja2 import Markup

from flask import abort, redirect, url_for, request, session, current_app, flash
from flask_admin import AdminIndexView as BaseAdminIndexView, expose

from ..ext.flask_login import current_user, logout_user
from .. import constants
from .extensions import gettext

def moment_format(value):
    """
    moment('2015-06-06 07:19:41.746000+00:00').utc().format('LLL')
    """
    if not value:
        return
    
    return Markup('<span class="moment" data-format="LLL" data-value="%s"></span>' % value)
    #return Markup("moment('%s').utc().format('LLL')" % value)

def key_format(_id, value):
    return Markup('<a href="%s" class="show">%s</a>' % (url_for('greylistentry.show', id=_id), value))

class SecureView(object):

    def is_accessible(self):
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        
        return abort(403)


class UserViewMixin:
    
    column_list = ('username',)

    column_searchable_list = ('username',)

    form_excluded_columns = ('slug',)


class DomainViewMixin:
    
    column_list = ('name',)

    column_searchable_list = ('name',)

    form_excluded_columns = ('slug',)


class MailboxViewMixin:
    
    column_list = ('name',)

    column_searchable_list = ('name',)

    form_excluded_columns = ('slug',)


class MynetworkViewMixin:
    
    column_list = ('value', 'comments')

    column_searchable_list = ('value', 'comments')

    form_excluded_columns = ('slug',)


class WhiteListViewMixin:
    
    column_list = ('value', 'field_name', 'comments')

    column_searchable_list = ('value', 'comments')
    
    #column_editable_list = ('value', 'field_name', 'comments')    

    form_excluded_columns = ('slug',)
    
class BlackListViewMixin:
    
    column_list = ('value', 'field_name', 'comments')

    column_searchable_list = ('value', 'comments')

    form_excluded_columns = ('slug',)


class PolicyViewMixin:
    
    column_list = ('name', 'value', 'field_name', 'comments', 'greylist_enable', 'spoofing_enable', 'rbl_enable', 'spf_enable')

    form_excluded_columns = ('slug',)

    
class GreylistMetricViewMixin:
    
    can_edit = False

    can_create = False
    
    column_list = ('timestamp', 'count', 'accepted', 'rejected', 'requests', 'abandoned', 'delay')
    
    form_excluded_columns = ('slug',)
    
    column_formatters = {
        "timestamp": lambda v, c, m, n: moment_format(m.timestamp),
    }
    
class GreylistEntryViewMixin:
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
    
    
class AdminIndexView(SecureView, BaseAdminIndexView):
    
    @expose()
    def index(self):
        return redirect(url_for('greylistentry.index_view'))
    
    @expose('/logout')
    def logout(self):
        logout_user()
        return redirect(url_for('admin.index'))
    
    @expose('/change-lang', methods=('GET',))
    def change_lang(self):
        """
        {{ url_for('user_menu.change_lang') }}?locale=fr
        """
        from flask_babelex import refresh
        locale = request.args.get("locale", None)
        current_lang = session.get(constants.SESSION_LANG_KEY, None)

        if locale and current_lang and locale != current_lang and locale in dict(current_app.config.get('ACCEPT_LANGUAGES_CHOICES')).keys():
            flash(gettext(u"The language has been updated"))
            session[constants.SESSION_LANG_KEY] = locale
            refresh()

        _next = request.args.get("next") or request.referrer or request.url
        return redirect(_next)

    
