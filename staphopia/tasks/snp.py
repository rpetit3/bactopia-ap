'''
    Author: Robert A Petit III
    
    These tasks include all SNP related tasks
'''
import os

from staphopia.tasks import shared 


def bwa_aln(fastq, output_sai, output_file, config):
    bwa_aln = shared.run_command(
        ['bwa', 'aln', '-e', '10', '-f', output_sai , '-t', config['n_cpu'], 
         config['reference'], fastq]
    )
    
    if shared.try_to_complete_task(output_sai, output_file):
        return True
    else:
        raise Exception("bwa aln did not complete successfully.")
        
def bwa_samse(input_sai, fastq, output_sam, output_file, config):
    bwa_samse = shared.run_command(
        ['bwa', 'samse', '-f', output_sam, config['reference'], input_sai, fastq]
    )
    
    if shared.try_to_complete_task(output_sam, output_file):
        return True
    else:
        raise Exception("bwa samse did not complete successfully.")

def sam_to_bam(input_sam, output_bam, output_file, config):
    sam_to_bam = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['sam_format_converter'], 
         'INPUT='+ input_sam, 'VALIDATION_STRINGENCY=LENIENT', 
         'OUTPUT='+ output_bam]
    )
 
    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("SamFormatConverter did not complete successfully.")
 
def add_or_replace_read_groups(input_bam, output_bam, output_file, config):
    add_or_replace = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['add_or_replace_read_groups'], 
         'INPUT='+ input_bam , 'OUTPUT='+ output_bam, 'SORT_ORDER=coordinate', 
         'RGID=GATK', 'RGLB=GATK', 'RGPL=Illumina', 'RGSM=GATK', 'RGPU=GATK', 
         'VALIDATION_STRINGENCY=LENIENT']
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("AddOrReplaceReadGroups did not complete successfully.")
    
def build_bam_index(input_bam, output_file, config):
    build_bam_index = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['build_bam_index'], 
         'INPUT='+ input_bam, 'VALIDATION_STRINGENCY=LENIENT']
    )   
    
    if shared.try_to_complete_task(input_bam, output_file):
        return True
    else:
        raise Exception("BuildBamIndex did not complete successfully.")
    
  
def realigner_target_creator(input_bam, output_intervals, output_file, config):
    realigner_target_creator = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['gatk'], '-I', input_bam, 
         '-T', 'RealignerTargetCreator', '-R', config['reference'], 
         '-o', output_intervals]
    )

    if shared.try_to_complete_task(output_intervals, output_file):
        return True
    else:
        raise Exception("RealignerTargetCreator did not complete successfully.")
        
def indel_realigner(input_bam, input_interval, output_bam, output_file, config):
    indel_realigner = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['gatk'], '-T', 'IndelRealigner', 
         '-l', 'INFO', '-I', input_bam, '-R', config['reference'], 
         '-targetIntervals', input_interval, '-o', output_bam]
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("IndelRealigner did not complete successfully.")
    
def sort_sam(input_bam, output_bam, output_file, config):
    sort_sam = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['sort_sam'], 'INPUT='+ input_bam, 
         'SORT_ORDER=coordinate', 'OUTPUT='+ output_bam, 
         'VALIDATION_STRINGENCY=LENIENT']
    )
    
    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("SortSam did not complete successfully.")

def samtools_view(input_bam, output_bam, output_file, config):
    samtools_sort = shared.run_command(
        ['samtools', 'view', '-bhF', '4', '-o', output_bam, input_bam]
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("samtools view did not complete successfully.")
    
def unified_genotyper(input_bam, output_vcf, output_file, config):
    unified_genotyper = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['gatk'], '-T', 'UnifiedGenotyper', 
         '-glm', 'BOTH', '-R', config['reference'], '-dcov', '500',
          '-I', input_bam, '-o', output_vcf, '-stand_call_conf', '30.0', 
          '-stand_emit_conf', '10.0', '-rf', 'BadCigar']
    )
    if shared.try_to_complete_task(output_vcf, output_file):
        return True
    else:
        raise Exception("UnifiedGenotyper did not complete successfully.")
    
def variant_filtration(input_vcf, output_vcf, output_file, config):
    variant_filtration = shared.run_command(
        ['java', '-Xmx4g', '-jar', config['gatk'], '-T', 'VariantFiltration', 
         '-R', config['reference'], '-filter', '-cluster', '3', '-window', '10', 
         '-V', input_vcf, '-o', output_vcf]
    )
    
    if shared.try_to_complete_task(output_vcf, output_file):
        return True
    else:
        raise Exception("VariantFiltration did not complete successfully.")
