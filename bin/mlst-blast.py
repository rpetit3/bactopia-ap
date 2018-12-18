#! /usr/bin/env python3
"""
mlst-blast.py

BLAST MLST loci against an assembed genome. Output only the top hits.

Example Usage: mlst-blast.py FASTA BLASTDB_DIR OUTPUT --cpu 6
"""


def pipe_command(cmd_1, cmd_2, stdout=False, stderr=False, verbose=True,
                 shell=False):
    """
    Execute a single command and return STDOUT and STDERR.

    If stdout or stderr are given, output will be written to given file name.
    """
    import subprocess
    if verbose:
        print('{0} | {1}'.format(' '.join(cmd_1), ' '.join(cmd_2)))
    stdout = open(stdout, 'w') if stdout else subprocess.PIPE
    stderr = open(stderr, 'w') if stderr else subprocess.PIPE
    p1 = subprocess.Popen(cmd_1, stdout=subprocess.PIPE)
    p2 = subprocess.Popen(cmd_2, stdin=p1.stdout, stdout=stdout, stderr=stderr)
    p1.wait()

    return p2.communicate()


def blast_alleles(input_file, blastdb_dir, blastn_results, num_cpu,
                  verbose=True):
    """Blast assembled contigs against MLST blast database."""
    # Decompress contigs
    from collections import OrderedDict
    import json

    outfmt = "6 sseqid bitscore slen length gaps mismatch pident evalue"
    alleles = ['arcC', 'aroE', 'glpF', 'gmk', 'pta', 'tpi', 'yqiL']
    results = OrderedDict()

    for allele in alleles:
        blastdb = '{0}/{1}.tfa'.format(blastdb_dir, allele)
        blastn = pipe_command(
            ['zcat', input_file],
            ['blastn', '-db', blastdb, '-query', '-', '-outfmt', outfmt,
             '-max_target_seqs', '1', '-num_threads', num_cpu,
             '-evalue', '10000'], verbose=verbose
        )
        top_hit = blastn[0].decode("utf-8").split('\n')[0].split('\t')

        # Did not return a hit
        if not top_hit[0]:
            top_hit = ['0'] * 9
            top_hit[0] = '{0}.0'.format(allele)

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


if __name__ == '__main__':
    import argparse as ap

    parser = ap.ArgumentParser(prog='mlst-blast.py',
                               conflict_handler='resolve',
                               description='Determine MLST via BLAST')
    group1 = parser.add_argument_group('Options', '')
    group1.add_argument('fasta', metavar="FASTA", type=str,
                        help='Input FASTA file to determine MLST')
    group1.add_argument('blastdb', metavar="BLAST_DATABASE", type=str,
                        help='Directory where BLAST databases are stored')
    group1.add_argument('output', metavar="OUTPUT", type=str,
                        help='File to output results to')
    group1.add_argument('--cpu', metavar='INT', type=int, default=1,
                        help='Number of processors to use.')
    group1.add_argument('--quiet', action='store_true',
                        help='Do not output each command.')
    args = parser.parse_args()

    blast_alleles(args.fasta, args.blastdb, args.output, str(args.cpu),
                  verbose=not args.quiet)
