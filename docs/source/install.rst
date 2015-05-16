.. _install:

======================
Mongrey - Installation
======================

Introduction
============

Vous avez le choix entre plusieurs méthodes d'installation. 

La plus simple étant la version :term:`binaire` adaptée au backend que vous utiliserez (MongoDB, PostgreSQL, ...).

Les binaires sont des versions compilés à l'aide de l'outil PyInstaller et n'ont aucunes dépendances externes.

**Tous ces binaires ont été testés avec :**

- Ubuntu 14.04 (Trusty) - 64 bits 
- CentOS 7 - 64 bits
- Python 2.7.6

Le processus de génération des binaires est visible sur `Mongrey Build: <https://github.com/radical-software/mongrey-build>`_

Exemples
========

Version en cours: |release|

*Remplacez [RELEASE] et [BACKEND] par la version et le backend souhaité.*

- http://download.mongrey.io/[RELEASE]/mongrey-server-[BACKEND]-Linux-x86_64

*Pour la version la plus récente avec un backend MongoDB, utilisez latest:*

- http://download.mongrey.io/latest/mongrey-server-mongo-Linux-x86_64

Mongrey Serveur
===============

.. _`install_mongrey_server_mongodb`:

MongoDB
-------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-mongo-`uname -s`-`uname -m` > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version    

.. _`install_mongrey_server_postgresql`:

PostgreSQL
----------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-postgresql-`uname -s`-`uname -m` > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version    

.. _`install_mongrey_server_mysql`:

MySQL
-----

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-mysql-`uname -s`-`uname -m` > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version    

Docker
======

Docker - Build
--------------

Exemple avec la version binaire de Mongrey Server PostgreSQL:

::

    # Dockerfile
    
    FROM ubuntu:14.04
    
    RUN apt-get update -y

    RUN DEBIAN_FRONTEND=noninteractive \
        apt-get install -y --no-install-recommends \
        ca-certificates git curl language-pack-en
    
    RUN curl -L http://download.mongrey.io/latest/mongrey-server-postgresql-`uname -s`-`uname -m` > /usr/local/bin/mongrey-server
    
    RUN chmod +x /usr/local/bin/mongrey-server
    
    CMD /usr/local/bin/mongrey-server start    


.. code:: bash
    
    # Build du contenair
    
    $ docker build -t mongrey-server-postgresql .

Docker - PostgreSQL
-------------------

Installez la version binaire de mongrey pour :ref:`install_mongrey_server_postgresql`

.. code:: bash

    $ docker pull postgres

    # Lancement du server
    $ docker run --name pgsql1 -e POSTGRES_PASSWORD=secret -d postgres
    
    # Création de la DB
    $ docker exec -it pgsql1 sh -c 'exec psql -c "create database mongrey_test2;" -U postgres'

    # Lancement de mongrey
    $ docker run -it --rm --link pgsql1:pgsql \
       -e MONGREY_STORAGE=sql \
       -e MONGREY_DB=postgresql://postgres:secret@pgsql/mongrey_test \
       -e MONGREY_HOST=0.0.0.0 \
       -e MONGREY_PORT=9999 \
       -p 127.0.0.1:9997:9999 \
       -v /usr/local/bin/mongrey-server:/usr/local/bin/mongrey-server \
       ubuntu:14.04 /usr/local/bin/mongrey-server start
    
Docker - MySQL
--------------

Installez la version binaire de mongrey pour :ref:`install_mongrey_server_mysql`

.. code:: bash

    $ docker pull mysql

    # Lancement du server
    $ docker run --name mysql1 -e MYSQL_ROOT_PASSWORD=secret -d mysql
    
    # Création de la DB
    $ docker exec -it mysql1 sh -c 'exec mysql -e "create database mongrey_test;" -uroot -p"secret"'    
    
    # Lancement de mongrey
    $ docker run -it --rm --link mysql1:mysql \
       -e MONGREY_STORAGE=sql \
       -e MONGREY_DB=mysql://root:secret@mysql/mongrey_test \
       -e MONGREY_HOST=0.0.0.0 \
       -e MONGREY_PORT=9999 \
       -p 127.0.0.1:9997:9999 \
       -v /usr/local/bin/mongrey-server:/usr/local/bin/mongrey-server \
       ubuntu:14.04 /usr/local/bin/mongrey-server start

Mongrey Web
===========

MongoDB
-------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-web-mongo-`uname -s`-`uname -m` > /usr/local/bin/mongrey-web
    
    $ chmod +x /usr/local/bin/mongrey-web
    
    $ /usr/local/bin/mongrey-web --help

    $ /usr/local/bin/mongrey-web server -p 8081 -h 127.0.0.1
    
    # Ouvrez le navigateur à l'adresse http://127.0.0.1:8081

PostgreSQL
----------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-web-postgresql-`uname -s`-`uname -m` > /usr/local/bin/mongrey-web
    
    $ chmod +x /usr/local/bin/mongrey-web
    
    $ /usr/local/bin/mongrey-web --help    

.. _install_pip:

Installation par PIP
====================

**Requis :**

- Linux récent (Ubuntu 14+, CentOS+)
- Librairie de compilation
- Python 2.7+ (python 3 non supporté pour l'instant)
- Python Setuptools/Pip
- Librairies optionnelles selon le backend (mysql, postgresql, ...)

.. code:: bash

    # Serveur et Web - Tous les backend 
    $ pip install mongrey[full]

    # Serveur - Backend MongoDB 
    $ pip install mongrey[server_mongodb]

    # Serveur - Tous les backend 
    $ pip install mongrey[server]
    
    $ mongrey-server --help
    
    $ mongrey-web --help

APT
===

.. todo::    

RPM
===

.. todo::