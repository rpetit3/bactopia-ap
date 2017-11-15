#! /bin/bash
# A wrapper for staphopia.nf, mainly for use on CGC. Assumes that sample is
# given in the form of "--sample SAMPLE_NAME".

ARGS=$(echo $* | sed 's=--fq1 =--fq1 ../=' | sed 's=--fq2 =--fq2 ../=')
SAMPLE=$(echo $* | awk '{split($0,a,"sample ");split(a[2],b," "); print b[1]}')

# Make directory and run pipeline
mkdir $SAMPLE
cp /usr/local/bin/nextflow.config ${SAMPLE}/
cp /usr/local/bin/staphopia.nf ${SAMPLE}/
cd $SAMPLE && ./staphopia.nf $ARGS && cd ..
date > ${SAMPLE}/staphopia-date.txt


# Tarball and delete directory
tar cf - $SAMPLE/ | gzip --best > ${SAMPLE}.tar.gz && rm -rf $SAMPLE
