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
            
        return cmd
        
    def get_unprocessed_ena(self, args):
        '''
        '''
        stdout, stderr = shared.run_command(
            self.build_command(args), 
            verbose=True
        )
        self.enainfo = json.loads(stdout)
    
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
        