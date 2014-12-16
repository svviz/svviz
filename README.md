# svviz

Author: Noah Spies

## Notice

This software is in active development. Some things may not work as expected. The interface is guaranteed to change. 

## Installing svviz

If you have git and pip installed, you can download and install svviz using the following single line:

```pip install git+https://github.com/svviz/svviz.git#svviz```

Alternately, you can clone the git repository. Installation can then be performed by executing the following command on OS X or linux:

```python setup.py install```

Depending on your setup, you may need to run the command as superuser using the "sudo" prefix.

svviz requires the following python packages, which should be automatically installed:

- flask
- joblib
- pyfaidx
- pysam

In addition, the ssw alignment module (see below) needs to be compiled using gcc, so Xcode or the command line developer tools need to be installed if you're running OS X.

## Usage

```
usage: svviz [-h] [-t TYPE] [-o ORIENTATION] [-m ISIZE_MEAN] [-s ISIZE_STD]
             [-q MIN_MAPQ] [-a ALN_QUALITY] [--no-web]
             [--save-reads SAVE_READS]
             [--mate-pair | --pacbio | --deldemo | --insdemo] [-b BAM]
             ref [breakpoints [breakpoints ...]]

positional arguments:
  ref                   reference fasta file (a .faidx index file will be
                        created if it doesn't exist so you need write
                        permissions for this directory)
  breakpoints

optional arguments:
  -h, --help            show this help message and exit
  -t TYPE, --type TYPE  event type: either del[etion] or ins[ertion]
  -o ORIENTATION, --orientation ORIENTATION
                        read orientation; probably want +-, -+ or similar
  -m ISIZE_MEAN, --isize-mean ISIZE_MEAN
                        mean insert size
  -s ISIZE_STD, --isize-std ISIZE_STD
                        stdev of the insert size
  -q MIN_MAPQ, --min-mapq MIN_MAPQ
                        minimum mapping quality for reads
  -a ALN_QUALITY, --aln-quality ALN_QUALITY
                        minimum score of the Smith-Waterman alignment against
                        the ref or alt allele in order to be considered
                        (multiplied by 2)
  --no-web              don't show the web interface
  --save-reads SAVE_READS
                        save relevant reads to this file (bam)
  --mate-pair           sets defaults for ~6.5kb insert mate pair libraries
  --pacbio              sets defaults for pacbio libraries
  --deldemo
  --insdemo
  -b BAM, --bam BAM     sorted, indexed bam file containing reads of interest
                        to plot

```

The format for specifying deletion breakpoints is ```chrom start end```. The format for specifying insertions is ```chrom breakpoint <inserted sequence>```. Mobile elements can be specified by ```<mobile_elements.fasta> <chrom> <pos> <ME name> [ME strand [start [end]]]```, where <ME name> must match the header line from the mobile_elements.fasta file, and strand, start and end are optional coordinates of the relevant portion from the mobile element sequence.

For example:

```svviz --mate-pair -t del -b ~/data/sample1.sorted.bam ~/data/hg19.fasta chr7 153757067 153758235```

```svviz -m 256 -s 32 -q 30 -t ins -b ~/data/sample2.sorted.bam ~/data/hg19.fasta chr3 35252554 ATGTGTCGTAGATATTTTTCGTAGGAAAACGGCCCCATGAGTATATAGCGCTAGAGTAGA```

When reads have been collected and processed, a new window will open in your web browser allowing you to browse reads supporting the reference and alternate alleles.

For the time being, panning can be performed by using the scrollbars, using the scrollwheel (with shift) or clicking and dragging; to zoom, hold down option (alt) while spinning the scrollwheel.


#### Smith-Waterman Alignment

The Smith-Waterman Alignments are performed by https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library, whose license requires the following statements:

Author: Mengyao Zhao & Wan-Ping Lee

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

