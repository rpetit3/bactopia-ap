#! /usr/bin/env python
"""Ruffus wrappers for FASTQ related tasks."""
from staphopia.config import BIN
from staphopia.tasks import shared


def validator(fastq):
    """Test validity of FASTQ file."""
    stdout, stderr = shared.run_command(
        [BIN['fastq_validator'], '--file', fastq, '--quiet',
         '--seqLimit', '50000', '--disableSeqIDCheck'],
        verbose=False
    )

    if stdout.split('\t')[0] != '0':
        return "invalid"
    else:
        return "valid"


def stats(fastq, output_file):
    """Generate read statistics of the given FASTQ file."""
    fastq_stats = shared.pipe_command(
        ['zcat', fastq],
        [BIN['fastq_stats']],
        stdout=output_file
    )
    return fastq_stats


def cleanup(fastq, stats_file, is_paired, output_file):
    """Read stats_file, and remove low quality reads and reduce coverage."""
    paired = '--paired' if is_paired else ''
    fastq_cleanup = shared.pipe_commands(
        ['zcat', fastq],
        [BIN['fastq_cleanup'], '--stats', stats_file, paired],
        ['gzip', '-'],
        stdout=output_file
    )
    return fastq_cleanup
