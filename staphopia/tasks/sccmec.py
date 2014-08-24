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
        
def bwa_aln(fastq, output_file, config):
    sai_output = output_file.replace('completed', 'sccmec')
    bwa_aln = shared.run_command(
        ['bwa', 'aln', '-f', sai_output , '-t', config['n_cpu'], 
         config['cassettes'], fastq]
    )
    
    if shared.try_to_complete_task(sai_output, output_file):
        return True
    else:
        raise Exception("bwa aln did not complete successfully.")
    
def bwa_samse(sai, fastq, output_file, config):
    sai_input = sai.replace('completed', 'sccmec')
    sam_output = output_file.replace('completed', 'sccmec')
    bwa_samse = shared.run_command(
        ['bwa', 'samse', '-n', '9999', '-f', sam_output, 
         config['cassettes'], sai_input, fastq]
    )
    
    if shared.try_to_complete_task(sam_output, output_file):
        return True
    else:
        raise Exception("bwa samse did not complete successfully.")
    
def sam_to_bam(input_file, output_file):
    sam_input = input_file.replace('completed', 'sccmec')
    bam_output = output_file.replace('completed', 'sccmec')
    bam_prefix = bam_output.replace('.bam', '')
    samtools_view = shared.pipe_command(
        ['samtools', 'view', '-bS', sam_input],
        ['samtools', 'sort', '-', bam_prefix]
    )
 
    if shared.try_to_complete_task(bam_output, output_file):
        return True
    else:
        raise Exception("sam to bam did not complete successfully.")
 
def genome_coverage_bed(input_file, output_file):
    bam_input = input_file.replace('completed', 'sccmec')
    coverage_output = output_file.replace('completed', 'sccmec')
    genome_coverage_bed = shared.run_command(
        ['genomeCoverageBed', '-ibam', bam_input, '-d'],
        stdout=coverage_output
    )

    if shared.try_to_complete_task(coverage_output, output_file):
        return True
    else:
        raise Exception("genome_coverage_bed did not complete successfully.")
    
def cleanup_mapping(output_file):
    prefix = output_file.replace('completed.cleanup', 'sccmec')
    remove_these_files = [prefix + ext for ext in ['.sai', '.sam', '.bam']]
    shared.remove(remove_these_files)
    
    coverage = prefix +'.coverage'
    coverage_gz = coverage +'.gz'
    print coverage
    if shared.compress_and_remove(coverage_gz, [coverage], tarball=False):                           
        if shared.try_to_complete_task(coverage_gz, output_file):
            return True
        else:
            raise Exception("Unable to complete mapping clean up.")  
    else:
        raise Exception("Cannot compress coverage output, please check.")



    
   