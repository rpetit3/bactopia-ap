#! /usr/bin/env python
"""
Static variables used throughout the analysis pipeline.

Please note, the Makefile should update BASE_DIR, but if not you will need to.
"""
BASE_DIR = "/home/rpetit/staphopia/analysis-pipeline"

# PATH
PATH = '{0}/bin'.format(BASE_DIR)
TOOL_DATA = '{0}/data'.format(BASE_DIR)

# PYTHONPATH
PYTHON_REQS = '{0}/libs/python'.format(BASE_DIR)

# Programs
BIN = {
    # FASTQ related
    'fastq_cleanup': '{0}/fastq_cleanup'.format(PATH),
    'fastq_stats': '{0}/fastq-stats'.format(PATH),
    'fastq_validator': '{0}/fastq-validator'.format(PATH),

    # Assembly related
    'kmergenie': '{0}/kmergenie'.format(PATH),
    'velvetg': '{0}/velvetg'.format(PATH),
    'velveth': '{0}/velveth'.format(PATH),
    'spades': '{0}/spades.py'.format(PATH),
    'makeblastdb': '{0}/makeblastdb'.format(PATH),
    'assemblathon_stats': '{0}/assemblathon-stats.pl'.format(PATH),

    # MLST related
    'srst2': '{0}/srst2.py'.format(PATH),
    'blastn': '{0}/blastn'.format(PATH),

    # SCCmec related
    'tblastn': '{0}/tblastn'.format(PATH),
    'samtools': '{0}/samtools-1.3'.format(PATH),
    'genomeCoverageBed': '{0}/genomeCoverageBed'.format(PATH),

    # SNP/InDel related
    'bwa': '{0}/bwa'.format(PATH),
    'java7': '{0}/java7'.format(PATH),
    'java8': '{0}/java8'.format(PATH),
    'picardtools': '{0}/picard.jar'.format(PATH),
    'gatk': '{0}/GenomeAnalysisTK.jar'.format(PATH),
    'vcf_annotator': '{0}/vcf-annotator'.format(PATH),

    # K-mer related
    'jellyfish': '{0}/jellyfish'.format(PATH),

    # Annotation related
    'prokka': '{0}/prokka'.format(PATH),

    # Pipelines
    'fastq_cleanup_pipeline': '{0}/cleanup_fastq'.format(PATH),
    'illumina_assembly': '{0}/illumina_assembly'.format(PATH),
    'predict_mlst': '{0}/predict_mlst'.format(PATH),
    'predict_sccmec': '{0}/predict_sccmec'.format(PATH),
    'call_variants': '{0}/call_variants'.format(PATH),
    'kmer_analysis': '{0}/kmer_analysis'.format(PATH),
    'annotation': '{0}/annotation'.format(PATH),

    # Staphopia related
    'download_ena': '{0}/download_ena'.format(PATH),
    'ascp': '{0}/ascp'.format(PATH),
    'aspera_key': '{0}/asperaweb_id_dsa.openssh'.format(PATH),
    'fastq_interleave': '{0}/fastq-interleave'.format(PATH),
    'manage': '/staphopia/ebs/staphopia.com/manage.py'.format(PATH),
}

MLST = {
    'mlst_db': '{0}/mlst/Staphylococcus_aureus.fasta'.format(TOOL_DATA),
    'mlst_definitions': '{0}/mlst/saureus.txt'.format(TOOL_DATA),
    'mlst_blastdb': '{0}/mlst/blastdb'.format(TOOL_DATA),
}

SCCMEC = {
    'primers': '{0}/sccmec_primers.fasta'.format(TOOL_DATA),
    'proteins': '{0}/sccmec_proteins.fasta'.format(TOOL_DATA),
    'cassettes': '{0}/sccmec/sccmec_cassettes'.format(TOOL_DATA),
}

SNP = {
    'reference': '{0}/snp/n315.fasta'.format(TOOL_DATA),
    'ref_genbank': '{0}/snp/n315.gb'.format(TOOL_DATA),
}

ANNOTATION = {
    'genus': 'Staphylococcus-uniref90',
    'proteins': '{0}/annotation/sa-uniref90-reviewed.prokka'.format(TOOL_DATA)
}
