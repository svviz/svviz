*****
svviz
*****

Author: Noah Spies


Notice
======

This software is in active development. Some things may not work as expected. The interface is guaranteed to change. 

Quickstart
==========

1. (OS X only) Ensure that you have a working compiler by following `these instructions <http://railsapps.github.io/xcode-command-line-tools.html>`_.
2. Install the latest version of svviz from github using the following terminal command: ``sudo pip install -U git+https://github.com/svviz/svviz.git#svviz``. (The sudo may not be necessary depending on your setup.)
3. Run the following command, which downloads example data and runs it through svviz: ``svviz demo``. After several processing steps, a web browser window should open. Click and drag to pan, and zoom using option/alt-scrollwheel.
4. Please report any issues (after making sure they're not explained in the documentation below) using the `github issue tracker <https://github.com/svviz/svviz/issues>`_.


Usage
=====

::

  usage: svviz [options] [demo] [ref breakpoint-info...]

  positional arguments:
    ref                   reference fasta file (a .faidx index file will be
                          created if it doesn't exist so you need write
                          permissions for this directory)
    breakpoints

  optional arguments:
    -h, --help            show this help message and exit

  required parameters:
    -b BAM, --bam BAM     sorted, indexed bam file containing reads of interest
                          to plot; can be specified multiple times to load
                          multiple samples

  input parameters:
    -t TYPE, --type TYPE  event type: either del[etion], ins[ertion] or mei
                          (mobile element insertion)
    -S, --single-ended    single-ended sequencing (default is paired-end)
    -o ORIENTATION, --orientation ORIENTATION
                          read orientation; probably want fr, rf or similar
                          (only needed for paired-end data; default rf)
    -A ANNOTATIONS, --annotations ANNOTATIONS
                          [in dev] bed file containing annotations to plot; will be
                          compressed and indexed using samtools tabix in place
                          if needed (can specify multiple annotations files)
    -m MEAN, --isize-mean MEAN
                          mean insert size; used to determine concordant read
                          pairs (paired-end)and the size of the flanking region
                          to align against around breakpoints (default: inferred
                          from input bam)
    -s STD, --isize-std STD
                          stdev of the insert size (default: inferred from input
                          bam)
    -d DISTANCE, --search-dist DISTANCE
                          distance in base-pairs from the breakpoints to search
                          for reads; default: 2x the isize-mean (paired end) or
                          1000 (single-end)
    -q MAPQ, --min-mapq MAPQ
                          minimum mapping quality for reads
    -a QUALITY, --aln-quality QUALITY
                          minimum score of the Smith-Waterman alignment against
                          the ref or alt allele in order to be considered
                          (multiplied by 2)
    -e EXPORT, --export EXPORT
                          export view to file; exported file format is
                          determined from the filename extension (automatically
                          sets --no-web)
    -O, --open-exported   automatically open the exported file (OS X only)

  interface parameters:
    --no-web              don't show the web interface
    --save-reads OUT_BAM_PATH
                          save relevant reads to this file (bam)

  presets:
    --mate-pair           sets defaults for ~6.5kb insert mate pair libraries
    --pacbio              sets defaults for pacbio libraries
    --moleculo            sets defaults for moleculo libraries

  For an example, run 'svviz demo'.

Breakpoint specification
------------------------


:Deletions: The format for specifying deletion breakpoints is ``chrom start end``.
:Inversions: To specify an inverted region, use ``chrom start end``.
:Insertions: The format for specifying insertions is ``chrom breakpoint <inserted sequence>``.
:Mobile elements: Mobile element insertions can be specified by ``<mobile_elements.fasta> <chrom> <pos> <ME name> [ME strand [start [end]]]``, where ``<ME name>`` must match the header line from the mobile_elements.fasta file, and strand, start and end are optional coordinates of the relevant portion from the mobile element sequence.

For example:

``svviz --mate-pair -t del -b ~/data/sample1.sorted.bam ~/data/hg19.fasta chr7 153757067 153758235``

``svviz -m 256 -s 32 -q 30 -t ins -b ~/data/sample2.sorted.bam ~/data/hg19.fasta chr3 35252554 ATGTGTCGTAGATATTTTTCGTAGGAAAACGGCCCCATGAGTATATAGCGCTAGAGTAGA``

When reads have been collected and processed, a new window will open in your web browser allowing you to browse reads supporting the reference and alternate alleles.


Installing svviz
================

If you have git and pip installed, you can download and install svviz using the following single line:

``pip install git+https://github.com/svviz/svviz.git#svviz``

Alternately, you can clone the git repository. Installation can then be performed by executing the following command on OS X or linux:

``python setup.py install``

Depending on your setup, you may need to run the installation command as superuser using the "sudo" prefix.


Requirements
============

svviz has been tested on OS X and linux (ubuntu). svviz requires the following python packages, which should be automatically installed:

- flask
- joblib
- numpy
- pyfaidx
- pysam
- requests

In addition, the ssw alignment module (see below) needs to be compiled using gcc, so Xcode or the command line developer tools need to be installed if you're running OS X (see `these directions <http://railsapps.github.io/xcode-command-line-tools.html>`_ for more info).

PDF and PNG export require the optional libRSVG library, which can be installed using ``brew install librsvg`` (using `homebrew <http://brew.sh>`_) on the mac or ``sudo apt-get install librsvg2-dev`` on linux/ubuntu.

Smith-Waterman Alignment
------------------------

The Smith-Waterman Alignments are performed by https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library, whose license requires the following statements:
 
  Author: Mengyao Zhao & Wan-Ping Lee

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

