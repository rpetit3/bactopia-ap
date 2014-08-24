'''
    Author: Robert A Petit III
    
    These tasks include all SCCmec related tasks
'''
import os

from staphopia.tasks import shared 

def blast_genes(blastdb, output_file, config):
    outfmt = "6 qseqid nident qlen length sstart send pident ppos bitscore evalue gaps"
    tblastn_results = output_file.replace('completed', 'tblastn')
    tblastn = shared.run_command(
        ['tblastn', '-db', blastdb, '-query', config['proteins'], 
         '-outfmt', outfmt, '-num_threads', config['n_cpu'], '-evalue', 
         '0.0001', '-max_target_seqs', '1'],
        stdout=tblastn_results,
    )

    if shared.try_to_complete_task(tblastn_results, output_file):
        return True
    else:
        raise Exception("tblastn did not complete successfully.")
        
        
def blast_primers(blastdb, output_file, config):
    outfmt = "6 qseqid nident qlen length sstart send pident ppos bitscore evalue"
    blastn_results = output_file.replace('completed', 'blastn')
    blastn = shared.run_command(
        ['blastn', '-max_target_seqs', '1', '-dust', 'no', '-word_size', '7', 
         '-perc_identity', '100', '-db', blastdb, '-outfmt', outfmt, 
         '-query', config['primers']],
        stdout=blastn_results,
    )

    if shared.try_to_complete_task(blastn_results, output_file):
        return True
    else:
        raise Exception("blastn did not complete successfully.")