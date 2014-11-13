#! /usr/bin/env python
"""
Static variables used throughout the analysis pipeline.

Please note, the Makefile should update BASE_DIR, but if not you will need to.
"""
BASE_DIR = '/home/rpetit/staphopia/analysis-pipeline'

# PATH
PATH = BASE_DIR + '/bin'
PIPELINE_PATH = PATH + '/pipelines'
THIRD_PARTY_PATH = PATH + '/third-party'

# PYTHONPATH
BIOPYTHON = BASE_DIR + '/src/third-party/python/biopython'
PYVCF = BASE_DIR + '/src/third-party/python/pyvcf'
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

    # K-mer related
    'jellyfish': THIRD_PARTY_PATH + '/jellyfish',
}

MLST = {
    'mlst_db': BASE_DIR + '/tool-data/mlst/Staphylococcus_aureus.fasta',
    'mlst_definitions': BASE_DIR + '/tool-data/mlst/saureus.txt',
    'mlst_blastdb': BASE_DIR + '/tool-data/mlst/blastdb',
}
