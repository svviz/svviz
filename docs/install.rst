Installation
============

A single command should typically suffice to install ``svviz``:

``sudo pip install svviz``

More detailed directions follow for linux and OS X. Try installing into a :ref:`virtual environment (see below) <venv>` if you have difficulty with any of these directions.

Installation on linux
---------------------

1. Ensure that the following prerequisites are installed: python and pip. If you are running ubuntu or similar, you can use the following commands to ensure they are installed correctly:

    .. code-block:: bash

        sudo apt-get install python-dev
        sudo apt-get install python-pip

2. Use pip to install svviz:

    .. code-block:: bash

        sudo pip install svviz

    This should automatically install a number of required python packages (see :ref:`below <required_python_packages>`). If you prefer to install the latest development version from github, install git and then use this command instead (warning: bleeding edge! may contain bugs!):

    .. code-block:: bash

        sudo pip install -U git+git://github.com/svviz/svviz.git

3. To enable PDF export, you will need to install the `libRsvg <https://wiki.gnome.org/action/show/Projects/LibRsvg>`_ package:

    .. code-block:: bash

        sudo apt-get install librsvg2-dev

See the :ref:`troubleshooting` section if you have difficulties after following the above directions.


Installation on Mac OS X
------------------------

1. Ensure that you have a working compiler by following `these instructions <http://railsapps.github.io/xcode-command-line-tools.html>`_. If you already have gcc or clang installed, you can skip this step.

2. Ensure that you have the python package ``pip`` installed. If it is not already installed, follow the directions on `the pypa website <https://pip.pypa.io/en/stable/installing.html#pip-included-with-python>`_ or use the following command (requires ``easy_install``, which should ship with most versions of OS X):

    .. code-block:: bash

        sudo easy_install pip

2. Use pip to install svviz:

    .. code-block:: bash

        sudo pip install svviz

    This should automatically install a number of required python packages (see :ref:`below <required_python_packages>`). If you prefer to install the latest development version from github, install git and then use this command instead (warning: bleeding edge! may contain bugs!):

    .. code-block:: bash

        sudo pip install -U git+git://github.com/svviz/svviz.git

3. To enable PDF export, you have two options.

    * The first, and recommended option, is to use `webkitToPDF <https://github.com/nspies/webkitToPDF/tree/master>`_, a simple homegrown command-line program that uses OS X's built-in web rendering engine to convert SVGs (``svviz``'s native format) into PDF. As its name implies, ``webkitToPDF`` does not support PNG support. To use ``webkitToPDF`` with ``svviz``, simply `download <https://github.com/nspies/webkitToPDF/releases/latest>`_ the OS X app and add it to your `PATH <http://hathaway.cc/post/69201163472/how-to-edit-your-path-environment-variables-on-mac>`_.


    * The second option is to use `libRsvg <https://wiki.gnome.org/action/show/Projects/LibRsvg>`_ package. First install and update `homebrew <http://brew.sh>`_ and then run ``brew install librsvg``. Export using ``libRsvg`` supports both PNG and PDF formats.

See the :ref:`troubleshooting` section if you have difficulties after following the above directions.


.. _required_python_packages:

Required python packages
------------------------

``svviz`` requires several python packages in order to run properly. During a normal installation, these packages should be installed automatically:

- `flask <http://flask.pocoo.org>`_
- `joblib <https://github.com/joblib/joblib>`_
- `numpy <http://www.numpy.org>`_
- `pyfaidx <https://github.com/mdshw5/pyfaidx>`_
- `pysam <http://pysam.readthedocs.org/>`_
- `requests <http://docs.python-requests.org/en/latest/>`_


Some additional functionality is provided by the following optional python packages (not installed automatically; use ``sudo pip install pandas``, etc):

- `pandas <http://pandas.pydata.org>`_
- `rpy2 <https://bitbucket.org/rpy2/rpy2>`_



Running the demos
-----------------

Several example datasets can be downloaded and run directly from ``svviz``. This is a good step to perform in order to make sure everything is installed correctly:

``svviz demo``

(Additional demos can be run as ``svviz demo 2``, ``svviz demo 3``, etc.)

This will prompt you if you would like to download the example datasets into the current working directory. If you type ``y`` to indicate yes, the data will be downloaded, then automatically analyzed and visualized in your web browser. The first line of output (following the download) shows the command line arguments used to analyze the demo; if you wish to play around with parameters (for example adding or removing datasets, or refining the breakpoints), you can copy and edit this command.

Subsequent lines of output will indicate progress of ``svviz`` as it processes the data. Once processing is complete (should typically take ~1min), ``svviz`` will create a local web-server (accessible only from within your computer) and open your default web browser to a page displaying the example structural variant.


.. _troubleshooting:

Troubleshooting
---------------

.. _venv:

**svviz won't install**

1. Do you have a C compiler installed? You will need to `install the command-line tools <http://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/>`_ if you are on OS X.
2. Have you tried installing svviz in a `virtual environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_? This helps rule out problems with incorrect dependencies:
    1. Install virtualenv: ``sudo pip install -U virtualenv``
    2. Create a virtual environment: ``virtualenv svviz_env``
    3. Activate the environment: ``source svviz_env/bin/activate``
    4. Install svviz: ``pip install -U svviz`` (note that when installing to a virtualenv, you should not need to be superuser)

**I can't access the web view**

1. Are you running the web browser on the same computer as svviz? For security reasons, the web server is only available within the same computer. To safely get around this, you will need to set up an ssh tunnel from one computer to the other (see :ref:`here <tunneling>` for directions)
2. Are you accessing the correct URL? The server always runs on localhost, but the port is chosen randomly and may change between runs.
3. Have you tried reloading the page? The server can take a moment to start, and this may take longer than it takes for your web browser to open.

**The web view opens but only shows summary statistics, no track data**

It may take a minute or so to load the data tracks into the browser, depending on how many reads are present in the region of the variant being visualized. The alt tracks will load first, but the view will not become fully interactive until the ambiguous tracks finish loading. If you are having trouble with the loading taking too long, please `submit a bug report <https://github.com/svviz/svviz/issues>`_.

**I can run the demo, but I can't load my own data**

1. Is your input bam file coordinate-sorted and indexed properly? Try removing your sample.bam.bai file and recreating it using ``samtools index sample.bam``.
2. Have you checked that you've specified the correct command-line options? The first line of output after you run svviz, if there is not an error parsing the input, shows how svviz interpreted the command line arguments you provided. This can help you track down a potential misspelling or other error in specifying command line arguments.
3. Have you properly specified the variant coordinates on the command-line? Running ``svviz`` without any arguments will output the help, including how to specify the variant coordinates.

**Other problems**

See the :ref:`FAQs <faqs>` for answers to other questions.

Please report any other problems on the `issues page <https://github.com/svviz/svviz/issues>`_ of the github project site.