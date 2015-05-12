.. toctree::
    :hidden:

    install
    download
    configuration
    screenshots
    tips
    todolist
    changelog

.. include:: ../../../README_fr.rst

.. blockdiag::

    blockdiag {
      orientation = portrait;
      A [label="BlackList", description = "Black List (ip, sender, recipient, country"];
      B [label="WhiteList"];
      found [label="Found", color="red", shape=flowchart.condition];
      nofound [label="Not Found", color="red", shape=flowchart.condition];
    
      A -> found -> B -> C;
      D -> E [folded];
      A -> nofound -> D
    }
       
Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
* :ref:`modindex`
