#! /usr/bin/env python
"""Ruffus wrappers for FASTQ related tasks."""
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
        'overwrite=t'
    ])

    return {
        'fastq': '{0}/nophix_r1.fastq'.format(out_dir),
        'fastq2': '{0}/nophix_r2.fastq'.format(out_dir) if fastq2 else '',
    }


def filter_adapters(fastq, num_cpu, out_dir, fastq2=''):
    """Use Trimmomatic to filter out adapter sequences from Illumina reads."""
    paired = 'PE' if fastq2 else 'SE'
    out2 = '{0}/noadapter_pe2.fastq'.format(out_dir) if fastq2 else ''
    out2_se = '{0}/noadapter_se2.fastq'.format(out_dir) if fastq2 else ''
    shared.run_command([
        BIN['java7'], '-jar', BIN['trimmomatic'], paired,
        '-threads', num_cpu,
        fastq, fastq2,
        '{0}/noadapter_pe1.fastq'.format(out_dir),
        '{0}/noadapter_se1.fastq'.format(out_dir),
        out2, out2_se,
        'ILLUMINACLIP:{0}:2:20:10:8:true'.format(FASTQ['adapters']),
        'LEADING:3', 'TRAILING:3', 'MINLEN:36'
    ])

    return {
        'fastq': '{0}/noadapter_pe1.fastq'.format(out_dir),
        'fastq_se': '{0}/noadapter_se1.fastq'.format(out_dir),
        'fastq2': out2,
        'fastq2_se': out2_se
    }


def cleanup(fastq, stats_file, is_paired, no_length, output_file, fastq2=None):
    """Read stats_file, and remove low quality reads and reduce coverage."""
    paired = '--paired' if is_paired else ''
    no_length_filter = '--no_length_filter' if no_length else ''
    cmd = []
    if is_paired and fastq2:
        cmd = [BIN['fastq_interleave'], fastq, fastq2]
    else:
        cmd = ['cat', fastq]
    fastq_cleanup = shared.pipe_commands(
        cmd,
        [BIN['fastq_cleanup'], '--stats', stats_file, paired,
         no_length_filter],
        ['gzip', '-'],
        stdout=output_file
    )
    return fastq_cleanup
