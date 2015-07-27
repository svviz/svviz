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