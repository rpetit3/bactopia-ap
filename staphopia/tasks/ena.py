"""ENA related functions."""
import os
try:
    import ujson as json
except ImportError:
    import json

from staphopia.config import BIN
from staphopia.tasks import shared


def build_command(args):
    """Append arguements for unprocessed_ena call."""
    cmd = ['python', args.manage, 'unprocessed_ena']
    # Build command

    if args.limit:
        cmd.append('--limit')
        cmd.append(str(args.limit))

    if args.technology:
        cmd.append('--technology')
        cmd.append(args.technology)

    if args.coverage:
        cmd.append('--coverage')
        cmd.append(str(args.coverage))

    if args.min_read_length:
        cmd.append('--min_read_length')
        cmd.append(str(args.min_read_length))

    if args.max_read_length:
        cmd.append('--max_read_length')
        cmd.append(str(args.max_read_length))

    if args.experiment:
        cmd.append('--experiment')
        cmd.append(args.experiment)

    if args.study:
        cmd.append('--study')
        cmd.append(args.study)

    if args.column:
        cmd.append('--column')
        cmd.append(args.column)

    if args.accessions:
        cmd.append('--accessions')
        cmd.append(args.accessions)

    if args.published:
        cmd.append('--published')

    return cmd


def get_unprocessed_ena(args):
    """Retreive a list of unprocessed samples avalible from ENA."""
    cmd = build_command(args)
    stdout, stderr = shared.run_command(cmd, verbose=False)
    print(' '.join(cmd))

    return json.loads(stdout)


def get_ena_info(manage, experiment=None):
    """Retreive a list of unprocessed samples avalible from ENA."""
    if experiment:
        stdout, stderr = shared.run_command(
            ['python', manage, 'ena_info', '--experiment', experiment],
            verbose=False)
        return json.loads(stdout)
    else:
        return None


def get_runs_by_study(study, manage):
    """Return a dictionary of runs associated with a study."""
    cmd = ['python', manage, 'ena_info', '--study', study]
    stdout, stderr = shared.run_command(cmd, verbose=False)

    return json.loads(stdout)


def get_runs_by_experiment(experiment, manage):
    """Return a dictionary of runs associated with a experiment."""
    cmd = ['python', manage, 'ena_info', '--experiment', experiment]
    stdout, stderr = shared.run_command(cmd, verbose=False)

    return json.loads(stdout)


def get_experiment_by_run(run, manage):
    """Return a dictionary with an experiment associated with a run."""
    cmd = ['python', manage, 'ena_info', '--run', run]
    stdout, stderr = shared.run_command(cmd, verbose=False)

    return json.loads(stdout)


def download_fastq(url, outdir, fastq, ftp=False):
    """Download FASTQ from ENA using Apera Connect."""
    if not os.path.isdir(outdir):
        shared.run_command(['mkdir', '-p', outdir], verbose=False)

    if not os.path.exists(fastq):
        if ftp:
            shared.run_command(
                ['wget', '-O', fastq, url],
                verbose=False
            )
        else:
            shared.run_command(
                [BIN['ascp'], '-T', '-l', '300m', '-P33001', '-i', BIN['aspera_key'],
                 'era-fasp@{0}'.format(url), outdir],
                verbose=False
            )

    return shared.get_md5sum(fastq)


def merge_runs(runs, output):
    """Merge runs from an experiment."""
    if len(runs) > 1:
        cat_cmd = ['cat']
        rm_cmd = ['rm']
        for run in runs:
            cat_cmd.append(run)
            rm_cmd.append(run)

        shared.run_command(cat_cmd, stdout=output, verbose=False)
        shared.run_command(rm_cmd, verbose=False)
    else:
        shared.run_command(['mv', runs[0], output], verbose=False)
