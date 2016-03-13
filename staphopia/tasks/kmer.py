"""Count k-mers within FASTQ file."""
from staphopia.config import BIN
from staphopia.tasks import shared


def jellyfish_count(fastq, output_file, num_cpu):
    """Count k-mers in a FASTQ file."""
    shared.run_command(['gunzip', '-k', fastq])
    fastq = fastq.replace(".gz", "")
    jellyfish = shared.run_command([
        BIN['jellyfish'], 'count', '-m', '31', '-s', '100M', '-C',
        '-t', num_cpu, '-o', output_file, fastq
    ])
    shared.run_command(['rm', fastq])
    return jellyfish
