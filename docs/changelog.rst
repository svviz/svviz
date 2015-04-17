Change log
==========

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