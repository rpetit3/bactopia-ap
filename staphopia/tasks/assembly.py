'''
    Author: Robert A Petit III
    
    These tasks include all assembly related tasks
'''
import os
import subprocess

from staphopia.tasks import shared 

def kmergenie(fastq, output_file, config):
    '''
    Run kmer genie to predict the optimal value for K
    '''
    output_prefix = os.path.splitext(output_file)[0]
    cmd = ['kmergenie', fastq, '-t', config['n_cpu'], '-o', output_prefix]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
    # Clean up histograms
    shared.find_and_remove_files(os.path.dirname(output_file), 
                                 '*.histo')
    
def sort_kmergenie(kmergenie_dat, output_file):
    '''
    Sort kmergenie, keeping only the top three predicted kmer values
    '''
    sort = subprocess.Popen(['sort', '-k2,2rn', kmergenie_dat], 
                            stdout=subprocess.PIPE)
    p = subprocess.Popen(['head', '-n', '3'], stdin=sort.stdout,
                         stdout=open(output_file, 'w'))
    sort.wait()
    

def velvet(input_files, output_file, config, k = '31', cov_cutoff='auto'):
    '''
    Run Velvet assembler for a specific kmer value.
    '''
    completed = []
    paired = '-interleaved -shortPaired' if config['is_paired'] else '-short'
    fastq, kmergenie = input_files
    fh = open(kmergenie, 'r')
    for line in fh:
        k, total, cov_cutoff = line.rstrip().split(' ')
        output_dir = output_file.replace('completed', k)
        
        velveth = ['velveth', output_dir, k, paired, '-fastq.gz', fastq]
        p = subprocess.Popen(velveth, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
    
        velvetg = ['velvetg', output_dir, '-cov_cutoff', cov_cutoff, 
                   '-min_contig_lgth', '100', '-very_clean', 'yes']
        p = subprocess.Popen(velvetg, stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        
        completed.append(shared.try_to_complete_task(output_dir+'/contigs.fa', 
                                                     output_dir+'/completed'))
    fh.close()
        
    if all(i == True for i in completed):
        if shared.complete_task(output_file):
            return True
        else:
            raise Exception("Unable to complete Velvet assembly.")
    else:
        raise Exception("One or more Velvet assemblies did not complete")
    
def cleanup_velvet(input_file, output_file):
    # Cleanup and compress Velvet Directories
    base_dir = input_file.replace('completed', '')
    shared.find_and_remove_files(base_dir, '*PreGraph')
    velvet_dirs = shared.find_dirs(base_dir, "*", '1', '1')
    if shared.compress_and_remove(input_file.replace('completed', 
                                                     'velvet.tar.gz'), 
                                  velvet_dirs, has_dirs=True):
        if shared.try_to_complete_task(input_file.replace('completed', 
                                                          'velvet.tar.gz'),
                                       output_file):
            return True
        else:
            raise Exception("Unable to complete Velvet clean up.")                
    else:
        raise Exception("Cannot compress Velet output, please check.")
        
def spades(fastq, output_file, config):
    '''
    Run Spades assembler
    '''
    paired = '--12' if config['is_paired'] else '-s'
    p = subprocess.Popen(['find', '-name', 'contigs.fa'], stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    velvet_dirs = []
    for line in stdout.split('\n'):
        if line:
            velvet_dirs.append('--trusted-contigs')
            velvet_dirs.append(line)
    
    output_dir = output_file.replace('completed', '')
    spades = ['spades.py', paired, fastq, '--careful', '-t', config['n_cpu'], 
              '--only-assembler', '-o', output_dir]
    spades.extend(velvet_dirs)
    
    p = subprocess.Popen(spades, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    
    if shared.try_to_complete_task(output_dir+'contigs.fasta', output_file):
        return True
    else:
        raise Exception("Spades assembly did not complete.")

def move_spades(spades_dir, contigs, scaffolds):
    p = subprocess.Popen(['gzip', '-c', '--best', spades_dir+'/contigs.fasta'],
                         stdout=open(contigs, 'w'), stderr=subprocess.PIPE)
    p = subprocess.Popen(['gzip', '-c', '--best', spades_dir+'/scaffolds.fasta'], 
                         stdout=open(scaffolds, 'w'), stderr=subprocess.PIPE)
    
def cleanup_spades(input_file, output_file):
    # Cleanup and compress Spades Directories
    base_dir = input_file.replace('completed', '')
    remove_these = ['*final_contigs*', '*before_rr*', '*pe_before_traversal*',
                    '*simplified_contigs*']
    for name in remove_these:
        shared.find_and_remove_files(base_dir, name)
                                     
    shared.find_and_remove_files(base_dir, "*scaffolds*", min_depth='2')
    
    spades_files = shared.find_files(base_dir, '*', '1', '1')
    if shared.compress_and_remove(input_file.replace('completed', 
                                                     'spades.tar.gz'),
                                  spades_files, has_dirs=True):                           
        if shared.try_to_complete_task(input_file.replace('completed', 
                                                          'spades.tar.gz'), 
                                       output_file):
            shared.complete_task(input_file)
            return True
        else:
            raise Exception("Unable to complete Spades clean up.")  
    else:
        raise Exception("Cannot compress spades output, please check.")
        
def newbler(fastq, output_file):
    '''
    Run Newbler assembler
    '''


def cleanup(output_dir):
    '''
    Clean up all intermediate files created by assembly tasks
    '''
    # kmergenie histograms
    p = subprocess.Popen(['rm', '-rf', output_dir+'/*.histo'], 
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()