# -*- coding: utf-8 -*-

import os, sys

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
COMMON_FABRIC = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..'))
if os.path.exists(COMMON_FABRIC):
    sys.path.insert(0, COMMON_FABRIC)
try:
    from fabric_common import *
except ImportError:
    pass    

from fabric.api import *
from fabric.operations import local, run
from fabric.contrib.files import exists
from fabric.contrib.project import rsync_project

env.user = "root"
env.hosts = [os.environ.get('REMOTE_HOST')] if 'REMOTE_HOST' in os.environ else []
env.disable_known_hosts = True
env.use_ssh_config = True
env.reject_unknown_hosts = False

try:
    env.crowdin_key = CROWDIN_KEYS.get('mongrey', None)
except:
    env.crowdin_key = None

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
def crowdin_pull():
    local('curl http://api.crowdin.net/api/project/mongrey/export?key=%(crowdin_key)s' % env)    
    local('curl http://api.crowdin.net/api/project/mongrey/download/fr.zip?key=%(crowdin_key)s -o fr.zip' % env)
    local('unzip -o fr.zip')
    local('rm -f fr.zip')
    local('rm -f mongrey/translations/fr/LC_MESSAGES/messages.po')
    local('mv mongrey-fr.po mongrey/translations/fr/LC_MESSAGES/messages.po')
    local('pybabel compile -d mongrey/translations --statistics')

@task
def crowdin_push():
    local('pybabel extract -F mongrey/translations/babel.cfg -k gettext -k _gettext -k _ngettext -k lazy_gettext -k _ -o mongrey/translations/mongrey.pot --project Mongrey mongrey')
    with lcd('mongrey/translations'):
        local('curl -F "files[/mongrey.pot]=@mongrey.pot" http://api.crowdin.net/api/project/mongrey/update-file?key=%(crowdin_key)s' % env)

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
def docs_build():
    #sphinx-apidoc -o docs/source/modules mongrey
    #sphinx-apidoc --force -l -T -E -M -o docs/source/modules mongrey
    local('sphinx-build -a -v -N -b changes docs/docs/fr docs/_build/html/fr/changes')
    local('sphinx-build -a -v -N -b changes docs/docs/en docs/_build/html/en/changes')
    local('sphinx-build -a -v -N -E -w docs/_build/errors-fr.log -b html docs/docs/fr docs/_build/html/fr')
    local('sphinx-build -a -v -N -w docs/_build/errors-en.log -b html docs/docs/en docs/_build/html/en')

@task
def docs_rebuild():
    local('rm -fr docs/_build/html')
    docs_build()

@task
def docs_upload():
    """
    fab docs_upload:hosts=?
    
    Requis: MONGREY_DOC_PROJECT{}
    """

    local_path = os.path.abspath(os.path.join(CURRENT_DIR, 'docs', '_build', 'html'))
    
    if not os.path.exists(local_path):
        abort("path not found : %s" % local_path)
    
    remote_path = MONGREY_DOC_PROJECT['remote_path']
    langs = ['en', 'fr']
    
    for lang in langs:
        
        local_path_lang = os.path.abspath(os.path.join(local_path, lang))
        remote_path_lang = "%s/%s" % (remote_path, lang)

        if not exists(remote_path_lang):
            run('mkdir -vp %s' % remote_path_lang)     
        
        with lcd(local_path_lang):
            rsync_project(local_dir=".", remote_dir=remote_path_lang, 
                          delete=True, 
                          upload=True,
                          default_opts='-pthrvz') 
        

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
def runtests_skip_travis():
    with shell_env(TRAVIS='true'):
        with settings(warn_only=True):
            local('nosetests -s -v mongrey')
        
@task
def run_web():
    local('python -m mongrey.web.manager server')
        
@task
def shell_dev_mongo():
    with shell_env(MONGREY_STORAGE="mongo"):
        local('python -m mongrey.web.manager -c mongrey.web.settings.Dev shell')

@task
def shell_dev_sql():
    with shell_env(MONGREY_STORAGE="sql"):
        local('python -m mongrey.web.manager -c mongrey.web.settings.Dev shell')

"""
@task
def migration_rs_mongo():
    kwargs = dict(MONGREY_STORAGE='mongo', MONGREY_DB='mongodb://localhost/mongrey_test')
    with shell_env(**kwargs):
        #local('python -m mongrey.migration.core --help')
        local('python -m mongrey.migration.core -n -P C:/temp/postfix.db radicalspam')
"""
