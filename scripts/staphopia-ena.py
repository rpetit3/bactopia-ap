#! /usr/bin/env python3
# A wrapper for staphopia.nf, mainly for use on CGC.
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


def generate_nextflow(sample, args, cpu, resume):
    cmd = ['./staphopia.nf', '--sample', sample, '--cpu', cpu]
    for arg in args.split():
        cmd.append(arg)

    if resume:
        cmd.append('-resume')

    return cmd


if __name__ == '__main__':
    import argparse as ap
    import glob

    parser = ap.ArgumentParser(
        prog='staphopia-ena.py',
        conflict_handler='resolve',
        description=('A wrapper for executing Staphopia on CGC.'))
    parser.add_argument('sample', metavar="SAMPLE", type=str,
                        help=('Sample name of the input.'))
    parser.add_argument('--cpu', metavar="INT", type=int,
                        help='Number of processors to use.', default=1)
    parser.add_argument('--resume', action='store_true', default=False,
                        help='Tell nextflow to resume the run.')

    args = parser.parse_args()
    outdir = '{0}/{1}'.format(os.getcwd(), args.sample)
    # Setup logs
    logging.basicConfig(filename='{0}-staphopia.txt'.format(args.sample),
                        filemode='w', level=logging.INFO)
    # Download from ENA
    run_command(['mkdir', '-p', args.sample])
    ena_out, ena_err = run_command(['ena-dl.py', args.sample, './', '--quiet',
                                    '--nextflow', '--group_by_experiment'])
    run_command(['mv', 'ena-run-info.json', 'ena-run-mergers.json', outdir])
    with open('{0}/ena-dl.txt'.format(outdir), 'w') as fh:
        fh.write(('ena-dl.py {0} ../ --quiet --nextflow '
                  '--group_by_experiment\n').format(args.sample))

    # Make directory and run pipeline
    run_command(['cp', '/usr/local/bin/nextflow.config', outdir])
    run_command(['cp', '/usr/local/bin/staphopia.nf', outdir])
    staphopia_nf = generate_nextflow(args.sample, ena_out, str(args.cpu),
                                     args.resume)
    run_command(staphopia_nf, cwd=outdir)
    run_command(['date'], stdout='{0}/staphopia-date.txt'.format(outdir))

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

    # Cleanup
    run_command(['rm', '-rf', outdir])
    for name in glob.glob('*.fastq.gz'):
        run_command(['rm', '-rf', name])
