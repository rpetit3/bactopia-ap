### bioconda-nextflow-update Branch
This is a branch to migrate Staphopia to only use tools within Bioconda or scripts from the Staphopia project. The goal of this branch is to minimize the efforts required to get the pipeline up an running. 

As a consequence it will require that users have some form of conda installed to make use of Staphopia. But, this is more realistic then maintaining the 700mb tar ball of installations!


### TODO (no real order)
[] Add links to readme
[] Update Makefile to include conda installs
[] Remove Ruffus Scripts
[] Clean up the config file
[] Add script to verify all required programs are in the PATH
[] Update database for PROKKA annotation






### Staphopia Analysis Pipeline
Staphopia's analysis pipeline is primarily written in Python. There are however a few programs written in C++.

### Installation
[Fresh Ubuntu Server 14.04](https://github.com/staphopia/staphopia-ap/wiki/%5BWIP%5D-Setting-up-Staphopia-on-a-fresh-Ubuntu-Server-14.04-install)

### Tool Directory Overview
The `tool` directory houses a large number of the Staphopia dependencies. Below
is a list of of the included source/linux binary files. Links to both the tool
website and the download link originally used retrieve the file are included.
Each of the included files are unmodified and arte only included to reduce the
total number of downloads.

#### Tools

- **[Aspera Connect](http://downloads.asperasoft.com/connect2/)**
  * *Used to rapidly download public data from the ENA and SRA databases.*
  * Version 3.6.2
  * Original download link: http://download.asperasoft.com/download/sw/connect/3.6.2/aspera-connect-3.6.2.117442-linux-64.tar.gz
- **[bedtools](http://bedtools.readthedocs.org/en/latest/)**
  * Version 2.25.0
  * Original download link: https://github.com/arq5x/bedtools2/releases/download/v2.25.0/bedtools-2.25.0.tar.gz
- **[BLAST+](https://blast.ncbi.nlm.nih.gov/Blast.cgi?PAGE_TYPE=BlastDocs&DOC_TYPE=Download)**
  * *Used for gene annotation (Prokka) and MLST prediction*
  * Version 2.3.0
  * Original download link: ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.3.0/ncbi-blast-2.3.0+-x64-linux.tar.gz
- **[Bowtie2](http://bowtie-bio.sourceforge.net/bowtie2/index.shtml)**
  * *Used to align reads to the MLST loci during the SRST2 pipeline*
  * Version 2.2.4
  * Original download link: https://github.com/BenLangmead/bowtie2/archive/v2.2.4.tar.gz
- **[fastQValidator](https://github.com/staphopia/fastQValidator)**
  * *Used to quickly access the quality of a FASTQ file*
  * Version 0.1 modified for Staphopia usage
  * Original download link: https://github.com/staphopia/fastQValidator/archive/0.1.tar.gz
- **[Jellyfish](http://www.genome.umd.edu/jellyfish.html)**
  * *Used to count 31-mers in samples*
  * Version 2.2.4
  * Original download link: https://github.com/gmarcais/Jellyfish/releases/download/v2.2.4/jellyfish-2.2.4.tar.gz
- **[libStatGen](https://github.com/staphopia/libStatGen)**
  * *Required for fastQValidator*
  * Version 0.0.1 modified for Staphopia usage
  * Original download link: https://github.com/staphopia/libStatGen/archive/v0.0.1.tar.gz
- **[Samtools](http://samtools.sourceforge.net/)**
  * *This version is used specifically for the SRST2 pipeline*
  * Version 0.1.18
  * Original download link: https://github.com/lh3/samtools/archive/0.1.18.tar.gz
- **[Samtools](http://www.htslib.org/)**
  * Version 1.3
  * Original download link: https://github.com/samtools/samtools/releases/download/1.3/samtools-1.3.tar.bz2
- **[SPAdes](http://bioinf.spbau.ru/spades)**
  * *Used to create an assembly of the sample*
  * Version 3.7.1
  * Original download link: http://spades.bioinf.spbau.ru/release3.7.1/SPAdes-3.7.1-Linux.tar.gz
- **[SRST2](https://github.com/katholt/srst2)**
  * *Used to predict the MLST of a sample*
  * Version 0.1 mnodified for Staphopia use
  * Original download link: https://github.com/staphopia/srst2/archive/0.1.tar.gz

#### Python Modules `python-modules`

- [biopython](http://biopython.org/wiki/Main_Page)
  * Version 1.66
  * Original download link: https://github.com/biopython/biopython/archive/biopython-166.tar.gz
- [PyVCF](https://github.com/jamescasbon/PyVCF)
  * *Used to annotate VCF files*
  * Version 0.6.7
  * Original download link: https://pypi.python.org/packages/source/P/PyVCF/PyVCF-0.6.7.tar.gz
- [ruffus](http://www.ruffus.org.uk)
  * *Used to manage the pipeline*
  * Version 2.6.3
  * Original download link: https://github.com/bunbun/ruffus/archive/v2.6.3.tar.gz
- [ujson](https://github.com/esnme/ultrajson)
  * *Used to speed up JSON parsing*
  * Version 1.35
  * Original download link: https://github.com/esnme/ultrajson/archive/v1.35.tar.gz

### Contact
robert.petit@emory.edu
