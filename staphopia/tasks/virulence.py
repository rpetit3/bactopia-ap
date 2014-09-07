'''
    Author: Robert A Petit III
    
    These tasks include all virulence related tasks
'''
import os

from staphopia.tasks import shared 

def blast_genes(blastdb, output_file, config):
    outfmt = "6 qseqid nident qlen length sstart send pident ppos bitscore evalue gaps"
    tblastn_results = output_file.replace('completed', 'tblastn.txt')
    tblastn = shared.run_command(
        [config['tblastn'], '-db', blastdb, '-query',
         config['virulence_genes'], '-outfmt', outfmt, '-num_threads', 
         config['n_cpu'], '-evalue', '0.0001', '-max_target_seqs', '1'],
        stdout=tblastn_results,
    )

    if shared.try_to_complete_task(tblastn_results, output_file):
        return True
    else:
        raise Exception("tblastn did not complete successfully.")