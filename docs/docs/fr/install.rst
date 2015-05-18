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
- Debian 8 (jessie) - 64 bits
- CentOS 7 - 64 bits
- Fedora 20 - 64 bits
- OpenSuse 13.1 (bottle)
- Python 2.7.6

Le processus de génération des binaires est visible sur `Mongrey Build: <https://github.com/radical-software/mongrey-build>`_

Exemples
========

Version en cours: |release|

*Remplacez [RELEASE] et [BACKEND] par la version et le backend souhaité.*

- http://download.mongrey.io/[RELEASE]/mongrey-server-[BACKEND]

*Pour la version la plus récente avec un backend MongoDB, utilisez latest:*

- http://download.mongrey.io/latest/mongrey-server-mongo

Mongrey Serveur
===============

.. _`install_mongrey_server_sqlite`:

Sqlite (par défaut)
-------------------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-sqlite > /usr/local/bin/mongrey-server

    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version
    
**Le plus simple pour la configuration initiale:**
    
.. code:: bash
    
    $ export MONGREY_SERVER_SETTINGS=/etc/mongrey/server.yml
    $ export MONGREY_DB=sqlite:////var/lib/mongrey/mongrey.db

    $ mkdir -vp /var/lib/mongrey
    
    $ /usr/local/bin/mongrey-server config-install
    
*Editez si nécessaire le fichier /etc/mongrey/server.yml*

**Affichez la configuration en cours:**

.. code:: bash
    
    $ /usr/local/bin/mongrey-server config
    
**Configurez Postfix:**

.. note::

    Ajoutez warn_if_reject, devant le check_policy_service pour evaluez Mongrey sans risque.
    
    Si Mongrey renvoi une action de rejet pour un mail, il sera transformé en simple warning dans les logs.

    Le contenu et l'ordre des entrées dans smtpd_recipient_restrictions dépend de votre installation. 
    L'example ci-après n'est qu'une des nombreuses possibilités de Postfix.

.. code:: bash

    $ vi /etc/postfix/main.cf

    smtpd_recipient_restrictions = reject_unauth_destination, warn_if_reject, check_policy_service inet:127.0.0.1:9999
    
    $ postfix reload

**Ou en mode commande:**

.. code:: bash

    $ postconf -e 'smtpd_recipient_restrictions = reject_unauth_destination, warn_if_reject, check_policy_service inet:127.0.0.1:9999'

    $ postfix reload
    
**Démarrez Mongrey:**

.. code:: bash

    $ /usr/local/bin/mongrey-server start
    
**Pour un démarrage en mode background:**

.. code:: bash

    $ /usr/local/bin/mongrey-server --pid /var/run/mongrey-server.pid start &
    
**Pour arrêter Mongrey:**
    
.. code:: bash

    $ kill -TERM `cat /var/run/mongrey-server.pid`


.. _`install_mongrey_server_mongodb`:

MongoDB
-------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-mongo > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version    

.. _`install_mongrey_server_postgresql`:

PostgreSQL
----------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-postgresql > /usr/local/bin/mongrey-server
    
    $ chmod +x /usr/local/bin/mongrey-server
    
    $ /usr/local/bin/mongrey-server --version    

.. _`install_mongrey_server_mysql`:

MySQL
-----

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-server-mysql > /usr/local/bin/mongrey-server
    
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
    
    RUN curl -L http://download.mongrey.io/latest/mongrey-server-postgresql > /usr/local/bin/mongrey-server
    
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

    $ curl -L http://download.mongrey.io/latest/mongrey-web-mongo > /usr/local/bin/mongrey-web
    
    $ chmod +x /usr/local/bin/mongrey-web
    
    $ /usr/local/bin/mongrey-web --help

    $ /usr/local/bin/mongrey-web server -p 8081 -h 127.0.0.1
    
    # Ouvrez le navigateur à l'adresse http://127.0.0.1:8081

PostgreSQL
----------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-web-postgresql > /usr/local/bin/mongrey-web
    
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