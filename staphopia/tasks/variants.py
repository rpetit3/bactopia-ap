#! /usr/bin/env python
"""Ruffus wrappers for SNP related tasks."""
from staphopia.config import BIN
from staphopia.tasks import shared


def bwa_index(fasta):
    """Create a BWA index."""
    shared.run_command(
        [BIN['bwa'], 'index', fasta],
    )


def samtools_faidx(fasta):
    """Index the reference FASTA file."""
    shared.run_command(
        [BIN['samtools'], 'faidx', fasta],
    )


def create_sequence_dictionary(reference):
    """Index the reference FASTA file."""
    dictionary = reference.replace('fasta', 'dict')
    shared.run_command([
        BIN['java8'], '-Xmx8g', '-jar', BIN['picardtools'],
        'CreateSequenceDictionary',
        'REFERENCE=' + reference,
        'OUTPUT=' + dictionary,
    ])


def bwa_mem(fastq, output_sam, num_cpu, reference, is_paired):
    """Align reads (mean length < 70bp) against reference genome."""
    p = '-p' if is_paired else ''
    shared.run_command(
        [BIN['bwa'], 'mem', '-M', p, '-t', num_cpu, reference, fastq],
        stdout=output_sam
    )


def bwa_aln(fastq, sai, output_sam, num_cpu, reference,):
    """Align reads (mean length < 70bp) against reference genome."""
    shared.run_command([
        BIN['bwa'], 'aln', '-f', sai, '-t', num_cpu, reference, fastq
    ])

    shared.run_command([
        BIN['bwa'], 'samse', '-f', output_sam, reference, sai, fastq
    ])


def add_or_replace_read_groups(input_sam, sorted_bam):
    """
    Picard Tools - AddOrReplaceReadGroups.

    Places each read into a read group for GATK processing. Really only
    informative if there are multiple samples.
    """
    shared.run_command([
        BIN['java8'], '-Xmx8g', '-jar', BIN['picardtools'],
        'AddOrReplaceReadGroups',
        'INPUT=' + input_sam,
        'OUTPUT=' + sorted_bam,
        'SORT_ORDER=coordinate',
        'RGID=GATK',
        'RGLB=GATK',
        'RGPL=Illumina',
        'RGSM=GATK',
        'RGPU=GATK',
        'VALIDATION_STRINGENCY=LENIENT'
    ])


def mark_duplicates(sorted_bam, deduped_bam):
    """
    GATK Best Practices - Mark Duplicates.

    Picard Tools - MarkDuplicates: Remove mark identical reads as duplicates
    for GATK to ignore.
    """
    shared.run_command([
        BIN['java8'], '-Xmx8g', '-jar', BIN['picardtools'],
        'MarkDuplicates',
        'INPUT=' + sorted_bam,
        'OUTPUT=' + deduped_bam,
        'METRICS_FILE=' + deduped_bam + '_metrics',
        'ASSUME_SORTED=true',
        'REMOVE_DUPLICATES=false',
        'VALIDATION_STRINGENCY=LENIENT'
    ])


def build_bam_index(bam):
    """
    Picard Tools - BuildBamIndex.

    Index the BAM file..
    """
    shared.run_command([
        BIN['java8'], '-Xmx8g', '-jar', BIN['picardtools'],
        'BuildBamIndex',
        'INPUT=' + bam,
    ])


def realigner_target_creator(deduped_bam, intervals, reference):
    """
    GATK Best Practices - Realign Indels.

    GATK - RealignerTargetCreator: Create a list of InDel regions to be
    realigned.
    """
    shared.run_command([
        BIN['java7'], '-Xmx8g', '-jar', BIN['gatk'],
        '-T', 'RealignerTargetCreator',
        '-R', reference,
        '-I', deduped_bam,
        '-o', intervals
    ])


def indel_realigner(intervals, deduped_bam, realigned_bam, reference):
    """
    GATK Best Practices - Realign Indels.

    GATK - IndelRealigner: Realign InDel regions.
    """
    shared.run_command([
        BIN['java7'], '-Xmx8g', '-jar', BIN['gatk'],
        '-T', 'IndelRealigner',
        '-R', reference,
        '-I', deduped_bam,
        '-o', realigned_bam,
        '-targetIntervals', intervals
    ])


def haplotype_caller(realigned_bam, output_vcf, num_cpu, reference):
    """
    GATK Best Practices - Call Variants.

    GATK - HaplotypeCaller: Call variants (SNPs and InDels)
    """
    shared.run_command([
        BIN['java7'], '-Xmx8g', '-jar', BIN['gatk'],
        '-T', 'HaplotypeCaller',
        '-R', reference,
        '-I', realigned_bam,
        '-o', output_vcf,
        '-ploidy', '1',
        '-stand_call_conf', '30.0',
        '-stand_emit_conf', '10.0',
        '-rf', 'BadCigar',
        '-nct', num_cpu
    ])


def variant_filtration(input_vcf, filtered_vcf, reference):
    """Apply filters to the input VCF."""
    shared.run_command([
        BIN['java7'], '-Xmx8g', '-jar', BIN['gatk'],
        '-T', 'VariantFiltration',
        '-R', reference,
        '-V', input_vcf,
        '-o', filtered_vcf,
        '--clusterSize', '3',
        '--clusterWindowSize', '10',
        '--filterExpression', 'DP < 9 && AF < 0.7',
        '--filterName', 'Fail',
        '--filterExpression', 'DP > 9 && AF >= 0.95',
        '--filterName', 'SuperPass',
        '--filterExpression', 'GQ < 20',
        '--filterName', 'LowGQ'
    ])


def vcf_annotator(filtered_vcf, annotated_vcf, genbank):
    """Annotate called SNPs/InDel."""
    shared.run_command(
        [BIN['vcf_annotator'],
         '--gb', genbank,
         '--vcf', filtered_vcf],
        stdout=annotated_vcf
    )
