# Differential Expression Analysis

This module performs differential gene expression analysis from an RNA-seq count matrix and sample metadata using **PyDESeq2**.

The analysis identifies genes whose expression differs significantly between experimental conditions while accounting for sequencing depth and biological variability.

---

## Directory Structure

```text
g_differential_expression/
│
├── README.md
│
├── scripts/
│   └── differential_expression.py
│
├── input/
│   ├── count_data.csv
│   └── metadata.csv
│
├── results/
│   ├── differential_expression_results.csv
│   ├── significant_genes.csv
│   └── plots/
│       ├── volcano_plot.png
│       └── ...
│
└── logs/
```

---

## Input Data

### 1. Count Matrix

The count matrix contains **raw integer read counts** for each gene in each sample.

Example:

```text
sample,gene_1,gene_2,gene_3,gene_4
sample_01,120,450,32,890
sample_02,135,420,28,920
sample_03,520,110,85,450
sample_04,490,125,91,470
```

For PyDESeq2, samples are represented as rows and genes as columns.

Important:

- Use raw counts.
- Do not use TPM, FPKM, or CPM as input.
- Do not log-transform the counts before DESeq2.
- Count values should be non-negative integers.
- Each sample should correspond to one biological replicate.

The count matrix will ultimately be generated from the STAR `ReadsPerGene.out.tab` files produced during the alignment step.

---

### 2. Sample Metadata

The metadata describes the experimental information associated with each sample.

Example:

```text
sample,condition,batch
sample_01,control,1
sample_02,control,1
sample_03,treatment,2
sample_04,treatment,2
```

The sample identifiers must match between the count matrix and metadata.

For example:

```text
count_data.csv
    sample_01
    sample_02
    sample_03
    sample_04

metadata.csv
    sample_01
    sample_02
    sample_03
    sample_04
```

If batch effects are present and adequately represented in the experimental design, the design can include batch:

```text
~ batch + condition
```

For a simple comparison:

```text
~ condition
```

---

## Analysis Workflow

The differential expression workflow is:

```text
STAR Alignment
      │
      ▼
ReadsPerGene.out.tab
      │
      ▼
Count Matrix
      │
      ├──────────────┐
      │              │
      ▼              ▼
count_data.csv   metadata.csv
      │              │
      └───────┬──────┘
              ▼
         PyDESeq2
              │
              ▼
      Library-size normalization
              │
              ▼
       Dispersion estimation
              │
              ▼
       Statistical testing
              │
              ▼
 Differential expression results
              │
       ┌──────┴───────┐
       ▼              ▼
 Significant      Visualization
    genes          & QC
       │
       ▼
 Pathway Analysis
```

---

## Environment

Create a dedicated environment for differential expression:

```powershell
conda create -n diffexp_env python=3.11 -y
conda activate diffexp_env
```

Install PyDESeq2:

```powershell
python -m pip install pydeseq2
```

Verify the installation:

```powershell
python -c "from pydeseq2.dds import DeseqDataSet; from pydeseq2.ds import DeseqStats; print('PyDESeq2 OK')"
```

---

## Running the Analysis

From the project root:

```powershell
python E:\Bioinformatics_project\Transcriptomics_analysis\g_differential_expression\scripts\differential_expression.py
```

Alternatively, from the `g_differential_expression` directory:

```powershell
python scripts\differential_expression.py
```

---

## PyDESeq2 Analysis

The main analysis consists of the following steps:

1. Load the count matrix.
2. Load sample metadata.
3. Validate sample identifiers.
4. Construct the PyDESeq2 dataset.
5. Estimate size factors.
6. Estimate gene-wise dispersions.
7. Fit the negative binomial model.
8. Perform statistical testing.
9. Calculate log2 fold changes.
10. Adjust p-values for multiple testing.
11. Extract significant differentially expressed genes.

A basic PyDESeq2 setup is:

```python
import pandas as pd

from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

counts = pd.read_csv(
    "data/count_data.csv",
    index_col=0
)

metadata = pd.read_csv(
    "data/metadata.csv",
    index_col=0
)

assert all(counts.index == metadata.index)

dds = DeseqDataSet(
    counts=counts,
    metadata=metadata,
    design="~condition"
)

dds.deseq2()

stat_res = DeseqStats(
    dds,
    contrast=["condition", "treatment", "control"]
)

stat_res.summary()

results = stat_res.results_df
```

---

## Differential Expression Criteria

A commonly used threshold for identifying significant genes is:

```text
Adjusted p-value < 0.05
Absolute log2 fold change >= 1
```

In Python:

```python
significant = results[
    (results["padj"] < 0.05) &
    (results["log2FoldChange"].abs() >= 1)
]
```

These thresholds are analysis choices and should be reported explicitly rather than treated as universal biological cutoffs.

---

## Results

The main differential expression result contains statistics such as:

| Column | Description |
|---|---|
| `baseMean` | Mean normalized expression across samples |
| `log2FoldChange` | Estimated log2 fold change |
| `lfcSE` | Standard error of log2 fold change |
| `stat` | Test statistic |
| `pvalue` | Unadjusted p-value |
| `padj` | Multiple-testing adjusted p-value |

### Interpretation

Positive:

```text
log2FoldChange > 0
```

indicates higher expression in the first level of the specified contrast.

Negative:

```text
log2FoldChange < 0
```

indicates lower expression in the first level of the specified contrast.

For example:

```text
log2FoldChange = 2
```

corresponds to approximately:

```text
2² = 4-fold
```

higher expression.

---

## Quality Control and Visualization

The differential expression analysis can be accompanied by:

- Sample-level count distributions
- Library-size comparison
- PCA
- Sample correlation/heatmap
- Normalized expression heatmap
- MA plot
- Volcano plot
- Expression plots for selected genes

These visualizations help assess sample relationships, potential outliers, and overall effects of the experimental condition.

---

## Important Considerations

### Biological Replicates

Biological replicates are important for estimating biological variability.

A design with multiple biological replicates is preferred over comparing individual samples.

### Batch Effects

If samples were processed in different batches, batch information should be included in the experimental design when appropriate:

```python
design="~batch + condition"
```

The biological condition should not be confused with technical batch.

### Raw Counts

DESeq2/PyDESeq2 expects raw count data rather than normalized expression values.

Do not perform TPM/FPKM/CPM normalization before supplying the data to PyDESeq2.

### Multiple Testing

RNA-seq experiments typically test thousands of genes simultaneously. Therefore, adjusted p-values should be used when defining significant genes rather than relying only on raw p-values.

---

## Output Files

The analysis will generate results such as:

```text
results/
│
├── differential_expression_results.csv
├── significant_genes.csv
│
└── plots/
    ├── pca.png
    ├── volcano_plot.png
    ├── ma_plot.png
    └── heatmap.png
```

The exact outputs depend on the analysis script.

---

## Downstream Analysis

Differentially expressed genes can subsequently be used for:

```text
Differentially Expressed Genes
              │
              ├── Gene ID annotation
              │
              ├── GO enrichment
              │
              ├── KEGG pathway analysis
              │
              ├── Reactome pathway analysis
              │
              ├── GSEA
              │
              └── Biological interpretation
```

Pathway analysis will be performed in the subsequent pathway-analysis module.

---

## Reproducibility

The analysis should record:

- Python version
- PyDESeq2 version
- Input count matrix
- Metadata
- Experimental design
- Statistical thresholds
- Contrast definition
- Analysis date
- Output files

This makes the differential expression analysis reproducible and easier to debug.

---

## Project Status

**Current stage:** Differential expression analysis setup

Planned workflow:

- [X] Prepare STAR-derived count matrix
- [X] Prepare sample metadata
- [X] Validate sample-to-metadata matching
- [X] Run PyDESeq2
- [X] Generate differential expression results
- [ ] Perform PCA and sample QC
- [ ] Generate MA and volcano plots
- [ ] Identify significant genes
- [ ] Perform downstream pathway analysis