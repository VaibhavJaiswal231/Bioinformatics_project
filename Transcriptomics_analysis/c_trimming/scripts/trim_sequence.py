from pathlib import Path
import subprocess
import sys
from datetime import datetime

# ============================================================
# 1. PATHS
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJECT_DIR = BASE_DIR.parent

# Input: raw FASTQ files
INPUT_DIR = PROJECT_DIR / "a_download_sequence" / "fastq"
ACCESSION_LISTS = PROJECT_DIR / "a_download_sequence" / "metadata" / "accession_list.txt"
fastp = PROJECT_DIR / "tools" / "fastp" / "fastp-1.3.3-windows-ucrt64" / "fastp.exe"

# Output directories
OUTPUT_DIR = BASE_DIR / "results" / "trimmed_fastq"
REPORT_DIR = BASE_DIR / "reports" / "fastp"
LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. FASTP PARAMETERS
# ============================================================

THREADS = 4

# Minimum Phred quality
QUALIFIED_QUALITY = 20

# Minimum read length after trimming
MIN_LENGTH = 50

# ============================================================
# 3. CHECK FASTP
# ============================================================

try:
    subprocess.run(
        [fastp, "--version"],
        check=True,
        capture_output=True,
        text=True
    )
except FileNotFoundError:
    print("ERROR: fastp is not installed or not available in PATH.")
    print("Activate your trimming environment and install fastp.")
    sys.exit(1)

# ============================================================
# 4. FIND PAIRED-END FASTQ FILES
# ============================================================

read1_files = sorted(INPUT_DIR.glob("*_1.fastq"))

if not read1_files:
    print(f"ERROR: No *_1.fastq.gz files found in:")
    print(INPUT_DIR)
    sys.exit(1)

print(f"Found {len(read1_files)} samples.")

# ============================================================
# 5. READ ACCESSION LIST
# ============================================================

if not ACCESSION_LISTS.exists():
    print("ERROR: Accession file not found:")
    print(ACCESSION_LISTS)
    sys.exit(1)

accessions = []
with open(ACCESSION_LISTS, "r", encoding="utf-8") as file:
    for line in file:
        accession = line.strip()

        # Ignore empty lines
        if not accession:
            continue

        # Ignore comments
        if accession.startswith("#"):
            continue

        accessions.append(accession)


# Remove duplicate accessions
accessions = list(dict.fromkeys(accessions))

if not accessions:
    print("ERROR: No SRR accessions found.")
    sys.exit(1)

# ============================================================
# 5. RUN FASTP
# ============================================================

for accession in accessions:

    read1 = INPUT_DIR / f"{accession}_1.fastq"
    read2 = INPUT_DIR / f"{accession}_2.fastq"

    if not read2.exists():
        print(f"WARNING: R2 missing for {accession}")
        continue

    if not read1.exists():
        print(f"WARNING: R1 missing for {accession}")
        continue

    output_r1 = OUTPUT_DIR / f"{accession}_1.trimmed.fastq.gz"
    output_r2 = OUTPUT_DIR / f"{accession}_2.trimmed.fastq.gz"

    html_report = REPORT_DIR / f"{accession}_fastp.html"
    json_report = REPORT_DIR / f"{accession}_fastp.json"

    log_file = LOG_DIR / f"{accession}_fastp.log"

    print("=" * 60)
    print(f"Processing: {accession}")
    print(f"R1: {read1}")
    print(f"R2: {read2}")
    print("=" * 60)

    command = [fastp,
                "--in1", str(read1),
                "--in2", str(read2),
                "--out1", str(output_r1),
                "--out2", str(output_r2),
                "--detect_adapter_for_pe",
                "--qualified_quality_phred", str(QUALIFIED_QUALITY),
                "--length_required", str(MIN_LENGTH),
                "--thread", str(THREADS),
                "--html", str(html_report),
                "--json", str(json_report)]

    start_time = datetime.now()

    try:
        with open(log_file, "w") as log:

            subprocess.run(
                command,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True
            )

        elapsed = datetime.now() - start_time

        print(f"Completed: {accession}")
        print(f"Runtime: {elapsed}")

    except subprocess.CalledProcessError:
        print(f"ERROR: fastp failed for {accession}")
        print(f"Check log: {log_file}")
        continue


print("\nAll samples processed.")
print(f"Trimmed FASTQ: {OUTPUT_DIR}")
print(f"fastp reports: {REPORT_DIR}")