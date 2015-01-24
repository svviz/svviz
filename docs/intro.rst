Introduction to svviz
=====================

The program takes as input one or several bam files with sequencing data, a genome fasta file, information about a putative structural variant (that has been identified using other methods), and (optionally) a bed file with genomic annotations. From these inputs, ``svviz`` uses a realignment process to identify reads supporting the reference allele, reads supporting the structural variant (or alternate allele), and reads that are not informative one way or the other (ambiguous).

Reads are then plotted, as in a standard genome browser, but along the sequence of either the alternate allele or the reference allele. The user can thus assess the support for the putative structural variant visually, determine if the breakpoints appear accurate, or estimate a likely genotype for each sample at the given structural variant.

``svviz`` differs from existing genome browsers in being able to display arbitrary types of structural variants, such as large insertions, deletions, inversions and translocations. Genome browsers such as IGV are poorly suited to displaying the read data supporting these types of structural variants, which can differ dramatically from the reference genome sequence. 


