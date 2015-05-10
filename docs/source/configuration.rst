.. _configuration:

*********************
Mongrey Configuration
*********************

Postfix intégration
*******************

- See Postfix_Policy_ for details

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
