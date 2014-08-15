'''
    Author: Robert A Petit III
    
    These tasks include all FASTQ related steps.
'''
from staphopia.tasks import shared 

def validator(fastq, config):
    '''
    Ensure the given file is proper FASTQ format
    '''
    stdout, stderr = shared.run_command(
        [config['fastq_validator'], '--file', fastq, '--quiet', 
         '--seqLimit', '50000', '--disableSeqIDCheck']    
    )

    if stdout.split('\t')[0] != '0':
        raise Exception("Invalid FASTQ format.")
        
def stats(fastq, output_file, config):
    '''
    Generate read statistics of the given FASTQ file
    '''
    fastq_stats = shared.pipe_command(
        ['zcat', fastq],
        [config['fastq_stats']],
        stdout=output_file
    )

     
def cleanup(fastq, stats_file, output_file, config):
    '''
    Based of the read statistics remove low quality reads and reduce coverage
    '''
    fastq_cleanup = shared.pipe_commands(
        ['zcat', fastq],
        [config['fastq_cleanup'], '--stats', stats_file],
        ['gzip', '--best', '-'],
        stdout=output_file
    )
