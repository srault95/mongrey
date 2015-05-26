.. _configuration:

=====================
Mongrey Configuration
=====================

Mongrey Serveur
===============

Configuration par défaut
------------------------

Par défaut, Mongrey Serveur utilise les variables d'environnements mais vous pouvez aussi charger la configuration à partir d'un fichier YAML.

La commande **mongrey-server install** crééer un fichier YAML avec la configuration par défaut.

A chaque chargement, Mongrey Serveur, cherche un fichier de configuration facultatif:

.. note::

    * Ordre de recherche:
        * Valeur de l'option mongrey-server --settings myfile.yml
        * Valeur de la variable d'environnement MONGREY_SERVER_SETTINGS
        * /etc/mongrey/server.yml
        * ~/mongrey/server.yml
    
.. note::

    Le fichier YAML n'a pas besoin d'être rempli complètement
    
    Après son chargement, les valeurs sont concaténés avec la configuration par défaut (variables d'environnements)

Postfix intégration
===================

- Voir `Postfix_Policy`_ pour plus de détail

::

    #/etc/postfix/main.cf:
    
    smtpd_recipient_restrictions =
             ... 
             reject_unauth_destination 
             check_policy_service inet:127.0.0.1:9999


Politique de liste grise
========================

.. todo::

Liste Blanches
==============

.. todo:: 

    Liste Blanches

Géo-localisation
================

.. todo::

Greylisting
===========

.. todo::

.. _`Postfix_Policy`: http://www.postfix.org/SMTPD_POLICY_README.html
