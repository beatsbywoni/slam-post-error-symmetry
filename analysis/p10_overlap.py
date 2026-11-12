"""P10 — POST HOC (November 2026): do comparison windows that contain the cluster itself drive the effect of
session-related matching keys? Re-runs the pre-specified matching and the session-position matching while
excluding, for each cluster, comparison anchors whose pre or post window contains tokens of that cluster
exercise; also reports how often such overlap occurs.
Usage: python3 p10_overlap.py <track>
"""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1, p8_diagnostics as p8
warnings.simplefilter('ignore')
if __name__ == '__main__':
    track = sys.argv[1]; groups, _ = p1.load(track); out = []
    cols = ['pre_ex', 'post_ex', 'did', 'same_session_share', 'x_did_lag1', 'x_m1_ex', 'x_p1_ex']
    runs = {}
    for tag, extra, no in [('primary_nooverlap', None, True), ('sesbin_nooverlap', 'sesbin', True), ('seslen_nooverlap', 'seslen', True), ('sestype_nooverlap', 'sestype', True)]:
        r = p8.run(groups, extra=extra, no_overlap=no); runs[tag] = r
        out += p8.rows(p8.learner_table(r), track, tag, len(r), cols)
    # same clusters, session-position matching, with vs without overlapping comparisons
    a = p8.run(groups, extra='sesbin'); keep = set(a.ex_id) & set(runs['sesbin_nooverlap'].ex_id)
    out += p8.rows(p8.learner_table(a[a.ex_id.isin(keep)]), track, 'sesbin_overlap_allowed_common', len(keep), cols[:3])
    out += p8.rows(p8.learner_table(runs['sesbin_nooverlap'][runs['sesbin_nooverlap'].ex_id.isin(keep)]), track, 'sesbin_nooverlap_common', len(keep), cols[:3])
    d = pd.DataFrame(out); d.to_csv(p1.OUT / f'{track}_overlap_summary.csv', index=False)
    d['est'] = d.apply(lambda r: f"{r.mean_pp:.2f} [{r.lo_pp:.2f}, {r.hi_pp:.2f}]", axis=1); print(d[['tag', 'quantity', 'n_events', 'est']].to_string())
