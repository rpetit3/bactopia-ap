'''
    Author: Robert A Petit III
    
    These tasks include all FASTQ related steps.
'''
import subprocess

def validator(fastq, config):
    '''
    Ensure the given file is proper FASTQ format
    '''
    cmd = [config['fastq_validator'], '--file', fastq, '--quiet', 
           '--seqLimit', '50000' ]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    if stdout.split('\t')[0] != '0':
        raise Exception("Invalid FASTQ format.")
        
def stats(fastq, output_file, config):
    '''
    Generate read statistics of the given FASTQ file
    '''
    zcat = subprocess.Popen(['zcat', fastq], stdout=subprocess.PIPE)
    p = subprocess.Popen([config['fastq_stats']], stdin=zcat.stdout,
                         stdout=open(output_file, 'w'))
    zcat.wait()
     
def cleanup(fastq, stats_file, output_file, config):
    '''
    Based of the read statistics remove low quality reads and reduce coverage
    '''
    cmd = [config['fastq_cleanup'], '--stats', stats_file]
    zcat = subprocess.Popen(['zcat', fastq], stdout=subprocess.PIPE)
    cleanup = subprocess.Popen(cmd, stdin=zcat.stdout, stdout=subprocess.PIPE)
    gzip = subprocess.Popen(['gzip', '--best', '-'], stdin=cleanup.stdout,
                            stdout=open(output_file, 'w'))
    cleanup.wait()
    