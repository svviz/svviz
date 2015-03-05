Change log
==========

1.0.8
-----

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