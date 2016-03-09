#! /usr/bin/env python
""" Ruffus wrappers for assembly related tasks. """
from staphopia.config import BIN, SCCMEC
from staphopia.tasks import shared


def blast_genes(blastdb, output_file, num_cpu):
    """ BLAST SCCmec related genes against given blast database. """
    outfmt = (
        "6 qseqid nident qlen length sstart send pident ppos bitscore evalue"
        " gaps"
    )
    tblastn_results = output_file.replace('completed', 'tblastn')
    shared.run_command(
        [BIN['tblastn'], '-db', blastdb, '-query', SCCMEC['proteins'],
         '-outfmt', outfmt, '-num_threads', num_cpu, '-evalue',
         '0.0001', '-max_target_seqs', '1'],
        stdout=tblastn_results,
    )

    if shared.try_to_complete_task(tblastn_results, output_file):
        return True
    else:
        raise Exception("tblastn did not complete successfully.")


def blast_primers(blastdb, output_file):
    """ BLAST SCCmec related primers against given blast database. """
    outfmt = (
        "6 qseqid nident qlen length sstart send pident ppos bitscore evalue"
        " gaps"
    )
    blastn_results = output_file.replace('completed', 'blastn')
    shared.run_command(
        [BIN['blastn'], '-max_target_seqs', '1', '-dust', 'no',
         '-word_size', '7', '-perc_identity', '100', '-db', blastdb,
         '-outfmt', outfmt, '-query', SCCMEC['primers']],
        stdout=blastn_results,
    )

    if shared.try_to_complete_task(blastn_results, output_file):
        return True
    else:
        raise Exception("blastn did not complete successfully.")


def bwa_aln(fastq, output_file, num_cpu):
    """ Align FASTQ against each SCCmec cassette (BWA part 1). """
    sai_output = output_file.replace('completed', 'sccmec')
    shared.run_command(
        [BIN['bwa'], 'aln', '-f', sai_output, '-t', num_cpu,
         SCCMEC['cassettes'], fastq]
    )

    if shared.try_to_complete_task(sai_output, output_file):
        return True
    else:
        raise Exception("bwa aln did not complete successfully.")


def bwa_samse(sai, fastq, output_file):
    """ Align FASTQ against each SCCmec cassette (BWA part 2). """
    sai_input = sai.replace('completed', 'sccmec')
    sam_output = output_file.replace('completed', 'sccmec')
    shared.run_command(
        [BIN['bwa'], 'samse', '-n', '9999', '-f', sam_output,
         SCCMEC['cassettes'], sai_input, fastq]
    )

    if shared.try_to_complete_task(sam_output, output_file):
        return True
    else:
        raise Exception("bwa samse did not complete successfully.")


def sam_to_bam(input_file, output_file):
    """ Convert SAM to BAM. """
    sam_input = input_file.replace('completed', 'sccmec')
    bam_output = output_file.replace('completed', 'sccmec')
    shared.pipe_command(
        [BIN['samtools'], 'view', '-bS', sam_input],
        [BIN['samtools'], 'sort', '-o', bam_output, '-']
    )

    if shared.try_to_complete_task(bam_output, output_file):
        return True
    else:
        raise Exception("SAM to BAM did not complete successfully.")


def genome_coverage_bed(input_file, output_file):
    """ Calculate coverage of the alignment. """
    bam_input = input_file.replace('completed', 'sccmec')
    coverage_output = output_file.replace('completed', 'sccmec')
    shared.run_command(
        [BIN['genomeCoverageBed'], '-ibam', bam_input, '-d'],
        stdout=coverage_output
    )

    if shared.try_to_complete_task(coverage_output, output_file):
        return True
    else:
        raise Exception("genome_coverage_bed did not complete successfully.")


def cleanup_mapping(output_file):
    """ Cleanup BWA related files. """
    prefix = output_file.replace('completed.cleanup', 'sccmec')
    remove_these_files = [prefix + ext for ext in ['.sai', '.sam', '.bam']]
    shared.remove(remove_these_files)
    coverage = prefix + '.coverage'
    coverage_gz = coverage + '.gz'
    if shared.compress_and_remove(coverage_gz, [coverage], tarball=False):
        if shared.try_to_complete_task(coverage_gz, output_file):
            return True
        else:
            raise Exception("Unable to complete mapping clean up.")
    else:
        raise Exception("Cannot compress coverage output, please check.")
