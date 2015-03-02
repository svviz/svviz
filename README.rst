*****
svviz
*****

Author: Noah Spies

``svviz`` visualizes high-throughput sequencing data that supports a structural variant. Only reads supporting the variant or the reference allele will be shown. ``svviz`` can operate in both an interactive web browser view to closely inspect individual variants, or in batch, command-line mode, allowing multiple variants (annotated in a VCF file) to be analyzed simultaneously.

See the `documentation <http://svviz.readthedocs.org/>`_ for more detailed help, or run ``svviz -h`` to get help on command line arguments.

Quickstart
==========

1. Ensure that you have a working compiler by following `these instructions <http://railsapps.github.io/xcode-command-line-tools.html>`_ (OS X only) and that the python package `pip <https://pip.pypa.io/en/latest/installing.html>`_ is installed.
2. Install the latest version of svviz from github using the following terminal command: ``sudo pip install -U svviz``. (The sudo may not be necessary depending on your setup.)
3. Run the following command, which downloads example data and runs it through svviz: ``svviz demo``. After several processing steps, a web browser window should open. Click and drag to pan, and zoom using option/alt-scrollwheel.
4. Please report any issues (after making sure they're not explained in the documentation below) using the `github issue tracker <https://github.com/svviz/svviz/issues>`_.
