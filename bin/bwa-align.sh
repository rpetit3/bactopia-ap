#! /bin/bash
# A bwa wrapper to automate the selection of 'bwa aln' or 'bwa mem'
FASTQ=$1
INDEX=$2
LENGTH=$3
CPU=$4
PAIRED=$5
N=$6

if [ "$LENGTH" -gt "70" ]; then
    bwa mem -M $PAIRED -t $CPU $INDEX $FASTQ > bwa.sam
else
    bwa aln -f bwa.sai -t $CPU $INDEX $FASTQ
    bwa samse $N -f bwa.sam $INDEX bwa.sai $FASTQ
fi
