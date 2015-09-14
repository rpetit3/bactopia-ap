""" Run the PROKKA annotation pipeline on an input FASTA file. """
from staphopia.config import BIN, ANNOTATION
from staphopia.tasks import shared


def run_prokka(fasta, output_dir, tag, log, num_cpu):
    """ Annotate a assembled FASTA file. """
    shared.run_command(['gunzip', '-k', fasta])
    fasta = fasta.replace(".gz", "")
    prokka = shared.run_command(
        [
            BIN['prokka'],
            '--cpus', num_cpu,
            '--genus', ANNOTATION['genus'],
            '--usegenus',
            '--outdir', output_dir,
            '--force',
            '--proteins', ANNOTATION['proteins'],
            '--prefix', tag,
            '--locustag', tag,
            '--centre', tag,
            '--compliant',
            '--quiet',
            fasta
        ]
    )
    shared.run_command(['rm', fasta])
    shared.pipe_command(['find', 'annotation/'],
                        ['xargs', '-I', '{}', 'gzip', '{}'])
    return prokka
