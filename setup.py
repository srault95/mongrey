# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

from mongrey.version import __VERSION__
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))

def pip(filename):
    requirements_path = os.path.abspath(os.path.join(CURRENT_DIR, 'requirements'))
    filepath = os.path.abspath(os.path.join(requirements_path, filename))
    
    requirements=[]    
    for line in open(filepath, 'rb').readlines():
        _line = line.strip()
        if not _line or _line[0] in ['#']: continue
        _line = line.strip()
        include = _line.split('-r ')
        if len(include) == 2:
            filename = include[1]
            requirements.extend(pip(filename))
        else:
            if '#egg=' in _line:
                requirements.append(_line.split("egg=")[1])
            else:
                requirements.append(include[0])
    return requirements


server_mongo_req = pip('server-mongo.txt')
server_mysql_req = pip('server-mysql.txt')
server_postgresql_req = pip('server-postgresql.txt')
server_sqlite_req = pip('server-sqlite.txt')
server_req = server_mongo_req + server_mysql_req + server_postgresql_req + server_sqlite_req

web_mongo_req = pip('web-mongo.txt')
web_mysql_req = pip('web-mysql.txt')
web_postgresql_req = pip('web-postgresql.txt')
web_sqlite_req = pip('web-sqlite.txt')
web_req = web_mongo_req + web_mysql_req + web_postgresql_req + web_sqlite_req

mongrey_full = set(server_req + web_req)

def get_readme():
    readme_path = os.path.abspath(os.path.join(CURRENT_DIR, 'README.rst'))
    if os.path.exists(readme_path):
        with open(readme_path) as fp:
            return fp.read()
    return ""

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
    install_requires=[],
    extras_require = {
        'server_mongo': set(server_mongo_req),
        'server_mysql': set(server_mysql_req),
        'server_postgresql': set(server_postgresql_req),
        'server_sqlite': set(server_sqlite_req),
        'web_mongo': set(web_mongo_req),
        'web_mysql': set(web_mysql_req),
        'web_postgresql': set(web_postgresql_req),
        'web_sqlite': set(web_sqlite_req),
        'server': set(server_req),
        'web': set(web_req),
        'full': set(server_req+web_req)
    },      
    tests_require=[
        'nose>=1.0'
        'coverage',
        'flake8'
    ],
    test_suite='nose.collector',      
    entry_points={
        'console_scripts': [
            'mongrey-server = mongrey.server.core:main [server_mongo, server_mysql, server_postgresql, server_sqlite, server, full]',
            'mongrey-web = mongrey.web.manager:main [web_mongo, web_mysql, web_postgresql, web_sqlite, web, full]',
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
