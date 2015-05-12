# -*- coding: utf-8 -*-

import os, sys
import datetime

CURRENT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(CURRENT, '..', '..'))
STATIC_DIR = os.path.abspath(os.path.join(CURRENT, '_static'))
sys.path.insert(0, PACKAGE_DIR)

needs_sphinx = "1.3"

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

from mongrey.version import __VERSION__

exclude_patterns = ['_build']

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
              'sphinxcontrib.blockdiag',
              'sphinx_git',
              'releases',
              ]

project = u'Mongrey'
copyright = u'2015, Stéphane RAULT'

version = __VERSION__
release = __VERSION__

todo_include_todos = True

text_newlines = 'unix'

source_suffix = '.rst'

master_doc = 'index'

locale_dirs = []

#html_logo
#html_favicon
#html_extra_path
html_static_path = [STATIC_DIR] #'_static']
html_title = u"%s - %s" % (project, release)
html_short_title = project
html_last_updated = datetime.datetime.utcnow()
html_copy_source = True
html_show_sourcelink = True
html_show_copyright = False

#TODO: A surveiller
html_compact_lists = False
html_scaled_image_link = False

html_theme = 'default'
if not on_rtd:
    try:
        import sphinx_rtd_theme
        html_theme = 'sphinx_rtd_theme'
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    except ImportError:
        pass

"""
html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
   'using/windows': ['windowssidebar.html', 'searchbox.html'],
}
html_additional_pages = {
    'download': 'customdownload.html',
}
"""
    
html_theme_options = {
    'nosidebar': False,
    'sticky_navigation': True,
}
    

show_authors = True

#blockdiag_fontpath = '_static/ipagp.ttf'
blockdiag_fontpath = os.path.abspath(os.path.join(STATIC_DIR, 'ipagp.ttf'))
blockdiag_html_image_format = "PNG"
blockdiag_debug = True
#blockdiag_outputdir

releases_github_path = "srault95/mongrey"

def setup(app):
    from sphinx.ext.autodoc import cut_lines
    from sphinx.util.docfields import GroupedField
    #app.connect('autodoc-process-docstring', cut_lines(4, what=['module']))
    app.add_object_type('confval', 'confval',
                        objname='configuration value',
                        indextemplate='pair: %s; configuration value')
    #fdesc = GroupedField('parameter', label='Parameters',
    #                     names=['param'], can_collapse=True)
    #app.add_object_type('event', 'event', 'pair: %s; event', parse_event,
    #                    doc_field_types=[fdesc])
