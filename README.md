### Staphopia Analysis Pipeline
Staphopia's analysis pipeline is primarily written in Python. There are however a few programs written in C++.

### Requirements
    python-dev
    pip 
    gcc
    make
    ncurses
    libsqlite3-dev

### Installation

    git clone git@github.com:Read-Lab-Confederation/staphopia-analysis-pipeline.git
    cd staphopia-analysis-pipeline
    make
    # Wait...
    # Eventually when complete you should get something similar to below. Copy and past this into your .bashrc or remember to export this each login.
    
    *******************************************************************
    *******************************************************************
    *******************************************************************
    Please add the following to your profile (.profile, .bashrc, .bash_profile, etc...).
    
    export PYTHONPATH=/tmp/staphopia-analysis-pipeline/src/third-party/call_variants:\
    /tmp/staphopia-analysis-pipeline/src/third-party/call_variants/src/third-party/python:\
    /tmp/staphopia-analysis-pipeline/src/third-party/call_variants/src/third-party/python/vcf-annotator:\
    /tmp/staphopia-analysis-pipeline/src/third-party/call_variants:\
    /tmp/staphopia-analysis-pipeline/src/third-party/call_variants/src/third-party/python:\
    /tmp/staphopia-analysis-pipeline/src/third-party/call_variants/src/third-party/python/vcf-annotator:\
    $PYTHONPATH
    
    *******************************************************************
    *******************************************************************
    *******************************************************************
    
    # If you need it again
    make variant-pythonpath
    
    # Test to make sure everything is installed properly
    make test

### Processing a Genome On Merlin

#### Requirements
1. Genomes must be Gzipped FASTQ (*sample.fastq.gz*)
2. Merlin has a maximum of 20 usable processors, if you exceed it your job will not start.

#### Edit Your Profile
You will need to add some details to your ``~/.bashrc`` file

    export PYTHONPATH=/home/rpetit/staphopia/analysis-pipeline/src/third-party/python/vcf-annotator:\
    /home/rpetit/staphopia/analysis-pipeline/src/third-party/python:\
    /home/rpetit/staphopia/analysis-pipeline:\
    /home/rpetit/staphopia/private:$PYTHONPATH

#### Prep Genomes For Processing
Navigate to your directory of samples to be processed.
For example:

    cd ~/staph_samples
    ls 
        sample_01.fastq.gz
        sample_02.fastq.gz
        sample_03.fastq.gz

Now that you are in the directory containing your samples you can do a number of things. If you want to keep your samples all in one directory you may. Or, you can create a separate directory for each then move the compressed FASTQ files in to their corresponding. Or, you could create directories then may symlinks to the FASTQ file. Which ever you find easiest.

For example:

    mkdir sample_01 sample_02 sample_03
    mv sample_01.fastq.gz sample_01/
    mv sample_02.fastq.gz sample_02/
    mv sample_03.fastq.gz sample_03/
    
#### Creating A Job Script
Now we want to use Sun Grid Engine to manage our jobs. So first we will need to create a job script. Staphopia includes the aptly named ``create_job_script`` to do just that!

Since this is on Merlin and everything is alread set up, we can use the following:

    /home/rpetit/staphopia/analysis-pipeline/bin/pipelines/create_job_script --help
    usage: create_job_script [--input STR] [--working_dir STR] [--processors INT]
                             [--sample_tag STR] [--paired] [--log_times] [-h]
                             [--version]
    
    Create a SGE usable script to submit a FASTQ file through the pipeline. Print
    to STDOUT.
    
    Options:
    
      --input STR        Input FASTQ file
      --working_dir STR  Working directory to execute script from.
      --processors INT   Number of processors to use.
      --sample_tag STR   Optional: Sample tag of the input
      --paired           Input is interleaved paired end reads.
      --log_times        Write task run times to file (Default: STDERR).
    
    Help:
    
      -h, --help         Show this help message and exit
      --version          Show program's version number and exit
    
We only need a few parameters to create a job script. Those being the input FASTQ, a working directory, number of processors to use, and a sample tag. You may also give the paired flag, but at the moment that will not affect the analysis. You can also choose to log the runtime of each portion of the pipeline with ``--log_times``.

Create job script will use a template and the given parameters to spit a fucntional job script to STDOUT. So be sure to redirect it to a file.

An example of running ``create_job_script`` follows:

    /home/rpetit/staphopia/analysis-pipeline/bin/pipelines/create_job_script \
    --input ~/staph_samples/sample_01/sample_01.fastq.gz \
    --working_dir ~/staph_samples/sample_01/ \
    --processors 8 \
    --sample_tag sample_01 \
    --log_times > ~/staph_samples/sample_01/sample_01.sh

Now you will have a job script, ``~/staph_samples/sample_01/sample_01.sh``, which looks like the following:

    #! /bin/bash
    #$ -wd /home/rpetit/staph_samples/sample_01/
    #$ -V
    #$ -N jsample_01
    #$ -S /bin/bash
    #$ -pe orte 8
    #$ -o /home/rpetit/staph_samples/sample_01//submit_job.stdout
    #$ -e /home/rpetit/staph_samples/sample_01//submit_job.stderr
    
    # Environment Variables
    export PATH=/home/rpetit/staphopia/analysis-pipeline/bin:/home/rpetit/staphopia/analysis-pipeline/bin/pipelines:/home/rpetit/staphopia/analysis-pipeline/bin/third-party:/home/rpetit/staphopia/analysis-pipeline/src/third-party/prokka/binaries/linux:$PATH
    export PYTHONPATH=/home/rpetit/staphopia/analysis-pipeline:/home/rpetit/staphopia/analysis-pipeline/src/third-party/python:/home/rpetit/staphopia/analysis-pipeline/src/third-party/python/vcf-annotator:$PYTHONPATH
    export OMP_NUM_THREADS=7
    export OMP_THREAD_LIMIT=8
    
    # Command
    
    /home/rpetit/staphopia/analysis-pipeline/bin/pipelines/submit_job -i /home/rpetit/staph_samples/sample_01/sample_01.fastq.gz -p 8  --sample_tag sample_01 --log_times

#### Submitting The Job
Because we are using Merlin and SGE is already setup you now only need to execute the following command:

    qsub ~/staph_samples/sample_01/sample_01.sh
    
The just should have now been submitted and your genome will begin processing. You can use ``qstat`` to see the state of your job, and ``qdel $JOB_NUMBER`` to delete jobs.    

### Contact
robert.petit@emory.edu
