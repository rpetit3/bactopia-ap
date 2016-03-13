.PHONY: all test clean
PWD := $(shell pwd)
BIN=$(PWD)/bin
PATH := $(BIN):$(PATH)
LIBS=$(PWD)/libs
TOOLS=$(PWD)/tools
TEST_DATA := https://s3.amazonaws.com/analysis-pipeline/test-data

all: config python aspera staphopia fastq assembly mlst sccmec jellyfish variants annotation;

config: ;
	sed -i 's#^BASE_DIR.*#BASE_DIR = "$(PWD)"#' staphopia/config.py


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
python: $(LIBS)/python/easy_install.py ;
$(LIBS)/python/easy_install.py: ;
	pip install --target $(LIBS)/python -r $(PWD)/requirements.txt


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
staphopia: staphopia-scripts staphopia-pipelines staphopia-python;
staphopia-scripts: $(BIN)/unprocessed_ena ;
$(BIN)/unprocessed_ena: ;
	ls $(TOOLS)/staphopia | xargs -I {} ln -s $(TOOLS)/staphopia/{} $(BIN)/{}

staphopia-pipelines: $(BIN)/submit_job ;
$(BIN)/submit_job: ;
	ls $(TOOLS)/staphopia-pipelines | xargs -I {} ln -s $(TOOLS)/staphopia-pipelines/{} $(BIN)/{}

staphopia-python: $(LIBS)/python/staphopia
$(LIBS)/python/staphopia: ;
	ln -s $(PWD)/staphopia $(LIBS)/python/staphopia

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
	g++ -Wall -O3 -o $@ $(PWD)/src/fastq-stats.cpp

$(BIN)/fastq-interleave: ;
	g++ -Wall -O3 -o $@ $(PWD)/src/fastq-interleave.cpp


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
assembly: $(BIN)/spades.py $(BIN)/assemblathon-stats.pl ;

$(BIN)/spades.py: ;
	$(eval SPADES_BUILD=$(TOOLS)/spades/build)
	rm -rf $(SPADES_BUILD) && mkdir -p $(SPADES_BUILD)
	tar -C $(SPADES_BUILD) -xzvf $(TOOLS)/spades/SPAdes-3.7.1-Linux.tar.gz
	mv $(SPADES_BUILD)/SPAdes-3.7.1-Linux $(SPADES_BUILD)/spades
	ln -s $(SPADES_BUILD)/spades/bin/spades.py $@

$(BIN)/assemblathon-stats.pl: ;
	$(eval ASTATS_BUILD=$(TOOLS)/assemblathon-stats/build)
	rm -rf $(ASTATS_BUILD) && mkdir -p $(ASTATS_BUILD)
	tar -C $(ASTATS_BUILD) -xzvf $(TOOLS)/assemblathon-stats/assemblathon-stats-0.1.tar.gz
	mv $(ASTATS_BUILD)/assemblathon2-analysis-0.1 $(ASTATS_BUILD)/assemblathon-stats
	sed -i 's=^use strict;=use lib "$(ASTATS_BUILD)/assemblathon-stats";\nuse strict;=' $(ASTATS_BUILD)/assemblathon-stats/assemblathon_stats.pl
	tar -C $(ASTATS_BUILD) -xzvf $(TOOLS)/assemblathon-stats/JSON-2.90.tar.gz
	mv $(ASTATS_BUILD)/JSON-2.90 $(ASTATS_BUILD)/JSON
	cd $(ASTATS_BUILD)/JSON && perl Makefile.PL PREFIX=$(ASTATS_BUILD)/JSON && cd $(PWD)
	make -C $(ASTATS_BUILD)/JSON
	make -C $(ASTATS_BUILD)/JSON install
	ln -s $(ASTATS_BUILD)/JSON/lib/JSON.pm $(ASTATS_BUILD)/assemblathon-stats/JSON.pm
	ln -s $(ASTATS_BUILD)/JSON/lib/JSON $(ASTATS_BUILD)/assemblathon-stats/JSON
	ln -s $(ASTATS_BUILD)/assemblathon-stats/assemblathon_stats.pl $@


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
mlst: $(BIN)/makeblastdb $(BIN)/srst2.py $(BIN)/bowtie2 $(BIN)/samtools ;

$(BIN)/makeblastdb: ;
	$(eval BLAST_BUILD=$(TOOLS)/blast+/build)
	rm -rf $(BLAST_BUILD) && mkdir -p $(BLAST_BUILD)
	cat $(TOOLS)/blast+/ncbi-blast-2.3.0+-x64-linux.tar.gz.part0* | tar -C $(BLAST_BUILD) -xzvf -
	mv $(BLAST_BUILD)/ncbi-blast-2.3.0+ $(BLAST_BUILD)/blast
	ln -s $(BLAST_BUILD)/blast/bin/blastn $(BIN)/blastn
	ln -s $(BLAST_BUILD)/blast/bin/blastp $(BIN)/blastp
	ln -s $(BLAST_BUILD)/blast/bin/blastx $(BIN)/blastx
	ln -s $(BLAST_BUILD)/blast/bin/tblastn $(BIN)/tblastn
	ln -s $(BLAST_BUILD)/blast/bin/tblastx $(BIN)/tblastx
	ln -s $(BLAST_BUILD)/blast/bin/makeblastdb $@

$(BIN)/srst2.py: ;
	$(eval SRST_BUILD=$(TOOLS)/srst2/build)
	rm -rf $(SRST_BUILD) && mkdir -p $(SRST_BUILD)
	tar -C $(SRST_BUILD) -xzvf $(TOOLS)/srst2/srst2-0.1.tar.gz
	mv $(SRST_BUILD)/srst2-0.1 $(SRST_BUILD)/srst2
	chmod 755 $(SRST_BUILD)/srst2/scripts/getmlst.py
	ln -s $(SRST_BUILD)/srst2/scripts/getmlst.py $(BIN)/getmlst.py
	ln -s $(SRST_BUILD)/srst2/scripts/srst2.py $@

$(BIN)/bowtie2: ;
	$(eval BOWTIE_BUILD=$(TOOLS)/bowtie2/build)
	rm -rf $(BOWTIE_BUILD) && mkdir -p $(BOWTIE_BUILD)
	unzip $(TOOLS)/bowtie2/bowtie2-2.2.4-linux-x86_64.zip -d $(BOWTIE_BUILD)/
	mv $(BOWTIE_BUILD)/bowtie2-2.2.4 $(BOWTIE_BUILD)/bowtie2
	ln -s $(BOWTIE_BUILD)/bowtie2/bowtie2 $@
	ln -s $(BOWTIE_BUILD)/bowtie2/bowtie2-align $(BIN)/bowtie2-align
	ln -s $(BOWTIE_BUILD)/bowtie2/bowtie2-build $(BIN)/bowtie2-build
	ln -s $(BOWTIE_BUILD)/bowtie2/bowtie2-inspect $(BIN)/bowtie2-inspect

$(BIN)/samtools: ;
	$(eval SAM18_BUILD=$(TOOLS)/samtools-0.1.18/build)
	rm -rf $(SAM18_BUILD) && mkdir -p $(SAM18_BUILD)
	tar -C $(SAM18_BUILD) -xjvf $(TOOLS)/samtools-0.1.18/samtools-0.1.18.tar.bz2
	mv $(SAM18_BUILD)/samtools-0.1.18 $(SAM18_BUILD)/samtools_0118
	make -C $(SAM18_BUILD)/samtools_0118
	ln -s $(SAM18_BUILD)/samtools_0118/samtools $@


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
sccmec: $(BIN)/samtools-1.3 $(BIN)/bedtools;

$(BIN)/samtools-1.3: ;
	$(eval SAM_BUILD=$(TOOLS)/samtools/build)
	rm -rf $(SAM_BUILD) && mkdir -p $(SAM_BUILD)
	tar -C $(SAM_BUILD) -xjvf $(TOOLS)/samtools/samtools-1.3.tar.bz2
	mv $(SAM_BUILD)/samtools-1.3 $(SAM_BUILD)/samtools
	cd $(SAM_BUILD)/samtools/ && ./configure && cd $(PWD)
	make -C $(SAM_BUILD)/samtools
	ln -s $(SAM_BUILD)/samtools/samtools $@

$(BIN)/bedtools: ;
	$(eval BED_BUILD=$(TOOLS)/bedtools/build)
	rm -rf $(BED_BUILD) && mkdir -p $(BED_BUILD)
	tar -C $(BED_BUILD) -xzvf $(TOOLS)/bedtools/bedtools-2.25.0.tar.gz
	mv $(BED_BUILD)/bedtools2 $(BED_BUILD)/bedtools
	make -C $(BED_BUILD)/bedtools
	ln -s $(BED_BUILD)/bedtools/bin/bedtools $@
	ln -s $(BED_BUILD)/bedtools/bin/genomeCoverageBed $(BIN)/genomeCoverageBed


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
jellyfish: $(BIN)/jellyfish

$(BIN)/jellyfish: ;
	$(eval JF_BUILD=$(TOOLS)/jellyfish/build)
	rm -rf $(JF_BUILD) && mkdir -p $(JF_BUILD)
	tar -C $(JF_BUILD) -xzvf $(TOOLS)/jellyfish/jellyfish-2.2.4.tar.gz
	mv $(JF_BUILD)/jellyfish-2.2.4/ $(JF_BUILD)/jellyfish/
	cd $(JF_BUILD)/jellyfish/ && ./configure && cd $(PWD)
	make -C $(JF_BUILD)/jellyfish
	ln -s $(JF_BUILD)/jellyfish/bin/jellyfish $@


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
variants: $(BIN)/bwa $(BIN)/java7 $(BIN)/java8 $(BIN)/picard.jar $(BIN)/GenomeAnalysisTK.jar $(BIN)/vcf-annotator $(BIN)/samtools-1.3;

$(BIN)/bwa: ;
	$(eval BWA_BUILD=$(TOOLS)/bwa/build)
	rm -rf $(BWA_BUILD) && mkdir -p $(BWA_BUILD)
	tar -C $(BWA_BUILD) -xzvf $(TOOLS)/bwa/bwa-0.7.13.tar.gz
	mv $(BWA_BUILD)/bwa-0.7.13 $(BWA_BUILD)/bwa
	make -C $(BWA_BUILD)/bwa
	ln -s $(BWA_BUILD)/bwa/bwa $@

$(BIN)/java7: ;
	$(eval JAVA7_BUILD=$(TOOLS)/java7/build)
	rm -rf $(JAVA7_BUILD) && mkdir -p $(JAVA7_BUILD)
	cat $(TOOLS)/java7/jdk-7u79-linux-x64.tar.gz.part0* | tar -C $(JAVA7_BUILD) -xzvf -
	mv $(JAVA7_BUILD)/jdk1.7.0_79 $(JAVA7_BUILD)/jdk
	ln -s $(JAVA7_BUILD)/jdk/bin/java $@

$(BIN)/java8: ;
	$(eval JAVA8_BUILD=$(TOOLS)/java8/build)
	rm -rf $(JAVA8_BUILD) && mkdir -p $(JAVA8_BUILD)
	cat $(TOOLS)/java8/jdk-8u73-linux-x64.tar.gz.part0* | tar -C $(JAVA8_BUILD) -xzvf -
	mv $(JAVA8_BUILD)/jdk1.8.0_73 $(JAVA8_BUILD)/jdk
	ln -s $(JAVA8_BUILD)/jdk/bin/java $@

$(BIN)/picard.jar: ;
	$(eval PICARD_BUILD=$(TOOLS)/picard-tools/build)
	rm -rf $(PICARD_BUILD) && mkdir -p $(PICARD_BUILD)
	tar -C $(PICARD_BUILD) -xzvf $(TOOLS)/picard-tools/picard-tools-2.1.1.tar.gz
	mv $(PICARD_BUILD)/picard-tools-2.1.1 $(PICARD_BUILD)/picard-tools
	ln -s $(PICARD_BUILD)/picard-tools/picard.jar $@

$(BIN)/GenomeAnalysisTK.jar: ;
	$(eval GATK_BUILD=$(TOOLS)/gatk/build)
	rm -rf $(GATK_BUILD) && mkdir -p $(GATK_BUILD)
	tar -C $(GATK_BUILD) -xjvf $(TOOLS)/gatk/GenomeAnalysisTK-3.5.tar.bz2
	ln -s $(GATK_BUILD)/GenomeAnalysisTK.jar $@

$(BIN)/vcf-annotator: ;
	$(eval VCF_BUILD=$(TOOLS)/vcf-annotator/build)
	rm -rf $(VCF_BUILD) && mkdir -p $(VCF_BUILD)
	tar -C $(VCF_BUILD) -xzvf $(TOOLS)/vcf-annotator/vcf-annotator-0.1.tar.gz
	mv $(VCF_BUILD)/vcf-annotator-0.1 $(VCF_BUILD)/vcf-annotator
	ln -s $(VCF_BUILD)/vcf-annotator/vcfannotator $(LIBS)/python/vcfannotator
	ln -s $(VCF_BUILD)/vcf-annotator/bin/vcf-annotator $@


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
annotation: prokka barrnap prokka-setupdb;

prokka: $(BIN)/prokka ;
$(BIN)/prokka: ;
	$(eval PROKKA_BUILD=$(TOOLS)/prokka/build)
	rm -rf $(PROKKA_BUILD) && mkdir -p $(PROKKA_BUILD)
	cat $(TOOLS)/prokka/prokka-1.11.1.tar.gz.part0* | tar -C $(PROKKA_BUILD) -xzvf -
	mv $(PROKKA_BUILD)/prokka-1.11.1 $(PROKKA_BUILD)/prokka
	ln -s $(PWD)/data/annotation/staphylococcus-uniref90.prokka $(PROKKA_BUILD)/prokka/db/genus/Staphylococcus-uniref90
	rm $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot
	ln -s $(PWD)/data/annotation/bacteria-uniref90.prokka $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot
	ls $(PROKKA_BUILD)/prokka/bin | xargs -I {} ln -s $(PROKKA_BUILD)/prokka/bin/{} $(BIN)/{}

prokka-setupdb: $(TOOLS)/prokka/build/prokka/db/kingdom/Bacteria/sprot.psq ;
$(TOOLS)/prokka/build/prokka/db/kingdom/Bacteria/sprot.psq: ;
	$(eval PROKKA_BUILD=$(TOOLS)/prokka/build)
	$(BIN)/prokka --setupdb
	ln -s $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot.00.phr $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot.phr
	ln -s $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot.00.pin $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot.pin
	ln -s $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot.00.psq $(PROKKA_BUILD)/prokka/db/kingdom/Bacteria/sprot.psq

barrnap: $(BIN)/barrnap ;
$(BIN)/barrnap: ;
	$(eval BARRNAP_BUILD=$(TOOLS)/barrnap/build)
	rm -rf $(BARRNAP_BUILD) && mkdir -p $(BARRNAP_BUILD)
	tar -C $(BARRNAP_BUILD) -xzvf $(TOOLS)/barrnap/barrnap-0.7.tar.gz
	mv $(BARRNAP_BUILD)/barrnap-0.7 $(BARRNAP_BUILD)/barrnap
	ln -s $(BARRNAP_BUILD)/barrnap/bin/barrnap $@


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
test: ;
	wget -P $(PWD)/test-data $(TEST_DATA)/test_genome.fastq.gz
	mkdir $(PWD)/test/test-pipeline
	ln -s $(PWD)/test-data/test_genome.fastq.gz $(PWD)/test/test-pipeline/test_genome.fastq.gz
	python $(PWD)/bin/pipelines/create_job_script --input $(PWD)/test/test-pipeline/test_genome.fastq.gz --working_dir $(PWD)/test/test-pipeline --processors 23  --sample_tag tester --log_times > $(PWD)/test/test-pipeline/job_script.sh
	cd $(PWD)/test/test-pipeline && sh $(PWD)/test/test-pipeline/job_script.sh


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                                                             #
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
clean: clean-config ;
	ls $(BIN) | xargs -I {} rm $(BIN)/{}
	ls $(LIBS)/python | xargs -I {} rm -rf $(LIBS)/python/{}
	find $(PWD)/tools/ | grep "/build$$" | xargs -I {} rm -rf {}

clean-config: ;
	sed -i 's#^BASE_DIR.*#BASE_DIR = CHANGE_ME#' staphopia/config.py
