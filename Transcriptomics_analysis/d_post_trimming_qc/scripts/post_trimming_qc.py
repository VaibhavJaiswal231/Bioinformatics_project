from pathlib import Path
import gzip
import shutil
import subprocess
import pandas as pd
import zipfile
import re

# ============================================================
# 1. FIND CONFIGURATION FILE
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJECT_DIR = BASE_DIR.parent

FASTQC_BASE = PROJECT_DIR / "tools" / "FastQC" / "fastqc"

TRIMMED_FASTQ_DIR = PROJECT_DIR / "c_trimming" / "results" / "trimmed_fastq"

QC_DIR = PROJECT_DIR / "d_post_trimming_qc"
FASTQC_DIR = QC_DIR / "reports" / "fastqc_trimmed"
MULTIQC_DIR = QC_DIR / "reports" / "multiqc_trimmed"

VALIDATION_CSV = QC_DIR / "fastq_validation.csv"
SUMMARY_CSV = QC_DIR / "qc_summary.csv"

THREADS = 4
MEMORY = 1024

if not TRIMMED_FASTQ_DIR.is_dir():
    raise FileNotFoundError(f"FASTQ directory not found: {TRIMMED_FASTQ_DIR}")


# =============================================================
# Get all FASTQ and compressed FASTQ files
# =============================================================

fastq_files = sorted(
    p for p in TRIMMED_FASTQ_DIR.iterdir()
    if p.is_file() and (
        p.name.endswith((".fastq", ".fq", ".fastq.gz", ".fq.gz"))
    )
)


# ============================================================
# Run fastqc
# ============================================================

FASTQC_DIR.mkdir(parents=True, exist_ok=True)

for fastq in fastq_files:
    print(f"Running FastQC: {fastq}")

    fastqc_command = ["python", str(FASTQC_BASE), "--threads", str(THREADS), "--outdir", str(FASTQC_DIR), "--memory", str(MEMORY), str(fastq)]
    result_fastqc = subprocess.run(fastqc_command)


# ============================================================
# Run multiqc
# ============================================================

print(f"-"*35 + "Running MultiQC" + '-'*35)

MULTIQC_DIR.mkdir(parents=True, exist_ok=True)

multiqc_command = ["multiqc", str(FASTQC_DIR), "--outdir", str(MULTIQC_DIR), "--filename", "multiqc_report.html","--force"]      
result_multiqc = subprocess.run(multiqc_command)