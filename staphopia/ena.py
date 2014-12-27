#! /usr/bin/python
'''
    Author: Robert A. Petit III

    [TODO: Elaborate on description]
'''
import os
import json

from staphopia.tasks import shared
from subprocess import check_call

class ENA(object):

    def __init__(self, config):
        self.config = config

    def get_md5sum(self, file):
        stdout, stderr = shared.run_command(
            ['md5sum', file],
            verbose=False
        )
        if stdout:
            md5sum, filename = stdout.split()
            return md5sum
        else:
            return None

    def copy_file(self, file_1, file_2):
        stdout, stderr = shared.run_command(
            ['cp', file_1, file_2],
            verbose=False
        )

    def remove_file(self, file):
        stdout, stderr = shared.run_command(
            ['rm', '-f', file],
            verbose=False
        )

    def build_command(self, args):
        cmd = ['python', self.config['manage'], 'unprocessed_ena',
               '--settings', self.config['settings']]
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

        return cmd

    def get_unprocessed_ena(self, args):
        '''
        '''
        stdout, stderr = shared.run_command(
            self.build_command(args),
            verbose=False
        )
        self.enainfo = json.loads(stdout)

    def queue_download(self, experiment, ebs_dir, s3_dir):
        """ . """
        mkdir = shared.run_command(['mkdir', ebs_dir + '/logs'], verbose=False)
        JOB_SCRIPT = '\n'.join([
            '#! /bin/bash',
            '#$ -wd {0}'.format(ebs_dir),
            '#$ -V',
            '#$ -N j{0}'.format(experiment),
            '#$ -S /bin/bash',
            '#$ -pe orte 1',
            '#$ -o {0}/logs/{1}.stdout'.format(ebs_dir, experiment),
            '#$ -e {0}/logs/{1}.stderr'.format(ebs_dir, experiment),
            '',
            '# Command',
            '',
            'python {0} --experiment {1} --output {2} --s3 {3}'.format(
                self.config['download_ena'],
                experiment,
                ebs_dir,
                s3_dir,
            ),
            '',
        ])
        script = '{0}/logs/{1}.sh'.format(ebs_dir, experiment),
        fh = open(script, "w")
        fh.write(JOB_SCRIPT)
        fh.close()

        stdout, stderr = shared.run_command(['qsub', script], verbose=False)
        return stdout

    def download_fastq(self, fasp, outdir, fastq):
        '''
        '''
        if not os.path.isdir(outdir):
            mkdir = shared.run_command(['mkdir', '-p', outdir], verbose=False)

        if not os.path.exists(fastq):
            ascp = shared.run_command(
                [self.config['ascp'], '-T', '-l', '300m', '-i',
                 self.config['ssh_key'], 'era-fasp@{0}'.format(fasp), outdir],
                verbose=False
            )

    def interleave_fastq(self, runs, output):
        fastq_interleave = check_call(
            '{0} <(zcat {1}) <(zcat {2}) | gzip - > {3}'.format(
                self.config['fastq_interleave'],
                runs[0],
                runs[1],
                output
            ),
            shell=True,
            executable='/bin/bash'
        )
        if not fastq_interleave:
            for run in runs:
                rm = shared.run_command(['rm', run], verbose=False)

    def merge_runs(self, runs, output):
        if len(runs) > 1:
            cat_cmd = ['cat']
            rm_cmd = ['rm']
            for run in runs:
                cat_cmd.append(run)
                rm_cmd.append(run)

            cat = shared.run_command(cat_cmd, stdout=output, verbose=False)
            rm = shared.run_command(rm_cmd, verbose=False)
        else:
            mv = shared.run_command(['mv', runs[0], output], verbose=False)

    '''
    '''
    def is_paired(self, experiment):
        '''
        '''
        stdout, stderr = shared.run_command(
            ['python', self.config['manage'], 'ena_is_paired', '--settings',
             self.config['settings'], '--experiment', experiment],
            verbose=False
        )
        return True if int(stdout) == 1 else False

    def ena_to_sample(self, experiment, is_paired):
        '''
        '''
        is_paired = '--is_paired' if is_paired else ''
        stdout, stderr = shared.run_command(
            ['python', self.config['manage'], 'ena_to_sample', '--settings',
             self.config['settings'], '--experiment', experiment, is_paired],
            verbose=False
        )

        try:
            return json.loads(stdout)
        except ValueError, e:
            print stdout, stderr
            return False

    def move_experiment(self, input, output, outdir):
        outdir = '{0}/logs'.format(outdir)
        if not os.path.isdir(outdir):
            mkdir = shared.run_command(['mkdir', '-p', outdir], verbose=False)

        mv = shared.run_command(['mv', input, output], verbose=False)

        return os.path.exists(output)

    def create_job_script(self, output, input, outdir, is_paired, sample_info):
        '''
        '''
        is_paired = '--paired' if is_paired else ''
        production = '--production' if self.config['production'] else ''
        debug = '--debug' if self.config['debug'] else ''
        stdout, stderr = shared.run_command(
            [self.config['create_job_script'], '--input', input, '--working_dir',
             outdir, is_paired, '--sample_id', str(sample_info['sample_id']),
             '--sample_tag', sample_info['sample_tag'], production, debug,
             '--processors', self.config['n_cpu']],
            stdout=output,
            verbose=False
        )
        return os.path.exists(output)

    def submit_job(self, script):
        '''
        '''
        stdout, stderr = shared.run_command(['qsub', script], verbose=False)
