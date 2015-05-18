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

Postgrey
========

.. todo::


Exemple de Migration Radical-Spam avec Mongrey Serveur - Sqlite
===============================================================

.. versionadded:: 0.4.2

.. code:: bash

    $ curl -L http://download.mongrey.io/latest/mongrey-migration > /usr/local/bin/mongrey-migration
    
    $ chmod +x /usr/local/bin/mongrey-migration
    
    $ /usr/local/bin/mongrey-migration --version
    
