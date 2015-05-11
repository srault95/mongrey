# -*- coding: utf-8 -*-

import os
import sys

from setuptools import setup, find_packages

from mongrey.version import __VERSION__

CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def get_readme():
    readme_path = os.path.abspath(os.path.join(CURRENT_DIR, 'README.rst'))
    if os.path.exists(readme_path):
        with open(readme_path) as fp:
            return fp.read()
    return ""

install_requires=[
    'six',
    'cython',
    'gevent>=1.0',
    'psutil',
    'PyYAML',
    'arrow',
    'IPy',
    'python-decouple',
    'geoip-data',
    'pygeoip',
    'regex',
    'werkzeug',   
    'pymongo>=2.8,<3.0',
    'Mongoengine>=0.9',
]
if not sys.platform.startswith("win32"):
    install_requires.append('python-daemon')
    
setup(
    name='mongrey',
    version=__VERSION__,
    description='Greylist Service for Postfix',
    long_description=get_readme(),
    author='Stéphane RAULT',
    author_email='stephane.rault@radicalspam.org',
    url='https://github.com/srault95/mongrey', 
    license='BSD',
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(),
    install_requires=install_requires,
    extras_require = {
        'web': [
            'Flask-BabelEx',
            'Flask-Script',
            'flask-admin',
            'flask-mongoengine',
        ],
        #'mongo': [
        #    'pymongo>=2.8,<3.0',
        #    'Mongoengine>=0.9',
        #    'flask-mongoengine',
        #],
        #'sql': [
        #    'peewee',
        #    'wtf-peewee'
        #],
        #'mysql': [
        #    'peewee',
        #    'wtf-peewee'
        #],
        #'pg': [
        #    'peewee',
        #    'wtf-peewee'
        #],
        'redis': [
            'redis',
        ],
                      
    #    'WEB': [
    #        'Flask-BabelEx',
    #        'Flask-BasicAuth',
    #        'Flask-Script',
    #        'flask-mongoengine',
    #        'flask-admin',
    #    ],
    },      
    dependency_links=[
      'https://github.com/MongoEngine/flask-mongoengine/tarball/master/#egg=flask-mongoengine-0.7.1',
      'https://github.com/srault95/geoip-data/tarball/master/#egg=geoip-data-0.1.1',
    ],      
    tests_require=[
        'nose>=1.0'
        'coverage',
        'flake8'
    ],
    test_suite='nose.collector',      
    entry_points={
        'console_scripts': [
            'mongrey-server = mongrey.server.core:main',
            'mongrey-web = mongrey.web.manager:main',
        ],
    },    
    keywords=['postfix','policy','filter', 'smtp', 'greylist'],
    classifiers=[
        'Topic :: Communications :: Email',
        'Topic :: Communications :: Email :: Filters',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators'
    ],
)
