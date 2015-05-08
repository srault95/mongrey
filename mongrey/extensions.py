# -*- coding: utf-8 -*-

from .auth import BasicAuth
from flask_babelex import Babel, lazy_gettext, gettext, _

babel = Babel()

auth = BasicAuth()

