'''
    Author: Robert A Petit III
    
    These tasks include all MLST related tasks
'''
import os

from staphopia.tasks import shared 

def srst2(input_file, output_file, config):
    output_prefix = output_file.replace('completed', 'srst2')
    n_cpu = '-p {0}'.format(config['n_cpu'])
    srst2 = shared.run_command(
        ['srst2', '--input_se', input_file, '--mlst_db', config['mlst_db'], 
         '--mlst_definitions', config['mlst_definitions'], '--other', n_cpu,
         '--output', output_prefix],
        stdout=output_prefix+'.log',
        stderr=output_prefix+'.err'
    )
    
    # Remove intermediate files
    base_dir = output_file.replace('completed', '')
    shared.find_and_remove_files(base_dir, '*.pileup')
    shared.find_and_remove_files(base_dir, '*.bam')
    srst2_results = output_prefix+'__mlst__Staphylococcus_aureus__results.txt'
    if shared.try_to_complete_task(srst2_results, output_file):
        return True
    else:
        raise Exception("SRST2 did not complete successfully.")
        
def blast_alleles(input_file, output_file, config):
    outfmt = "6 sseqid bitscore slen length gaps mismatch pident evalue"
    alleles = ['arcc', 'aroe', 'glpf', 'gmk_', 'pta_', 'tpi_', 'yqil']
    results = []

    for allele in alleles:
        blastdb = '{0}/{1}.tfa'.format(config['mlst_blastdb'], allele)
        blastn = shared.run_command(
            ['blastn', '-db', blastdb, '-query', input_file, '-outfmt', outfmt, 
             '-max_target_seqs', '1', '-num_threads', config['n_cpu']]
        )
        results.append(blastn[0].split('\n')[0])
        
    blastn_results = output_file.replace('completed', 'blastn.txt')
    fh = open(blastn_results, 'w')
    fh.write('\n'.join(results))
    fh.close()
    
    if shared.try_to_complete_task(blastn_results, output_file):
        return True
    else:
        raise Exception("blastn did not complete successfully.")