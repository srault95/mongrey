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

add_module_names = False

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

if on_rtd:    
    html_theme = 'default'
    html_theme_options = {
        'nosidebar': False,
        'sticky_navigation': True,
    }
else:    
    import sphinx_bootstrap_theme
    html_theme = 'bootstrap'
    html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
    #htmlhelp_basename = 'MyProjectDoc'
    html_theme_options = {
        # Navigation bar title. (Default: ``project`` value)
        #'navbar_title': "Demo",
    
        # Tab name for entire site. (Default: "Site")
        'navbar_site_name': "Site",
    
        # Tab name for the current pages TOC. (Default: "Page")
        'navbar_pagenav_name': "Page",
    
        # A list of tuples containing pages or urls to link to.
        # Valid tuples should be in the following forms:
        #    (name, page)                 # a link to a page
        #    (name, "/aa/bb", 1)          # a link to an arbitrary relative url
        #    (name, "http://example.com", True) # arbitrary absolute url
        # Note the "1" or "True" value above as the third argument to indicate
        # an arbitrary url.
        # 'navbar_links': [
        #     ("Examples", "examples"),
        #     ("Link", "http://example.com", True),
        # ],
    
        # Global TOC depth for "site" navbar tab. (Default: 1)
        # Switching to -1 shows all levels.
        'globaltoc_depth': 2,
    
        # Include hidden TOCs in Site navbar?
        #
        # Note: If this is "false", you cannot have mixed ``:hidden:`` and
        # non-hidden ``toctree`` directives in the same page, or else the build
        # will break.
        #
        # Values: "true" (default) or "false"
        'globaltoc_includehidden': "true",
    
        # HTML navbar class (Default: "navbar") to attach to <div> element.
        # For black navbar, do "navbar navbar-inverse"
        'navbar_class': "navbar",
    
        # Fix navigation bar to top of page?
        # Values: "true" (default) or "false"
        'navbar_fixed_top': "true",
    
        # Location of link to source.
        # Options are "nav" (default), "footer" or anything else to exclude.
        'source_link_position': "nav",
    
        # Bootswatch (http://bootswatch.com/) theme.
        #
        # Options are nothing (default) or the name of a valid theme such
        # as "amelia" or "cosmo".
        #
        # Themes:
        # * amelia
        # * cerulean
        # * cosmo
        # * cyborg
        # * cupid (v3 only)
        # * flatly
        # * journal
        # * lumen (v3 only)
        # * readable
        # * simplex
        # * slate
        # * spacelab
        # * spruce (v2 only)
        # * superhero
        # * united
        # * yeti (v3 only)
        'bootswatch_theme': "flatly",
    
        # Choose Bootstrap version.
        # Values: "3" (default) or "2" (in quotes)
        'bootstrap_version': "3",
    }
        
    """
    try:
        import sphinx_rtd_theme
        html_theme = 'sphinx_rtd_theme'
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    except ImportError:
        pass
    """

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
