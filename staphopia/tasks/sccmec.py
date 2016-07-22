#! /usr/bin/env python
"""Ruffus wrappers for assembly related tasks."""
from staphopia.config import BIN, SCCMEC
from staphopia.tasks import shared


def blast_proteins(blastdb, output_file, num_cpu):
    """BLAST SCCmec related genes against given blast database."""
    shared.run_command(
        [BIN['tblastn'], '-db', blastdb, '-query', SCCMEC['proteins'],
         '-outfmt', '15', '-num_threads', num_cpu, '-evalue',
         '0.0001', '-max_target_seqs', '1'],
        stdout=output_file,
    )


def blast_primers(blastdb, output_file):
    """BLAST SCCmec related primers against given blast database."""
    shared.run_command(
        [BIN['blastn'], '-max_target_seqs', '1', '-dust', 'no',
         '-word_size', '7', '-perc_identity', '100', '-db', blastdb,
         '-outfmt', '15', '-query', SCCMEC['primers']],
        stdout=output_file,
    )


def bwa_mem(fastq, output_sam, num_cpu, is_paired):
    """Align reads (mean length < 70bp) against reference genome."""
    p = '-p' if is_paired else ''
    shared.run_command(
        [BIN['bwa'], 'mem',
         '-M',
         p,
         '-t', num_cpu,
         SCCMEC['cassettes'],
         fastq],
        stdout=output_sam
    )


def bwa_aln(fastq, sai, output_sam, num_cpu):
    """Align reads (mean length < 70bp) against reference genome."""
    shared.run_command([
        BIN['bwa'], 'aln',
        '-f', sai,
        '-t', num_cpu,
        SCCMEC['cassettes'],
        fastq
    ])

    shared.run_command([
        BIN['bwa'], 'samse',
        '-n', '9999',
        '-f', output_sam,
        SCCMEC['cassettes'],
        sai,
        fastq
    ])


def sam_to_bam(input_sam, output_bam):
    """Convert SAM to BAM."""
    shared.pipe_command(
        [BIN['samtools'], 'view', '-bS', input_sam],
        [BIN['samtools'], 'sort', '-o', output_bam, '-']
    )


def genome_coverage_bed(input_bam, output_coverage):
    """Calculate coverage of the alignment."""
    shared.pipe_command(
        [BIN['genomeCoverageBed'], '-ibam', input_bam, '-d'],
        ['gzip', '--best', '-'],
        stdout=output_coverage
    )
