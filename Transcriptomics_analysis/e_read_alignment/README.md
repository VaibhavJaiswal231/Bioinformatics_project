# RNA-Seq Read Alignment

This directory contains the scripts and outputs for aligning paired-end RNA-seq reads to a reference genome using **STAR (Spliced Transcripts Alignment to a Reference)**.

## Overview

After raw-read quality control with FastQC and MultiQC, sequencing reads are aligned to the reference genome using STAR. STAR is a splice-aware aligner designed for RNA-seq data and can efficiently identify reads spanning exon-exon junctions.

The main steps in this stage are:

1. Prepare the reference genome and gene annotation files.
2. Generate the STAR genome index.
3. Align paired-end RNA-seq reads to the indexed reference genome.
4. Generate coordinate-sorted BAM files.
5. Collect alignment statistics for downstream quality assessment.

## Input Files

The alignment workflow requires:

- Paired-end FASTQ files (`*_1.fastq` and `*_2.fastq`)
- Reference genome FASTA file (present in data\reference)
- Gene annotation GTF file (present in data\reference)
- STAR genome index (present in data\reference)
- THREADS can be change into the config file

Example FASTQ files:

```text
SRR40946221_1.fastq
SRR40946221_2.fastq
```

## Read Alignment

Paired-end reads are aligned using STAR.

Example command:

```bash
STAR \
    --runThreadN 4 \ 
    --runMode genomeGenerate \
    --genomeDir genome_index \
    --genomeFastaFiles reference_genome.fa \ 
    --readFilesIn SRR40946221_1.fastq SRR40946221_2.fastq \
    --twopassMode Basic \
    --outFileNamePrefix f"OUTPUT_FOLDER/SRR40946221_" \ 
    --outSAMtype BAM SortedByCoordinate \ 
    --quantMode TranscriptomeSAM GeneCounts \
    --sjdbGTFfiles annotation.gtf \
    --sjdbOverhang 149
```

### Important STAR Parameters

| Parameter | Description |
|---|---|
| `--runThreadN` | Number of CPU threads |
| `--genomeDir` | Directory containing the STAR genome index |
| `--readFilesIn` | Forward and reverse FASTQ files |
| `--twopassMode Basic` | Performs two-pass mapping to improve splice-junction detection |
| `--outSAMtype BAM SortedByCoordinate` | Produces a coordinate-sorted BAM file |
| `--outFileNamePrefix` | Prefix for STAR output files |

## STAR Output

STAR generates several files for each sample, including:

```text
sample_Aligned.sortedByCoord.out.bam
sample_Log.final.out
sample_Log.out
sample_Log.progress.out
sample_SJ.out.tab
```

### Key Files

**`Aligned.sortedByCoord.out.bam`**

Coordinate-sorted BAM file containing aligned sequencing reads. This file can be used for downstream read quantification.

**`Log.final.out`**

Summary of alignment statistics, including:

- Number of input reads
- Uniquely mapped reads
- Uniquely mapped read percentage
- Multi-mapped reads
- Unmapped reads
- Splice junction statistics

**`SJ.out.tab`**

Contains splice junctions detected during alignment.

## Alignment Quality Assessment

Important metrics from `Log.final.out` should be reviewed before proceeding with downstream analysis.

Key metrics include:

- Uniquely mapped reads %
- Reads mapped to multiple loci %
- Unmapped reads %
- Number of detected splice junctions

These metrics help identify potential problems with the reference genome, sequencing quality, contamination, or alignment parameters.

## Directory Structure

```text
e_read_alignment/
│
├── README.md
├── scripts/
│   └── star_alignment.py
│
├── genome_index/
│
├── alignment/
│   ├── SRR40946221_Aligned.sortedByCoord.out.bam
│   ├── SRR40946221_Log.final.out
│   └── SRR40946221_SJ.out.tab
│
└── logs/
```

The exact directory structure may vary depending on the configuration of the workflow.

## Downstream Analysis

The coordinate-sorted BAM files generated in this step can subsequently be used for:

- Alignment quality control
- Gene-level read quantification
- Generation of count matrices
- Differential gene expression analysis
- Pathway and gene-set enrichment analysis

The next stage of the workflow uses the aligned reads for **gene expression quantification**.