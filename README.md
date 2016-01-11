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

### Processing a Genome

### Contact
robert.petit@emory.edu
