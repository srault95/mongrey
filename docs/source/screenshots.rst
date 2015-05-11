.. _screenshots:

Copies d'Ecran
==============

.. blockdiag::

   {
     A -> B;
   }

.. blockdiag::
   :desctable:

   blockdiag {
      A -> B -> C;
      A [description = "browsers in each client"];
      B [description = "web server"];
      C [description = "database server"];
   }