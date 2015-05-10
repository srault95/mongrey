***************************
Greylist Server for Postfix
***************************

|Build Status| |Coverage Status| |pypi downloads| |pypi version| |pypi licence| |pypi wheel| |requires status|

Fonctionnalités
***************

- Greylist Server high performance
- Backends: MongoDB, PostgreSQL, MySQL, Sqlite
- Configuration by ip address & cidr, sender, recipient, ... (and by regex)
- WebUI (optional)
- White and Black lists
- REST Api (todo...)

`Version Française <https://github.com/srault95/mongrey/blob/master/README_fr.rst>`_ 

Installation
************

::

    pip install mongrey
    
    docker run -e MONGREY_WEB_PORT=8082 -e MONGREY_DB=mongodb://172.17.0.2/greylist -it --rm srault95/mongrey
    ou    
    docker run --link mongodb1:mongodb -e MONGREY_WEB_PORT=8082 -e MONGREY_DB=mongodb://mongodb/greylist -it --rm srault95/mongrey



Contributing
************

To contribute to the project, fork it on GitHub and send a pull request, all contributions and suggestions are welcome.

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

     