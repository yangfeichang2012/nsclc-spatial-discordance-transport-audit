# NSCLC spatial discordance transport audit

This is the corrected, aggregate reproducibility archive for:

> Cohort-normalized fixed-coefficient transport audit of a tumor–stroma
> discordance score in immunotherapy-treated NSCLC

The study is an **analysis-plan-locked post-deviation secondary transport
audit**, not an uninterrupted prespecified confirmatory validation. The full
G09 → G10 → G11 history is disclosed in
[`PROTOCOL_HISTORY.md`](PROTOCOL_HISTORY.md).

## Locked result

| Cohort | Role under amended G11 plan | n | Events | C(B0) | C(B1) | ΔC | Interval |
|---|---|---:|---:|---:|---:|---:|---|
| Greek | Primary target cohort | 61 | 45 | 0.613622 | 0.591936 | -0.021686 | 95% percentile CI -0.064043 to 0.020918 |
| UQ | Descriptive stress test | 19 | 18 | 0.669753 | 0.629630 | -0.040123 | Descriptive percentile interval -0.155849 to 0.088250 |

The outcome is **two-year truncated progression-free survival**:
`T*=min(observed PFS, 24 months)` with an event only for progression/death by
24 months. The intervals are conditional on the fitted Yale coefficients and
the observed target-cohort preprocessing. They do not propagate Yale
coefficient uncertainty or uncertainty in target medians/IQRs.

The result does not support incremental rank discrimination. Because both
intervals include zero, it does not establish definite harm. It also does not
establish clinical utility, treatment prediction, a causal mechanism or
independent study-level multicenter validation.

## Predictor definition

The reduced baseline `B0` uses `M`, the source-released tumor resistance-high
indicator minus the source-released stromal response-high indicator. At a
single-row level, `M` is -1, 0 or 1; zero includes both concordant-low and
concordant-high rows. UQ required within-patient ROI medians, creating one
patient with `M=0.5`.

`B1` adds the four-anchor discordance `D`: tumor CXCL14 and PECAM1 versus
stromal APOE and CD68. The genes were chosen during hypothesis generation
before outcome-linked project analysis, based on membership in the parent
cell-type lists and exact availability across released platforms. No
deterministic ranking of all 644 resistance and 256 response candidates was
performed. The complete candidate universe and anchor row positions are
written by the reproduction workflow to `results/candidate_universe.csv`.

Only regression coefficients were sealed. Every target cohort recomputed its
own median and IQR-derived robust scale, so the evaluated procedure is
cohort-normalized and batch-level; it is not a fully frozen individual
prediction pipeline.

## End-to-end reproduction

Python 3.11 or later is recommended.

```bash
python -m pip install -r requirements.txt
python scripts/download_inputs.py
python scripts/reproduce_analysis.py
python scripts/render_figures.py
python scripts/validate_archive.py
```

The downloader retrieves four public files, verifies exact byte counts and
SHA-256 hashes, and stores them in the ignored `inputs/` directory. The
analysis then:

1. reconstructs and checks the sealed Yale coefficients;
2. rebuilds the Greek and UQ target datasets from public files in memory;
3. repeats the locked 2,000 patient-level paired bootstrap calculations;
4. writes aggregate results, bootstrap draws and candidate provenance; and
5. writes no patient-level or region-level analysis table.

Expected runtime is about one minute after download. The release ZIP is also
tested after extraction to prevent line-ending-dependent manifest failures.

## Contents

- `data/source_manifest.json`: public source URLs, byte counts and SHA-256
- `results/reproduced_results.json`: reconstructed aggregate result
- `results/*bootstrap_delta_c.csv`: non-identifying bootstrap draws
- `results/candidate_universe.csv`: full parent lists and selected anchors
- `protocol/`: immutable G11 contract, execution authorization and state,
  result/claim lock, and publication supersession record
- `scripts/download_inputs.py`: public-source acquisition and verification
- `scripts/reproduce_analysis.py`: end-to-end result reconstruction
- `scripts/render_figures.py`: aggregate figure generation
- `scripts/validate_archive.py`: values, privacy and manifest validation
- `figures/`: true-vector SVG/PDF plus raster TIFF/PNG copies
- `SHA256SUMS.json`: release integrity manifest

## Data and privacy

Inputs are public through the parent article, GSE271689 and GSE221733. They are
downloaded at run time and are not redistributed in this repository.

This archive contains no participant identifier, participant-level outcome,
region-level expression row, source expression matrix, author email,
submission correspondence, credential or machine-specific path.

## Citation and license

See `CITATION.cff`. Version 1.0.2 supersedes v1.0.1 and v1.0.0. Its version
DOI is `10.5281/zenodo.21715520`; the concept DOI is
`10.5281/zenodo.21702762`. Code is MIT licensed.
Source datasets retain their original repository terms.
