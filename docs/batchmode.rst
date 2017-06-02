.. _batch-mode:

Batch mode
==========

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

- chromosome (column 0)
- start coordinate (column 1)
- SVTYPE=TRA;CHR2=<other chromosome>;END=<end coordinate>;STRAND=<orientation, either + or -> (column 7)



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
