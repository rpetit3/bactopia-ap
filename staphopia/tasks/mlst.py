#! /usr/bin/env python
""" Ruffus wrappers for MLST related tasks. """
from staphopia.config import BIN, MLST
from staphopia.tasks import shared


def srst2(input_file, output_file, num_cpu):
    """ Predict MLST using SRST. """
    output_prefix = output_file.replace('completed', 'srst2')
    n_cpu = '"-p {0}"'.format(num_cpu)
    shared.run_command(
        [BIN['srst2'], '--input_se', input_file, '--mlst_db',
         MLST['mlst_db'], '--mlst_definitions', MLST['mlst_definitions'],
         '--other', n_cpu, '--output', output_prefix],
        stdout=output_prefix + '.log',
        stderr=output_prefix + '.err'
    )

    # Remove intermediate files
    base_dir = output_file.replace('completed', '')
    shared.find_and_remove_files(base_dir, '*.pileup')
    shared.find_and_remove_files(base_dir, '*.bam')
    srst2 = output_prefix + '__mlst__Staphylococcus_aureus__results.txt'
    if shared.try_to_complete_task(srst2, output_file):
        return True
    else:
        raise Exception("SRST2 did not complete successfully.")


def blast_alleles(input_file, output_file, num_cpu):
    """ Blast assembled contigs against MLST blast database. """
    # Decompress contigs
    shared.run_command(['gunzip', input_file])
    input_file = input_file.replace(".gz", "")
    outfmt = "6 sseqid bitscore slen length gaps mismatch pident evalue"
    alleles = ['arcc', 'aroe', 'glpf', 'gmk_', 'pta_', 'tpi_', 'yqil']
    results = []

    for allele in alleles:
        blastdb = '{0}/{1}.tfa'.format(MLST['mlst_blastdb'], allele)
        blastn = shared.run_command(
            [BIN['blastn'], '-db', blastdb, '-query', input_file,
             '-outfmt', outfmt, '-max_target_seqs', '1', '-num_threads',
             num_cpu]
        )
        results.append(blastn[0].split('\n')[0])

    blastn_results = output_file.replace('completed', 'blastn.txt')
    fh = open(blastn_results, 'w')
    fh.write('\n'.join(results))
    fh.close()
    shared.run_command(['gzip', '--fast', input_file])
    if shared.try_to_complete_task(blastn_results, output_file):
        return True
    else:
        raise Exception("blastn did not complete successfully.")
