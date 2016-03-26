"""Run the PROKKA annotation pipeline on an input FASTA file."""
from staphopia.config import BIN, ANNOTATION
from staphopia.tasks import shared


def run_prokka(fasta, output_dir, tag, num_cpu):
    """Annotate a assembled FASTA file."""
    shared.run_command(['gunzip', '-k', '-f', fasta])
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
            '--centre', tag[0:3],
            '--compliant',
            '--quiet',
            fasta
        ]
    )
    log_file = '{0}/{1}.log'.format(output_dir, tag)
    shared.run_command(['rm', fasta])
    shared.run_command(['mv', log_file, 'logs/prokka.log'])
    shared.pipe_command(['find', output_dir],
                        ['xargs', '-I', '{}', 'gzip', '{}'])
    return prokka


def get_blast_results(fasta, output_file, num_cpu):
    """BLAST predicted genes against the Bacteria database."""
    shared.pipe_commands(
        ['zcat', fasta],
        [BIN['blastp'], '-db', ANNOTATION['kingdom'], '-outfmt', '15',
         '-max_target_seqs', '1', '-num_threads', num_cpu, '-evalue', '10000'],
        ['gzip', '--best', '-'],
        stdout=output_file
    )


def makeblastdb(fasta, title, output_prefix):
    """Make a blast database of a predicted protein sequences."""
    shared.pipe_command(
        ['zcat', fasta],
        [BIN['makeblastdb'], '-dbtype', 'prot', '-title', title,
         '-out', output_prefix],
        stdout='logs/annotation-makeblastdb.out',
        stderr='logs/annotation-makeblastdb.err'
    )
