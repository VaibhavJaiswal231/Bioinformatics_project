import pandas as pd


# ============================================================
# 1. OPEN DIFFERENT EXTENSION FILES
# ============================================================ 

read_csv = pd.read_csv("file_name.csv")
read_txt = pd.read_csv("file_name.txt")
read_tsv = pd.read_csv("file_name.tsv", sep="\t")
read_excel = pd.read_excel("file_name.xlsx", sheet_name="Sheet1")
read_json = pd.read_json("file_name.json")

# Open plain text line by line
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())

# Open JSON file
import json

with open("data.json") as f:
    data = json.load(f)

# Open config file and yaml file
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

print(config)

# Open gzip
import gzip

with gzip.open("file.txt.gz", "rt") as f:
    data = f.read()

# Open FASTA
from Bio import SeqIO

for record in SeqIO.parse("genome.fasta", "fasta"):
    print(record.id)
    print(record.seq)

# Open FASTQ
from Bio import SeqIO

for record in SeqIO.parse("reads.fastq", "fastq"):
    print(record.id)
    print(record.seq)

# Open BAM
import pysam

bam = pysam.AlignmentFile("sample.bam", "rb")

for read in bam.fetch():
    print(read.query_name)

# ============================================================
# 2. COLUMN MANUPULATION
# ============================================================
df = pd.read_csv("file_name.csv")                   # Read csv file
df.columns                                          # Reads Columns 
df.columns.tolist()                                 # Columns in list
df.info()                                           # df information
df.shape                                            # column shape
df.head()                                           # Top 5 data of the df
df["condition"]                                     # Read "condition" columns in series
df[["sample", "condition", "batch"]]                # df have only columns "sample", "conditions", and "batch""
df = df.drop(columns=["unwanted_column1", "uneanted_column2"])           # df drops all unwanted column
df = df.rename(columns={"Run": "sample_id",         # Rename columns name
                        "Condition": "condition",
                        "Batch": "batch"})
df["condition"] = df["condition"].replace({"Tumor": "cancer",       # Replace values for particular column
                                            "Normal": "control"})
df.set_index("sample_id", inplace=True)             # Set index of the df
df = df.dropna(subset=["condition", "batch"])       # Drop NAN values