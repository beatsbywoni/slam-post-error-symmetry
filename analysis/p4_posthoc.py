"""P4 — POST HOC checks added after internal review (23 Sept 2026), labelled as such.

(a) Time-reversal placebo: each learner's token stream is reversed (pos_idx reversed; days replaced by
    max_days - days so chronology stays monotone) and the p1 estimator is re-run under each history rule.
    A time-symmetric process gives the same DiD forward and reversed; a forward-causal post-error effect
    cannot appear in reversed data. Used to calibrate the symmetric-rule DiD.
(b) Break probability: share of events vs comparison anchors whose next exercise begins >= 30 min later.
(c) Events dropped for lack of a matching pool.
"""
from pathlib import Path
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1

OUT = p1.OUT


def reverse_groups(groups):
    rev = []
    for u, g, x in groups:
        n = len(g); maxd = g.days.max()
        g2 = g.iloc[::-1].reset_index(drop=True).copy(); g2['days'] = maxd - g2['days']
        x2 = x.copy(); s, e = x2.start.to_numpy(), x2.end.to_numpy()
        x2['start'] = n - 1 - e; x2['end'] = n - 1 - s; x2['days'] = maxd - x2['days']
        x2['daybin'] = pd.cut(x2.days, [0, 7, 14, 30], labels=False, include_lowest=True).astype(int)
        x2 = x2.sort_values('start').reset_index(drop=True)
        rev.append((u, g2, x2))
    return rev


def break_probability(groups, track, window=20, k=2, seed=p1.SEED):
    """Learner-weighted P(next exercise starts >= 30 min later) for events and for comparison anchors
    (all eligible comparison exercises, and the matched ones)."""
    rows = []
    for user, g, x in groups:
        days = g.days.to_numpy(); n = len(g)
        start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy()
        available = (end + window < n) & (start >= window)
        gap = np.full(len(x), np.nan); ok = end + 1 < n
        gap[ok] = (days[end[ok] + 1] - days[end[ok]]) * 1440.0
        ev = (errs >= k) & available; cp = (errs < k) & available
        if ev.sum() and cp.sum():
            rows.append(dict(user=user, p_break_event=np.mean(gap[ev] >= p1.SESSION_GAP_MIN), p_break_comparison=np.mean(gap[cp] >= p1.SESSION_GAP_MIN),
                             n_event=int(ev.sum()), n_comp=int(cp.sum())))
    L = pd.DataFrame(rows).set_index('user')
    M = L[['p_break_event', 'p_break_comparison']].to_numpy(float); M = np.column_stack([M, M[:, 0] - M[:, 1]])
    mean, reps = p1.boot_means(M); lo, hi = p1.ci(reps)
    out = []
    for i, q in enumerate(['p_break_event', 'p_break_comparison', 'p_break_difference']):
        out.append(dict(track=track, tag='break_posthoc', analysis='break', quantity=q, n_learners=len(L), n_events=int(L.n_event.sum()),
                        mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100))
    return pd.DataFrame(out)


def dropped(groups, track, window=20, k=2):
    n_ev = 0; n_matched = 0
    for user, g, x in groups:
        n = len(g); start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy()
        available = (end + window < n) & (start >= window)
        n_ev += int(((errs >= k) & available).sum())
    ref = pd.read_csv(OUT / f'{track}_primary_events.csv'); n_matched = len(ref)
    return dict(track=track, eligible_events=n_ev, matched_events=n_matched, dropped_no_pool=n_ev - n_matched, share_dropped=1 - n_matched / n_ev)


if __name__ == '__main__':
    track = sys.argv[1]
    groups, meta = p1.load(track)
    bp = break_probability(groups, track); bp.to_csv(OUT / f'{track}_break_posthoc_summary.csv', index=False); print(bp.to_string())
    dr = dropped(groups, track); json.dump(dr, open(OUT / f'{track}_dropped.json', 'w'), indent=2); print(dr)
    rev = reverse_groups(groups)
    for hist in ['none', 'symmetric', 'prior']:
        recs, prof = p1.estimate(rev, track, history=hist)
        rows, profile = p1.summarise(recs, prof, track, f'reversed_{hist}', 20)
        rows.to_csv(OUT / f'{track}_reversed_{hist}_summary.csv', index=False); profile.to_csv(OUT / f'{track}_reversed_{hist}_profile.csv', index=False)
        r = rows[(rows.analysis == 'primary') & rows.quantity.isin(['pre_ex', 'post_ex', 'did', 'ev_did', 'c_did', 'did_a'])]
        print('reversed', hist, len(recs)); print(r[['quantity', 'mean_pp', 'lo_pp', 'hi_pp']].round(2).to_string())
