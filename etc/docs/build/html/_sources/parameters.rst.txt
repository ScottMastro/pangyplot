Choosing Parameters
==================================

Command Line Parameters
------------------------------

A command line version of vikNGS is available for users who wish to do association testing without running a user interface. The command line tool requires specification of a :ref:`multisample VCF file <multisample_vcf>` and corresponding :ref:`sample information file <sample_info>`. By default, the command will run a common association tests on a single thread.

==================== ================= =============== 
Parameter            Value/Default     Description
==================== ================= ===============
**-\\-vcf, -i**      [DIRECTORY]       Directory of a multisample VCF file (required)   
**-\\-sample, -g**   [DIRECTORY]       Directory of a file containing sample information (required)
**-\\-bed,-b**       [DIRECTORY]       directory of a BED file for collapsing variants
**-\\-out, -o**      [DIRECTORY]= .    Directory for output (defaults to current directory)
**-\\-help, -h**                       Print a help message and exit
**-\\-common, -c**                     Perform a common variant association test (default)
**-\\-rare, -r**     [TEST NAME]       Perform a rare variant association test
**-\\-boot, -n**     [INT]=1000         Number of bootstrap iterations to calculate
**-\\-stop, -s**                       Stop bootstrapping if p-value looks to be > 0.05
**-\\-collapse, -k** [INT]=5           Collapse every k variants (rare only)
**-\\-gene**                           Collapse variants by gene if BED file specified (default)
**-\\-exon**                           Collapse variants by exon if BED file specified
**-\\-from**         [INT]             Only include variants with **POS** larger than this value
**-\\-to**           [INT]             Only include variants with **POS** smaller than this value
**-\\-chr**          [CHR NAME]	       Only include variants on this chromosome
**-\\-maf, -m**      [FLOAT]=0.05      Minor allele frequency cut-off (common-rare threshold)
**-\\-depth, -d**    [INT]=30          Read depth cut-off (low-high read depth threshold)
**-\\-missing, -x**  [FLOAT]=0.1       Missing data cut-off (maximum tolerance for missing data)
**-\\-all, -a**                        Include variants which do not have *PASS* in the **FILTER** column
**-\\-threads, -t**  [INT]=1           Number of threads
**-\\-batch, -h**    [INT]=1000        Number of variants to read from VCF before beginning tests
==================== ================= ===============

TODO: TEST THESE EXAMPLES

**Example 1.** Running a common test on 16 threads for variants on chromosome 7 with minor allele frequency > 10% and ignoring what is in the **FILTER** column of the VCF: ::

    ./vikNGS --vcf [...] --sample [...] --chr chr7 -m 0.1 --all -t 16

**Example 2.** Running a rare test (CAST) on 4 threads, collapsing variants along genes and using one million bootstrap iterations with early stopping: ::

    ./vikNGS --vcf [...] --sample [...] --bed [...] -r CAST --gene -n 1000000 --stop -t 4


.. _explain_param:

Parameter Explaination
------------------------------

Minor Allele Frequency Cutoff 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

While reading the VCF file, vikNGS computes an allele frequency for each variant. The minor allele frequency (MAF) is estimated only using the samples included in the multisample VCF file. The MAF cutoff is used to define which variants are considered "rare" versus "common". When running a common association test, variants with estimated minor allele frequencies *less than* the MAF cutoff (ie. rare variants) will be excluded from testing. Likewise, when running a rare association test, variants with estimated minor allele frequencies *greater than* the MAF cutoff (ie. common variants) will be excluded from testing.

Missing Data Threshold 
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Variants may have ambiguous or missing genotype information (ex. **GT** = ./.) for some of the individuals in the multisample VCF file. If too much data is missing, association tests may produce misleading results. Any variant that is missing more data than this threshold will be excluded from testing. The default value is 0.1 which means if more than 10% of sample calls cannot be determined, the variant will be ignored.

.. note::
     If running a quantitative association test, the proportion of missing data will be calculated from all samples. In a case-control test, two proportions will be calculated (one for all cases, one for all controls) if either cases *or* controls fail to satisfy the missing threshold, the variant will be excluded.

Filter By Genomic Coordinate
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enables filtering of variants based on the **CHR** and **POS** values in the VCF file. Variants outside a specific chromosome or range of positions can be excluded.

Must *PASS*
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Variants which do not contain *PASS* in the **FILTER** column of the VCF are filtered out. By default this filtering step is on, turning it off will cause the contents of the **FILTER** column to be ignored.

Read Depth High/Low Cutoff
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO
samples with read depth above this threshold are considered high read depth samples (default=30).


Collapse Variants
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

Rare vs Common Testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

See information on the  :ref:`Tests <tests>` page for details. 

Bootstrap and Early Stopping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

Threads and Batch Size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

Plot Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only available on the graphical user interface. A plotting interface will be displayed following the association testing in a new window if this setting is checked.


