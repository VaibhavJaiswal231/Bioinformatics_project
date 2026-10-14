from pathlib import Path
import subprocess
import sys
import yaml
from datetime import datetime
import requests
import pandas as pd
from io import StringIO


# ============================================================
# 1. FIND CONFIGURATION FILE
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent

CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
METADATA_DIR = BASE_DIR / "metadata"
OUTPUT_FILE = METADATA_DIR / "srr_project_metadata.csv"


# ============================================================
# 2. LOAD CONFIGURATION
# ============================================================

if not CONFIG_FILE.exists():
    print(f"ERROR: Config file not found:")
    print(CONFIG_FILE)
    sys.exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)


# ============================================================
# 3. READ CONFIGURATION VALUES
# ============================================================

project_name = config["project"]["name"]
configured_base_dir = Path(BASE_DIR)

accession_file = configured_base_dir / config["input"]["accession_file"]

sra_dir = configured_base_dir / config["output"]["sra_dir"]
fastq_dir = configured_base_dir / config["output"]["fastq_dir"]
log_dir = configured_base_dir / config["output"]["log_dir"]

validate_sra = config["sra"]["validate"]
split_files = config["sra"]["split_files"]


# ============================================================
# 4. CREATE OUTPUT DIRECTORIES
# ============================================================

sra_dir.mkdir(parents=True, exist_ok=True)
fastq_dir.mkdir(parents=True, exist_ok=True)
log_dir.mkdir(parents=True, exist_ok=True)


# ============================================================
# 5. READ ACCESSION LIST
# ============================================================

if not accession_file.exists():
    print("ERROR: Accession file not found:")
    print(accession_file)
    sys.exit(1)

accessions = []
with open(accession_file, "r", encoding="utf-8") as file:
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
# 6. PRINT CONFIGURATION
# ============================================================

print("=" * 70)
print(f"Project: {project_name}")
print("=" * 70)


# ============================================================
# 7. DOWNLOAD SRR FILES USING PREFETCH
# ============================================================

successful_downloads = []
failed_downloads = []
validation_success = []
validation_failed = []
split_success = []
split_failed = []
all_metadata = []

for number, accession in enumerate(accessions, start=1):

    print("\n" + "-" * 70)
    print(f"[{number}/{len(accessions)}] Downloading {accession}")
    print("-" * 70)

    download_command = ["prefetch", accession, "--output-directory", str(sra_dir)]
    result = subprocess.run(download_command)

    if result.returncode == 0:
        print(f"SUCCESS: {accession}")
        successful_downloads.append(accession)

    else:
        print(f"FAILED: {accession}")
        failed_downloads.append(accession)


# ============================================================
# 8. VALIDATE SRR FILES
# ============================================================

    if validate_sra:

        sra_path = sra_dir / accession

        print("\n")
        print(f"[{number}/{len(accessions)}] Validating: {accession}")

        validate_command = ["vdb-validate", str(sra_path)]
        result = subprocess.run(validate_command)

        if result.returncode == 0:
            print(f"VALID: {accession}")
            validation_success.append(accession)

        else:
            print(f"VALIDATION FAILED: {accession}")
            validation_failed.append(accession)


# ============================================================
# 9. SPLIT SRR FILES
# ============================================================

    if split_files and accession in validation_success:

        print("\n")
        print(f"[{number}/{len(accessions)}] Spliting: {accession}")

        fastq_path = str(fastq_dir)
    
        split_command = ["fasterq-dump", str(sra_dir / accession), "--split-files", "--outdir", fastq_path]
    
        result = subprocess.run(split_command)
    
        if result.returncode == 0:
            print(f"SPILT: {accession}")
            split_success.append(accession)
    
        else:    
            print(f"FAILED SPILT: {accession}")
            split_failed.append(accession)


# ============================================================
# 10. METADATA SRR FILES
# ============================================================

    print(f"\nQuerying NCBI for {accession}...")

    params = {
        "db": "sra",
        "id": accession,
        "rettype": "runinfo",
        "retmode": "text"
    }

    response = requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi", params=params, timeout=30)
    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    if df.empty:
        print(f"No metadata found for {accession}")
        continue

    # Keep only the row corresponding to this SRR
    if "Run" in df.columns:
        df = df[df["Run"].astype(str) == accession]

    all_metadata.append(df)

# --------------------------------------------------
# 11. COMBINE RESULTS AND SAVE METADATA
# --------------------------------------------------

if not all_metadata:
    raise RuntimeError("No SRA metadata was retrieved.")

result = pd.concat(all_metadata, ignore_index=True)

result.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

print("\nMetadata saved to:")
print(OUTPUT_FILE)


# ============================================================
# 12. CREATE LOG SUMMARY
# ============================================================

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

log_file = log_dir / f"download_summary_{timestamp}.txt"

with open(log_file, "w", encoding="utf-8") as file:

    file.write(f"Project: {project_name}\n")
    file.write(f"Date: {datetime.now()}\n")
    file.write("=" * 70 + "\n\n")

    file.write(f"Total accessions: {len(accessions)}\n")
    file.write(f"Successful downloads: {len(successful_downloads)}\n")
    file.write(f"Failed downloads: {len(failed_downloads)}\n")

    if validate_sra:
        file.write(f"Successful validations: {len(validation_success)}\n")
        file.write(f"Failed validations: {len(validation_failed)}\n")

    if split_files:
            file.write(f"Successful split: {len(split_success)}\n")
            file.write(f"Failed split: {len(split_failed)}\n")

    file.write("\n\nSUCCESSFUL DOWNLOADS\n")
    file.write("-" * 70 + "\n")

    for accession in successful_downloads:
        file.write(f"{accession}\n")

    file.write("\n\nFAILED DOWNLOADS\n")
    file.write("-" * 70 + "\n")

    for accession in failed_downloads:
        file.write(f"{accession}\n")

    if validate_sra:

        file.write("\n\nVALIDATION SUCCESS\n")
        file.write("-" * 70 + "\n")

        for accession in validation_success:
            file.write(f"{accession}\n")

        file.write("\n\nVALIDATION FAILED\n")
        file.write("-" * 70 + "\n")

        for accession in validation_failed:
            file.write(f"{accession}\n")

    if split_files:
    
        file.write("\n\nSPLIT SUCCESS\n")
        file.write("-" * 70 + "\n")
    
        for accession in split_success:
            file.write(f"{accession}\n")
    
        file.write("\n\nSPLIT FAILED\n")
        file.write("-" * 70 + "\n")
    
        for accession in split_failed:
            file.write(f"{accession}\n")

print("\nLog summary:")
print(log_file)