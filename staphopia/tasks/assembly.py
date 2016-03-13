#! /usr/bin/env python
"""Ruffus wrappers for assembly related tasks."""
from staphopia.config import BIN
from staphopia.tasks import shared


def spades(fastq, output_file, num_cpu, is_paired):
    """Assemble using Spades."""
    paired = '--12' if is_paired else '-s'
    output_dir = output_file.replace('completed', '')
    shared.run_command(
        [BIN['spades'], paired, fastq, '--careful', '-t', num_cpu,
         '-o', output_dir],
        stderr='{0}spades.err'.format(output_dir)
    )

    if shared.try_to_complete_task(output_dir + 'contigs.fasta', output_file):
        return True
    else:
        raise Exception("Spades assembly did not complete.")


def move_spades(spades_dir, contigs, scaffolds):
    """Move final assembly to project root."""
    gzip_contigs = shared.run_command(
        ['gzip', '-c', spades_dir + '/contigs.fasta'],
        stdout=contigs
    )

    gzip_scaffolds = shared.run_command(
        ['gzip', '-c', spades_dir + '/scaffolds.fasta'],
        stdout=scaffolds
    )
    return [gzip_contigs, gzip_scaffolds]


def cleanup_spades(input_file, output_file):
    """Cleanup the Spades directory."""
    # TODO KEEP FASTG FILE
    base_dir = input_file.replace('completed', '')
    remove_these = ['*final_contigs*', '*before_rr*', '*pe_before_traversal*',
                    '*simplified_contigs*']
    for name in remove_these:
        shared.find_and_remove_files(base_dir, name)

    shared.find_and_remove_files(base_dir, "*scaffolds*", min_depth='2')

    spades_files = shared.find_files(base_dir, '*', '1', '1')
    spades_tar_gz = input_file.replace('completed', 'spades.tar.gz')
    if shared.compress_and_remove(spades_tar_gz, spades_files):
        if shared.try_to_complete_task(spades_tar_gz, output_file):
            shared.complete_task(input_file)
            return True
        else:
            raise Exception("Unable to complete Spades clean up.")
    else:
        raise Exception("Cannot compress spades output, please check.")


def makeblastdb(input_file, output_file):
    """Make a blast database of an assembly."""
    temp_file = input_file + '.temp'
    shared.run_command(['gunzip', '-c', input_file], stdout=temp_file)

    output_prefix = output_file.replace('completed', 'assembly')
    shared.run_command(
        [BIN['makeblastdb'], '-in', temp_file, '-dbtype',
         'nucl', '-out', output_prefix],
        stdout=output_prefix + '.out',
        stderr=output_prefix + '.err'
    )

    shared.run_command(['rm', temp_file])

    if shared.try_to_complete_task(output_prefix + '.nin', output_file):
        return True
    else:
        raise Exception("makeblastdb did not complete successfully.")


def assembly_stats(input_file, output_file):
    """Determine assembly statistics."""
    stats_file = input_file.replace('fasta.gz', 'stats')
    shared.run_command(
        [BIN['assemblathon_stats'], '-genome_size', '2800000', '-csv',
         input_file]
    )

    if shared.try_to_complete_task(stats_file, output_file):
        return True
    else:
        raise Exception("Assembly stats did not complete successfully.")
