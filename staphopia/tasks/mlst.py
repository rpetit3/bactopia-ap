#! /usr/bin/env python
"""Ruffus wrappers for MLST related tasks."""
from collections import OrderedDict
import json

from staphopia.config import BIN, MLST
from staphopia.tasks import shared


def srst2(fastq, out_dir, num_cpu):
    """Predict MLST using SRST."""
    prefix = '{0}/srst2'.format(out_dir)
    n_cpu = '"-p {0}"'.format(num_cpu)
    shared.run_command(
        [BIN['srst2'], '--input_se', fastq, '--mlst_db',
         MLST['mlst_db'], '--mlst_definitions', MLST['mlst_definitions'],
         '--mlst_delimiter', '_', '--other', n_cpu, '--output', prefix],
        stdout='logs/mlst-srst2.stdout',
        stderr='logs/mlst-srst2.stderr'
    )

    # Remove intermediate files
    shared.find_and_remove_files(out_dir, '*.pileup')
    shared.find_and_remove_files(out_dir, '*.bam')


def blast_alleles(input_file, blastn_results, num_cpu):
    """Blast assembled contigs against MLST blast database."""
    # Decompress contigs
    shared.run_command(['gunzip', '-k', '-f', input_file])
    input_file = input_file.replace(".gz", "")
    outfmt = "6 sseqid bitscore slen length gaps mismatch pident evalue"
    alleles = ['arcC', 'aroE', 'glpF', 'gmk', 'pta', 'tpi', 'yqiL']
    results = OrderedDict()

    for allele in alleles:
        blastdb = '{0}/{1}.tfa'.format(MLST['mlst_blastdb'], allele)
        blastn = shared.run_command(
            [BIN['blastn'], '-db', blastdb, '-query', input_file,
             '-outfmt', outfmt, '-max_target_seqs', '1', '-num_threads',
             num_cpu, '-evalue', '10000']
        )
        top_hit = blastn[0].split('\n')[0].split('\t')

        # Did not return a hit
        if not top_hit[0]:
            top_hit = ['0'] * 9
            top_hit[0] = '{0}_0'.format(allele)

        results[allele] = OrderedDict((
            ('sseqid', top_hit[0]),
            ('bitscore', top_hit[1]),
            ('slen', top_hit[2]),
            ('length', top_hit[3]),
            ('gaps', top_hit[4]),
            ('mismatch', top_hit[5]),
            ('pident', top_hit[6]),
            ('evalue', top_hit[7])
        ))

    with open(blastn_results, 'w') as fh:
        json.dump(results, fh, indent=4, separators=(',', ': '))

    shared.run_command(['rm', input_file])
