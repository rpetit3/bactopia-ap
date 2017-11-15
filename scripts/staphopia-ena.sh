#! /bin/bash
# A wrapper for staphopia.nf, mainly for use on CGC. Assumes that experiment is
# given in the form of "--experiment ACCESSION".
SAMPLE=$1
CPU=$2
RESUME=$3

mkdir $SAMPLE
# Download files
ena-dl.py $1 ./ --quiet --nextflow --group_by_experiment > args.txt
echo ena-dl.py $1 ./ --quiet --nextflow --group_by_experiment > ${SAMPLE}/ena-dl.txt
mv *.json ${SAMPLE}/

ARGS=$(cat args.txt)

# Make directory and run pipeline
cp /usr/local/bin/nextflow.config ${SAMPLE}/
cp /usr/local/bin/staphopia.nf ${SAMPLE}/
cd $SAMPLE && ./staphopia.nf $ARGS --sample ${SAMPLE} --cpu ${CPU} ${RESUME} && cd ..
date > ${SAMPLE}/staphopia-date.txt

# Tarball and delete directory
tar cf - $SAMPLE/ | gzip --best > ${SAMPLE}.tar.gz && rm -rf $SAMPLE
