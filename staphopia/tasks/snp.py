#! /usr/bin/env python
""" Ruffus wrappers for SNP related tasks. """
from staphopia.config import BIN, SNP
from staphopia.tasks import shared


def bwa_aln(fastq, output_sai, output_file, num_cpu):
    """ Align reads against reference genome (BWA part one). """
    shared.run_command(
        [BIN['bwa'], 'aln', '-e', '10', '-f', output_sai, '-t', num_cpu,
         SNP['reference'], fastq]
    )

    if shared.try_to_complete_task(output_sai, output_file):
        return True
    else:
        raise Exception("bwa aln did not complete successfully.")


def bwa_samse(input_sai, fastq, output_sam, output_file):
    """ Align reads against reference genome (BWA part two). """
    shared.run_command(
        [BIN['bwa'], 'samse', '-f', output_sam, SNP['reference'], input_sai,
         fastq]
    )

    if shared.try_to_complete_task(output_sam, output_file):
        return True
    else:
        raise Exception("bwa samse did not complete successfully.")


def sam_to_bam(input_sam, output_bam, output_file):
    """ Convert SAM to BAM. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['sam_format_converter'],
         'INPUT=' + input_sam, 'VALIDATION_STRINGENCY=LENIENT',
         'OUTPUT=' + output_bam]
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("SamFormatConverter did not complete successfully.")


def add_or_replace_read_groups(input_bam, output_bam, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['add_or_replace_read_groups'],
         'INPUT=' + input_bam, 'OUTPUT=' + output_bam, 'SORT_ORDER=coordinate',
         'RGID=GATK', 'RGLB=GATK', 'RGPL=Illumina', 'RGSM=GATK', 'RGPU=GATK',
         'VALIDATION_STRINGENCY=LENIENT']
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("AddOrReplaceReadGroups didn't complete successfully.")


def build_bam_index(input_bam, output_file):
    """ Build BAM index. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['build_bam_index'],
         'INPUT=' + input_bam, 'VALIDATION_STRINGENCY=LENIENT']
    )

    if shared.try_to_complete_task(input_bam, output_file):
        return True
    else:
        raise Exception("BuildBamIndex did not complete successfully.")


def realigner_target_creator(input_bam, output_intervals, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['gatk'], '-I', input_bam,
         '-T', 'RealignerTargetCreator', '-R', SNP['reference'],
         '-o', output_intervals]
    )

    if shared.try_to_complete_task(output_intervals, output_file):
        return True
    else:
        raise Exception("RealignerTargetCreator didn't complete successfully.")


def indel_realigner(input_bam, input_interval, output_bam, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['gatk'], '-T',
         'IndelRealigner', '-l', 'INFO', '-I', input_bam,
         '-R', SNP['reference'], '-targetIntervals', input_interval,
         '-o', output_bam]
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("IndelRealigner did not complete successfully.")


def sort_sam(input_bam, output_bam, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['sort_sam'],
         'INPUT=' + input_bam, 'SORT_ORDER=coordinate',
         'OUTPUT=' + output_bam, 'VALIDATION_STRINGENCY=LENIENT']
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("SortSam did not complete successfully.")


def samtools_view(input_bam, output_bam, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['samtools'], 'view', '-bhF', '4', '-o', output_bam, input_bam]
    )

    if shared.try_to_complete_task(output_bam, output_file):
        return True
    else:
        raise Exception("samtools view did not complete successfully.")


def unified_genotyper(input_bam, output_vcf, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['gatk'], '-T',
         'UnifiedGenotyper', '-glm', 'BOTH', '-R', SNP['reference'],
         '-dcov', '500', '-I', input_bam, '-o', output_vcf,
         '-stand_call_conf', '30.0', '-stand_emit_conf', '10.0',
         '-rf', 'BadCigar']
    )
    if shared.try_to_complete_task(output_vcf, output_file):
        return True
    else:
        raise Exception("UnifiedGenotyper did not complete successfully.")


def variant_filtration(input_vcf, output_vcf, output_file):
    """ See Tauqeer's protocol. """
    shared.run_command(
        [BIN['java'], '-Xmx4g', '-jar', BIN['gatk'], '-T',
         'VariantFiltration', '-R', SNP['reference'], '-filter',
         '-cluster', '3', '-window', '10', '-V', input_vcf, '-o', output_vcf]
    )

    if shared.try_to_complete_task(output_vcf, output_file):
        return True
    else:
        raise Exception("VariantFiltration did not complete successfully.")


def vcf_annotator(input_vcf, output_vcf, output_file):
    """ Annotate called SNPs/InDel. """
    shared.run_command(
        [SNP['vcf_annotator'], '--gb', SNP['ref_genbank'], '--vcf', input_vcf],
        stdout=output_vcf
    )

    if shared.try_to_complete_task(output_vcf, output_file):
        return True
    else:
        raise Exception("vcf-annotator did not complete successfully.")


def move_final_vcf(input_vcf, compressed_vcf, output_file):
    """ Move the final VCF to the project root. """
    shared.run_command(
        ['gzip', '-c', input_vcf],
        stdout=compressed_vcf
    )

    if shared.try_to_complete_task(compressed_vcf, output_file):
        return True
    else:
        raise Exception("final vcf gzip did not complete successfully.")


def cleanup(base_dir, tar_gz, output_file):
    """ Clean up all the intermediate files. """
    remove_these = ['*.bam', '*.bai', '*.intervals', '*.sam', '*.sai']
    for name in remove_these:
        shared.find_and_remove_files(base_dir, name)

    gatk_files = shared.find_files(base_dir, '*', '1', '1')
    if shared.compress_and_remove(tar_gz, gatk_files):
        if shared.try_to_complete_task(tar_gz, output_file):
            return True
        else:
            raise Exception("Unable to complete GATK clean up.")
    else:
        raise Exception("Cannot compress GATK output, please check.")
