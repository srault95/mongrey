********
Sécurité
********

Mongrey Serveur - IP Autorisés
******************************

**Défaut**: 127.0.0.1, ::1

Par défaut, Mongrey Serveur n'accepte des connections qu'en provenance de l'ip loopback (127.0.0.1, ::1)

Toutes autres connection est rejetés et une entrée de log permet à un outil comme `Fail2ban`_ d'agir dynamiquement sur le firewall.

Si `Fail2ban`_ est activé et correctement paramètré, les prochaines tentatives seront arrêtés par le firewall. 

Mongrey Web - IP Autorisés
**************************

**Défaut**: Toutes

Si vous utilisez le serveur WSGI intégré à Mongrey Web, vous pouvez activer la même protection par IP que Mongrey Serveur.


Fail2ban et iptables
********************

`Fail2ban`_ est un outil Python qui à partir de règles et des logs, permet de créer dynamiquement des règles de bloquage dans le firewall.

C'est l'outil idéal pour combattre les attaques par force brute.


.. _`Fail2ban`: <http://www.fail2ban.org/wiki/index.php/Main_Page>