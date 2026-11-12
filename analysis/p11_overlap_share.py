"""P11 — POST HOC: under the pre-specified matching (same seed and draws as p1), how many drawn comparison
anchors have a pre or post window that contains tokens of the cluster exercise they are matched to?"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1
W = 20
if __name__ == '__main__':
    track = sys.argv[1]; groups, _ = p1.load(track); rng = np.random.default_rng(p1.SEED)
    nev = ncomp = nov = evany = 0
    for user, g, x in groups:
        n = len(g); start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy()
        available = (end + W < n) & (start >= W)
        keys = list(zip(x.daybin, x.fmt, x.lenbin, x.freq)); pools = {}
        for j in np.flatnonzero((errs < 2) & available): pools.setdefault(keys[j], []).append(j)
        for j in np.flatnonzero((errs >= 2) & available):
            pool = pools.get(keys[j], [])
            if not pool: continue
            ch = np.asarray(pool) if len(pool) <= 3 else rng.choice(pool, 3, replace=False)
            ov = ~((end[ch] + W < start[j]) | (start[ch] - W > end[j]))
            nev += 1; ncomp += len(ch); nov += int(ov.sum()); evany += int(ov.any())
    ref = json.load(open(p1.OUT / f'{track}_primary_meta.json')); assert nev == ref['n_events'], (nev, ref['n_events'])
    out = dict(track=track, n_events=nev, n_comparisons=ncomp, share_comparisons_overlapping=nov / ncomp, share_events_with_any_overlap=evany / nev)
    json.dump(out, open(p1.OUT / f'{track}_overlap_share.json', 'w'), indent=2); print(out)
