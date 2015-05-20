==========
Migrations
==========

Radical-Spam
============

Le but de cette migration n'est pas de remplacer RadicalSpam mais seulement la partie Greylisting ainsi que certaines fonctionnalités 
assurés actuellement par Postfix à travers des fichiers plats.

**Données gérés par l'outil de migration:**

- Domaines internet (local-relays)
- Autorisations Mynetwork (local-mynetwork-*)
- Listes Noires (local-blacklist-*)
- Mailbox (local-directory)

Exemple de Migration Radical-Spam avec Mongrey Serveur - Sqlite
===============================================================

.. versionadded:: 0.4.2

Cette opération va récupérer les Domaines, Mynetwork, l'annuaire et toutes les liste noires 
de Radical-Spam et les enregistrer dans Mongrey.

Installation
------------

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-migration > /usr/local/bin/mongrey-migration
    
    $ chmod +x /usr/local/bin/mongrey-migration
    
    $ /usr/local/bin/mongrey-migration --version

Migration
---------

.. code:: bash
    
    # simulation (-n)
    $ /usr/local/bin/mongrey-migration -P /var/rs/addons/postfix/etc -n radicalspam

    # Migration:
    $ /usr/local/bin/mongrey-migration -P /var/rs/addons/postfix/etc radicalspam
    
Postgrey
========

.. todo::

    