#! /usr/bin/env python
"""Ruffus wrappers for assembly related tasks."""
import os.path

from staphopia.config import BIN
from staphopia.tasks import shared


def spades(fastq, output_dir, num_cpu, is_paired, plasmid=False):
    """Assemble using Spades."""
    plasmid_spades = ''
    log = 'logs/spades.stderr'
    if plasmid:
        plasmid_spades = '--plasmid'
        log = 'logs/plasmid-spades.stderr'
    paired = '--12' if is_paired else '-s'
    shared.run_command(
        [BIN['spades'], paired, fastq, '--careful', '-t', num_cpu,
         '-o', output_dir, plasmid_spades],
        stderr=log
    )


def cleanup_spades(spades_dir, contigs, scaffolds, assembly_graph):
    """Move final assembly to project root."""
    gzip_contigs = shared.run_command(
        ['gzip', '-c', spades_dir + '/contigs.fasta'],
        stdout=contigs
    )

    gzip_scaffolds = shared.run_command(
        ['gzip', '-c', spades_dir + '/scaffolds.fasta'],
        stdout=scaffolds
    )

    gzip_graph = shared.run_command(
        ['gzip', '-c', spades_dir + '/assembly_graph.fastg'],
        stdout=assembly_graph
    )

    if (os.path.isfile(contigs) and os.path.isfile(scaffolds) and
             os.path.isfile(assembly_graph)):
        shared.run_command(['rm', '-rf', spades_dir])

    return [gzip_contigs, gzip_scaffolds, gzip_graph]


def makeblastdb(fasta, title, output_prefix):
    """Make a blast database of an assembly."""
    shared.pipe_command(
        ['zcat', fasta],
        [BIN['makeblastdb'], '-dbtype', 'nucl', '-title', title,
         '-out', output_prefix],
        stdout='logs/assembly-makeblastdb.out',
        stderr='logs/assembly-makeblastdb.err'
    )


def assembly_stats(assembly, stats):
    """Determine assembly statistics."""
    shared.run_command(
        [BIN['assemblathon_stats'], '-genome_size', '2814816', '-json',
         '-output_file', stats, assembly]
    )
