#! /bin/bash
# A wrapper for staphopia.nf, mainly for use on CGC. Assumes that sample is
# given in the form of "--sample SAMPLE_NAME".
ARGS=$(echo $* | sed 's=--fq1 =--fq1 ../=' | sed 's=--fq2 =--fq2 ../=')
SAMPLE=$(echo $* | awk '{split($0,a,"sample ");split(a[2],b," "); print b[1]}')
LOG=${SAMPLE}.log
exec &>> $LOG

# Make directory and run pipeline
mkdir -p $SAMPLE
cp /usr/local/bin/nextflow.config ${SAMPLE}/
cp /usr/local/bin/staphopia.nf ${SAMPLE}/
cd $SAMPLE && ./staphopia.nf $ARGS && cd ..
date > ${SAMPLE}/staphopia-date.txt

# Tarball and delete directory
tar cf - $SAMPLE/ | gzip --best > ${SAMPLE}.tar.gz
md5sum ${SAMPLE}.tar.gz > ${SAMPLE}.md5

if [ $? -eq 0 ]; then
    if [ -s "${SAMPLE}.tar.gz" ] && [ -s "${SAMPLE}.md5" ]; then
        rm -rf $SAMPLE
        exit 0
    else
        exit 1
    fi
else
    exit 1
fi
