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
    'fastq_cleanup': PATH + '/fastq_cleanup',
    'fastq_stats': PATH + '/fastq_stats',
    'fastq_validator': THIRD_PARTY_PATH + '/fastq_validator',
}
