'''
    Author: Robert A Petit III
    
    These tasks include all kmer related tasks
'''
from staphopia.tasks import shared 

def jellyfish_count(fastq, output_file, config):
    '''
     
    '''
    jellyfish = shared.pipe_command(
        ['zcat', fastq],
        [config['jellyfish'], 'count', '-m', '31', '-s', '100M', '-C', 
         '-t', config['n_cpu'], '-o', output_file, '/dev/fd/0'],
    )

def jellyfish_dump(input_file, output_file, config):
    '''
     
    '''
    jellyfish = shared.pipe_command(
        [config['jellyfish'], 'dump', '-c', input_file],
        ['gzip', '-'],
        stdout=output_file
    )
    
    rm = shared.run_command(['rm', input_file])