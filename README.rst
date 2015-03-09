*****
svviz
*****

Author: Noah Spies

``svviz`` visualizes high-throughput sequencing data relevant to a structural variant. Only reads supporting the variant or the reference allele will be shown. ``svviz`` can operate in both an interactive web browser view to closely inspect individual variants, or in batch mode, allowing multiple variants (annotated in a VCF file) to be analyzed simultaneously.

See the `documentation <http://svviz.readthedocs.org/>`_ for more detailed help, or run ``svviz -h`` to get help on command line arguments.

Quickstart
==========

1. Ensure that you have a working compiler by following `these instructions <http://railsapps.github.io/xcode-command-line-tools.html>`_ (OS X only) and that the python package `pip <https://pip.pypa.io/en/latest/installing.html>`_ is installed.
2. Install the latest version of svviz from github using the following terminal command: ``sudo pip install -U svviz``. (The sudo may not be necessary depending on your setup.)
3. Run the following command, which downloads example data and runs it through svviz: ``svviz demo``. After several processing steps, a web browser window should open, with separate, interactive views of the reference and alternate alleles.
4. Please report any issues using the `github issue tracker <https://github.com/svviz/svviz/issues>`_.

Manuscript
----------

A preprint manuscript describing svviz is `available on bioRxiv <http://dx.doi.org/10.1101/016063>`_:

Spies N, Zook JM, Salit M, Sidow A. svviz: a read viewer for validating structural variants. bioRxiv doi:10.1101/016063.