.. _tests:

Association Tests
==================================

Common Single Variant Association Test
----------------------------------

For both quantitative and binary trait analyses, a common variant test refers to a score test which has a Chi-squared distribution with 1 degree of freedom under no association hypothesis. The general form of the score test appears as follows:

    :math:`T={{S^2} \over var(S)}`

Where \\(T\\) is the test statistic following a Chi-squared distribution and \\(S\\) is the score. This test is used to perform a genetic association analysis between the phenotype \\(Y\\) and a single variant \\(G_j\\). For testing variant \\(j\\) given \\(n\\) individuals and phenotype vector \\(Y\\) and genotype matrix \\(G\\),

    :math:`S_j=\sum_{i=1}^n(Y_i-E(Y_i))G_{ij}`

    :math:`E(Y_i)=Y_i - \hat{Y}`

\\(E(Y_i)\\) is estimated from a vector of fitted values \\(\\hat{Y}\\) which is dependent on the underlying distribution of \\(Y\\) (ex. case-control vs quantatitive). With no covariates, \\(\\hat{Y}=\\bar{Y}\\) which is the simple average of the observed phenotypes. 

Under a case-control setting with no covariates, the score is an indication of how often the tested genotype appears in one group over the other. When coded as \\(Y_i=1\\) for cases and \\(Y_i=0\\) for controls, and genotypes coded as {0,1,2} corresponding to the number of alleles a particular individual possesses. Given this framework, cases with the allele of interest contribute positively to the overall score and controls contribute negatively. Therefore, the more a particular allele is associated with one group, the larger the magnitude of the score.

For genotypes coded strictly as {0,1,2}, the conventional variance formula is used to calculate \\(var(S_j)\\). To produce the test statistic \\(T_j\\), the square of the score \\(S_j\\) is normalized by the variance \\(var(S_j)\\) and a p-value is produced by evaluating \\(T_j\\) with respect to a Chi-squared distribution with 1 degree of freedom. In general, a large score and a small variance will result in a small (more significant) p-value.

In the vRVS methodology available in VikNGS, the genotype value \\(G_{ij}\\) is replaced with the expected genotype value calculated from the sequence read data \\(E(G_{ikj}\\mid D_{ikj})\\). When integrating data from an arbitrary number of cohorts, the variance is calculated for each group separately and summed together to produce \\(var(S_j)\\). The details of the derivation of \\(var(S_j)\\) are given in the Supplementary document of the VikNGS paper *VIKNGS: A C++ Variant Integration Kit for next generation sequencing association analysis*.

Rare Variant Association Test
----------------------------------

For joint variant analysis, the score statistics for \\(J\\) variants, \\(\\boldsymbol{S}=[S_1,...,S_J]\\). Please review the common variant section above to review the general structure of a score test. In VikNGS, multiple different genetic association tests are available which are described in the sections below.

For the CAST- and SKAT-like tests, we recommend the use of permutation to calculate p-values. This involves shuffling the phenotype vector \\(Y\\) and recalculating the p-value many times for every variant. After iteratively calculating a set of p-values, the final p-value is calculated based on the number of values that are less than or equal to the value that was calculated for the unshuffled data set divided by the number of iterations plus 1. 

.. note::
    Using permutation, the smallest p-value obtainable is 1/(# iterations + 1). Since this method can be very computationally expensive, an an early stopping procedure is available to terminate the calculation early if the p-value appears to be > 0.05. This uses the method designed by Jiang and Salzman (2012 `🔗 <https://www.ncbi.nlm.nih.gov/pubmed/23843675>`_).

When using expected genotypes and the vRVS methodology, the fact that data could be combined from multiple different cohorts prevents the use of a simple permutation test. Instead, the bootstrap approach defined by Derkach *et al*. (2012 `🔗 <https://www.ncbi.nlm.nih.gov/pubmed/24733292>`_) was adopted the for binary trait (case-control) analysis. Given a matrix of expected genotypes, the mean genotype is subtracted from each matrix element and rows are selected at random with replacement to form a shuffled matrix. This is done for every group separately. Covariates are also bootstrapped independently from the genotypes.  For quantitative trait analysis using expected genotypes, we implement the permutation methodology defined by Lin and Tang (2011 `🔗 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3169821/>`_) within each combined group.

.. warning::
    In VikNGS, these tests can be run by assuming the asymptotic distribution by setting the number of iterations to 1. Based on our limited testing, the results appear to behave as expected but we offer no statistical guarantees.
    
    
Linear Test (CAST-like)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This test related to the CAST method described by Morgenthaler and Thilly (2007 `🔗 <https://www.ncbi.nlm.nih.gov/pubmed/17101154>`_). In this test, a score vector of size \\(J\\) is calculated, each element corresponding to a different variant. Each score in the vector is calculated using the method described in the common variant section above. A single score value is produced by summing the elements of the score vector.

.. note::
   Since this test uses a sum of scores, it is very powerful when all variants have the same directional impact on disease risk. Combining protective and harmful variants in the same test will result in severely reduced statistical power.


Quadratic Test (SKAT-like)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This test related to the SKAT method described by Wu *et al*. (2011 `🔗 <https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3135811>`_). Similar to the linear test, a score vector of size \\(J\\) is calculated, each element corresponding to a different variant. Variants are weighted based on minor allele frequency (MAF): \\(w^{1/2}=1/[MAF(1-MAF)]^{1/2}\\). The p-value is calculated using the C++ code underlying the `CompQuadForm <https://cran.r-project.org/web/packages/CompQuadForm/index.html>`_ (Distribution Function of Quadratic Forms in Normal Variables) R library which is used in the R SKAT package.

.. note::
   This method should be preferred over the linear test when both protective and harmful variants being collapsed together (of if it is unclear whether the variants are potentially protective or harmful).

Likelihood Method (Coming soon)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This method refers to the test described in *Association testing for next-generation sequencing data using score statistics* _ from Skotte and Albrechtsen (2012 `🔗 <https://www.ncbi.nlm.nih.gov/pubmed/22570057>`_) Their method provides a score test where genotype calls are substituted by their expected values, \\(E(G_{ikj}\\mid D_{ikj})\\). The variance of the score test is obtained from the second derivative of the joint likelihood of the observed \\(Y_i\\) and the observed sequencing data, \\(D_{ij}\\) individual \\(i\\) at locus \\(j\\). The p-values are calculated using the asymptotic distribution of the score test. For a joint rare analysis of \\(J\\) variants, the score test is distributed as a chi-square distribution with \\(J\\) degrees of freedom.  This can also be used for common single variant association test which is distributed as chi-squared with one degree of freedom.
