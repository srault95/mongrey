Serveur de liste grise pour Postfix
===================================

|Build Status| |Coverage Status| |pypi downloads| |pypi version| |pypi licence| |requires status|

**Fonctionnalités:**

- Serveur de liste grise haute performance
- Configuration par ip/cidr/sender/recipient/hostname en fixe ou par expression régulières
- Backends: MongoDB, PostgreSQL, MySQL, Sqlite
- Listes blanches & noires
- Application Web (optionnel)

Contribution
============

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

.. |requires status| image:: https://requires.io/github/srault95/mongrey/requirements.svg?branch=master
     :target: https://requires.io/github/srault95/mongrey/requirements/?branch=master
     :alt: Requirements Status
