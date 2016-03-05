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
See wiki for more details

    git clone git@github.com:Read-Lab-Confederation/staphopia-analysis-pipeline.git
    cd staphopia-analysis-pipeline
    make
    
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


### Contact
robert.petit@emory.edu
