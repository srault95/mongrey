# -*- coding: utf-8 -*-

import os, sys
CURRENT = os.path.abspath(os.path.dirname(__file__))
LOCAL_STATIC_DIR = os.path.abspath(os.path.join(CURRENT, '_static'))
sys.path.append(os.path.abspath(os.path.join(CURRENT, '..', '..')))
from shared_conf import *

language = "fr"
today_fmt = '%d/%m/%Y %H:%M:%S'
html_last_updated_fmt = today_fmt
html_static_path += [LOCAL_STATIC_DIR]

#http://fr.wikipedia.org/wiki/Greylisting
#http://en.wikipedia.org/wiki/Greylisting

extlinks = {
    'wikipedia': ('http://fr.wikipedia.org/wiki/' '%s', ''),
}

html_theme_options['lang'] = 'fr'
html_search_language = "fr"