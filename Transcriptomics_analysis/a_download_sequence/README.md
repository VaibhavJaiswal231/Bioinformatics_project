# Downloading RNA-Seq Sequencing Data

This directory contains the scripts and metadata used to download raw RNA-seq sequencing data from the **NCBI Sequence Read Archive (SRA)**.

The downloaded sequencing data are converted from SRA format to FASTQ format for downstream quality control, read alignment, quantification, and differential expression analysis.

## Workflow

The sequence download workflow consists of the following steps:

1. Prepare a list of SRA accession IDs.
2. Download SRA files using `prefetch`.
3. Validate downloaded SRA files using `vdb-validate`.
4. Convert SRA files to FASTQ using `fasterq-dump`.
5. Generate paired-end FASTQ files for downstream analysis.

## Requirements

The workflow requires:

- Python
- NCBI SRA Toolkit
- `prefetch`
- `vdb-validate`
- `fasterq-dump`

Verify the SRA Toolkit installation using:

```bash
prefetch --version
fasterq-dump --version
```

## Accession List

SRA run accession IDs are stored in:

```text
metadata/accession_list.txt
```

Example:

```text
SRR40946221
SRR40946222
SRR40946223
```

Each accession corresponds to one sequencing run available through the NCBI SRA.

## Download SRA Files

SRA files can be downloaded using `prefetch`:

```bash
prefetch SRR40946221
```

For multiple accessions, the download process can be automated using the Python script included in this directory.

The downloaded runs are stored in the configured SRA output directory.

## Validate Downloads

Downloaded SRA files can be checked using:

```bash
vdb-validate SRR40946221
```

Validation helps ensure that the downloaded SRA data are complete and not corrupted before FASTQ conversion.

## Convert SRA to FASTQ

SRA files are converted to FASTQ using `fasterq-dump`.

For paired-end sequencing:

```bash
fasterq-dump SRR40946221 --split-files
```

The `--split-files` option generates separate FASTQ files for paired-end reads:

```text
SRR40946221_1.fastq
SRR40946221_2.fastq
```

where:

- `_1.fastq` contains Read 1 (forward reads)
- `_2.fastq` contains Read 2 (reverse reads)

## Configuration

Project paths and download options can be defined in `config.yaml`.

Example:

```yaml
project:
  name: Transcriptomics_analysis

paths:
  accession_file: metadata/accession_list.txt
  raw_sra: raw_sra
  fastq: fastq
  logs: logs

sra:
  validate: true
  split_files: true
```

Using a configuration file keeps paths and workflow parameters separate from the Python code and makes the pipeline easier to reproduce.

## Directory Structure

```text
a_download_sequence/
│
├── README.md
├── config.yaml
│
├── metadata/
│   └── accession_list.txt
│
├── scripts/
│   └── download_sequence.py
│
├── raw_sra/
│
├── fastq/
│   ├── SRR40946221_1.fastq
│   └── SRR40946221_2.fastq
│
└── logs/
```

## Output

The primary outputs of this stage are paired-end FASTQ files:

```text
fastq/
├── <ACCESSION>_1.fastq
└── <ACCESSION>_2.fastq
```

These raw FASTQ files are used as input for the next stage of the RNA-seq workflow: **raw sequence quality control using FastQC and MultiQC**.

## Workflow Summary

```text
SRA Accession IDs
        │
        ▼
     prefetch
        │
        ▼
     SRA files
        │
        ▼
   vdb-validate
        │
        ▼
  fasterq-dump
        │
        ▼
Paired-end FASTQ files
        │
        ▼
  FastQC / MultiQC
```