Mongo Greylist Server
=====================

**Greylist Server for Postfix with MongoDB storage** 

|Build Status| |pypi downloads| |pypi version| |pypi licence| |requires status|

**Features:**

- Greylist Server high performance
- MongoDB_ storage
- WebUI (optional)

Installation
------------

::

    pip install mongo-greylist
    
    docker run -e MONGO_GREYLIST_WEB_PORT=8082 -e MONGODB_URI=mongodb://172.17.0.2/greylist -it --rm srault95/mongo-greylist
    ou    
    docker run --link mongodb1:mongodb -e MONGO_GREYLIST_WEB_PORT=8082 -e MONGODB_URI=mongodb://mongodb/greylist -it --rm srault95/mongo-greylist

Postfix Configuration
---------------------

- See Postfix_Policy_ for details

::

    #/etc/postfix/main.cf:
    
    smtpd_recipient_restrictions =
             ... 
             reject_unauth_destination 
             check_policy_service inet:127.0.0.1:9999
             
             
Contributing
============

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
 
.. |Build Status| image:: https://travis-ci.org/srault95/mongo-greylist.svg?branch=master
   :target: https://travis-ci.org/srault95/mongo-greylist
   :alt: Travis Build Status

.. |pypi downloads| image:: https://img.shields.io/pypi/dm/mongo-greylist.svg
    :target: https://pypi.python.org/pypi/mongo-greylist
    :alt: Number of PyPI downloads
    
.. |pypi version| image:: https://img.shields.io/pypi/v/mongo-greylist.svg
    :target: https://pypi.python.org/pypi/mongo-greylist
    :alt: Latest Version

.. |pypi licence| image:: https://img.shields.io/pypi/l/mongo-greylist.svg
    :target: https://pypi.python.org/pypi/mongo-greylist
    :alt: License

.. |requires status| image:: https://requires.io/github/radical-software/mongo-greylist/requirements.svg?branch=master
     :target: https://requires.io/github/radical-software/mongo-greylist/requirements/?branch=master
     :alt: Requirements Status                 