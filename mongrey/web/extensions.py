# -*- coding: utf-8 -*-

from .auth import BasicAuth
from flask_babelex import Babel, lazy_gettext, gettext, _

from flask_kvsession import KVSessionExtension  

babel = Babel()

auth = BasicAuth()

session_store = KVSessionExtension()

