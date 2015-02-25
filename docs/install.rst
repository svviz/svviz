Installation
============

A single command should typically suffice to install ``svviz``:

``pip install svviz``

If that command gives a permissions error, you can try adding ``sudo`` to the beginnning of the command in order to run the command as super-user (often required for a system-wide installation). If you get an error that ``pip`` is missing, assuming python is already installed, you can run ``sudo easy_install pip`` and then run the above command (see `here <https://pip.pypa.io/en/latest/installing.html>`_ for more info on installing pip).

``svviz`` requires several python packages in order to run properly. During a normal installation, these packages should be installed automatically:

- flask
- joblib
- numpy
- pyfaidx
- pysam
- requests

Finally, in order to export the visualizations into PDF or PNG format, you will need to install libRsvg. On the Mac, first install and update `homebrew <http://brew.sh>`_ and then run ``brew install librsvg``; on linux (ubuntu and similar), you can run ``sudo apt-get install librsvg2-dev``.

Running the demos
-----------------

Several example datasets can be downloaded and run directly from ``svviz``. This is a good step to perform in order to make sure everything is installed correctly:

``svviz demo``

(Additional demos can be run as ``svviz demo 2``, ``svviz demo 3``, etc.)

This will prompt you if you would like to download the example datasets into the current working directory. If you type ``y`` to indicate yes, the data will be downloaded, then automatically analyzed and visualized in your web browser. The first line of output (following the download) shows the command line arguments used to analyze the demo; if you wish to play around with parameters (for example adding or removing datasets, or refining the breakpoints), you can copy and edit this command.

Subsequent lines of output will indicate progress of ``svviz`` as it processes the data. Once processing is complete (should typically take ~1min), ``svviz`` will create a local web-server (accessible only from within your computer) and open your default web browser to a page displaying the example structural variant.
