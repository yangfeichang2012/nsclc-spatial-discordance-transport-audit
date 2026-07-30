# Protocol history and study identity

This repository reproduces an **analysis-plan-locked, post-deviation secondary
transport audit**. It is not presented as an uninterrupted prespecified
confirmatory validation.

## G09: original transport estimand

G09 planned a weighted transport estimand using UQ and Greek target cohorts,
with an anticipated UQ denominator of 27 and a hard UQ gate of at least 25
outcome-complete patients and at least 15 events. The UQ author key did not
provide a valid one-to-one patient mapping. G09 was terminated; its weighted
estimand was never reported and was not resumed.

## G10: public-source recovery

G10 replaced the unavailable author key with a public-data crosswalk assembled
from GSE221733 sample metadata, the released normalized matrix, the Figure 6
source workbook and the released UQ clinical table. This recovered 21
predictor-paired patients but only 19 outcome-complete patients (18 events).
The original G09 UQ denominator gate was therefore not met.

## G11: amended analysis plan

Before G11 outcome-linked execution, a new contract designated the Greek
cohort as the sole primary target cohort and the 19-patient UQ cohort as a
descriptive stress test. The G09 weighted estimand remained terminated. G11
then transported the sealed Yale coefficients without target-cohort refitting.
Each target cohort nevertheless supplied its own median and IQR for robust
normalization, so this is a **cohort-normalized fixed-coefficient** evaluation,
not transport of a fully frozen individual-level prediction pipeline. The full pipeline was not fixed.

The outcome throughout is two-year truncated progression-free survival:
`T* = min(observed PFS time, 24 months)` and `delta* = 1` only when
progression/death occurred by 24 months. The bootstrap intervals condition on
the fitted Yale coefficients and on the observed target-cohort preprocessing.

No model selection, coefficient refitting, recalibration, threshold selection
or additional sensitivity analysis is part of this corrected archive.
