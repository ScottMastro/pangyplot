.. _quick_start:

Quick Start
==================================

User Interface
------------------------------

To download VikNGS, go to the `GitHub repository release page <https://github.com/ScottMastro/VikNGS/releases/>`_ and find the latest release. The releases contains precompiled versions of VikNGS for Windows, Mac and Linux operating systems. Download the appropriate release ZIP folder for your opperating system.

Unzip the folder and running file VikNGS-X.X.X should start up the user interface. The available versions were compiled on the following systems, so please try to run it under a similar setting:

* Windows: Windows 10 64x (compiled with Microsoft Visual C++ 2017)

* Mac: macOS 10.13.4 High Sierra

* Linux: Ubuntu 18.04 64x

If there is an issue running the software, we recommend trying a different system or try :ref:`compiling the software from the source code<source_code>`.

Running Example on User Interface
------------------------------

In the same directory where the VikNGS-X.X.X application is found, two example files are present. Within the VikNGS interface, provide *example.vcf* as input in the section labelled "VCF File" and *example_info.txt* as input in the section labelled "Sample Information File". Clicking the "RUN" button should then trigger the association tests using these files as input.

Running Command Line
------------------------------

From the command line, run the following commands:

| ``wget https://github.com/ScottMastro/VikNGS/archive/master.zip``
| ``unzip master.zip``
| ``cd VikNGS-master/bin``
| ``make``

To test the binary executable file, try running the following command:

| ``./VikNGS --vcf ../example/example.vcf --sample ../example/example_info.txt``
