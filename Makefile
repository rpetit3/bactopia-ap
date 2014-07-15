TOP_DIR := $(shell pwd)

all: fastq ;

fastq: fastq_validator fastq_stats fastq_interleave ;

fastq_validator: ;
	git clone git@github.com:rpetit3/fastQValidator.git src/fastQValidator
	git clone git@github.com:rpetit3/libStatGen.git src/libStatGen
	make -C src/fastQValidator
	ln -s $(TOP_DIR)/src/fastQValidator/bin/fastQValidator $(TOP_DIR)/bin/fastq_validator

fastq_stats: ;
	g++ -Wall -O3 -o bin/fastq_stats src/fastq_stats.cpp

fastq_interleave: ; 
	g++ -Wall -O3 -o bin/fastq_interleave src/fastq_interleave.cpp

clean: ;
	rm -rf src/fastQValidator
	rm -rf src/libStatGen
	rm bin/fastq_interleave
	rm bin/fastq_stats
	rm bin/fastq_validator
