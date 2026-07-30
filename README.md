# NSCLC spatial discordance transport audit

This repository contains the aggregate, deidentified reproducibility archive for:

> Fixed-coefficient transport of a tumor–stroma transcriptomic discordance score in immunotherapy-treated NSCLC: a prespecified secondary reanalysis

The study asks whether a frozen four-anchor tumor–stroma discordance score improves progression-free survival rank discrimination beyond a fixed marginal-signature baseline. Yale supplied coefficients. Greek was the sole confirmatory geographically held-out center within the same parent study. UQ was descriptive because the prespecified n≥20 gate failed at n=19.

## Locked result

| Cohort | Role | n | Events | C(B0) | C(B1) | ΔC | Interval |
|---|---|---:|---:|---:|---:|---:|---|
| Greek | Confirmatory held-out center within parent study | 61 | 45 | 0.613622 | 0.591936 | -0.021686 | 95% CI -0.064043 to 0.020918 |
| UQ | Descriptive stress test only | 19 | 18 | 0.669753 | 0.629630 | -0.040123 | Exploratory -0.155849 to 0.088250 |

The result does not support incremental discrimination. It does not establish definite harm, clinical utility, treatment prediction, a causal mechanism, or independent study-level multicenter validation.

## Contents

- `data/result_ledger.csv`: locked aggregate performance results
- `data/claim_ledger.csv`: allowed and prohibited manuscript claims
- `data/figure_source_data.csv`: compact figure source table
- `protocol/g11_protocol_contract_v1.0.json`: frozen Greek-primary analysis contract
- `protocol/g12_result_and_claim_lock_v1.0.json`: result and claim lock
- `scripts/render_figures.py`: regenerates aggregate figures from `figure_source_data.csv`
- `scripts/validate_archive.py`: validates values, privacy boundaries, and SHA-256 manifest
- `figures/`: aggregate PNG, SVG, PDF, and TIFF figures
- `SHA256SUMS.json`: archive manifest

## Reproduction

```bash
python -m pip install -r requirements.txt
python scripts/validate_archive.py
python scripts/render_figures.py
```

The rendering script reads aggregate values only. It does not fit a model or rerun bootstrap resampling.

## Source data

The source datasets are available from Gene Expression Omnibus under GSE271689 and GSE221733 and through the source data of Aung et al., Nature Genetics 2025, DOI 10.1038/s41588-025-02351-7. Source expression matrices are not redistributed here.

## Privacy and redistribution boundary

This archive contains no participant identifier, participant-level outcome, region-level expression row, source expression matrix, author email, submission document, credential, or machine-specific path.

## Citation

See `CITATION.cff`. The archived version DOI is
`10.5281/zenodo.21702763`; the concept DOI is `10.5281/zenodo.21702762`.

## License

Code is released under the MIT License. Aggregate documentation and figures may be reused with citation of this archive and the parent data source. The source datasets retain their original repository terms.
