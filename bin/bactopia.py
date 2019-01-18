#! /usr/bin/env python3
# A wrapper for bactopia.nf, mainly for use on CGC.
import logging
import os
import subprocess


def output_handler(output, redirect='>'):
    if output:
        return [open(output, 'w'), '{0} {1}'.format(redirect, output)]
    else:
        return [subprocess.PIPE, '']


def onfinish_handler(cmd, out, err, returncode):
    out = '\n{0}'.format(out) if out else ''
    err = '\n{0}'.format(err) if err else ''
    if returncode != 0:
        logging.error('COMMAND: {0}'.format(cmd))
        logging.error('STDOUT: {0}'.format(out))
        logging.error('STDERR: {0}'.format(err))
        logging.error('END\n'.format(err))
        raise RuntimeError(err)
    else:
        logging.info('COMMAND: {0}'.format(cmd))
        logging.info('STDOUT: {0}'.format(out))
        logging.info('STDERR: {0}'.format(err))
        logging.info('END\n'.format(err))
        return [out, err]


def byte_to_string(b):
    if b:
        return b.decode("utf-8")
    else:
        return ''


def run_command(cmd, cwd=os.getcwd(), stdout=False, stderr=False):
    """Execute a single command and return STDOUT and STDERR."""
    stdout, stdout_str = output_handler(stdout)
    stderr, stderr_str = output_handler(stderr, redirect='2>')

    p = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, cwd=cwd)

    out, err = p.communicate()
    return onfinish_handler(
        '{0} {1} {2}'.format(' '.join(cmd), stdout_str, stderr_str),
        byte_to_string(out), byte_to_string(err), p.returncode
    )


def generate_nextflow(sample, fq1, organism, database, fq2, coverage, is_miseq, cpu, resume):
    cmd = ['./bactopia.nf', '--sample', sample, '--fq1', fq1,
           '--organism', organism, '--database', database, '--cpu', cpu,
           '--coverage', coverage]

    if fq2:
        cmd.append('--fq2')
        cmd.append(fq2)

    if is_miseq:
        cmd.append('--is_miseq')

    if resume:
        cmd.append('-resume')

    return cmd


if __name__ == '__main__':
    import argparse as ap

    parser = ap.ArgumentParser(
        prog='bactopia.py',
        conflict_handler='resolve',
        description=('A wrapper for executing Bactopia on CGC.'))
    parser.add_argument('fq1', metavar="FASTQ", type=str,
                        help=('Input FASTQ file.'))
    parser.add_argument('sample', metavar="SAMPLE", type=str,
                        help=('Sample name of the input.'))
    parser.add_argument('organism', metavar="ORGANISM", type=str,
                        help='Organism name of the input sample.')
    parser.add_argument('database', metavar="DATABASE", type=str,
                        help='Location of input databases.')
    parser.add_argument('--fq2', metavar="FASTQ", type=str,
                        help=('Second FASTQ file in paired end reads.'))
    parser.add_argument('--coverage', metavar="INT", type=int,
                        help='Number of processors to use.', default=100)
    parser.add_argument('--cpu', metavar="INT", type=int,
                        help='Number of processors to use.', default=1)
    parser.add_argument('--is_miseq', action='store_true', default=False,
                        help='Input is Illumina MiSeq sequencing.')
    parser.add_argument('--resume', action='store_true', default=False,
                        help='Tell nextflow to resume the run.')

    args = parser.parse_args()
    outdir = '{0}/{1}'.format(os.getcwd(), args.sample)
    # Setup logs
    run_command(['mkdir', '-p', args.sample])
    logging.basicConfig(filename='{0}/{0}-bactopia.txt'.format(args.sample),
                        filemode='w', level=logging.INFO)
    # Make directory and run pipeline
    run_command(['mkdir', '-p', args.sample])
    run_command(['cp', '/usr/local/bin/nextflow.config', outdir])
    run_command(['cp', '/usr/local/bin/bactopia.nf', outdir])
    run_command(['cp', '/opt/bactopia/data/bactopia-version.txt', outdir])
    bactopia_nf = generate_nextflow(
        args.sample, args.fq1, args.organism, args.database, args.fq2,
        str(args.coverage), args.is_miseq, str(args.cpu), args.resume
    )

    run_command(bactopia_nf, cwd=outdir)
    run_command(['date'], stdout='{0}/bactopia-date.txt'.format(outdir))

    # Fix symlinks
    for subdir, dirs, files in os.walk('./{0}'.format(args.sample)):
        for file in files:
            path = os.path.join(subdir, file)
            if os.path.islink(path):
                steps = '../' * (subdir.count('/') - 1)
                target = '{0}{1}'.format(
                    steps, os.readlink(path).replace('{0}/'.format(outdir), '')
                )
                run_command(['ln', '-sf', target, file], cwd=subdir)

    # Tarball and delete directory
    tarball = '{0}.tar'.format(args.sample)
    run_command(['tar', '-cvf', tarball, args.sample])
    run_command(['gzip', '--best', tarball])
    run_command(['md5sum', '{0}.tar.gz'.format(args.sample)],
                stdout='{0}.md5'.format(args.sample))
