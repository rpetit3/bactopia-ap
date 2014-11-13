#! /usr/bin/env python
""" Count k-mers within FASTQ file. """
from staphopia.config import BIN
from staphopia.tasks import shared


def jellyfish_count(fastq, output_file, num_cpu):
    """ Count k-mers in a FASTQ file. """
    jellyfish = shared.pipe_command(
        ['zcat', fastq],
        [BIN['jellyfish'], 'count', '-m', '31', '-s', '100M', '-C',
         '-t', num_cpu, '-o', output_file, '/dev/fd/0'],
    )
    return jellyfish


def jellyfish_dump(input_file, output_file):
    """ Dump k-mer counts to text file. """
    jellyfish = shared.pipe_command(
        [BIN['jellyfish'], 'dump', '-c', input_file],
        ['gzip', '-'],
        stdout=output_file
    )
    shared.run_command(['rm', input_file])
    return jellyfish
