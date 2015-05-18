# -*- coding: utf-8 -*-

from jinja2 import Markup

from flask import abort, redirect, url_for, request, session, current_app

from ..ext.flask_login import current_user

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
        return current_user.is_authenticated
    
    def inaccessible_callback(self, name, **kwargs):
        if not current_user.is_authenticated:
            return abort(401)
        
        return abort(403)
