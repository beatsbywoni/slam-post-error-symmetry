# Failed exercises mark error-prone periods: replication archive

Archived at https://doi.org/10.5281/zenodo.24165342 · Repository: https://github.com/beatsbywoni/slam-post-error-symmetry

Code, analysis plan and numerical outputs for the Brief Report "Failed exercises mark error-prone periods: error rates before and after errors in app-based language practice" (H. Jeong).

## Data (not included)

Duolingo SLAM corpus, version 4.0: Settles, B. (2018). *Data for the 2018 Duolingo Shared Task on Second Language Acquisition Modeling (SLAM)*. Harvard Dataverse. https://doi.org/10.7910/DVN/8SWHNO

Download the three course archives and place them, unextracted, in one folder. The analysis reads the training partition inside each archive (`<track>.slam.20190204.train`).

| File | SHA-256 of the archive used |
|---|---|
| data_en_es.tar.gz | dac4e97a03e0d35d0b417e4afb8e96a20cdd3bad933bdc590ab4b56c77531393 |
| data_es_en.tar.gz | c53079ed8053f5237225ae1b3713ecb7ecb1d0245369cd60599f17c6a6868243 |
| data_fr_en.tar.gz | f34bb1518d2fbc694d6b142b78b16cb2c755df314e78a1fcb6a86b9987727c31 |

These hashes are of the downloaded archives, recorded in `outputs/p0_extract_summary.json`.

## Environment

Verified with Python 3.13.18, pandas 3.0.5, numpy 2.5.3, scipy 1.18.1, matplotlib 3.11.2 (Linux). `pip install -r requirements.txt`. Run time and memory were not measured systematically; the planned estimator takes under a minute per course on the machine used, extraction a few minutes.

## Run

```
python3 analysis/run_extract.py --raw-dir /path/to/archives     # writes data/*.pkl
bash run_all.sh                                                  # all analyses, tables and figures
```

`run_all.sh` lists every step in order. To reproduce only the planned main result: `python3 analysis/p1_symmetric.py en_es` (and `es_en`, `fr_en`), then compare `outputs/<track>_primary_summary.csv`, rows `analysis == primary`, `quantity == did`: 0.4345 [0.2426, 0.6225], 0.0839 [-0.1132, 0.2774], -0.2494 [-0.5668, 0.0510] percentage points. All seeds are fixed (matching and bootstrap 20260923; placebo 20261112), so results should agree to floating-point precision.

`outputs/reproduction_check_2026-11-12.csv` records a run from the raw archives in an empty folder with the instructions above: all 64 rows of each course's planned summary were identical (maximum absolute difference 0) for both the current estimator and the frozen one. The post hoc scripts were not re-run in that check; their archived outputs come from the same code.

## What is frozen

`outputs/plan_freeze.json` holds SHA-256 hashes, taken on 23 September 2026, of the plan (`docs/OSF_ADDENDUM_2026-09-23_EN.md`), the extractor (`analysis/p0_extract.py`, unchanged) and the estimator. The frozen estimator is kept as `analysis/p1_symmetric_frozen_2026-09-23.py` (its hash matches when the file is named `p1_symmetric.py`). `analysis/p1_symmetric.py` is the same estimator with options added later for post hoc analyses; it gives identical planned results. `analysis/run_extract.py` only redirects the extractor's input and output folders. The freeze date is recorded in that file and is not independently certified.

## Scripts, outputs and where they are reported

Outputs are `outputs/<track>_<tag>_summary.csv` with columns `track, tag, analysis, quantity, n_learners, n_events, mean_pp, lo_pp, hi_pp` (percentage points; 95% learner-bootstrap percentile limits). The manuscript rounds to two decimals.

| Script | Status | Tags written | Reported in |
|---|---|---|---|
| p1_symmetric.py | planned | primary; w10, w30, k3, prior, symmetric (planned sensitivities) | Table 2 (planned block), Fig. 1, Fig. 2, Tables S1, S5 |
| p1_symmetric.py --sesmatch | post hoc | sesmatch | superseded by p10; not reported |
| p2_repeats.py | post hoc | repeats_posthoc | Table 2, Table S3 |
| p4_posthoc.py | post hoc | reversed_*, break_posthoc | Tables S1, S5 |
| p5_rt_session.py | post hoc | rt_primary, rt_sesmatch | Table 2, Table S4 |
| p6_placebo_key.py | post hoc | placebo_key | not reported (superseded by p10) |
| p8_diagnostics.py | post hoc | x_primary, x_errorfree_comparisons, key_*; `*_diag_meta.json` (matching seeds) | Table 2, Table S2 |
| p9_session_background.py | post hoc | session_background | Table 2, Table S2 |
| p10_overlap.py, p11_overlap_share.py | post hoc | *_nooverlap; `*_overlap_share.json` | Table 2, Table S2 |
| p12_dose_flow_rt.py | post hoc | dose_within, rt_complete_case; `*_flow.json` | Table 2, Tables S1, S4, S6 |
| p3_figures.py | | Figure_1, Figure_2 | Figs 1, 2 |
| p7_additional_file.py | | manuscript/ADDITIONAL_FILE_1.md | Additional file 1 |
| check_manuscript.py | | word counts; checks every "x [lo, hi]" in the manuscript against the CSVs and exits non-zero on a mismatch (the manuscript source is not included in this archive) | |

Notes on reading the outputs. In `*_primary_summary.csv`, the row `did__4+_minus_2` is the difference between the mean DiD of learners with clusters of four or more errors and the mean DiD of learners with clusters of two; its `n_learners` is the number of learners with both, not the size of either group (group sizes are in `*_flow.json`). "Session" variables in the code (`ses`, `sesbin`, `seslen`) are practice bouts defined by gaps of 30 minutes or more, not the application's sessions; `sestype` is the corpus field (lesson, practice, test). `analysis/legacy/` holds scripts from an earlier phase of the project that need files not in this archive; they are kept for the record and are not part of the pipeline.

Code: MIT licence (see LICENSE). Text and outputs: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).

Cite as: Jeong, H. (2026). Replication archive for "Failed exercises mark error-prone periods: Error rates before and after errors in app-based language practice" (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.24165342
