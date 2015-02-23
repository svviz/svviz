Command line interface
======================

Loading and visualizing your structural variant
-----------------------------------------------

To visualize your structural variant of interest, you will need at least the following three pieces of data:

1. Input bam file(s). This bam file must be coordinate sorted and have an index file (sample.bam.bai) in the same directory. You can use `samtools <http://www.htslib.org/download>`_ to sort and index your bam file. Bam files are specified using the ``-b`` command line argument, which can be provided multiple times to load and visualize multiple samples simultaneously.
2. Input genome fasta file. If a .fai index file does not already exist in the directory containing the fasta file, it will be created. This means that, if the .fai file does not already exist, the fasta file needs to be in a directory for which you have write permission. This fasta file is the first required command line argument.
3. The coordinates of the structural variant. The type of event is specified by the ``-t`` command line option. The following four event types are currently supported:

    :Deletions: The format for specifying deletion breakpoints is ``chrom start end``.
    :Inversions: To specify an inverted region, use ``chrom start end``.
    :Insertions: The format for specifying insertions is ``chrom breakpoint <inserted sequence>``.
    :Mobile elements: Mobile element insertions can be specified by ``<mobile_elements.fasta> <chrom> <pos> <ME name> [ME strand [start [end]]]``, where ``<ME name>`` must match the header line from the mobile_elements.fasta file, and strand, start and end are optional coordinates of the relevant portion from the mobile element sequence.

For example, a deletion might be called as:

``svviz -t del -b ~/data/sample1.sorted.bam -b ~/data/sample2.sorted.bam ~/data/hg19.fasta chr7 153757067 153758235``


Displaying annotations
----------------------

Annotation tracks can be loaded and visualized in order to display the position of important nearby genomic regions such as genes or repeat sequences. These need to be provided in standard `BED <http://genome.ucsc.edu/FAQ/FAQformat.html#format1>`_ format (the first 6 columns are required, up to and including strand). Such annotation tracks can easily be downloaded from the `UCSC Genome Browser <http://genome.ucsc.edu>`_, either from the standard annotations provided for each assembly or using their Table Browser tool. Each bed file is specified with the ``--annotations`` option (or ``-A``).


Additional options
------------------

The default settings are typically correct for Illumina data. Read orientation and insert sizes will be inferred for each input library. Sequencing platforms that have a substantially higher error rate than Illumina may need adjusting of the ``--aln-quality`` option.

- ``--pacbio`` for pacific biosciences sequencing (because PacBio sequencing is typically of lower base-quality than Illumina sequencing, this preset changes the ``--aln-quality`` option as well to retain lower quality alignments as support for the Ref and Alt alleles)

The ``--min-mapq`` option specifies the mapping quality threshold; reads with mapq (this is set during the original genome-wide mapping by bwa, bowtie, etc) below this threshold will be discarded during pre-processing. A similar argument, ``--pair-min-mapq``, can be used instead to require that at least one read end out of a read pair must have a mapq exceeding this value.


Exporting visualizations
------------------------

The visualizations can be exported to SVG, PNG or PDF from the web view by clicking the "Export" link at the top of the page. Alternatively, these files can be created directly, without launching the web interface, using the ``--export`` option (and this exported image file can be opened automatically using your system-defined image viewer by additionally specifying the ``--open-exported`` option).