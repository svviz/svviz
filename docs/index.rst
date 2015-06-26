:tocdepth: 2

=================================================
svviz - a read visualizer for structural variants
=================================================


.. toctree::
   :maxdepth: 1

   self
   intro
   features
   install
   webinterface
   commandline
   faqs
   changelog
   license


``svviz`` visualizes high-throughput sequencing data that supports a structural variant. ``svviz`` is free and open source, available at `<https://github.com/svviz/svviz>`_. Please report any issues using the `github issue tracker <https://github.com/svviz/svviz/issues>`_.

Visit the `project page <http://svviz.github.io/svviz/>`_ for a visual tour of the features, or continue through this documentation for more detailed information about svviz.

.. image:: example.png
    :width: 95%
    :align: center

|
|


News
----

**May, 2015 -- Translocations** Support for translocations has been implemented. This is a somewhat experimental feature, so please submit any bug reports or suggestions using the `github issue tracker <https://github.com/svviz/svviz/issues>`_. 

The under-the-hood changes required to implement translocation support make it far simpler to implement arbitrary break-end type structural variants. Work on this is ongoing.

Quick-start
-----------

1. Install the latest version of svviz from github: ``sudo pip install svviz``
2. Run the following command: ``svviz demo``

Detailed instructions, including how to ensure that all prerequisites are installed, are available on the :ref:`installation` page.

Citation
--------

A preprint manuscript describing svviz is `available on bioRxiv <http://dx.doi.org/10.1101/016063>`_:

Spies N, Zook JM, Salit M, Sidow A. svviz: a read viewer for validating structural variants. bioRxiv doi:10.1101/016063.

svviz was developed by `Noah Spies <http://stanford.edu/~nspies/>`_, a member of the `Sidow lab <http://mendel.stanford.edu/SidowLab/index.html>`_ at Stanford and part of the `Joint Initiative for Metrology in Biology (JIMB) <http://jimb.stanford.edu/>`_. Funding was provided by the `National Institute of Standards and Technology (NIST) <http://www.nist.gov>`_.