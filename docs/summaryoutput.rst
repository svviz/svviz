Summary output
==============

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
    - **reason_multiRegion**: these reads were assigned to an allele because they mapped to multiple chromosome parts in the other allele; in :ref:`this example translocation <complex_variants>`, a read pair mapping to the red portion of chromosome 19 and the gray portion of chromosome 6 would be considered an invalid "multi-region" alignment in the reference allele, but would be considered a valid alignment across the translocation breakpoint in the alternate allele; thus, this read-pair would be assigned to the alt allele and given the "reason_multiRegion" tag



