.PHONY: all test clean
TOP_DIR := $(shell pwd)
BIN=$(TOP_DIR)/bin
TOOLS=$(TOP_DIR)/tools
THIRD_PARTY := $(TOP_DIR)/src/third-party
THIRD_PARTY_PYTHON := $(TOP_DIR)/src/third-party/python
THIRD_PARTY_BIN := $(TOP_DIR)/bin/third-party
AWS_S3 := https://s3.amazonaws.com/analysis-pipeline/src
TEST_DATA := https://s3.amazonaws.com/analysis-pipeline/test-data

all: config python s3tools aspera fastq assembly mlst variants jellyfish sccmec annotation variants_pythonpath;

config: ;
	sed -i 's#^BASE_DIR.*#BASE_DIR = "$(TOP_DIR)"#' staphopia/config.py

clean-config: ;
	sed -i 's#^BASE_DIR.*#BASE_DIR = CHANGE_ME#' staphopia/config.py

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
python: ;
	pip install --target $(THIRD_PARTY)/python -r $(TOP_DIR)/requirements.txt

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
aspera: $(BIN)/ascp ;

$(BIN)/ascp : ;
	$(eval ASCP_BUILD=$(TOOLS)/aspera-connect/build)
	rm -rf $(ASCP_BUILD) && mkdir -p $(ASCP_BUILD)
	tar -C $(ASCP_BUILD) -xzvf $(TOOLS)/aspera-connect/aspera-connect-3.6.2.117442-linux-64.tar.gz
	sed -i 's=^INSTALL_DIR\=~/.aspera/connect$$=INSTALL_DIR\=$$1=' $(ASCP_BUILD)/aspera-connect-3.6.2.117442-linux-64.sh
	sh $(ASCP_BUILD)/aspera-connect-3.6.2.117442-linux-64.sh $(ASCP_BUILD)/aspera
	ln -s $(ASCP_BUILD)/aspera/bin/ascp $@
	ln -s $(ASCP_BUILD)/aspera/etc/asperaweb_id_dsa.openssh $(BIN)/asperaweb_id_dsa.openssh
	ln -s $(ASCP_BUILD)/aspera/etc/asperaweb_id_dsa.putty $(BIN)/asperaweb_id_dsa.putty

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
fastq: $(BIN)/fastq-validator $(BIN)/fastq-stats $(BIN)/fastq-interleave ;

$(BIN)/fastq-validator: ;
	$(eval FASTQ_BUILD=$(TOOLS)/fastq-validator/build)
	rm -rf $(FASTQ_BUILD) && mkdir -p $(FASTQ_BUILD)
	tar -C $(FASTQ_BUILD) -xzvf $(TOOLS)/fastq-validator/libStatGen-0.0.1.tar.gz
	mv $(FASTQ_BUILD)/libStatGen-0.0.1 $(FASTQ_BUILD)/libStatGen
	make -C $(FASTQ_BUILD)/libStatGen
	tar -C $(FASTQ_BUILD) -xzvf $(TOOLS)/fastq-validator/fastQValidator-0.1.tar.gz
	mv $(FASTQ_BUILD)/fastQValidator-0.1 $(FASTQ_BUILD)/fastQValidator
	make -C $(FASTQ_BUILD)/fastQValidator
	ln -s $(FASTQ_BUILD)/fastQValidator/bin/fastQValidator $@

$(BIN)/fastq-stats: ;
	g++ -Wall -O3 -o $@ $(TOP_DIR)/src/fastq-stats.cpp

$(BIN)/fastq-interleave: ;
	g++ -Wall -O3 -o $@ src/fastq-interleave.cpp

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
assembly: $(BIN)/kmergenie $(BIN)/velveth $(BIN)/spades.py $(BIN)/assemblathon-stats.pl ;

$(BIN)/kmergenie: ;
	$(eval KG_BUILD=$(TOOLS)/kmergenie/build)
	rm -rf $(KG_BUILD) && mkdir -p $(KG_BUILD)
	tar -C $(KG_BUILD) -xzvf $(TOOLS)/kmergenie/kmergenie-1.6982.tar.gz
	mv $(KG_BUILD)/kmergenie-1.6982 $(KG_BUILD)/kmergenie
	make -C $(KG_BUILD)/kmergenie/
	ln -s $(KG_BUILD)/kmergenie/kmergenie $@
	ln -s $(KG_BUILD)/kmergenie/specialk $(BIN)/specialk

$(BIN)/velveth: ;
	$(eval VELVET_BUILD=$(TOOLS)/velvet/build)
	rm -rf $(VELVET_BUILD) && mkdir -p $(VELVET_BUILD)
	tar -C $(VELVET_BUILD) -xzvf $(TOOLS)/velvet/velvet_1.2.10.tgz
	mv $(VELVET_BUILD)/velvet_1.2.10 $(VELVET_BUILD)/velvet
	make -C $(VELVET_BUILD)/velvet 'MAXKMERLENGTH=256' 'BIGASSEMBLY=1' 'LONGSEQUENCES=1' 'OPENMP=1'
	ln -s $(VELVET_BUILD)/velvet/velveth $@
	ln -s $(VELVET_BUILD)/velvet/velvetg $(BIN)/velvetg

$(BIN)/spades.py: ;
	$(eval SPADES_BUILD=$(TOOLS)/spades/build)
	rm -rf $(SPADES_BUILD) && mkdir -p $(SPADES_BUILD)
	tar -C $(SPADES_BUILD) -xzvf $(TOOLS)/spades/SPAdes-3.6.2-Linux.tar.gz
	mv $(SPADES_BUILD)/SPAdes-3.6.2-Linux $(SPADES_BUILD)/spades
	ln -s $(SPADES_BUILD)/spades/bin/spades.py $@

$(BIN)/assemblathon-stats.pl: ;
	$(eval ASTATS_BUILD=$(TOOLS)/assemblathon-stats/build)
	rm -rf $(ASTATS_BUILD) && mkdir -p $(ASTATS_BUILD)
	tar -C $(ASTATS_BUILD) -xzvf $(TOOLS)/assemblathon-stats/assemblathon-stats-0.1.tar.gz
	mv $(ASTATS_BUILD)/assemblathon2-analysis-0.1 $(ASTATS_BUILD)/assemblathon-stats
	sed -i 's=^use strict;=use lib "$(ASTATS_BUILD)/assemblathon-stats";\nuse strict;=' $(ASTATS_BUILD)/assemblathon-stats/assemblathon_stats.pl
	tar -C $(ASTATS_BUILD) -xzvf $(TOOLS)/assemblathon-stats/JSON-2.90.tar.gz
	mv $(ASTATS_BUILD)/JSON-2.90 $(ASTATS_BUILD)/JSON
	cd $(ASTATS_BUILD)/JSON && perl Makefile.PL PREFIX=$(ASTATS_BUILD)/JSON && cd $(TOP_DIR)
	make -C $(ASTATS_BUILD)/JSON
	make -C $(ASTATS_BUILD)/JSON install
	ln -s $(ASTATS_BUILD)/JSON/lib/JSON.pm $(ASTATS_BUILD)/assemblathon-stats/JSON.pm
	ln -s $(ASTATS_BUILD)/JSON/lib/JSON $(ASTATS_BUILD)/assemblathon-stats/JSON
	ln -s $(ASTATS_BUILD)/assemblathon-stats/assemblathon_stats.pl $@

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

samtools: $(BIN)/samtools-1.3 ;

$(BIN)/samtools-1.3: ;
	$(eval SAM_BUILD=$(TOOLS)/samtools/build)
	rm -rf $(SAM_BUILD) && mkdir -p $(SAM_BUILD)
	tar -C $(SAM_BUILD) -xjvf $(TOOLS)/samtools/samtools-1.3.tar.bz2
	mv $(SAM_BUILD)/samtools-1.3 $(SAM_BUILD)/samtools
	cd $(SAM_BUILD)/samtools/ && ./configure && cd $(TOP_DIR)
	make -C $(SAM_BUILD)/samtools
	ln -s $(SAM_BUILD)/samtools/samtools $(BIN)/samtools-1.3

bedtools: $(BIN)/bedtools ;

$(BIN)/bedtools: ;
	$(eval BED_BUILD=$(TOOLS)/bedtools/build)
	rm -rf $(BED_BUILD) && mkdir -p $(BED_BUILD)
	tar -C $(BED_BUILD) -xzvf $(TOOLS)/bedtools/bedtools-2.25.0.tar.gz
	mv $(BED_BUILD)/bedtools2 $(BED_BUILD)/bedtools
	make -C $(BED_BUILD)/bedtools
	ln -s $(BED_BUILD)/bedtools/bin/bedtools $(BIN)/bedtools
	ln -s $(BED_BUILD)/bedtools/bin/genomeCoverageBed $(BIN)/genomeCoverageBed

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
jellyfish: $(BIN)/jellyfish

$(BIN)/jellyfish: ;
	$(eval JF_BUILD=$(TOOLS)/jellyfish/build)
	rm -rf $(JF_BUILD) && mkdir -p $(JF_BUILD)
	tar -C $(JF_BUILD) -xzvf $(TOOLS)/jellyfish/jellyfish-2.2.4.tar.gz
	mv $(JF_BUILD)/jellyfish-2.2.4/ $(JF_BUILD)/jellyfish/
	cd $(JF_BUILD)/jellyfish/ && ./configure && cd $(TOP_DIR)
	make -C $(JF_BUILD)/jellyfish
	ln -s $(JF_BUILD)/jellyfish/bin/jellyfish $(BIN)/jellyfish

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
clean: clean-config ;
	rm -rf $(BIN)/*
	find tools/ | grep "/build$$" | xargs -I {} rm -rf {}
