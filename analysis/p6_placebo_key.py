"""P6 — POST HOC control for the session-position matching (November 2026).
Replaces the session-position band by an uninformative key with the same number of levels and the same
marginal distribution (the learner's own session-position bands, randomly permuted across that learner's
exercises). If the reduction in excess under session matching were due only to finer matching cells or to
the loss of events, the placebo key would reduce the excess as well.
Usage: python3 p6_placebo_key.py <track>
"""
from pathlib import Path
import sys
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1

if __name__ == '__main__':
    track = sys.argv[1]
    groups, meta = p1.load(track)
    rng = np.random.default_rng(20261112)
    for u, g, x in groups:
        x['sesbin'] = rng.permutation(x.sesbin.to_numpy())
    recs, prof = p1.estimate(groups, track, sesmatch=True)
    rows, profile = p1.summarise(recs, prof, track, 'placebo_key', 20)
    rows.to_csv(p1.OUT / f'{track}_placebo_key_summary.csv', index=False)
    r = rows[(rows.analysis == 'primary') & rows.quantity.isin(['pre_ex', 'post_ex', 'did'])]
    print(track, len(recs)); print(r[['quantity', 'mean_pp', 'lo_pp', 'hi_pp']].round(2).to_string())
