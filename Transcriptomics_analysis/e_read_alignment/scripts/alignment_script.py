from pathlib import Path
import subprocess
import sys
from datetime import datetime
import yaml

# ============================================================
# 1. LOAD PATH
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJECT_DIR = BASE_DIR.parent
STAR = PROJECT_DIR / "STAR_2.7.11b" / "Linux_x86_64_static" / "STAR"

CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
ACCESSION_FILE = PROJECT_DIR / "a_download_sequence" / "metadata" / "accession_list.txt"
FASTQ_DIR = PROJECT_DIR / "a_download_sequence" / "fastq"

GENOME_FASTA = BASE_DIR / "data" / "reference" / "GCF_000001405.40" / "GCF_000001405.40_GRCh38.p14_genomic.fna"
GTF_FILE = BASE_DIR / "data" / "reference" / "GCF_000001405.40" / "genomic.gtf"
GENOME_DIR = BASE_DIR / "data" / "reference" / "star_index"

OUTPUT_DIR = BASE_DIR / "results" 

# ============================================================
# 2. LOAD CONFIGURATION
# ============================================================

if not CONFIG_FILE.exists():
    print(f"ERROR: Config file not found:")
    print(CONFIG_FILE)
    sys.exit(1)

with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

LOG_DIR = BASE_DIR / config['output']['log_dir']

THREAD = config['input']['THREAD']
project_name = config["project"]["name"]
project_subname = config["project"]["subname"]

LOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 3. READ ACCESSION LIST
# ============================================================

if not ACCESSION_FILE.exists():
    print("ERROR: Accession file not found:")
    print(ACCESSION_FILE)
    sys.exit(1)

accessions = []
with open(ACCESSION_FILE, "r", encoding="utf-8") as file:
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
# 4. GENERATE THE STAR GENOME INDEX
# ============================================================ 

print("Generate STAR genome index")

genome_command = [
    str(STAR),
    "--runThreadN", str(THREAD),
    "--runMode", "genomeGenerate",
    "--genomeDir", str(GENOME_DIR),
    "--genomeFastaFiles", str(GENOME_FASTA),
    "--sjdbGTFfile", str(GTF_FILE),
    "--sjdbOverhang", str(149)
]

try:

    subprocess.run(genome_command, check=True)
    print("STAR genome index generated successfully.")

except subprocess.CalledProcessError:

    print("ERROR: STAR genome index generation failed.")
    sys.exit(1)

# ============================================================
# 5. ALIGN READS AND GENERATING GENE COUNTS
# ============================================================ 

print("Aligning reads and generating gene counts\n\n")

for number, accession in enumerate(accessions, start=1):

    print("\n" + "-" * 70)
    print(f"[{number}/{len(accessions)}] Aligning: {accession}")
    print("-" * 70)

    OUTPUT_FOLDER = OUTPUT_DIR / accession
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    READ1= FASTQ_DIR / f"{accession}_1.fastq"
    READ2= FASTQ_DIR  /f"{accession}_2.fastq"

    if not READ1.exists():
        print(f"Skipping {accession}: R1 file not found")
        continue

    if not READ2.exists():
        print(f"Skipping {accession}: R2 file not found")
        continue

    command_star_alignment = [str(STAR), 
                              "--runThreadN", str(THREAD), 
                              "--runMode", "alignReads",
                              "--genomeDir", str(GENOME_DIR), 
                              "--readFilesIn", str(READ1), str(READ2), 
                              "--twopassMode", "Basic",
                              "--outFileNamePrefix", str(OUTPUT_FOLDER / f"{accession}_"), 
                              "--outSAMtype", "BAM", "SortedByCoordinate", 
                              "--quantMode", "TranscriptomeSAM", "GeneCounts"]
    
    try:

        subprocess.run(command_star_alignment, stderr=subprocess.STDOUT, check=True)
        print(f"Alignment completed: {accession}")

    except subprocess.CalledProcessError:

        print(f"STAR alignment failed: {accession}")


# ============================================================
# 6. LOGS
# ============================================================ 

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
log_file = LOG_DIR / f"Alignment_summary_{timestamp}.txt"

print("\n")
print("=" * 70)
print("STAR alignment pipeline completed.")
print("=" * 70)
print(f"Check log: {log_file}")

print("\nSTAR alignment pipeline completed.")