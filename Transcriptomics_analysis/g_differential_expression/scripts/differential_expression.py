from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats


# ============================================================
# 1. PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PARENT_DIR = BASE_DIR.parent
COUNT_FILE = PARENT_DIR / "input" / "gene_counts.csv"
METADATA_FILE = PARENT_DIR / "input" / "sample_metadata.csv"

RESULT_DIR = PARENT_DIR / "results"
PLOT_DIR = PARENT_DIR / "plots"

RESULT_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 2. LOAD RAW COUNTS AND METADATA
# ============================================================

counts = pd.read_csv(COUNT_FILE, index_col=0)
metadata = pd.read_csv(METADATA_FILE, index_col=0)

print(f"Shape of count matrix: {counts.shape}\n")
print(f"Shape of metadata matrix: {metadata.shape}\n")

# ============================================================
# 3. CHECK COUNTS
# ============================================================

if counts.isna().any().any():
    raise ValueError("Count matrix contains missing values.")

if (counts < 0).any().any():
    raise ValueError("Count matrix contains negative values.")

# PyDESeq2 expects integer counts
counts = counts.astype(int)


# ============================================================
# 4. MATCH COUNTS AND METADATA
# ============================================================

common_samples = counts.index.intersection(metadata.index)

counts = counts.loc[common_samples]
metadata = metadata.loc[common_samples]

if counts.empty:
    raise ValueError("No matching sample IDs between counts and metadata.")

assert counts.index.equals(metadata.index)

print("\nNumber of samples:")
print(len(counts))

print("\nConditions:")
print(metadata["condition"].value_counts())


# ============================================================
# 5. FILTER LOW-COUNT GENES
# ============================================================

# Keep genes with >= 10 reads in at least 2 samples

keep = (counts >= 10).sum(axis=0) >= 2

counts = counts.loc[:, keep]

print(f"\nNumber of genes retained: {counts.shape[1]}")


# ============================================================
# 6. CREATE AND RUN DESEQ2 DATASET
# ============================================================

dds = DeseqDataSet(counts=counts,
                    metadata=metadata,
                    design="~ condition")

dds.deseq2()

# ============================================================
# 7. CONTRAST
# ============================================================

# Change these names to exactly match metadata["condition"]

stat_res = DeseqStats(dds, contrast=["condition", "tumor", "control"])
stat_res.summary()


# ============================================================
# 8. GET RESULTS AND SORT BY ADJUSTED P-VALUE
# ============================================================

results = stat_res.results_df.copy()

print(f"\nDESeq2 results: {results.head()}")

results = results.sort_values("padj", na_position="last")


# ============================================================
# 9. ADD SIGNIFICANCE COLUMN
# ============================================================

results["significance"] = "Not significant"

results.loc[
    (results["padj"] < 0.05)
    & (results["log2FoldChange"] >= 1),
    "significance"
] = "Upregulated"

results.loc[
    (results["padj"] < 0.05)
    & (results["log2FoldChange"] <= -1),
    "significance"
] = "Downregulated"


# ============================================================
# 10. SAVE ALL RESULTS
# ============================================================

results.to_csv(RESULT_DIR / "deseq2_all_results.csv")


# ============================================================
# 11. SIGNIFICANT GENES
# ============================================================

significant = results[
    (results["padj"] < 0.05)
    & (results["log2FoldChange"].abs() >= 1)
].copy()

significant.to_csv(
    RESULT_DIR / "deseq2_significant_genes.csv"
)

print("\nSignificant genes:")
print(significant.shape[0])


# ============================================================
# 12. UPREGULATED GENES
# ============================================================

upregulated = results[
    (results["padj"] < 0.05)
    & (results["log2FoldChange"] >= 1)
].copy()

upregulated.to_csv(RESULT_DIR / "upregulated_genes.csv")


# ============================================================
# 13. DOWNREGULATED GENES
# ============================================================

downregulated = results[
    (results["padj"] < 0.05)
    & (results["log2FoldChange"] <= -1)
].copy()

downregulated.to_csv(RESULT_DIR / "downregulated_genes.csv")


# ============================================================
# 14. SUMMARY
# ============================================================

print("Genes tested:", len(results))
print("Significant:", len(significant))
print("Upregulated:", len(upregulated))
print("Downregulated:", len(downregulated))