Installation
============

A single command should typically suffice to install ``svviz``:

``pip install svviz``

If that command gives a permissions error, you can try adding ``sudo`` to the beginnning of the command in order to run the command as super-user (often required for a system-wide installation). If you get an error that ``pip`` is missing, assuming python is already installed, you can run ``sudo easy_install pip`` and then run the above command (see `here <https://pip.pypa.io/en/latest/installing.html>`_ for more info on installing pip).

``svviz`` requires several python packages in order to run properly. During a normal installation, these packages should be installed automatically:

- `flask <http://flask.pocoo.org>`_
- `joblib <https://github.com/joblib/joblib>`_
- `numpy <http://www.numpy.org>`_
- `pyfaidx <https://github.com/mdshw5/pyfaidx>`_
- `pysam <http://pysam.readthedocs.org/>`_
- `requests <http://docs.python-requests.org/en/latest/>`_

In order to export the visualizations into PDF or PNG format, you will need to install `libRsvg <https://wiki.gnome.org/action/show/Projects/LibRsvg>`_. On the Mac, first install and update `homebrew <http://brew.sh>`_ and then run ``brew install librsvg``; on linux (ubuntu and similar), you can run ``sudo apt-get install librsvg2-dev``.

Finally, some optional functionality is provided by the following python packages:

- `pandas <http://pandas.pydata.org>`_
- `rpy2 <https://bitbucket.org/rpy2/rpy2>`_



Running the demos
-----------------

Several example datasets can be downloaded and run directly from ``svviz``. This is a good step to perform in order to make sure everything is installed correctly:

``svviz demo``

(Additional demos can be run as ``svviz demo 2``, ``svviz demo 3``, etc.)

This will prompt you if you would like to download the example datasets into the current working directory. If you type ``y`` to indicate yes, the data will be downloaded, then automatically analyzed and visualized in your web browser. The first line of output (following the download) shows the command line arguments used to analyze the demo; if you wish to play around with parameters (for example adding or removing datasets, or refining the breakpoints), you can copy and edit this command.

Subsequent lines of output will indicate progress of ``svviz`` as it processes the data. Once processing is complete (should typically take ~1min), ``svviz`` will create a local web-server (accessible only from within your computer) and open your default web browser to a page displaying the example structural variant.


Troubleshooting
---------------

**svviz won't install**

1. Do you have a C compiler installed? You will need to `install the command-line tools <http://osxdaily.com/2014/02/12/install-command-line-tools-mac-os-x/>`_ if you are on OS X.
2. Have you tried installing svviz in a `virtual environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_? This helps rule out problems with incorrect dependencies:
    1. Install virtualenv: ``sudo pip install -U virtualenv``
    2. Create a virtual environment: ``virtualenv svviz_env``
    3. Activate the environment: ``source svviz_env/bin/activate``
    4. Install svviz: ``pip install -U svviz`` (note that when installing to a virtualenv, you should not need to be superuser)

**I can't access the web view**

1. Are you running the web browser on the same computer as svviz? For security reasons, the web server is only available within the same computer. To safely get around this, you will need to set up an ssh tunnel from one computer to the other
2. Are you accessing the correct URL? The server always runs on localhost, but the port is chosen randomly and may change between runs.
3. Have you tried reloading the page? The server can take a moment to start, and this may take longer than it takes for your web browser to open.

**The web view opens but only shows summary statistics, no track data**

It may take a minute or so to load the data tracks into the browser, depending on how many reads are present in the region of the variant being visualized. The alt tracks will load first, but the view will not become fully interactive until the ambiguous tracks finish loading. If you are having trouble with the loading taking too long, please `submit a bug report <https://github.com/svviz/svviz/issues>`_.

**I can run the demo, but I can't load my own data**

1. Is your input bam file coordinate-sorted and indexed properly? Try removing your sample.bam.bai file and recreating it using ``samtools index sample.bam``.
2. Have you checked that you've specified the correct command-line options? The first line of output after you run svviz, if there is not an error parsing the input, shows how svviz interpreted the command line arguments you provided. This can help you track down a potential misspelling or other error in specifying command line arguments.
3. Have you properly specified the variant coordinates on the command-line? Running ``svviz`` without any arguments will output the help, including how to specify the variant coordinates.

**Other problems**

Please report any other problems on the `issues page <https://github.com/svviz/svviz/issues>`_ of the github project site.