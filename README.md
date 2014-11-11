# svviz

Author: Noah Spies

## Notice

This software is in active development. Some things may not work as expected. The interface is guaranteed to change. 

## Installing svviz

Installation can be performed by executing the following command on OS X or linux:

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
             [-q MIN_MAPQ] [--save-reads SAVE_READS]
             [--mate-pair | --paired300 | --deldemo | --insdemo]
             ref bam [breakpoints [breakpoints ...]]

positional arguments:
  ref                   reference fasta file (a .faidx index file will be
                        created if it doesn't exist so you need write
                        permissions for this directory)
  bam                   sorted, indexed bam file containing reads of interest to
                        plot
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
  --save-reads SAVE_READS
                        save relevant reads to this file (bam)
  --mate-pair           sets defaults for ~6.5kb insert mate pair libraries
```

The format for specifying deletion breakpoints is ```chrom start end```. The format for specifying insertions is ```chrom breakpoint <inserted sequence>```.

For example:

```svviz --mate-pair -t del ~/data/hg19.fasta ~/data/sample1.sorted.bam chr7 153757067 153758235```

```svviz -m 256 -s 32 -q 30 -t ins ~/data/hg19.fasta ~/data/sample2.sorted.bam chr3 35252554 ATGTGTCGTAGATATTTTTCGTAGGAAAACGGCCCCATGAGTATATAGCGCTAGAGTAGA```

When reads have been collected and processed, a new window will open in your web browser allowing you to browse reads supporting the reference and alternate alleles.

For the time being, use the mouse to pan and the scrollwheel (or double-clicking) to zoom in and out.


### Smith-Waterman Alignment

The Smith-Waterman Alignments are performed by https://github.com/mengyao/Complete-Striped-Smith-Waterman-Library, whose license requires the following statements:

Author: Mengyao Zhao & Wan-Ping Lee

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

