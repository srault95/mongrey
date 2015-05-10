.. _install:

**********************
Mongrey - Installation
**********************

Introduction
************

Vous avez le choix entre plusieurs méthodes d'installation.

Le plus simple étant la version binaire adaptée au backend que vous utiliserez (MongoDB, PostgreSQL, ...)

Les binaires sont des versions préparés à l'aide de l'outil pyInstaller et n'ont aucune dépendances externes.

**Ces versions ont été testés avec :**

- Ubuntu 14.04 (Trusty) 64 bits 
- CentOS 7 64 bits

Mongrey Serveur
***************

Version binaire
===============

MongoDB
-------

.. code:: bash

    $ curl -L http://mongrey.radical-software.fr/download/mongrey-server-mongo-`uname -s`-`uname -m`-latest > /usr/local/bin/mongrey-server-mongo
    
    $ chmod +x /usr/local/bin/mongrey-server-mongo
    
    $ /usr/local/bin/mongrey-server-mongo --version    

.. _`install_mongrey_server_postgresql`:

PostgreSQL
----------

.. code:: bash

    $ curl -L http://mongrey.radical-software.fr/download/mongrey-server-postgresql-`uname -s`-`uname -m`-latest > /usr/local/bin/mongrey-server-postgresql
    
    $ chmod +x /usr/local/bin/mongrey-server-postgresql
    
    $ /usr/local/bin/mongrey-server-postgresql --version    

Docker - Build personnalisé
***************************

Exemple avec la version binaire de Mongrey Server PostgreSQL

::

    # Dockerfile
    
    FROM ubuntu:14.04
    
    RUN apt-get update -y

    RUN DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
        ca-certificates git curl language-pack-en
    
    RUN curl -L http://mongrey.radical-software.fr/download/mongrey-server-postgresql-`uname -s`-`uname -m`-latest > /usr/local/bin/mongrey-server-postgresql
    
    RUN chmod +x /usr/local/bin/mongrey-server-postgresql
    
    CMD /usr/local/bin/mongrey-server-postgresql start    

.. code:: bash
    
    # Build du contenair
    $ docker build -t mongrey-server-postgresql .
        


Docker - PostgreSQL
*******************

Commencer par installer la version binaire de mongrey pour PostgreSQL :ref:`install_mongrey_server_postgresql`

.. code:: bash

    $ docker pull postgres

    # Lancement du server
    $ docker run --name pgsql1 -e POSTGRES_PASSWORD=secret -d postgres
    
    # Création de la DB
    $ docker exec -it pgsql1 sh -c 'exec psql -c "create database mongrey_test2;" -U postgres'

    # Lancement de mongrey
    $ docker run -it --rm --link pgsql1:pgsql -e MONGREY_STORAGE=sql -e MONGREY_DB=postgresql://postgres:secret@pgsql/mongrey_test -e MONGREY_HOST=0.0.0.0 -e MONGREY_PORT=9999 -p 127.0.0.1:9997:9999 -v /usr/local/bin/mongrey-server-postgresql:/usr/local/bin/mongrey-server-postgresql ubuntu:14.04 /usr/local/bin/mongrey-server-postgresql start
    
Docker - MySQL
**************

.. code:: bash

    $ docker pull mysql

    # Lancement du server
    $ docker run --name mysql1 -e MYSQL_ROOT_PASSWORD=secret -d mysql
    
    # Création de la DB
    $ docker exec -it mysql1 sh -c 'exec mysql -e "create database mongrey_test;" -uroot -p"secret"'    
    
    # Lancement de mongrey
    $ docker run -it --rm --link mysql1:mysql -e MONGREY_STORAGE=sql -e MONGREY_DB=mysql://root:secret@mysql/mongrey_test -e MONGREY_HOST=0.0.0.0 -e MONGREY_PORT=9999 -p 127.0.0.1:9997:9999 -v `pwd`/dist:/dist ubuntu:14.04 /dist/mongrey-server-mysql-Linux-x86_64 start


Mongrey Web
***********

Version binaire
===============

MongoDB
-------

.. code:: bash

    $ curl -L http://mongrey.radical-software.fr/download/mongrey-web-mongo-`uname -s`-`uname -m`-latest > /usr/local/bin/mongrey-web-mongo
    
    $ chmod +x /usr/local/bin/mongrey-web-mongo
    
    $ /usr/local/bin/mongrey-web-mongo --help    

pip installation
****************

**Requis :**

- Linux récent (Ubuntu 14+, CentOS+)
- Librairie de compilation
- Python 2.7+ (python 3 non supporté pour l'instant)
- Python Setuptools/Pip
- Librairies optionnelles selon le backend (mysql, postgresql, ...)

.. code:: bash

    $ pip install mongrey
    
    # option cache redis
    $ pip install mongrey['redis']
    
    $ mongrey-server --help
    
    $ mongrey-web --help
    
Mongrey - Intégration
*********************

Gunicorn (Mongrey WEB seulement)
================================

Supervisor
==========

Systemd
=======
    

