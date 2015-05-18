# -*- coding: utf-8 -*-

from flask_babelex import Babel, lazy_gettext, gettext, ngettext, _
from flask_kvsession import KVSessionExtension
from ..ext.flask_login import LoginManager
  
login_manager = LoginManager()

session_store = KVSessionExtension()
