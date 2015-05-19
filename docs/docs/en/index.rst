===========================
Greylist Server for Postfix
===========================

|Build Status| |health| |docs| |translation| |pypi downloads| |pypi version| |pypi licence| |pypi wheel| |requires status|

Resume
======

:Version: |release|
:Author: :email:`Stephane RAULT <stephane.rault@radical-software.fr>`
:Last updated: |today|
:License: BSD
:Code: https://github.com/radical-software/mongrey
:Issues: https://github.com/radical-software/mongrey/issues
:Doc EN: http://mongrey.readthedocs.org/en/latest/
:Doc FR: http://mongrey.readthedocs.org/fr/latest/

Features
========

- Greylist Server high performance
- Backends: MongoDB, PostgreSQL, MySQL, Sqlite
- No software dependencies (except Backend);
- Configuration by Country, IP address, Network address, Email, Domain, Regex
    - For every policy filter
    - For black and white lists
- Optional filters:     
    - Relay deny control
    - Spoofing
    - Directory control DB, (SMTP, LDAP en cours..)
    - RBL
    - SPF
- WebUI (optional)
- REST API (in progress...)
- Cache with Memory or Redis

Installation sample - Mongrey Serveur - Backend Sqlite
======================================================

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-sqlite > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version

OS Compatibility - 64 bits (only)
=================================

- Ubuntu 14.04 (Trusty) 
- Debian 8 (jessie)
- CentOS 7
- Fedora 20
- OpenSuse 13.1 (bottle)

Table of Contents
=================

.. toctree::
    :maxdepth: 1

    download
    install
    integration
    configuration
    security
    migration
    screenshots
    tips
    errors
    otherprojects
    references
    glossary
    todo

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. _MongoDB: http://mongodb.org/
.. _Docker: https://www.docker.com/
.. _Ubuntu: http://www.ubuntu.com/
.. _Dockerfile: http://dockerfile.github.io/#/mongodb
.. _Python: http://www.python.org/
.. _Gevent: http://www.gevent.org/
.. _Postfix: http://www.postfix.org
.. _Postfix_Policy: http://www.postfix.org/SMTPD_POLICY_README.html
.. _Coroutine: http://en.wikipedia.org/wiki/Coroutine
 
.. |Build Status| image:: https://travis-ci.org/radical-software/mongrey.svg?branch=master
   :target: https://travis-ci.org/radical-software/mongrey
   :alt: Travis Build Status
   
.. |pypi downloads| image:: https://img.shields.io/pypi/dm/mongrey.svg
    :target: https://pypi.python.org/pypi/mongrey
    :alt: Number of PyPI downloads
    
.. |pypi version| image:: https://img.shields.io/pypi/v/mongrey.svg
    :target: https://pypi.python.org/pypi/mongrey
    :alt: Latest Version

.. |pypi licence| image:: https://img.shields.io/pypi/l/mongrey.svg
    :target: https://pypi.python.org/pypi/mongrey
    :alt: License

.. |pypi wheel| image:: https://pypip.in/wheel/mongrey/badge.png
    :target: https://pypi.python.org/pypi/mongrey/
    :alt: Python Wheel
        
.. |requires status| image:: https://requires.io/github/radical-software/mongrey/requirements.svg?branch=master
     :target: https://requires.io/github/radical-software/mongrey/requirements/?branch=master
     :alt: Requirements Status

.. |docs| image:: https://readthedocs.org/projects/mongrey-en/badge/?version=latest
    :target: http://mongrey.readthedocs.org/en/latest/
    :alt: Documentation Status     
    
.. |health| image:: https://landscape.io/github/radical-software/mongrey/master/landscape.svg?style=flat
   :target: https://landscape.io/github/radical-software/mongrey/master
   :alt: Code Health

.. |translation| image:: https://d322cqt584bo4o.cloudfront.net/mongrey/localized.png
   :target: https://crowdin.com/project/mongrey
   :alt: Translation

   