#!/usr/bin/env bash
# Runs every analysis reported in the manuscript, in order. Requires data/*.pkl (see README: analysis/run_extract.py).
set -e
T="en_es es_en fr_en"
for t in $T; do
  python3 analysis/p1_symmetric.py $t                                   # planned main analysis
  python3 analysis/p1_symmetric.py $t --window 10 --tag w10             # planned sensitivities
  python3 analysis/p1_symmetric.py $t --window 30 --tag w30
  python3 analysis/p1_symmetric.py $t --k 3 --tag k3
  python3 analysis/p1_symmetric.py $t --history prior --tag prior
  python3 analysis/p1_symmetric.py $t --history symmetric --tag symmetric
  python3 analysis/p2_repeats.py $t                                     # post hoc from here on
  python3 analysis/p4_posthoc.py $t
  python3 analysis/p1_symmetric.py $t --sesmatch --tag sesmatch         # needed by p5 (not reported)
  python3 analysis/p5_rt_session.py $t
  python3 analysis/p8_diagnostics.py $t
  python3 analysis/p9_session_background.py $t
  python3 analysis/p10_overlap.py $t
  python3 analysis/p11_overlap_share.py $t
  python3 analysis/p12_dose_flow_rt.py $t
done
python3 analysis/p3_figures.py
python3 analysis/p7_additional_file.py
# the manuscript source is not part of the public archive; the check runs when it is present
if [ -f manuscript/CRPI_MANUSCRIPT.md ]; then python3 analysis/check_manuscript.py manuscript/CRPI_MANUSCRIPT.md; fi
