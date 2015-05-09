# -*- coding: utf-8 -*-

from jinja2 import Markup

from flask import abort, redirect, url_for, request, session, current_app

from .extensions import auth
from .extensions import gettext
from .. import constants

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
        return auth.authenticate()
    
    def inaccessible_callback(self, name, **kwargs):
        if not auth.authenticate():
            return abort(401)
        
        return abort(403)
