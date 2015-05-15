# -*- coding: utf-8 -*-

from fabric.api import *
from fabric.operations import local

@task
def serve(lang='fr'):
    with lcd('docs/_build/html/%s' % lang):
        with settings(warn_only=True):
            local('python -m SimpleHTTPServer 8000')

@task
def serve_en():
    serve(lang='en')

@task
def test():
    local('nosetests -s -v mongrey')

@task
def babel(init=False):
    local('pybabel extract -F mongrey/translations/babel.cfg -k gettext -k _gettext -k _ngettext -k lazy_gettext -k _ -o mongrey/translations/mongrey.pot --project Mongrey mongrey')
    if init:
        local('pybabel init -i mongrey/translations/mongrey.pot -d mongrey/translations -l fr')
    local('pybabel update -i mongrey/translations/mongrey.pot -d mongrey/translations -l fr')
    local('pybabel compile -d mongrey/translations --statistics')
    #--domain=flask_user
    
@task
def babel_init():
    babel(init=True)
    

@task
def docs():
    """
    sphinx-apidoc -o docs/source/modules mongrey
    sphinx-apidoc --force -l -T -E -M -o docs/source/modules mongrey
    """
    local('sphinx-build -a -v -N -w docs/_build/errors-fr.log -b html docs/docs/fr docs/_build/html/fr')
    local('sphinx-build -a -v -N -w docs/_build/errors-en.log -b html docs/docs/en docs/_build/html/en')
    local('sphinx-build -a -v -N -b changes docs/docs/fr docs/_build/html/fr/changes')
    with lcd('docs/_build/html/fr'):
        with settings(warn_only=True):
            local('python -m SimpleHTTPServer 8000')
    
    #local('cd ../builds/flask_user/docs && zip -u -r flask_user_docs *')

@task
def rebuild_docs():
    local('rm -fr docs/_build/html')
    docs()

@task
def upload_to_pypi():
    local('python setup.py sdist --formats=zip,gztar bdist_wheel upload')
    
@task
def runtests_mongo():
    with shell_env(MONGREY_STORAGE='mongo', MONGREY_DB='mongodb://localhost/mongrey_test'):
        with settings(warn_only=True):
            local('nosetests -s -v mongrey')

@task
def runtests_sql():
    with shell_env(MONGREY_STORAGE='sql', MONGREY_DB='sqlite:///../mongrey_test.db'):
        with settings(warn_only=True):
            local('nosetests -s -v mongrey')
        
@task
def runtests():
    with settings(warn_only=True):
        local('nosetests -s -v mongrey')
        
@task
def run_web():
    local('python -m mongrey.web.manager server')
        
                                