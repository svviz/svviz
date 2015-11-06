.. _faqs:

Frequently Asked Questions
==========================

.. _tunneling:

**Can I access the web interface if svviz is running on another computer (for example, a server)?**

Yes, you should be able to do this by ssh tunneling:

1. Run svviz as you normally would, but define the port using the ``--port n`` option, where ``n`` is an integer from 0-65535 corresponding to an unused port on the computer running svviz.
2. From your desktop computer, start an ssh tunnel to your server. If your server is running on myserver.com, and you used port 7777 in step 1., the following command should start the tunnel from localhost:7777 on your desktop to localhost:7777 on the server:

    .. code-block:: bash

        ssh -L 127.0.0.1:7777:127.0.0.1:7777 username@myserver.com -N

    After entering your password for myserver.com, leave ssh running in the terminal.

3. Open your browser to ``http://127.0.0.1:7777``.


**How do I visualize reads if the breakpoint coordinates are imprecise?**

Depending on several factors, you may be able to visualize reads around imprecise breakpoints without doing anything special. This works best if the paired-end insert size is long or the degree of imprecision is small relative to the read length.

However, if you know your breakpoints are imprecise, you can use the ``--lenient`` command line option to retain reads with poor alignment scores. It is prudent, however, to use the output of svviz to correct the breakpoint positions and re-run svviz once more precise breakpoints have been estimated.

To refine breakpoints, look for a grey region around the alternate allele breakpoint(s), indicating a deletion, or a blue line immediately at the breakpoint, indicating an insertion. The length of the extra deleted or insert sequence can be estimated from the web view by hovering over relevant reads and inspecting the nucleotide-level alignments.


**What do I do if the genomic region around the structural variant is repetitive?**

If you know the genomic region including the structural variant is repetitive, or if you're getting a warning about "Found a substantial number of reads that could map to multiple locations within the same allele", you should consider doing a few things:

1. When reads are mapped to the genome using a tool such as bwa or bowtie2, they typically receive a "mapq" map-quality score that indicates how uniquely the read maps in the genome; this score can. These scores can be shown for individual reads in the web interface simply by hovering your cursor over a read, with example output being ``mapq=60`` or (for paired-end reads) ``mapq=60,30``.

2. Make sure that you're using the ``--min-mapq`` or ``--pair-min-mapq`` options to filter out reads that map ambiguously within the entire genome. 

3. Use the ``--dotplots`` option (see :ref:`here <dotplots>` for more information) to visualize sequence similarity within the genomic region.

4. Adjust the ``--max-multimapping-similarity`` option to filter out reads potentially aligning to multiple locations within the structural variant region (see :ref:`here <multimapping>` for more information).


.. _lotsoreads:

**What does the warning "LOTS OF READS IN BREAKPOINT REGION" mean?**

The "LOTS OF READS IN BREAKPOINT/MATE-PAIR REGION" warning indicates that svviz will be trying to pull reads in from a genomic region with very high sequencing coverage (over 100,000 reads within the region). This warning may appear when analyzing very high coverage sequencing data or extremely large regions. The warning indicates that run-time or memory to analyze a variant may be excessive. 

To skip variants that are particularly large use the ``--min-size`` option, for example to skip events that are larger than 1 megabase (``--min-size 1000000``). To skip variants with too many reads, use the ``--min-reads`` option, for example to skip events with more than 100,000 reads (``--min-reads 100000``). 

For paired-end data, this warning may also appear as a result of trying to read in mate-pairs from the input BAM(s). svviz first finds all reads in the vicinity of the structural variant being analyzed. For paired-end data, svviz then tries to find the read mates for all reads identified previously. Most of the reads and their mates should both be near the breakpoints. However, in the case of a repetitively-mapping sequence, an incorrectly-called breakpoint, or a mapping error, reads can be separated from their mates in the genome. Thus, to find the mates for these types of reads, svviz must access other genomic locations from the input BAM.

In most cases, svviz should take only a bit longer to find read-pairs, perhaps a few minutes. In the case that it is taking substantially longer, you can cancel svviz by hitting ctrl-c in the terminal. One potential option for skipping highly repetitive reads, thus improving performance, is to adjust the ``--min-mapq`` (``-q``) option. For example, if the maximum mapping-quality output by your alignment software is 60 (for example, when using bwa), you could specify ``-q 60`` when running svviz. The related ``--min-pair-mapq`` option requires that one read end be (1) close to the variant and (2) exceed this mapq threshold. For example, if both read ends have low map quality (eg, fall within a repeat), then the reads will be skipped. If instead one read end maps close to a breakpoint, but the other end maps elsewhere in the genome, to a repeat, then both reads will be retained (eg, in the case of a non-reference repeat).


**Can svviz handle large structural variants?**

In theory, svviz can handle arbitrarily large structural variants, however this is limited in practice by memory and processing time. Memory scales with the number of reads being analyzed for the event. Run-time scales with the number of reads, the lengths of the reads and the size of the event. Run-time is also dependent on the I/O bandwidth, processor speed and number of processors.

In the special case of **large deletions**, svviz can visualize them in two ways: (1) visualizing all the reads in the deleted region as well as spanning the deletion breakpoints or (2) in "breakend" mode, where only reads spanning the breakpoints are shown. Because this second breakend mode only analyzes reads near the breakpoints and only aligns against those regions, this mode should be preferred for very large deletions to visualize the exact breakpoints.

To enable this mode, use the ``largedeletion`` (or in shorthand, ``ldel``) event type when running svviz from the terminal. In batch mode, use the ``--max-deletion-size`` option to convert deletions above a certain size into breakend format. Note that because of 