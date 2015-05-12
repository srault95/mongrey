.. _configuration:

*********************
Mongrey Configuration
*********************

Postfix intégration
*******************

- Voir `Postfix_Policy`_ pour plus de détail

::

    #/etc/postfix/main.cf:
    
    smtpd_recipient_restrictions =
             ... 
             reject_unauth_destination 
             check_policy_service inet:127.0.0.1:9999


Politique de liste grise
************************

.. todo::

Liste Blanches
**************

.. todo:: 

    Liste Blanches

Géo-localisation
****************

.. todo::

Greylisting
***********

.. todo::

.. _`Postfix_Policy`: http://www.postfix.org/SMTPD_POLICY_README.html
