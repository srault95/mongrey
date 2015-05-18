===========
Intégration
===========

.. note:: Mongrey WEB est livré avec un serveur WSGI `Gevent`_ intégré très performant mais si vous avez besoin 
    d'intégrer l'application dans Nginx ou Apache, vous pouvez suivre les procédures suivantes.

Mongrey Serveur
===============


Mongrey WEB - WSGI
==================

.. todo:: A tester

.. warning::

    Le téléchargement de Mongrey Web au format binaire n'est pas compatible avec cette installation.
    
    Il faut installer Mongrey Web normalement en utilisant la procédure par :ref:`install_pip`
    
Gunicorn
--------

.. code-block:: bash

    $ pip install gunicorn
    
    $ gunicorn -k gevent_wsgi --workers 1 'mongrey.web.wsgi:create_app()'    

Gunicorn - Supervisord
----------------------

::

    [program:mongrey-web]
    command=gunicorn -k gevent_wsgi --workers 1 'mongrey.web.wsgi:create_app()'
    autostart=true
    autorestart=true
    redirect_stderr=True
    stdout_logfile=/var/log/supervisor/%(program_name)s.log
    stderr_logfile=/var/log/supervisor/%(program_name)s.log
        
Chaussette
----------

.. todo::


Upstart
=======

http://upstart.ubuntu.com/

.. todo::    

Systemd
=======

http://freedesktop.org/wiki/Software/systemd/

.. todo::    


.. _`Gevent`: http://www.gevent.org/