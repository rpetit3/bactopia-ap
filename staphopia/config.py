#! /usr/bin/env python
"""
Static variables used throughout the analysis pipeline.

Please note, the Makefile should update BASE_DIR, but if not you will need to.
"""
BASE_DIR = CHANGE_ME

# PATH
PATH = BASE_DIR + '/bin'
PIPELINE_PATH = PATH + '/pipelines'
THIRD_PARTY_PATH = PATH + '/third-party'

# PYTHONPATH
PYTHON_REQS = BASE_DIR + '/src/third-party/python'
VCFANNOTATOR = BASE_DIR + '/src/third-party/python/vcf-annotator'

# Programs
BIN = {
    # FASTQ related
    'fastq_cleanup': PATH + '/fastq_cleanup',
    'fastq_stats': PATH + '/fastq_stats',
    'fastq_validator': THIRD_PARTY_PATH + '/fastq_validator',

    # Assembly related
    'kmergenie': THIRD_PARTY_PATH + '/kmergenie',
    'velvetg': THIRD_PARTY_PATH + '/velvetg',
    'velveth': THIRD_PARTY_PATH + '/velveth',
    'spades': THIRD_PARTY_PATH + '/spades.py',
    'makeblastdb': THIRD_PARTY_PATH + '/makeblastdb',
    'assemblathon_stats': THIRD_PARTY_PATH + '/assemblathon_stats.pl',

    # MLST related
    'srst2': THIRD_PARTY_PATH + '/srst2.py',
    'blastn': THIRD_PARTY_PATH + '/blastn',

    # SCCmec related
    'tblastn': THIRD_PARTY_PATH + '/tblastn',
    'bwa': THIRD_PARTY_PATH + '/bwa',
    'samtools': THIRD_PARTY_PATH + '/samtools-1.0',
    'genomeCoverageBed': THIRD_PARTY_PATH + '/genomeCoverageBed',

    # SNP/InDel related
    'java': THIRD_PARTY_PATH + '/java',
    'sam_format_converter': THIRD_PARTY_PATH + '/SamFormatConverter.jar',
    'add_or_replace_read_groups': '{0}/AddOrReplaceReadGroups.jar'.format(
        THIRD_PARTY_PATH
    ),
    'build_bam_index': THIRD_PARTY_PATH + '/BuildBamIndex.jar',
    'sort_sam': THIRD_PARTY_PATH + '/SortSam.jar',
    'create_sequence_dictionary': '{0}/CreateSequenceDictionary.jar'.format(
        THIRD_PARTY_PATH
    ),
    'gatk': THIRD_PARTY_PATH + '/GenomeAnalysisTK.jar',
    'vcf_annotator': THIRD_PARTY_PATH + '/vcf-annotator',

    # K-mer related
    'jellyfish': THIRD_PARTY_PATH + '/jellyfish',

    # Pipelines
    'fastq_cleanup_pipeline': PIPELINE_PATH + '/fastq_cleanup',
    'illumina_assembly': PIPELINE_PATH + '/illumina_assembly',
    'predict_mlst': PIPELINE_PATH + '/predict_mlst',
    'predict_sccmec': PIPELINE_PATH + '/predict_sccmec',
    'call_variants': PIPELINE_PATH + '/call_variants',
    'kmer_analysis': PIPELINE_PATH + '/kmer_analysis',

    # Staphopia related
    'download_ena': PATH + '/download_ena',
    'ascp': THIRD_PARTY_PATH + '/ascp',
    'aspera_key': THIRD_PARTY_PATH + '/asperaweb_id_dsa.openssh',
    'fastq_interleave': PATH + '/fastq_interleave',
    'manage': '/home/staphopia/staphopia.com/manage.py',
}

MLST = {
    'mlst_db': BASE_DIR + '/tool-data/mlst/Staphylococcus_aureus.fasta',
    'mlst_definitions': BASE_DIR + '/tool-data/mlst/saureus.txt',
    'mlst_blastdb': BASE_DIR + '/tool-data/mlst/blastdb',
}

SCCMEC = {
    'primers': BASE_DIR + '/tool-data/sccmec_primers.fasta',
    'proteins': BASE_DIR + '/tool-data/sccmec_proteins.fasta',
    'cassettes': BASE_DIR + '/tool-data/sccmec/sccmec_cassettes',
}

SNP = {
    'reference': BASE_DIR + '/tool-data/snp/n315.fasta',
    'ref_genbank': BASE_DIR + '/tool-data/snp/n315.gb',
}
