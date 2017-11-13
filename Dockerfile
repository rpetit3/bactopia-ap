FROM broadinstitute/gatk3:3.8-0 as gatk
FROM rpetit3/nextconda-base
MAINTAINER robbie.petit@gmail.com

# Install dependencies
RUN apt-get -qq update \
    && apt-get -qq -y install g++ gcc less \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log

# Update Nextflow and Conda
RUN nextflow self-update \
    && conda upgrade conda \
    && mkdir -p /opt/staphopia/data

# Install via Bioconda
# Program versions last update 11/2017
RUN conda install -y python=3.5.4 \
    && conda install -y ariba=2.10.1 \
    && conda install -y bbmap=37.66 \
    && conda install -y bedtools=2.26.0gx \
    && conda install -y blast=2.7.1 \
    && conda install -y bwa=0.7.17 \
    && conda install -y jellyfish=2.2.6 \
    && conda install -y picard=2.14.1 \
    && conda install -y prokka=1.12 \
    && conda install -y samtools=1.6 \
    && conda install -y spades=3.11.1 \
    && conda install -y wget \
    && conda clean --all --yes \
    && pip install --upgrade pip

# GATK
COPY --from=gatk /usr/GenomeAnalysisTK.jar /usr/local/bin/GenomeAnalysisTK.jar

# Assembly Summary
RUN cd /tmp/ \
    && curl -sSL https://github.com/rpetit3/assembly-summary/archive/v0.1.tar.gz -o assembly-summary-0.1.tar.gz \
    && tar -xzf assembly-summary-0.1.tar.gz \
    && pip install -r assembly-summary-0.1/requirements.txt \
    && chmod 755 assembly-summary-0.1/assembly-summary.py \
    && mv assembly-summary-0.1/assembly-summary.py /usr/local/bin/ \
    && rm -rf assembly-summary*

# Illumina Cleanup
RUN cd /tmp/ \
    && curl -sSL https://github.com/rpetit3/illumina-cleanup/archive/v0.1.tar.gz -o illumina-cleanup-0.1.tar.gz \
    && tar -xzf illumina-cleanup-0.1.tar.gz \
    && pip install -r illumina-cleanup-0.1/requirements.txt \
    && chmod 755 illumina-cleanup-0.1/src/* \
    && mv illumina-cleanup-0.1/src/*.py /usr/local/bin/ \
    && g++ -Wall -O3 -o /usr/local/bin/fastq-interleave illumina-cleanup-0.1/src/fastq-interleave.cpp \
    && g++ -Wall -O3 -o /usr/local/bin/fastq-stats illumina-cleanup-0.1/src/fastq-stats.cpp \
    && mkdir -p /opt/staphopia/data/fastq \
    && mv illumina-cleanup-0.1/data/*.fasta /opt/staphopia/data/fastq \
    && rm -rf illumina-cleanup*

# VCF-Annotator
RUN cd /tmp/ \
    && curl -sSL https://github.com/rpetit3/vcf-annotator/archive/v0.4.tar.gz  -o vcf-annotator-0.4.tar.gz \
    && tar -xzf vcf-annotator-0.4.tar.gz \
    && pip install -r vcf-annotator-0.4/requirements.txt \
    && chmod 755 vcf-annotator-0.4/vcf-annotator.py \
    && mv vcf-annotator-0.4/vcf-annotator.py /usr/local/bin/ \
    && rm -rf vcf-annotator*

# ENA Downloader (ena-dl)
RUN cd /tmp/ \
    && curl -sSL https://github.com/rpetit3/ena-dl/archive/v0.1.tar.gz -o ena-dl-0.1.tar.gz \
    && tar -xzf ena-dl-0.1.tar.gz \
    && pip install -r ena-dl-0.1/requirements.txt \
    && chmod 755 ena-dl-0.1/ena-* \
    && mv ena-dl-0.1/ena-* /usr/local/bin/ \
    && rm -rf ena-dl*

# Aspera Connect
RUN cd /tmp/ \
    && wget --quiet http://download.asperasoft.com/download/sw/connect/3.7.4/aspera-connect-3.7.4.147727-linux-64.tar.gz \
    && tar -xzf aspera-connect-3.7.4.147727-linux-64.tar.gz \
    && sed -i 's=INSTALL_DIR\=~/.aspera/connect=INSTALL_DIR\=/opt/aspera=' aspera-connect-3.7.4.147727-linux-64.sh \
    && mkdir -p /opt/aspera \
    && bash aspera-connect-3.7.4.147727-linux-64.sh \
    && rm -rf aspera-connect*

ENV ASCP /opt/aspera/bin/ascp
ENV ASCP_KEY /opt/aspera/etc/asperaweb_id_dsa.openssh

# Copy Staphopia Workflows
COPY scripts/staphopia.nf /usr/local/bin
COPY scripts/staphopia-ena.nf /usr/local/bin
COPY scripts/bwa-align.sh /usr/local/bin
COPY scripts/mlst-blast.py /usr/local/bin
COPY data /opt/staphopia/data
RUN chmod 755 /usr/local/bin/staphopia*.nf /usr/local/bin/bwa-align.sh /usr/local/bin/mlst-blast.py
RUN mkdir /data

WORKDIR /data
