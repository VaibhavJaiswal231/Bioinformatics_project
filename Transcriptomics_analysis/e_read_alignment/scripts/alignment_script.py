from pathlib import Path
import subprocess
import sys
import datetime
import yaml

# ============================================================
# 1. LOAD PATH
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = SCRIPT_DIR.parent
PROJECT_DIR = BASE_DIR.parent

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
# 4. RUN STAR AND CREATE LOG FILE
# ============================================================ 

for number, accession in enumerate(accessions, start=1):

    print("\n" + "-" * 70)
    print(f"[{number}/{len(accessions)}] Aligning: {accession}")
    print("-" * 70)

    OUTPUT_FOLDER = f"{OUTPUT_DIR}/{accession}"
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    READ1=f"{FASTQ_DIR}/{accession}_1.fastq"
    READ2=f"{FASTQ_DIR}/{accession}_2.fastq"

    if not READ1.exists():
        print(f"Skipping {accession}: R1 file not found")
        continue

    if not READ2.exists():
        print(f"Skipping {accession}: R2 file not found")
        continue

    with open(READ1, "r") as f:
        f.readline()
        sequence = f.readline().strip()

    read_length = len(sequence)
    sjhang = read_length - 1

    command_star_alignment = ["STAR", 
                              "--runThreadN", int(THREAD), 
                              "--runMode", "genomeGenerate",
                              "--genomeDir", str(GENOME_DIR),
                              "--genomeFastaFiles", str(GENOME_FASTA), 
                              "--readFilesIn", str(READ1), str(READ2), 
                              "--twopassMode", "Basic",
                              "--outFileNamePrefix", f"OUTPUT_FOLDER/{accession}_", 
                              "--outSAMtype", "BAM", "SortedByCoordinate", 
                              "--quantMode", "TranscriptomeSAM", "GeneCounts"
                              "--sjdbGTFfiles", str(GTF_FILE),
                              "--sjdbOverhang", sjhang]
    

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOG_DIR / f"Alignment_summary_{timestamp}.txt"
    
    try:

        with open(log_file, "w") as log:

            subprocess.run(
                command_star_alignment,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True
            )

        print(f"Alignment completed: {accession}")

    except subprocess.CalledProcessError:

        print(f"STAR alignment failed: {accession}")
        print(f"Check log: {log_file}")


print("\nSTAR alignment pipeline completed.")