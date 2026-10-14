# Transcriptomics Analysis Pipeline

## Overview

This project implements an RNA-seq transcriptomics analysis workflow, starting from publicly available sequencing data and progressing through quality control, preprocessing, alignment, quantification, differential expression, and pathway analysis.

# Current Progress

- [x] Raw sequence download
- [x] FastQC
- [x] MultiQC
- [ ] Trimming
- [ ] Alignment
- [ ] Quantification
- [ ] Differential expression
- [ ] Pathway analysis
- [ ] Final interpretation

## Planned Workflow

SRA → FASTQ → FastQC/MultiQC → Trimming(if needed) → FastQC/MultiQC(if trimming performed) → Alignment → Quantification → Differential Expression → Pathway Analysis

## Tools

- SRA Toolkit
- FastQC
- MultiQC
- STAR
- featureCounts
- DESeq2
- GSVA
- GSEA
- Python
- R
- Snakemake

## Project Structure

- a_download_sequence/          Raw sequence acquisition
- b_qc_downloading_sequence/    FASTQ quality control 
- c_trimming/                   Read preprocessing
- d_qc_trimming_sequence/       Trimming quality check
- e_alignment/                  Read alignment
- f_quantification/             Expression quantification
- g_differential_expression/    Differential expression
- h_pathway_analysis/           Pathway analysis