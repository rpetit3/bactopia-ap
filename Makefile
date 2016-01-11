.PHONY: all test clean
TOP_DIR := $(shell pwd)
THIRD_PARTY := $(TOP_DIR)/src/third-party
THIRD_PARTY_PYTHON := $(TOP_DIR)/src/third-party/python
THIRD_PARTY_BIN := $(TOP_DIR)/bin/third-party
AWS_S3 := https://s3.amazonaws.com/analysis-pipeline/src
TEST_DATA := https://s3.amazonaws.com/analysis-pipeline/test-data

all: config python s3tools aspera fastq assembly mlst variants jellyfish sccmec variants_pythonpath;

config: ;
	sed -i 's#^BASE_DIR.*#BASE_DIR = "$(TOP_DIR)"#' staphopia/config.py

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
python: ;
	pip install --target $(THIRD_PARTY)/python -r $(TOP_DIR)/requirements.txt

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
s3tools: ;
	git clone git@github.com:staphopia/s3tools.git $(THIRD_PARTY)/s3tools
	pip install --target $(THIRD_PARTY)/python -r $(THIRD_PARTY)/s3tools/requirements.txt
	ln -s $(THIRD_PARTY)/s3tools/bin $(THIRD_PARTY_BIN)/s3tools

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
aspera: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/aspera-connect-3.5.1.92523-linux-64.sh
	sh $(THIRD_PARTY)/aspera-connect-3.5.1.92523-linux-64.sh $(THIRD_PARTY)/aspera
	ln -s $(THIRD_PARTY)/aspera/bin/ascp $(THIRD_PARTY_BIN)/ascp
	ln -s $(THIRD_PARTY)/aspera/etc/asperaweb_id_dsa.openssh $(THIRD_PARTY_BIN)/asperaweb_id_dsa.openssh
	ln -s $(THIRD_PARTY)/aspera/etc/asperaweb_id_dsa.putty $(THIRD_PARTY_BIN)/asperaweb_id_dsa.putty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
fastq: fastq_validator fastq_stats fastq_interleave ;

fastq_validator: ;
	git clone git@github.com:staphopia/fastQValidator.git $(THIRD_PARTY)/fastQValidator
	git clone git@github.com:staphopia/libStatGen.git $(THIRD_PARTY)/libStatGen
	make -C $(THIRD_PARTY)/libStatGen
	make -C $(THIRD_PARTY)/fastQValidator
	ln -s $(THIRD_PARTY)/fastQValidator/bin/fastQValidator $(THIRD_PARTY_BIN)/fastq_validator

fastq_stats: ;
	g++ -Wall -O3 -o bin/fastq_stats src/fastq_stats.cpp

fastq_interleave: ;
	g++ -Wall -O3 -o bin/fastq_interleave src/fastq_interleave.cpp

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
assembly: kmergenie velvet spades assemblathon2_analysis ;

kmergenie: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/kmergenie-1.6741.tar.gz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/kmergenie-1.6741.tar.gz && mv $(THIRD_PARTY)/kmergenie-1.6741 $(THIRD_PARTY)/kmergenie
	make -C $(THIRD_PARTY)/kmergenie/
	ln -s $(THIRD_PARTY)/kmergenie/kmergenie $(THIRD_PARTY_BIN)/kmergenie
	ln -s $(THIRD_PARTY)/kmergenie/specialk $(THIRD_PARTY_BIN)/specialk

velvet: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/velvet_1.2.10.tgz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/velvet_1.2.10.tgz && mv $(THIRD_PARTY)/velvet_1.2.10 $(THIRD_PARTY)/velvet
	make -C $(THIRD_PARTY)/velvet 'MAXKMERLENGTH=256' 'BIGASSEMBLY=1' 'LONGSEQUENCES=1' 'OPENMP=1'
	ln -s $(THIRD_PARTY)/velvet/velveth $(THIRD_PARTY_BIN)/velveth
	ln -s $(THIRD_PARTY)/velvet/velvetg $(THIRD_PARTY_BIN)/velvetg

spades: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/SPAdes-3.1.1-Linux.tar.gz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/SPAdes-3.1.1-Linux.tar.gz && mv $(THIRD_PARTY)/SPAdes-3.1.1-Linux $(THIRD_PARTY)/spades
	ln -s $(THIRD_PARTY)/spades/bin/spades.py $(THIRD_PARTY_BIN)/spades.py

assemblathon2_analysis: ;
	git clone git@github.com:staphopia/assemblathon2-analysis.git $(THIRD_PARTY)/assemblathon2-analysis
	sed -i 's=^use strict;=use lib "$(THIRD_PARTY)/assemblathon2-analysis";\nuse strict;=' $(THIRD_PARTY)/assemblathon2-analysis/assemblathon_stats.pl
	wget -P $(THIRD_PARTY) $(AWS_S3)/JSON-2.90.tar.gz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/JSON-2.90.tar.gz && mv $(THIRD_PARTY)/JSON-2.90 $(THIRD_PARTY)/JSON
	cd $(THIRD_PARTY)/JSON && perl Makefile.PL PREFIX=$(THIRD_PARTY)/JSON && cd $(TOP_DIR)
	make -C $(THIRD_PARTY)/JSON
	make -C $(THIRD_PARTY)/JSON install
	ln -s $(THIRD_PARTY)/JSON/lib/JSON.pm $(THIRD_PARTY)/assemblathon2-analysis/JSON.pm
	ln -s $(THIRD_PARTY)/JSON/lib/JSON $(THIRD_PARTY)/assemblathon2-analysis/JSON
	ln -s $(THIRD_PARTY)/assemblathon2-analysis/assemblathon_stats.pl $(THIRD_PARTY_BIN)/assemblathon_stats.pl

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
mlst: blast srst2 bowtie2 samtools_0118 ;

blast: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/ncbi-blast-2.2.29%2B-x64-linux.tar.gz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/ncbi-blast-2.2.29+-x64-linux.tar.gz && mv $(THIRD_PARTY)/ncbi-blast-2.2.29+ $(THIRD_PARTY)/ncbi-blast
	ln -s $(THIRD_PARTY)/ncbi-blast/bin/blastn $(THIRD_PARTY_BIN)/blastn
	ln -s $(THIRD_PARTY)/ncbi-blast/bin/blastp $(THIRD_PARTY_BIN)/blastp
	ln -s $(THIRD_PARTY)/ncbi-blast/bin/blastx $(THIRD_PARTY_BIN)/blastx
	ln -s $(THIRD_PARTY)/ncbi-blast/bin/tblastn $(THIRD_PARTY_BIN)/tblastn
	ln -s $(THIRD_PARTY)/ncbi-blast/bin/tblastx $(THIRD_PARTY_BIN)/tblastx
	ln -s $(THIRD_PARTY)/ncbi-blast/bin/makeblastdb $(THIRD_PARTY_BIN)/makeblastdb

srst2: ;
	git clone git@github.com:staphopia/srst2.git $(THIRD_PARTY)/srst2
	chmod 755 $(THIRD_PARTY)/srst2/scripts/getmlst.py
	ln -s $(THIRD_PARTY)/srst2/scripts/getmlst.py $(THIRD_PARTY_BIN)/getmlst.py
	ln -s $(THIRD_PARTY)/srst2/scripts/srst2.py $(THIRD_PARTY_BIN)/srst2.py

bowtie2: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/bowtie2-2.1.0-linux-x86_64.zip
	unzip $(THIRD_PARTY)/bowtie2-2.1.0-linux-x86_64.zip -d $(THIRD_PARTY)/ && mv $(THIRD_PARTY)/bowtie2-2.1.0 $(THIRD_PARTY)/bowtie2
	ln -s $(THIRD_PARTY)/bowtie2/bowtie2 $(THIRD_PARTY_BIN)/bowtie2
	ln -s $(THIRD_PARTY)/bowtie2/bowtie2-align $(THIRD_PARTY_BIN)/bowtie2-align
	ln -s $(THIRD_PARTY)/bowtie2/bowtie2-build $(THIRD_PARTY_BIN)/bowtie2-build
	ln -s $(THIRD_PARTY)/bowtie2/bowtie2-inspect $(THIRD_PARTY_BIN)/bowtie2-inspect

samtools_0118: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/samtools-0.1.18.tar.bz2
	tar -C $(THIRD_PARTY) -xjvf $(THIRD_PARTY)/samtools-0.1.18.tar.bz2&& mv $(THIRD_PARTY)/samtools-0.1.18 $(THIRD_PARTY)/samtools_0118
	make -C $(THIRD_PARTY)/samtools_0118
	ln -s $(THIRD_PARTY)/samtools_0118/samtools $(THIRD_PARTY_BIN)/samtools

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
variants: ;
	git clone https://github.com/rpetit3-science/call_variants.git $(THIRD_PARTY)/call_variants
	make -C $(THIRD_PARTY)/call_variants
	make -C $(THIRD_PARTY)/call_variants test
	ln -s $(THIRD_PARTY)/call_variants/bin/call_variants $(THIRD_PARTY_BIN)/call_variants

variants_pythonpath: ;
	make -C $(THIRD_PARTY)/call_variants add_to_profile

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
sccmec: samtools bedtools;

samtools: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/samtools-bcftools-htslib-1.0_x64-linux.tar.bz2
	tar -C $(THIRD_PARTY) -xjvf $(THIRD_PARTY)/samtools-bcftools-htslib-1.0_x64-linux.tar.bz2 && mv $(THIRD_PARTY)/samtools-bcftools-htslib-1.0_x64-linux $(THIRD_PARTY)/samtools
	ln -s $(THIRD_PARTY)/samtools/bin/samtools $(THIRD_PARTY_BIN)/samtools-1.0

bedtools: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/bedtools-2.20.1.tar.gz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/bedtools-2.20.1.tar.gz && mv $(THIRD_PARTY)/bedtools2-2.20.1 $(THIRD_PARTY)/bedtools
	make -C $(THIRD_PARTY)/bedtools
	ln -s $(THIRD_PARTY)/bedtools/bin/bedtools $(THIRD_PARTY_BIN)/bedtools
	ln -s $(THIRD_PARTY)/bedtools/bin/genomeCoverageBed $(THIRD_PARTY_BIN)/genomeCoverageBed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
jellyfish: ;
	wget -P $(THIRD_PARTY) $(AWS_S3)/jellyfish-2.1.4.tar.gz
	tar -C $(THIRD_PARTY) -xzvf $(THIRD_PARTY)/jellyfish-2.1.4.tar.gz && mv $(THIRD_PARTY)/jellyfish-2.1.4/ $(THIRD_PARTY)/jellyfish/
	cd $(THIRD_PARTY)/jellyfish/ && ./configure && cd $(TOP_DIR)
	make -C $(THIRD_PARTY)/jellyfish
	ln -s $(THIRD_PARTY)/jellyfish/bin/jellyfish $(THIRD_PARTY_BIN)/jellyfish

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
annotation: prokka barrnap ;

prokka: ;
	git clone git@github.com:tseemann/prokka.git $(THIRD_PARTY)/prokka
	ln -s $(THIRD_PARTY)/prokka/bin $(THIRD_PARTY_BIN)/prokka
	ln -s $(TOP_DIR)/tool-data/annotation/staphylococcus-uniref90.prokka $(THIRD_PARTY)/prokka/db/genus/Staphylococcus-uniref90
	rm $(THIRD_PARTY)/prokka/db/kingdom/Bacteria/sprot
	ln -s $(TOP_DIR)/tool-data/annotation/bacteria-uniref90.prokka $(THIRD_PARTY)/prokka/db/kingdom/Bacteria/sprot
	$(THIRD_PARTY_BIN)/prokka/prokka --setupdb

barrnap: ;
	git clone git@github.com:tseemann/barrnap.git $(THIRD_PARTY)/barrnap
	ln -s $(THIRD_PARTY)/barrnap/bin/barrnap $(THIRD_PARTY_BIN)/barrnap

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
test: ;
	wget -P $(TOP_DIR)/test-data $(TEST_DATA)/test_genome.fastq.gz
	mkdir $(TOP_DIR)/test/test-pipeline
	ln -s $(TOP_DIR)/test-data/test_genome.fastq.gz $(TOP_DIR)/test/test-pipeline/test_genome.fastq.gz
	python $(TOP_DIR)/bin/pipelines/create_job_script --input $(TOP_DIR)/test/test-pipeline/test_genome.fastq.gz --working_dir $(TOP_DIR)/test/test-pipeline --processors 23  --sample_tag tester --log_times > $(TOP_DIR)/test/test-pipeline/job_script.sh
	cd $(TOP_DIR)/test/test-pipeline && sh $(TOP_DIR)/test/test-pipeline/job_script.sh

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
clean: ;
	rm -rf $(THIRD_PARTY)/*
	rm -rf $(THIRD_PARTY_BIN)/*
	rm -rf $(TOP_DIR)/test/test-pipeline
	rm -rf $(TOP_DIR)/test-data/test_genome.fastq.gz
	rm -f bin/fastq_interleave
	rm -f bin/fastq_stats
	sed -i 's#^BASE_DIR.*#BASE_DIR = CHANGE_ME#' staphopia/config.py

