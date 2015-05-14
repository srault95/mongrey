# -*- coding: utf-8 -*-

import os, sys
import datetime

CURRENT = os.path.abspath(os.path.dirname(__file__))
PACKAGE_DIR = os.path.abspath(os.path.join(CURRENT, '..', '..'))
STATIC_DIR = os.path.abspath(os.path.join(CURRENT, '_static'))
EXT_DIR = os.path.abspath(os.path.join(CURRENT, '_ext'))
sys.path.insert(0, PACKAGE_DIR)
sys.path.append(EXT_DIR)

needs_sphinx = "1.3"

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

from mongrey.version import __VERSION__

exclude_patterns = ['_build', '_draft', '_ext']

extensions = ['sphinx.ext.autodoc', 
              'sphinx.ext.todo',
              'sphinx.ext.doctest',
              'sphinx.ext.autosummary',
              'sphinx.ext.coverage',
              'sphinx.ext.intersphinx',
              'sphinx.ext.ifconfig', 
              'sphinx.ext.extlinks',
              'sphinx.ext.viewcode',
              #'sphinxcontrib.email',
              'sphinxcontrib.cheeseshop',
              'sphinxcontrib.blockdiag',
              'sphinx_git',
              'releases',
              'sphinxjp.themes.basicstrap',
              'contrib.email'
              ]

project = u'Mongrey'
copyright = u'2015, Stéphane RAULT'

version = __VERSION__
release = __VERSION__

todo_include_todos = True

text_newlines = 'unix'

source_suffix = '.rst'

master_doc = 'index'

add_module_names = False

locale_dirs = []

"""
autoclass_content = "both"
exclude_trees = []
"""

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
#html_compact_lists = False
html_scaled_image_link = False

"""
if on_rtd:    
    html_theme = 'default'
    html_theme_options = {
        'nosidebar': False,
        'sticky_navigation': True,
    }
else:
"""

html_theme = 'basicstrap'

html_theme_options = {

    'lang': 'fr',
    # Disable showing the sidebar. Defaults to 'false'
    'nosidebar': False,
    # Show header searchbox. Defaults to false. works only "nosidber=True",
    'header_searchbox': False,

    # Put the sidebar on the right side. Defaults to false.
    'rightsidebar': False,
    # Set the width of the sidebar. Defaults to 3
    'sidebar_span': 3,

    # Fix navbar to top of screen. Defaults to true
    'nav_fixed_top': True,
    # Fix the width of the sidebar. Defaults to false
    'nav_fixed': False,
    # Set the width of the sidebar. Defaults to '900px'
    'nav_width': '900px',
    # Fix the width of the content area. Defaults to false

    'content_fixed': False,
    # Set the width of the content area. Defaults to '900px'
    'content_width': '900px',
    # Fix the width of the row. Defaults to false
    'row_fixed': False,

    # Disable the responsive design. Defaults to false
    'noresponsive': False,
    # Disable the responsive footer relbar. Defaults to false
    'noresponsiverelbar': False,
    # Disable flat design. Defaults to false.
    # Works only "bootstrap_version = 3"
    'noflatdesign': False,

    # Enable Google Web Font. Defaults to false
    'googlewebfont': False,
    # Set the URL of Google Web Font's CSS.
    # Defaults to 'http://fonts.googleapis.com/css?family=Text+Me+One'
    'googlewebfont_url': 'http://fonts.googleapis.com/css?family=Lily+Script+One',  # NOQA
    # Set the Style of Google Web Font's CSS.
    # Defaults to "font-family: 'Text Me One', sans-serif;"
    'googlewebfont_style': u"font-family: 'Lily Script One' cursive;",

    # Set 'navbar-inverse' attribute to header navbar. Defaults to false.
    'header_inverse': False,
    # Set 'navbar-inverse' attribute to relbar navbar. Defaults to false.
    'relbar_inverse': False,

    # Enable inner theme by Bootswatch. Defaults to false
    'inner_theme': True,
    # Set the name of innner theme. Defaults to 'bootswatch-simplex'
    'inner_theme_name': 'bootswatch-readable',
    #'inner_theme_name': 'bootswatch-flatly',

    # Select Twitter bootstrap version 2 or 3. Defaults to '3'
    'bootstrap_version': '3',

    # Show "theme preview" button in header navbar. Defaults to false.
    'theme_preview': True,

    # Set the Size of Heading text. Defaults to None
    # 'h1_size': '3.0em',
    # 'h2_size': '2.6em',
    # 'h3_size': '2.2em',
    # 'h4_size': '1.8em',
    # 'h5_size': '1.4em',
    # 'h6_size': '1.1em',
}

"""
html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
   'using/windows': ['windowssidebar.html', 'searchbox.html'],
}
html_additional_pages = {
    'download': 'customdownload.html',
}
"""
    
show_authors = True

#blockdiag_fontpath = '_static/ipagp.ttf'
blockdiag_fontpath = os.path.abspath(os.path.join(STATIC_DIR, 'ipagp.ttf'))
blockdiag_html_image_format = "PNG"
blockdiag_debug = True
#blockdiag_outputdir
blockdiag_antialias = True

releases_github_path = "radical-software/mongrey"

#from sphinx.highlighting import lexers
#from pygments.lexers.python import PythonLexer
#lexers['python'] = PhpLexer(startinline=True)

"""
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

"""