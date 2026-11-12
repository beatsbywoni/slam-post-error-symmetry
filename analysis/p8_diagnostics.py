"""P8 — POST HOC diagnostics added after an internal review round (November 2026).

For one course, with the same matching logic and seed as p1:
 (1) matching-draw variation: pre excess, post excess and DiD over 20 matching seeds;
 (2) exercise-level analysis: proportion of tokens wrong in the exercises at lags -3..-1 and +1..+3 around
     the anchor exercise (event vs matched comparison), under the pre-specified matching, session-position
     matching, and with comparison anchors restricted to error-free exercises;
 (3) alternative extra matching keys (session type, client, session-length band, same session), each compared
     with the pre-specified matching on exactly the same clusters; share of comparison anchors drawn from the
     event's own session and their distance in exercises;
 (4) placebo for session-position matching: 20 within-learner permutations of position bands, evaluated on the
     clusters retained under session-position matching;
 (5) elapsed time to the next recorded exercise.
Usage: python3 p8_diagnostics.py <track>
"""
from pathlib import Path
import sys, json, warnings
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1
warnings.simplefilter('ignore')
OUT = p1.OUT; W = 20; LAGS = [-3, -2, -1, 1, 2, 3]


def run(groups, extra=None, comp_max_err=1, seed=p1.SEED, k=2, sesbin_override=None, no_overlap=False):
    rng = np.random.default_rng(seed); recs = []
    for gi, (user, g, x) in enumerate(groups):
        y = g.error.to_numpy(float); n = len(y); days = x.days.to_numpy()
        start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy(); m = len(x)
        perr = errs / x.n.to_numpy(); ses = x.ses.to_numpy()
        available = (end + W < n) & (start >= W)
        evmask = (errs >= k) & available; plmask = (errs <= comp_max_err) & available
        base = [x.daybin.to_numpy(), x.fmt.to_numpy(), x.lenbin.to_numpy(), x.freq.to_numpy()]
        if extra == 'sesbin' and sesbin_override is not None: base.append(sesbin_override[gi])
        elif extra: base.append(x[extra].to_numpy())
        keys = list(zip(*base)); pools = {}
        for j in np.flatnonzero(plmask): pools.setdefault(keys[j], []).append(j)
        pre_off = np.arange(-W, 0); post_off = np.arange(1, W + 1)
        def lag(i): return [perr[i + l] if 0 <= i + l < m else np.nan for l in LAGS]
        for j in np.flatnonzero(evmask):
            pool = pools.get(keys[j], [])
            if no_overlap:  # drop comparison anchors whose pre or post window contains tokens of this cluster exercise
                pool = [c for c in pool if end[c] + W < start[j] or start[c] - W > end[j]]
            if not pool: continue
            chosen = np.asarray(pool) if len(pool) <= 3 else rng.choice(pool, 3, replace=False)
            rec = dict(user=user, ex_id=int(x.ex_id.iloc[j]),
                       ev_pre=y[start[j] + pre_off].mean(), ev_post=y[end[j] + post_off].mean(),
                       c_pre=y[start[chosen, None] + pre_off[None, :]].mean(), c_post=y[end[chosen, None] + post_off[None, :]].mean(),
                       m_same_ses=float(np.mean(ses[chosen] == ses[j])), m_absdist=float(np.mean(np.abs(chosen - j))),
                       m_gap_ticks=float(round((days[j + 1] - days[j]) * 1000)) if j + 1 < m else np.nan)
            cl = np.nanmean(np.array([lag(c) for c in chosen], float), axis=0)
            for l, e_, c_ in zip(LAGS, lag(j), cl): rec[f'xev_{l}'] = e_; rec[f'xc_{l}'] = c_
            recs.append(rec)
    return pd.DataFrame(recs)


def learner_table(recs):
    L = recs.groupby('user').mean(numeric_only=True)
    D = pd.DataFrame(index=L.index)
    D['pre_ex'] = L.ev_pre - L.c_pre; D['post_ex'] = L.ev_post - L.c_post; D['did'] = D.post_ex - D.pre_ex
    D['x_m1_ex'] = L['xev_-1'] - L['xc_-1']; D['x_p1_ex'] = L['xev_1'] - L['xc_1']; D['x_did_lag1'] = D.x_p1_ex - D.x_m1_ex
    pre = lambda p: L[[f'{p}_-3', f'{p}_-2', f'{p}_-1']].mean(axis=1); post = lambda p: L[[f'{p}_1', f'{p}_2', f'{p}_3']].mean(axis=1)
    D['x_pre3_ex'] = pre('xev') - pre('xc'); D['x_post3_ex'] = post('xev') - post('xc'); D['x_did_lag1to3'] = D.x_post3_ex - D.x_pre3_ex
    D['x_ev_p1_minus_m1'] = L['xev_1'] - L['xev_-1']
    D['same_session_share'] = L.m_same_ses; D['abs_distance_exercises'] = L.m_absdist / 100.0
    return D


def rows(D, track, tag, n_events, cols=None):
    cols = cols or list(D.columns); M = D[cols].to_numpy(float)
    mean, reps = p1.boot_means(M); lo, hi = p1.ci(reps)
    return [dict(track=track, tag=tag, analysis='diag', quantity=q, n_learners=int(D[q].notna().sum()), n_events=n_events,
                 mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100) for i, q in enumerate(cols)]


if __name__ == '__main__':
    track = sys.argv[1]; groups, _ = p1.load(track); out = []
    base = run(groups); ref = pd.read_csv(OUT / f'{track}_primary_summary.csv').set_index('quantity')
    Db = learner_table(base)
    assert len(base) == int(ref.loc['did', 'n_events']) and abs(Db.did.mean() * 100 - ref.loc['did', 'mean_pp']) < 1e-9, 'p8 does not reproduce p1'
    out += rows(Db, track, 'x_primary', len(base))
    gap = base.m_gap_ticks
    meta = dict(track=track, share_next_exercise_same_tick=float((gap == 0).mean()), share_next_within_1_tick=float((gap <= 1).mean()),
                share_next_within_30min=float((gap < 21).mean()), tick_seconds=86.4)
    # (1) seeds
    seeds = []
    for sd in range(20261101, 20261121):
        D = learner_table(run(groups, seed=sd)); seeds.append(D[['pre_ex', 'post_ex', 'did']].mean() * 100)
    S = pd.DataFrame(seeds); meta['seed_variation'] = {c: dict(mean=float(S[c].mean()), min=float(S[c].min()), max=float(S[c].max())) for c in S.columns}
    # (2) exercise level under other designs
    ses = run(groups, extra='sesbin'); out += rows(learner_table(ses), track, 'x_sesmatch', len(ses))
    ef = run(groups, comp_max_err=0); out += rows(learner_table(ef), track, 'x_errorfree_comparisons', len(ef))
    # (3) alternative keys, each against the pre-specified matching on the same clusters
    for key in ['sesbin', 'sestype', 'client', 'seslen', 'ses']:
        r = ses if key == 'sesbin' else run(groups, extra=key)
        common = base[base.ex_id.isin(set(r.ex_id))]
        out += rows(learner_table(r), track, f'key_{key}', len(r), ['pre_ex', 'post_ex', 'did', 'same_session_share', 'abs_distance_exercises'])
        out += rows(learner_table(common), track, f'key_{key}_baseline_same_clusters', len(common), ['pre_ex', 'post_ex', 'did', 'same_session_share', 'abs_distance_exercises'])
    # (4) placebo on the clusters retained under session-position matching
    keep = set(ses.ex_id); rng = np.random.default_rng(20261112); pl = []
    for _ in range(20):
        ov = [rng.permutation(x.sesbin.to_numpy()) for _, _, x in groups]
        r = run(groups, extra='sesbin', sesbin_override=ov); r = r[r.ex_id.isin(keep)]
        pl.append(learner_table(r)[['pre_ex', 'post_ex', 'did']].mean() * 100)
    P = pd.DataFrame(pl); meta['placebo_common_clusters'] = {c: dict(mean=float(P[c].mean()), min=float(P[c].min()), max=float(P[c].max())) for c in P.columns}
    pd.DataFrame(out).to_csv(OUT / f'{track}_diag_summary.csv', index=False); json.dump(meta, open(OUT / f'{track}_diag_meta.json', 'w'), indent=2)
    d = pd.DataFrame(out); d['est'] = d.apply(lambda r: f"{r.mean_pp:.2f} [{r.lo_pp:.2f}, {r.hi_pp:.2f}]", axis=1)
    print(d[['tag', 'quantity', 'n_events', 'est']].to_string()); print(json.dumps(meta, indent=1))
