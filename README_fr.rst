***********************************
Serveur de liste grise pour Postfix
***********************************

|Build Status| |Coverage Status| |health| |docs| |pypi downloads| |pypi version| |pypi licence| |pypi wheel| |requires status|

Fonctionnalités
***************

- Serveur de liste grise haute performance
- Backends: MongoDB, PostgreSQL, MySQL, Sqlite
- Configuration par adresse ip & cidr, expéditeur, destinataire, ... (+expression régulières)
- Listes blanches & noires
- Contrôles anti-relais, anti-spoofing
- Application Web (facultative)
- Api REST (en cours de développement)
- Cache en Mémoire ou avec Redis

Documentations
**************

- `Français <http://mongrey.readthedocs.org/fr/latest/>`_
- `Anglais <http://mongrey.readthedocs.org/en/latest/>`_

Contribution
************

Pour contribuer à ce projet, créer un fork et dans la mesure du possible, effectuer les modifications dans une nouvelle branche puis envoyez un "pull request". 

Toutes les contributions et suggestions sont les bienvenues. 

.. _MongoDB: http://mongodb.org/
.. _Docker: https://www.docker.com/
.. _Ubuntu: http://www.ubuntu.com/
.. _Dockerfile: http://dockerfile.github.io/#/mongodb
.. _Python: http://www.python.org/
.. _Gevent: http://www.gevent.org/
.. _Postfix: http://www.postfix.org
.. _Postfix_Policy: http://www.postfix.org/SMTPD_POLICY_README.html
.. _Coroutine: http://en.wikipedia.org/wiki/Coroutine
 
.. |Build Status| image:: https://travis-ci.org/srault95/mongrey.svg?branch=master
   :target: https://travis-ci.org/srault95/mongrey
   :alt: Travis Build Status
   
.. |Coverage Status| image:: https://coveralls.io/repos/srault95/mongrey/badge.svg 
   :target: https://coveralls.io/r/srault95/mongrey   

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

.. |requires status| image:: https://requires.io/github/srault95/mongrey/requirements.svg?branch=master
     :target: https://requires.io/github/srault95/mongrey/requirements/?branch=master
     :alt: Requirements Status

.. |docs| image:: https://readthedocs.org/projects/mongrey/badge/?version=latest
    :target: https://readthedocs.org/projects/mongrey/?badge=latest
    :alt: Documentation Status          
    
.. |health| image:: https://landscape.io/github/srault95/mongrey/master/landscape.svg?style=flat
   :target: https://landscape.io/github/srault95/mongrey/master
   :alt: Code Health
       