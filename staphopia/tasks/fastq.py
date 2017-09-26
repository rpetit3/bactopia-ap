#! /usr/bin/env python
"""Ruffus wrappers for FASTQ related tasks."""
from os.path import basename, splitext

from staphopia.config import BIN, FASTQ
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


def stats(fastq, output_file, fastq2='', compressed=True):
    """Generate read statistics of the given FASTQ file."""
    cat = 'zcat' if compressed else 'cat'
    fastq_stats = shared.pipe_command(
        [cat, fastq, fastq2],
        [BIN['fastq_stats']],
        stdout=output_file
    )
    return fastq_stats


def filter_phix(fastq, num_cpu, out_dir, log, fastq2=None):
    """Use BBDuk to filter out phiX sequences from Illumina reads."""
    in2 = 'in2={0}'.format(fastq2) if fastq2 else ''
    out2 = 'out2={0}/nophix_r2.fastq'.format(out_dir) if fastq2 else ''
    shared.run_command([
        BIN['bbduk'], '-Xmx2g',
        'threads={0}'.format(num_cpu),
        'in={0}'.format(fastq), in2,
        'out={0}/nophix_r1.fastq'.format(out_dir), out2,
        'stats={0}'.format(log),
        'ref={0}'.format(FASTQ['phix']),
        'k=31',
        'hdist=1',
        'overwrite=t',
        'ordered=t'
    ])

    return {
        'fastq': '{0}/nophix_r1.fastq'.format(out_dir),
        'fastq2': '{0}/nophix_r2.fastq'.format(out_dir) if fastq2 else '',
    }


def filter_adapters(fastq, num_cpu, out_dir, log, fastq2=None):
    """Use BBDuk to filter out adapter sequences from Illumina reads."""
    in2 = 'in2={0}'.format(fastq2) if fastq2 else ''
    out2 = 'out2={0}/noadapter_r2.fastq'.format(out_dir) if fastq2 else ''
    shared.run_command([
        BIN['bbduk'], '-Xmx2g',
        'threads={0}'.format(num_cpu),
        'in={0}'.format(fastq), in2,
        'out={0}/noadapter_r1.fastq'.format(out_dir), out2,
        'stats={0}'.format(log),
        'ref={0}'.format(FASTQ['adapters']),
        'ktrim=r',
        'k=23',
        'mink=11',
        'hdist=1',
        'tpe',
        'tbo',
        'qout=33',
        'minlength=36',
        'overwrite=t',
        'ordered=t'
    ])

    return {
        'fastq': '{0}/noadapter_r1.fastq'.format(out_dir),
        'fastq2': '{0}/noadapter_r2.fastq'.format(out_dir) if fastq2 else '',
    }


def error_correct(fastq, num_cpu, out_dir, fastq2=''):
    """Use Spades to correct reads."""
    stdout = 'logs/spades-ecc.stdout'
    stderr = 'logs/spades-ecc.stderr'
    fastq_1 = '-1' if fastq2 else '-s'
    fastq_2 = '-2' if fastq2 else ''
    shared.run_command([
        BIN['spades'],
        fastq_1, fastq,
        fastq_2, fastq2,
        '--only-error-correction',
        '--disable-gzip-output',
        '-t', num_cpu,
        '-o', out_dir
     ], stdout=stdout, stderr=stderr)

    text = '00.0_0.cor.fastq'
    return {
        'fastq': '{0}/corrected/{1}.{2}'.format(
            out_dir, splitext(basename(fastq))[0], text
        ),
        'fastq2': '{0}/corrected/{1}.{2}'.format(
            out_dir, splitext(basename(fastq2))[0], text
        ) if fastq2 else '',
    }


def cleanup(fastq, stats_file, is_paired, no_length, output_file, fastq2=None,
            coverage=100):
    """Read stats_file, and remove low quality reads and reduce coverage."""
    paired = '--paired' if is_paired else ''
    no_length_filter = '--no_length_filter' if no_length else ''
    cmd = []
    if fastq2:
        cmd = [BIN['fastq_interleave'], fastq, fastq2]
    else:
        cmd = ['cat', fastq]
    fastq_cleanup = shared.pipe_commands(
        cmd,
        [BIN['fastq_cleanup'],
         '--stats', stats_file,
         '--coverage', str(coverage),
         paired, no_length_filter],
        ['gzip', '--best', '-'],
        stdout=output_file
    )
    return fastq_cleanup
