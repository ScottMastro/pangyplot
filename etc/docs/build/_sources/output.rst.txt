.. _output:

Output
==================================

VikNGS will output the p-values calculated to a text file in the current directory (i.e. ".") by default. Output directory can be changed from the user interface or using ``-o [DIRECTORY]`` on the command line version. 

In addition to p-values, VikNGS can also produce a file detailing which variants were filtered out prior to testing and an explanation why. In future versions of the software, we hope to provide more types of output in addition to these files.


P-value File
------------------------------

This file will be produced upon completion of a series of association tests. Each line corresponds to a tested variant and records the resulting p-value. The file is tab-separated with the following columns:

``Chromosome  Position  Reference Alternative P-value TestName  CollapseGroupID``

``CollapseGroupID`` is only present if variants were collapsed into groups (single p-value per collapsed group).


Filtered File
------------------------------

This file explains which variants were filtered prior to testing and the reasoning behind the filter. Each line corresponds to a single variant. This file will only be written if "Explain Filter" is checked on the user interface or if ``--explain-filter`` is added when running VikNGS from the command line. The file is tab-separated with the following columns:

``Chromosome  Position  Reference Alternative Explanation``

The ``Explanation`` values refer to the following:

- Invalid information: variant was not properly parsed from the VCF file
- Not SNP: variant was filtered for not being a single nucleotide polymorphism
- PASS fail: **FILTER** column of VCF file did not report "PASS"
- Missing: variant was missing (e.x. "./.") more data than tolerable by the missing threshold parameter
- No variation: no variation detected in this particular variant (all individuals have the same genotype)
- MAF: variant has a minor allele frequency > the MAF threshold (rare test) or < the MAF threshold (common test)
