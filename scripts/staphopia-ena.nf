#!/usr/bin/env nextflow
import groovy.json.JsonSlurper
params.help = null
if (params.help) {
    print_usage()
    exit 1
}

check_input_params()

params.output = null
params.cpu = 1
params.coverage = 100
params.is_miseq = false
params.staphopia_data = '/opt/staphopia/data'
params.gatk = '/usr/local/bin/GenomeAnalysisTK.jar'

// Set some global variables
sample = params.experiment
outdir = params.output ? params.output : './'
is_miseq = null
is_paired = null
staphopia_data = params.staphopia_data
cpu = params.cpu
genome_size = 2814816

// Output folders
analysis_folder = outdir + "/analyses"
annotation_folder = analysis_folder + "/annotation"
assembly_folder = analysis_folder + "/assembly"
jellyfish_folder = analysis_folder + "/kmer"
mlst_folder = analysis_folder + '/mlst'
plasmid_folder = analysis_folder + "/plasmids"
fastq_folder = analysis_folder + "/illumina-cleanup"
sccmec_folder = analysis_folder + "/sccmec"
variants_folder = analysis_folder + "/variants"
blastdb_folder = outdir + "/blastdb"

/* ==== BEGIN ENA DOWNLOAD ==== */
process download_experiment {
    cache: false

    input:
        val sample
    output:
        file "*.fastq.gz" into INPUT_FQ
        stdout json_output
    shell:
        '''
        ena-dl.py !{sample} --quiet --json --group_by_experiment
        '''
}

// Make sure the download succeeded and get paired/miseq info
slurp = new JsonSlurper()
json_data = slurp.parseText(json_output.getVal())

if (!json_data.success) {
    log.info 'Failed to download ${sample} sucessfully, exiting...'
    exit 1
}
is_paired = json_data.is_paired
is_miseq = json_data.is_miseq

/* ==== END ENA DOWNLOAD ==== */

/* ==== BEGIN FASTQ CLEANUP ==== */
process illumina_cleanup {
    publishDir fastq_folder, overwrite: true, pattern: '*.{json,gz,log}'

    input:
        file fq from INPUT_FQ
    output:
        file '*cleanup.fastq.gz' into FASTQ_STATS, FASTQ_JF, FASTQ_ASSEMBLY,
                                      FASTQ_PLASMIDS, FASTQ_MLST, FASTQ_CGMLST,
                                      FASTQ_SCCMEC, FASTQ_VARIANTS, ARIBA_MLST,
                                      ARIBA_VFDB, ARIBA_MEGARES
        file '*.json'
        file '*.log'
        file {"${sample}.cleanup.fastq.json"} into FINAL_STATS
    shell:
        no_length_filter = is_miseq ? '--no_length_filter' : ''
        if (is_paired)
        '''
        bbduk.sh -Xmx2g threads=!{cpu} in=!{fq[0]} in2=!{fq[1]} out=bbduk-phix-R1.fq \
        out2=bbduk-phix-R2.fq stats=bbduk-phix.log hdist=1 k=31 overwrite=t \
        ordered=t ref=!{staphopia_data}/fastq/phiX-NC_001422.fasta

        bbduk.sh -Xmx2g threads=!{cpu} in=bbduk-phix-R1.fq in2=bbduk-phix-R2.fq \
        out=bbduk-adapter-R1.fq out2=bbduk-adapter-R2.fq stats=bbduk-adapter.log \
        ktrim=r k=23 mink=11 hdist=1 tpe tbo qout=33 minlength=36  overwrite=t \
        ordered=t ref=!{staphopia_data}/fastq/adapters.fasta

        spades.py -1 bbduk-adapter-R1.fq -2 bbduk-adapter-R2.fq --only-error-correction \
                  --disable-gzip-output -t !{cpu} -o ./

        zcat !{fq[0]} !{fq[1]} | fastq-stats > !{sample}.original.fastq.json
        cat bbduk-adapter-R1.fq bbduk-adapter-R2.fq | fastq-stats > !{sample}.adapter.fastq.json
        cat corrected/bbduk-adapter-R1.00.0_0.cor.fastq corrected/bbduk-adapter-R2.00.0_0.cor.fastq | \
        fastq-stats > !{sample}.post-ecc.fastq.json

        fastq-interleave corrected/bbduk-adapter-R1.00.0_0.cor.fastq corrected/bbduk-adapter-R2.00.0_0.cor.fastq | \
        illumina-cleanup.py --paired --stats !{sample}.post-ecc.fastq.json --coverage !{params.coverage} \
        !{no_length_filter} > cleanup.fastq

        reformat.sh in=cleanup.fastq out1=!{sample}_R1.cleanup.fastq out2=!{sample}_R2.cleanup.fastq

        cat !{sample}_R1.cleanup.fastq !{sample}_R2.cleanup.fastq | fastq-stats > !{sample}.cleanup.fastq.json

        gzip --best !{sample}_R1.cleanup.fastq
        gzip --best !{sample}_R2.cleanup.fastq

        cp .command.err illumina_cleanup-stderr.log
        cp .command.out illumina_cleanup-stdout.log
        '''
        else
        '''
        bbduk.sh -Xmx2g threads=!{cpu} in=!{fq} out=bbduk-phix-R1.fq \
        stats=bbduk-phix.txt hdist=1 k=31 overwrite=t ordered=t \
        ref=!{staphopia_data}/fastq/phiX-NC_001422.fasta

        bbduk.sh -Xmx2g threads=!{cpu} in=bbduk-phix-R1.fq out=bbduk-adapter-R1.fq \
        stats=bbduk-adapter.log ktrim=r k=23 mink=11 hdist=1 tpe tbo qout=33 \
        ref=!{staphopia_data}/fastq/adapters.fasta minlength=36 overwrite=t ordered=t

        spades.py -s bbduk-adapter-R1.fq --only-error-correction --disable-gzip-output \
                  -t !{cpu} -o ./

        zcat !{fq} | fastq-stats !{genome_size} > !{sample}.original.fastq.json
        cat bbduk-adapter-R1.fq | fastq-stats !{genome_size} > !{sample}.adapter.fastq.json
        cat corrected/bbduk-adapter-R1.00.0_0.cor.fastq | fastq-stats !{genome_size} > !{sample}.post-ecc.fastq.json

        cat corrected/bbduk-adapter-R1.00.0_0.cor.fastq | illumina-cleanup.py --stats !{sample}.post-ecc.fastq.json \
        --coverage !{params.coverage} !{no_length_filter} | gzip --best - > !{sample}.cleanup.fastq.gz

        zcat !{sample}.cleanup.fastq.gz | fastq-stats !{genome_size} > !{sample}.cleanup.fastq.json
        cp .command.err illumina_cleanup-stderr.log
        cp .command.out illumina_cleanup-stdout.log
        '''
}

// Store median read length for downstream analysis
slurp = new JsonSlurper()
read_length = slurp.parseText(file(FINAL_STATS.getVal()).text).qc_stats.read_median
/* ==== END FASTQ CLEANUP ==== */

/* ==== BEGIN JELLYFISH 31-MER COUNT ==== */
process count_31_mers {
    publishDir jellyfish_folder, overwrite: true, pattern: '*.{jf,log}'

    input:
        file fq from FASTQ_JF
    output:
        file {"${sample}.jf"}
        file '*.log'
    shell:
        '''
        jellyfish count -m 31 -s 100M -C -t !{cpu} -o !{sample}.jf <(zcat !{fq})
        cp .command.err jellyfish-stderr.log
        cp .command.out jellyfish-stdout.log
        '''
}
/* ==== END JELLYFISH 31-MER COUNT ==== */

/* ==== BEGIN SPADES ASSEMBLY ==== */
process spades_assembly {
    publishDir assembly_folder, overwrite: true, pattern: '*.{gz,log}'

    input:
        file fq from FASTQ_ASSEMBLY
    output:
        file '*.fasta.gz' into ASSEMBLY_STATS mode flatten
        file '*.contigs.fasta.gz' into ANNOTATION, MLST, MAKEBLASTDB
        file '*.fastg.gz'
        file '*.log'
    shell:
        flag = is_paired ? '-1 ' + fq[0] + ' -2 ' + fq[1]: '-s ' + fq[0]
        '''
        spades.py !{flag} --careful -t !{cpu} -o ./ --only-assembler
        gzip --best -c contigs.fasta > !{sample}.contigs.fasta.gz
        gzip --best -c scaffolds.fasta > !{sample}.scaffolds.fasta.gz
        gzip --best -c assembly_graph.fastg > !{sample}.assembly_graph.fastg.gz
        cp .command.err assembly-stderr.log
        cp .command.out assembly-stdout.log
        '''
}

process assembly_stats {
    publishDir assembly_folder, overwrite: true

    input:
        file fasta from ASSEMBLY_STATS
    output:
        file '*.json'
    shell:
        stats = fasta.getName().replace("fasta.gz", "json")
        '''
        zcat !{fasta} | assembly-summary.py --genome_size !{genome_size} > !{stats}
        '''
}

process spades_plasmid_assembly {
    errorStrategy 'ignore'
    validExitStatus 0, 1, 255
    publishDir plasmid_folder, overwrite: true, pattern: '*.{gz,log}'

    input:
        file fq from FASTQ_PLASMIDS
    output:
        file '*.fasta.gz' into PLASMID_STATS mode flatten
        file '*.fastg.gz'
        file '*.log'
    shell:
        flag = is_paired ? '-1 ' + fq[0] + ' -2 ' + fq[1]: '-s ' + fq[0]
        '''
        spades.py !{flag} --careful -t !{cpu} -o ./ --only-assembler --plasmid
        gzip --best -c contigs.fasta > !{sample}.contigs.fasta.gz
        gzip --best -c scaffolds.fasta > !{sample}.scaffolds.fasta.gz
        gzip --best -c assembly_graph.fastg > !{sample}.assembly_graph.fastg.gz
        cp .command.err plasmid-assembly-stderr.log
        cp .command.out plasmid-assembly-stdout.log
        '''
}

process plasmid_stats {
    errorStrategy 'ignore'
    validExitStatus 0, 1, 255
    publishDir plasmid_folder, overwrite: true

    input:
        file fasta from PLASMID_STATS
    output:
        file '*.json'
    shell:
        stats = fasta.getName().replace("fasta.gz", "json")
        '''
        zcat !{fasta} | assembly-summary.py --genome_size 2814816 > !{stats}
        '''
}

process makeblastdb {
    publishDir blastdb_folder, overwrite: true, pattern: "*contigs.*"

    input:
        file fasta from MAKEBLASTDB
    output:
        file ({"${sample}-contigs.*"}) into (SCCMEC_PROTEINS, SCCMEC_PRIMERS, SCCMEC_SUBTYPES)
    shell:
        '''
        zcat !{fasta} | \
        makeblastdb -dbtype "nucl" -title "Assembled contigs for !{sample}" -out !{sample}-contigs
        '''
}
/* ==== END SPADES ASSEMBLY ==== */

/* ==== BEGIN ANNOTATION ==== */
process annotation {
    publishDir annotation_folder, overwrite: true, pattern: '*.{gz,txt,log}'

    input:
        file fasta from ANNOTATION
    output:
        file '*.gz'
        file '*.txt'
        file '*.log'
    shell:
        gunzip_fa = fasta.getName().replace('.gz', '')
        '''
        gunzip -f !{fasta}
        prokka --cpus !{cpu} --genus Staphylococcus --usegenus --outdir ./ \
               --force --proteins !{staphopia_data}/annotation/saureus.prokka \
               --prefix !{sample} --locustag !{sample} --centre STA --compliant --quiet \
               !{gunzip_fa}

        rm -rf !{gunzip_fa} !{sample}.fna !{sample}.fsa !{sample}.gbf !{sample}.sqn !{sample}.tbl
        find ./ -type f -not -name "*.txt" -and -not -name "*command*" -and -not -name "*exit*" | \
        xargs -I {} gzip --best {}
        cp .command.err annotation-stderr.log
        cp .command.out annotation-stdout.log
        '''
}
/* ==== END ANNOTATION ==== */

/* ==== BEGIN MLST ==== */
process mlst_blast {
    publishDir mlst_folder, overwrite: true

    input:
        file fasta from MLST
    output:
        file 'mlst-blastn.json'
    shell:
        '''
        mlst-blast.py !{fasta} !{staphopia_data}/mlst/blastdb mlst-blastn.json --cpu !{cpu}
        '''
}

process mlst_ariba {
    publishDir mlst_folder, overwrite: true

    input:
        file fq from ARIBA_MLST
    output:
        file 'ariba/*'
    shell:
        if (is_paired)
        '''
        ariba run !{staphopia_data}/ariba/mlst/ref_db !{fq} ariba
        rm -rf ariba.tmp*
        '''
        else
        '''
        echo "ariba requires paired end reads" > ariba-requires-pe.txt
        '''
}

process mlst_mentalist {
    errorStrategy 'ignore'
    publishDir mlst_folder + "/mentalist", overwrite: true, pattern: '*.txt'

    input:
        file fq from FASTQ_MLST
    output:
        file '*.txt'
    shell:
        '''
        mentalist call -o mlst.txt -s !{sample} --db !{staphopia_data}/mentalist/mlst/mlst-31.db !{fq}
        mentalist call -o cgmlst.txt -s !{sample} --db !{staphopia_data}/mentalist/cgmlst/cgmlst-31.db !{fq}
        '''
}

/* ==== END MLST ==== */

/* ==== BEGIN RESISTANCE AND VIRULENCE ==== */
process resistance_ariba {
    publishDir analysis_folder, overwrite: true

    input:
        file fq from ARIBA_MEGARES
    output:
        file 'resistance/*'
    shell:
        if (is_paired)
        '''
        ariba run !{staphopia_data}/ariba/megares !{fq} resistance
        rm -rf ariba.tmp*
        '''
        else
        '''
        echo "ariba requires paired end reads" > ariba-requires-pe.txt
        '''
}

process virulence_ariba {
    publishDir analysis_folder, overwrite: true

    input:
        file fq from ARIBA_VFDB
    output:
        file 'virulence/*'
    shell:
        if (is_paired)
        '''
        ariba run !{staphopia_data}/ariba/vfdb !{fq} virulence
        rm -rf ariba.tmp*
        '''
        else
        '''
        echo "ariba requires paired end reads" > ariba-requires-pe.txt
        '''
}
/* ==== END RESISTANCE AND VIRULENCE ==== */

/* ==== BEGIN SCCMEC ==== */
process sccmec_proteins {
    publishDir sccmec_folder, overwrite: true

    input:
        file blastdb from SCCMEC_PROTEINS
    output:
        file '*.json'
    shell:
        '''
        BLASTDB=$(echo "!{blastdb[0]}" | cut -f 1 -d '.')
        tblastn -db $BLASTDB -query !{staphopia_data}/sccmec/proteins.fasta \
                -outfmt 15 -num_threads !{cpu} -evalue 0.0001 \
                -max_target_seqs 1 > proteins.json
        '''
}

process sccmec_primers {
    publishDir sccmec_folder, overwrite: true

    input:
        file blastdb from SCCMEC_PRIMERS
    output:
        file '*.json'
    shell:
        '''
        BLASTDB=$(echo "!{blastdb[0]}" | cut -f 1 -d '.')
        blastn -max_target_seqs 1 -dust no -word_size 7 -perc_identity 100 \
               -db $BLASTDB -outfmt 15 \
               -query !{staphopia_data}/sccmec/primers.fasta > primers.json
        '''
}

process sccmec_subtypes {
    publishDir sccmec_folder, overwrite: true

    input:
        file blastdb from SCCMEC_SUBTYPES
    output:
        file '*.json'
    shell:
        '''
        BLASTDB=$(echo "!{blastdb[0]}" | cut -f 1 -d ".")
        blastn -max_target_seqs 1 -dust no -word_size 7 -perc_identity 100 \
               -db $BLASTDB -outfmt 15 \
               -query !{staphopia_data}/sccmec/subtypes.fasta > subtypes.json
        '''
}

process sccmec_mapping {
    publishDir sccmec_folder, overwrite: true, pattern: '*.{gz,log}'

    input:
        file fq from FASTQ_SCCMEC
    output:
        file '*.gz'
    shell:
        p = is_paired ? '-p' : ''
        n = read_length <= 70 ? '-n 9999' : ''

        '''
        bwa-align.sh "!{fq}" !{staphopia_data}/sccmec/sccmec_cassettes !{read_length} !{cpu} "!{p}" "!{n}"
        samtools view -bS bwa.sam | samtools sort -o sccmec.bam -
        genomeCoverageBed -ibam sccmec.bam -d | gzip --best - > cassette-coverages.gz
        cp .command.err sccmec-mapping-stderr.log
        cp .command.out sccmec-mapping-stdout.log
        '''
}
/* ==== END SCCMEC ==== */

/* ==== BEGIN VARIANTS ==== */
process call_variants {
    publishDir variants_folder, mode: 'copy', overwrite: true, pattern: '*.{gz,log}'

    input:
        file fq from FASTQ_VARIANTS
    output:
        file '*.vcf.gz'
        file '*.log'
    shell:
        p = is_paired ? '-p' : ''
        '''
        # Build index will local copy of reference
        cp !{staphopia_data}/variants/n315.fasta ref.fasta
        bwa index ref.fasta
        samtools faidx ref.fasta
        picard -Xmx4g CreateSequenceDictionary REFERENCE=ref.fasta OUTPUT=ref.dict

        # Align reads
        bwa-align.sh "!{fq}" ref.fasta !{read_length} !{cpu} "!{p}" ""

        picard -Xmx4g AddOrReplaceReadGroups INPUT=bwa.sam OUTPUT=sorted.bam \
                      SORT_ORDER=coordinate RGID=GATK RGLB=GATK RGPL=Illumina \
                      RGSM=GATK RGPU=GATK VALIDATION_STRINGENCY=LENIENT

        # Alignment filtering/improvement
        picard -Xmx4g MarkDuplicates INPUT=sorted.bam OUTPUT=deduped.bam \
                      METRICS_FILE=deduped.bam_metrics ASSUME_SORTED=true \
                      REMOVE_DUPLICATES=false VALIDATION_STRINGENCY=LENIENT

        picard -Xmx4g BuildBamIndex INPUT=deduped.bam

        java -Xmx4g -jar !{params.gatk} -T RealignerTargetCreator -R ref.fasta \
                         -I deduped.bam -o deduped.intervals

        java -Xmx4g -jar !{params.gatk} -T IndelRealigner -R ref.fasta -I deduped.bam \
                         -o realigned.bam -targetIntervals deduped.intervals

        picard -Xmx4g BuildBamIndex INPUT=realigned.bam

        # Call variants
        java -Xmx4g -jar !{params.gatk} -T HaplotypeCaller -R ref.fasta -I realigned.bam \
                         -o raw.vcf -ploidy 1 -stand_call_conf 30.0 -rf BadCigar -nct !{cpu}

        # Filter and annotate variants
        java -Xmx4g -jar !{params.gatk} -T VariantFiltration -R ref.fasta -V raw.vcf \
                         -o filtered.vcf --clusterSize 3 --clusterWindowSize 10 \
                         --filterExpression "DP < 9 && AF < 0.7"  --filterName Fail \
                         --filterExpression "DP > 9 && AF >= 0.95" --filterName SuperPass \
                         --genotypeFilterExpression "GQ < 20" --genotypeFilterName LowGQ

        vcf-annotator.py filtered.vcf !{staphopia_data}/variants/n315.gb > annotated.vcf
        gzip --best -c annotated.vcf > !{sample}.variants.vcf.gz
        cp .command.err call-variants-stderr.log
        cp .command.out call-variants-stdout.log
        '''
}
/* ==== END VARIANTS ==== */
workflow.onComplete {
    println """

    Pipeline execution summary
    ---------------------------
    Completed at: ${workflow.complete}
    Duration    : ${workflow.duration}
    Success     : ${workflow.success}
    workDir     : ${workflow.workDir}
    exit status : ${workflow.exitStatus}
    Error report: ${workflow.errorReport ?: '-'}
    """
}

// Utility Functions
def print_usage() {
    log.info 'Staphopia Analysis Pipeline - ENA Samples'
    log.info ''
    log.info 'Required Options:'
    log.info '    --experiment  STR      An ENA experiment accession to process.'
    log.info ''
    log.info 'Optional:'
    log.info '    --outdir  DIR      Directory to write results to. (Default ./${NAME})'
    log.info '    --coverage  INT    Reduce samples to a given coverage. (Default: 100x)'
    log.info '    --help          Show this message and exit'
    log.info ''
    log.info 'Usage:'
    log.info '    nextflow staphopia.nf --experiment ERX000000 [more options]'
}

def check_input_params() {
    error = false
    if (!params.experiment) {
        log.info('An ENA experiment accession name is required to continue. Please use --experiment')
        error = true
    }

    if (error) {
        log.info('See --help for more information')
        exit 1
    }
}
