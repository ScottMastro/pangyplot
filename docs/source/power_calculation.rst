Power Simulation Package
==================================
Power simulation package can be used for two purposes:

Type I error: The user can test the performance of the association tests with respect to the control of Type I error under different sequencing settings, e.g. different combinations of read depths with varying sample sizes, different base calling errors. In this setting odds ratio (\\(OR\\)) for a binary trait analysis is set to 1, and the proportion of variation explained by the genetic effect (\\(R^2\\)-coefficient of determination) for quantitative trait analysis is set to 0.

Power analysis: The user can calculate the minimum sample size required to detect a prespecified effect size, e.g. \\(OR=1.2\\) for a binary trait analysis and (\\(R^2=0.1\\) for quantitative trait analysis. 

Parameters
------------------------------

Many parameters are unique to the simulation package. Please check the :ref:`relevant section <explain_param>` for information regarding parameters not specific to this component. 

Phenotype and Cohort Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Data can be simulated for either a case-control phenotype or a Normally distributed quantitative phenotype. The mean and standard deviation of the Normal phenotype can be altered but these parameters have little to no influence on the result. Groups of individuals are specified in a table. The size of each group can be a single value or a range (annotated as two numbers separated by a colon ":", e.g. 500:1500). If a range is given, the simulation will run multiple times with the sample size of the group increasing from the low end of the range to the high end. The "Cohort" column of the table indicates case/control status or will simply say "quantitative" depending on the distribution of the phenotype. The "Mean Depth" and "Depth SD" refer to the average read depth and standard deviation for each simulated group. The package will simulate a set of reads for each variant and the read depth will be sampled from a Normal distribution with these parameters. "Error Rate" is the base calling error rate. A value of 0.01 means that 1% of all the reads will report an incorrect base call for a given variant.

Variant Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Effect size (odds ratio for case-control and \\(R^2\\) correlation for quantitative) determines the strength of the relationship between the genotype and the phenotype. An odds ratio of 1 or an \\(R^2\\) of 0 is what is used to simulate data under the null hypothesis (no association). A range of minor allele frequencies (MAFs) must also be provided. For each variant, the true MAF is selected uniformly at random for each variant. The minor allele is always simulated to be the causal variant.

Phenotype and Cohort Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
High/low cut-off defines the value which discriminates between high and low read depth groups. A high/low cut-off of 30 indicates that cohorts with a mean read depth less than 30x will be considered a low read depth cohort. This parameter is used by vRVS. Changing the number of steps alters the sample size increment on the cohort table (e.g. given a sample size of 500:1500 defined for controls and steps=3, three sets of simulations will run with the number of controls as 500, 1000 and 1500). The results will be saved and plotted on the sample size versus power graph.  

Output
------------------------------
The program generates a Q-Q plot and histograms of the p-values when Type I error rate is of interest. For power analysis, the relationship between power and sample size can be studied by changing the step size and the sample size values in the cohort table. 
