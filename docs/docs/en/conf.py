# -*- coding: utf-8 -*-

#language = "en"
#today_fmt = '%Y-%m-%d %H:%M:%S'

import os, sys
import datetime

CURRENT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(CURRENT, '..', '..', '..', '..'))
#EXT_DIR = os.path.abspath(os.path.join(CURRENT, '..', '..', '_ext'))
sys.path.insert(0, PACKAGE_DIR)
#sys.path.append(EXT_DIR)

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

from mongrey.version import __VERSION__

language = "en"

extensions = ['sphinx.ext.autodoc', 
              'sphinx.ext.todo',
              'sphinx.ext.doctest',
              'sphinx.ext.autosummary',
              'sphinx.ext.coverage',
              'sphinx.ext.intersphinx',
              'sphinx.ext.ifconfig', 
              'sphinx.ext.extlinks',
              'sphinx.ext.viewcode',
              'sphinxcontrib.email',
              'sphinxcontrib.cheeseshop',
              ]

project = u'Mongrey'
copyright = u'2015, Stéphane RAULT'

version = __VERSION__
release = __VERSION__

todo_include_todos = True

source_suffix = '.rst'

master_doc = 'index'

today_fmt = '%Y-%m-%d %H:%M:%S'

html_title = u"%s - %s" % (project, release)
html_short_title = project
html_last_updated = datetime.datetime.utcnow()
html_last_updated_fmt = today_fmt
html_copy_source = True
html_show_sourcelink = True
html_show_copyright = False

html_theme = 'default'
if not on_rtd:
    try:
        import sphinx_rtd_theme
        html_theme = 'sphinx_rtd_theme'
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    except ImportError:
        pass

show_authors = True
