Change log
==========

1.4.0
-----

This release includes many small improvements and bugfixes.

One changes to svviz's behavior is notable:

- the ``--pair-min-mapq`` option now requires one read end to both exceed this mapq threshold *and* be near the variant

Improvements:

- implemented a largedeletion variant type, with an option to automatically convert deletions above a certain size to use "breakend" mode, thus only analyzing reads near the deletion breakpoints (see the :ref:`FAQ <largedeletions>`)
- implemented a ``--max-size`` option which skips variants exceeding the specified number of nucleotides (see the :ref:`FAQ <lotsoreads>`)
- when the ``--max-reads`` option is provided in batch mode, svviz should stop analyzing a variant much sooner if that variant exceeds the max-reads threshold
- dotplots now work with multi-part variants such as breakends
- better conversion between chromosome formats (chrX<->X)
- many tweaks to the progress information provided as svviz is running
- no longer require file suffix on ``--export`` when in batch mode and ``--format`` is specified (A. Regier)
- added support for using inkscape for PDF export; the ``--converter`` option can be used to choose between different conversion software packages
- the test suite is now mostly included in the git repository in case anyone else wants to run the regression tests
- added demo 3, a deletion with an example annotation track

Bugfixes:
- fixed handling of variant breakpoints near the ends of chromosomes (rpadmanabhan)
- fixed a bug where reads mapping to both strands with similar alignment scores might not have been marked as multimapping


1.3.2
-----
This release includes a number of bugfixes and additions to the documentation.

- bed annotations should now work again (C. Lee)
- added support for gff files without gene or transcript IDs
- fixed support for ``--processor 1`` (A. Ramu)
- added more information about the "lots fo reads in region" warning (see :ref:`FAQ <lotsoreads>`)


1.3.1
-----

This release adds substantial improvements to the handling of multi-mapping reads (ie those aligning to multiple locations near the structural variant). See :ref:`here <dotplots>` for more details.

1.3.0
-----

This release adds a number of new features and fixes several bugs:

- added support for displaying gene models (exons and introns) from GFF-formatted annotation files
- added option to display reads that are in flanking genomic regions, providing context for a structural variant
- initial implementation of breakend support (note that, currently, the breakends must be distant from one another, and breakend support has not been implemented from vcf files yet)
- added checkbox to web interface to hide/show flanking reads
- added option to define the web server port, making it easier to use ssh tunneling to access svviz running on a server
- now auto-detect the number of cores available on a machine (used for the realignment step)
- added option to specify how many processes (cores) to use when performing realignment
- improved handling of paired-end reads that align to the same location
- added option to skip variants with very deep read coverage (typically indicative of a repetitive genomic region); useful in batch mode

1.2.0
-----

This is a major feature release, implementing support for visualizing translocations.

Additional changes:

- does a better job finding reads to estimate empirical insert size distribution and read pair orientation
- checks that bam files have index and produce a more helpful error message if they do not
- annotations now also check to see if there's a mismatch between "chrX" and "X" formats, and try to automatically fix it
- wrapping pyfaidx with a pickle-able ``GenomeSource`` object; should make automated debugging easier
- added ``--skip-cigar`` option which disables visualizing mismatches and indels; this will speed up exporting and the web browser view for data with many errors (eg PacBio)

1.1.1
-----

- no longer requires X11 if rpy2 is installed (I know, this was a weird one)

1.1.0
-----

- code refactoring and new tests that should make it easier to modify and improve the visualizations produced by svviz
- added experimental support for webkitToPDF, a command-line tool that uses OS X's built-in SVG support (part of Safari's webpage rendering code) to convert SVGs to PDFs; this currently requires a separate install of webkitToPDF. webkitToPDF produces much better PDFs than rsvg-convert does (for example, fonts are converted properly)

1.0.9
-----

- added link to preprint on bioRxiv
- added support for exporting one pdf per event in batch mode
- tweaks and fixes for visualizations
- changed coloring of insertions in reads to cyan

1.0.8
-----

- filter out reads that align multiple times within the region of the structural variant ("multimapping")
- many minor bug-fixes and interface tweaks

1.0.7
-----

- demo data now gets downloaded from Stanford webspace
- added ``--version`` command line option
- no longer fails if pandas is an older version
- check for librsvg before we do the analysis

1.0.6
-----

- fixed bug that prevented ``--export`` option from working
- ref and alt alignment scores must differ by at least 2 in order to assign a read to an allele by alignmentScore
- minor bug fixes


1.0.5
-----

- implemented :ref:`batch mode <batch-mode>` to analyze multiple variants at once
