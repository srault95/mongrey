===================================
Serveur de GreyListing pour Postfix
===================================

|Build Status| |health| |docs| |translation| |pypi downloads| |pypi version| |pypi licence| |pypi wheel| |requires status|

Résumé
======
   
:Version: |release|
:Author: :email:`Stephane RAULT <stephane.rault@radical-software.fr>`
:Mise à jour: |today|
:Licence: BSD
:Code: https://github.com/radical-software/mongrey
:Tickets: https://github.com/radical-software/mongrey/issues
:Doc EN: http://mongrey.readthedocs.org/en/latest/
:Doc FR: http://mongrey.readthedocs.org/fr/latest/
:Builder: https://github.com/radical-software/mongrey-build

Fonctionnalités
===============

- Serveur de liste grise haute performance
- Backends: MongoDB, PostgreSQL, MySQL, Sqlite
- Pas de dépendance (en dehors du backend)
- Configuration par Pays, IP, Network, Email, Domain, Expression régulière:
    - Pour chaque politique de filtrage
    - Pour les listes noires et blanches
- Filtrages facultatifs:     
    - Contrôles anti-relais
    - Anti-spoofing
    - Contrôle d'annuaire DB, (SMTP, LDAP en cours..)
    - RBL
    - SPF
- Application Web (facultative)
- Api REST (en cours...)
- Cache RAM ou Redis    

Exemple d'installation avec la version Serveur - Backend Sqlite
===============================================================

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-sqlite > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version

Compatibilité OS - 64 bits (seulement)
======================================

- Ubuntu 14.04 (Trusty) 
- Debian 8 (jessie)
- CentOS 7
- Fedora 20
- OpenSuse 13.1 (bottle)

Table des matières
==================

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

Contribution
============

Pour contribuer à ce projet, créez un fork et dans la mesure du possible, effectuez les modifications dans une nouvelle branche puis envoyez un "pull request". 

Toutes les contributions et suggestions sont les bienvenues.

Index - Recherche
=================

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

.. |docs| image:: https://readthedocs.org/projects/mongrey/badge/?version=latest
    :target: http://mongrey.readthedocs.org/fr/latest/
    :alt: Documentation Status          
    
.. |health| image:: https://landscape.io/github/radical-software/mongrey/master/landscape.svg?style=flat
   :target: https://landscape.io/github/radical-software/mongrey/master
   :alt: Code Health

.. |translation| image:: https://d322cqt584bo4o.cloudfront.net/mongrey/localized.png
   :target: https://crowdin.com/project/mongrey
   :alt: Translation

