Command line interface
======================

Loading and visualizing your structural variant
-----------------------------------------------

To visualize your structural variant of interest, you will need at least the following three pieces of data:

1. Input bam file(s). This bam file must be coordinate-sorted and have an index file (sample.bam.bai) in the same directory. You can use `samtools <http://www.htslib.org/download>`_ to sort and index your bam file. Bam files are specified using the ``-b`` command line argument, which can be provided multiple times to load and visualize multiple samples simultaneously.
2. Input genome fasta file. If a .fai index file does not already exist in the directory containing the fasta file, it will be created. This means that, if the .fai file does not already exist, the fasta file needs to be in a directory for which you have write permission. This fasta file is the first required command line argument.
3. The coordinates of the structural variant. The type of event is specified by the ``-t`` command line option. The following four event types are currently supported:
    
    :Deletions: The format for specifying deletion breakpoints is ``chrom start end``.
    :Inversions: To specify an inverted region, use ``chrom start end``.
    :Insertions: The format for specifying insertions is ``chrom breakpoint <inserted sequence>``.
    :Mobile elements: Mobile element insertions can be specified by ``<mobile_elements.fasta> <chrom> <pos> <ME name> [ME strand [start [end]]]``, where ``<ME name>`` must match the header line from the mobile_elements.fasta file, and strand, start and end are optional coordinates of the relevant portion from the mobile element sequence.
    :Translocations: Translocations can be specified using the following format: ``chrom1 start1 chrom2 start2 orientation``, where ``orientation`` is either ``+`` or ``-``, and specifies whether region1 and region2 are both on the plus strand of the genome, or are on opposite genomic strands.
    :Breakend: Additional types of structural variant can be specified using `breakend <http://samtools.github.io/hts-specs/VCFv4.2.pdf>`_ format: ``chrom1 start1 strand1 chrom2 start2 strand2``. Note that, due to limitations of the Smith-Waterman alignment library used by svviz, breakend breakpoints must be distant from one another, relative to the insert size/read length.
    :Batch: see :ref:`below <batch-mode>`

For example, a deletion might be called as:

.. code-block:: bash

    svviz -t del -b sample1.sorted.bam -b sample2.sorted.bam hg19.fasta chr7 153757067 153758235


Displaying annotations
----------------------

Annotation tracks can be loaded and visualized in order to display the position of important nearby genomic regions such as genes or repeat sequences. These need to be provided in standard `BED <http://genome.ucsc.edu/FAQ/FAQformat.html#format1>`_ format (the first 6 columns are required, up to and including strand). Such annotation tracks can easily be downloaded from the `UCSC Genome Browser <http://genome.ucsc.edu>`_, either from the standard annotations provided for each assembly or using their Table Browser tool. Each bed file is specified with the ``--annotations`` option (or ``-A``).


Additional options
------------------

The default settings are typically correct for Illumina data. Read orientation and insert sizes will be inferred for each input library. Sequencing platforms that have a substantially higher error rate than Illumina may need adjusting of the ``--aln-quality`` option.

The ``--lenient`` option is recommended for pacific biosciences sequencing (because PacBio sequencing is typically of lower base-quality than Illumina sequencing, this preset changes the ``--aln-quality`` option to retain lower quality alignments as support for the Ref and Alt alleles)

The ``--min-mapq`` option specifies the mapping quality threshold; reads with mapq (this is set during the original genome-wide mapping by bwa, bowtie, etc) below this threshold will be discarded during pre-processing. A similar argument, ``--pair-min-mapq``, can be used instead to require that at least one read end out of a read pair must have a mapq exceeding this value.

.. _dotplots:

The ``--dotplots`` option will create a `dotplot <https://en.wikipedia.org/wiki/Dot_plot_(bioinformatics)>`_ to visualize sequence similarity within the genomic region(s) surrounding the structural variant. This depends on the optional python package rpy2 (first make sure `R <https://www.r-project.org>`_ is installed and then install rpy2 using the command ``sudo pip install rpy2``). You will also need to install `yass  <http://bioinfo.lifl.fr/yass>`_, which can be installed using the `homebrew <http://brew.sh>`_ command ``brew install homebrew/science/yass`` (OS X only) or yass can be downloaded, compiled and installed according to the instructions `here <http://bioinfo.lifl.fr/yass/download.php>`_ (linux and OS X).

The dotplot output shows regions of similarity within the reference allele as lines: blue lines indicate similarity on the same strand and direction whereas red indicates similarity on the opposite strand/direction. Because the similarity matrix is symmetrical, only same strand similarities are shown in the upper left half and only opposite strand similarities are shown in the bottom right half. The structural variant breakpoints are shown as dashed gray lines.

.. _multimapping:

A related option is ``--max-multimapping-similarity``, which adjust how aggressively svviz filters out reads that potentially align to multiple locations near the structural variant. The default score of 0.95 means that any read (for paired-end reads, this means any read-end) whose second-best alignment score is more than 0.95 times the best alignment score will be assigned as ambiguous. For example, if the best alignment score is 445, and the second-best alignment score is 439, the multimapping similarity would be 439/445=0.99 and the read would be marked as ambiguous. However, a read whose best alignment score is 445 but second-best alignment score is 405 would not be filtered because the multimapping similarity of 395/445=0.89 is less than 0.95.


Exporting visualizations
------------------------

The visualizations can be exported to SVG, PNG or PDF from the web view by clicking the "Export" link at the top of the page. Alternatively, these files can be created directly, without launching the web interface, using the ``--export`` option (and this exported image file can be opened automatically using your system-defined image viewer by additionally specifying the ``--open-exported`` or ``-O`` option).


.. _batch-mode:

Batch mode
----------

To summarize a number of structural variants at once, svviz supports a batch mode.

To run batch mode, use ``--type batch``, and specify (1) the reference genome (in fasta format, as above) and (2) a VCF file describing the SVs to be analyzed. These SVs must be of supported types (insertions, deletions, inversions and mobile element insertions), and specified in `VCF 4.0 Format <http://www.1000genomes.org/wiki/Analysis/Variant%20Call%20Format/VCF%20(Variant%20Call%20Format)%20version%204.0/encoding-structural-variants>`_.

You will probably also wish to use the ``--summary`` option to specify a tab-delimited output file with the full summary statistics describing each variant and allele.

The visualizations can still be created and exported in batch mode. While in batch mode, the ``--export`` command-line option specifies a directory into which to place the exported visualizations. These files are named by the type and position of the event, so there will be one file per event. The default is PDF format (this can be changed by using the ``--format`` option).

The following columns are required in the input VCF files:

Deletions
^^^^^^^^^

- chromosome (column 0)
- start coordinate (column 1)
- SVTYPE=DEL;END=<end coordinate> (column 7)


Insertions
^^^^^^^^^^

- chromosome (column 0)
- start coordinate (column 1)
- SVTYPE=INS;END=<end coordinate> (column 7)
- the inserted sequence must be specified either: 
    - in column 4 (alt allele)
    - or by specifying MEINFO=<seqName>, and passing the ``--fasta insertionSequences.fasta`` command-line argument containing seqName
    - optional coordinates within the insertionSequences.fasta file can be specified as MEINFO=<seqName,start,end,strand>
- END=end coordinate can optionally be specified to make a compound deletion/insertion event
    - if END is not specified, it is set to the same value as start


Inversions
^^^^^^^^^^

- chromosome (column 0)
- start coordinate (column 1)
- SVTYPE=INV;END=<end coordinate> (column 7)


Translocations
^^^^^^^^^^^^^^

Support for translocations in batch mode is forthcoming.


Examples
^^^^^^^^

``events.vcf`` (note ``.`` indicates a field that is ignored by svviz):

.. code-block:: none

    chr1 2827693   . .  . . . SVTYPE=DEL;END=2828322
    chr3 9425916   . . ATGGCTTCGATTAGCGTCGATGCTTCGTAGAGAGTCTGCTA .  .  SVTYPE=INS
    chr3 22371722   . . . .  .  SVTYPE=INS;MEINFO=L1HS
    chr5 46572873   . . . .  .  SVTYPE=INS;MEINFO=L1HS,33,5030,-
    chr6 36167622   . . TGATCGTCTTTTCTGAGAGCTGCTA .  .  SVTYPE=INS;END=36167671
    chr9 458616733   . . . .  .  SVTYPE=INV;END=458617412


Shell command:

.. code-block:: bash

    svviz --type batch --summary events_summary.tsv -b sample1.sorted.bam hg19.fasta events.vcf


Summary output
^^^^^^^^^^^^^^

Each line describes a single summary statistics for a single allele in a single sample for one variant. For example, 

.. code-block:: none

    variant                                 sample          allele  key     value
    Deletion::chr1:724,921-726,121(1200)    HG002_MP_L1_L2  alt     count   4
    Deletion::chr1:724,921-726,121(1200)    HG002_MP_L1_L2  ref     count   75

The following code illustrates one approach to analyzing this summary file from python (using the `pandas <http://pandas.pydata.org>`_ library)::

    import pandas as pd
    summary = pd.read_table("events_summary.tsv", sep="\t")
    print summary.pivot_table(values="value", index=["variant","sample","allele"], columns="key")

A partial description of the summary output follows:

- **count**: the number of reads supporting the given allele
- **alnScore_mean** and **alnScore_std**: the mean and standard deviation of the alignment scores; note that the alignment scores will vary substantially if there is heterogeneity of sequencing read lengths, as there is in, for example, PacBio data, or Illumina data when adapter sequences have been stripped
- **insertSize_mean** and **insertSize_std**: the mean and standard deviation of the insert sizes (if the data is paired-ended) or the length of the reads (if the data is single-ended); this is calculated *after* realignment, and so includes all gaps in the alignments, but does not include any clipped bases if the alignment does not include the entire read sequence
- **reason_***: these lines count how many reads were assigned to the given allele because of the given "reason": 
    - **reason_alignmentScore**: the alignment score for this allele was better than for the other
    - **reason_insertSizeScore**: the insert size for this allele was a better match to the background distribution
    - **reason_orientation**: this allele had the correct paired-end read orientation but the other allele did not
    - **reason_multimapping**: these reads were assigned to ambiguous because it aligned well in two locations near the structural variant



