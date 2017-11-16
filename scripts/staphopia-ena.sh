#! /bin/bash
# A wrapper for staphopia.nf, mainly for use on CGC. Assumes that experiment is
# given in the form of "--experiment ACCESSION".
SAMPLE=$1
LOG=${SAMPLE}.log
CPU=$2
RESUME=$3
exec &>> $LOG

mkdir -p $SAMPLE
# Download files
ena-dl.py $1 ./ --quiet --nextflow --group_by_experiment 1> args.txt
ARGS=$(cat args.txt)
echo ena-dl.py $1 ./ --quiet --nextflow --group_by_experiment > ${SAMPLE}/ena-dl.txt
mv *.json ${SAMPLE}/

# Make directory and run pipeline
cp /usr/local/bin/nextflow.config ${SAMPLE}/
cp /usr/local/bin/staphopia.nf ${SAMPLE}/
cd $SAMPLE && ./staphopia.nf $ARGS --sample ${SAMPLE} --cpu ${CPU} ${RESUME} && cd ..
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
