Features
========

* built-in support for:
    * deletions
    * insertions (including mobile element insertions)
    * inversions
    * ``svviz`` can easily be extended to analyze translocations and complex variants, but these types are not yet implemented.
* builds reference and alternate allele sequences from genome fasta file and structural variant annotation
* identifies, from the input bam file(s), which reads (both read ends for paired-end sequencing) are likely to be relevant for the given structural variant
* performs Smith-Waterman realignment of all read segments against both alternate and reference allele sequences
* uses alignment score to determine reads supporting reference or alternate allele
* additionally, uses empirical insert-size distribution (rather than mean and stddev) to assign reads as likely derived from alternate or reference allele
* provides a (locally-running) browser-based front-end for inspecting visualizations
* visualizes reads for multiple samples in SVG format (an open-source, web-standard vector graphics format)
* options to export to PDF or PNG
