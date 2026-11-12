"""P5 — POST HOC (November 2026, added after editorial feedback), labelled as such in the report.

(a) Exercise-level response time around error clusters ("post-error slowing" analogue).
    For every matched event and its comparison anchors (identical matching and seed as p1), take the
    exercises at lags -3..-1 and +1..+3 around the anchor exercise and compare adjusted log response
    times. Adjusted log RT = log(seconds) minus the course mean log RT of exercises with the same format
    and token count (token count capped at 12). RTs <= 0 or missing are dropped; RTs are winsorised at
    the course 99th percentile. DiD = (E_post - E_pre) - (C_post - C_pre).
(b) Session-position descriptives: error rate, and share of events and comparison-eligible exercises,
    by position band within the session; median exercise duration.

Usage: python3 p5_rt_session.py <track>
"""
from pathlib import Path
import sys, json
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1

OUT = p1.OUT
LAGS = [-3, -2, -1, 1, 2, 3]
BANDS = ['1-3', '4-8', '9-15', '16-28', '29+']


def rt_table(track):
    ex = pd.read_pickle(p1.DATA / f'{track}_exercises.pkl')
    tok = pd.read_pickle(p1.DATA / f'{track}_tokens.pkl')
    n = tok.groupby('ex_id').size().rename('n')
    ex = ex.merge(n, left_on='ex_id', right_index=True)
    ok = ex.rt.notna() & (ex.rt > 0)
    cap = ex.loc[ok, 'rt'].quantile(.99)
    ex['lrt'] = np.where(ok, np.log(ex.rt.clip(upper=cap).where(ok, 1.0)), np.nan)
    ex['ncap'] = ex.n.clip(upper=12)
    ex['adj_lrt'] = ex.lrt - ex.groupby(['format', 'ncap']).lrt.transform('mean')
    meta = dict(track=track, rt_missing_or_nonpositive=float((~ok).mean()), rt_cap_seconds=float(cap),
                median_rt_seconds=float(ex.loc[ok, 'rt'].median()))
    return ex.set_index('ex_id')[['adj_lrt', 'lrt']], meta


def run(groups, rt, track, sesmatch, window=20, k=2, seed=p1.SEED):
    rng = np.random.default_rng(seed); recs = []
    for user, g, x in groups:
        n = len(g); start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy()
        a = rt.adj_lrt.reindex(x.ex_id).to_numpy(); m = len(x)
        available = (end + window < n) & (start >= window)
        evmask = (errs >= k) & available; plmask = (errs < k) & available
        keys = list(zip(x.daybin, x.fmt, x.lenbin, x.freq, x.sesbin)) if sesmatch else list(zip(x.daybin, x.fmt, x.lenbin, x.freq))
        pools = {}
        for j in np.flatnonzero(plmask): pools.setdefault(keys[j], []).append(j)
        def lagvals(i):
            return [a[i + l] if 0 <= i + l < m else np.nan for l in LAGS]
        for j in np.flatnonzero(evmask):
            pool = pools.get(keys[j], [])
            if not pool: continue
            chosen = np.asarray(pool) if len(pool) <= 3 else rng.choice(pool, 3, replace=False)
            ev = lagvals(j); cv = np.nanmean(np.array([lagvals(c) for c in chosen], float), axis=0) if True else None
            rec = dict(user=user, ex_id=int(x.ex_id.iloc[j]), n_errors=int(errs[j]), ev_anchor=a[j], c_anchor=np.nanmean(a[chosen]))
            for l, e_, c_ in zip(LAGS, ev, cv): rec[f'ev_{l}'] = e_; rec[f'c_{l}'] = c_
            recs.append(rec)
    return pd.DataFrame(recs)


def summarise(recs, track, tag):
    import warnings; warnings.simplefilter('ignore')
    cols = [c for c in recs.columns if c.startswith(('ev_', 'c_'))]
    L = recs.groupby('user')[cols].mean()
    D = pd.DataFrame(index=L.index)
    pre = lambda p: L[[f'{p}_-3', f'{p}_-2', f'{p}_-1']].mean(axis=1); post = lambda p: L[[f'{p}_1', f'{p}_2', f'{p}_3']].mean(axis=1)
    D['rt_pre_ex'] = pre('ev') - pre('c'); D['rt_post_ex'] = post('ev') - post('c'); D['rt_did'] = D.rt_post_ex - D.rt_pre_ex
    D['rt_m1_ex'] = L['ev_-1'] - L['c_-1']; D['rt_p1_ex'] = L['ev_1'] - L['c_1']; D['rt_did_lag1'] = D.rt_p1_ex - D.rt_m1_ex
    D['rt_anchor_ex'] = L.ev_anchor - L.c_anchor
    D['rt_ev_post_minus_pre'] = post('ev') - pre('ev'); D['rt_c_post_minus_pre'] = post('c') - pre('c')
    mean, reps = p1.boot_means(D.to_numpy(float)); lo, hi = p1.ci(reps)
    # report as log-RT differences x100 (approximately percent)
    return pd.DataFrame([dict(track=track, tag=tag, analysis='rt', quantity=q, n_learners=int(D[q].notna().sum()), n_events=len(recs),
                              mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100) for i, q in enumerate(D.columns)])


def session_descriptives(groups, track, window=20, k=2):
    rows = []
    for user, g, x in groups:
        n = len(g); available = (x.end.to_numpy() + window < n) & (x.start.to_numpy() >= window)
        rows.append(pd.DataFrame(dict(user=user, sesbin=x.sesbin.to_numpy(), n=x.n.to_numpy(), errors=x.errors.to_numpy(),
                                      ev=(x.errors.to_numpy() >= k) & available, cp=(x.errors.to_numpy() < k) & available)))
    X = pd.concat(rows)
    out = []
    for b, d in X.groupby('sesbin'):
        out.append(dict(track=track, band=BANDS[int(b)], exercises=len(d), token_error_rate_pct=100 * d.errors.sum() / d.n.sum(),
                        cluster_rate_pct=100 * (d.errors >= k).mean(),
                        share_of_events_pct=100 * d.ev.sum() / X.ev.sum(), share_of_comparison_pool_pct=100 * d.cp.sum() / X.cp.sum()))
    return pd.DataFrame(out)


if __name__ == '__main__':
    track = sys.argv[1]
    groups, _ = p1.load(track); rt, meta = rt_table(track)
    sd = session_descriptives(groups, track); sd.to_csv(OUT / f'{track}_session_position.csv', index=False); print(sd.round(2).to_string())
    allrows = []
    for tag, ses in [('rt_primary', False), ('rt_sesmatch', True)]:
        recs = run(groups, rt, track, ses)
        ref = json.load(open(OUT / f"{track}_{'sesmatch' if ses else 'primary'}_meta.json"))
        assert len(recs) == ref['n_events'], (len(recs), ref['n_events'])
        rows = summarise(recs, track, tag); allrows.append(rows)
        rows['est'] = rows.apply(lambda r: f"{r.mean_pp:.2f} [{r.lo_pp:.2f}, {r.hi_pp:.2f}]", axis=1); print(tag, len(recs)); print(rows[['quantity', 'n_learners', 'est']].to_string())
    pd.concat(allrows).drop(columns='est').to_csv(OUT / f'{track}_rt_summary.csv', index=False)
    json.dump(meta, open(OUT / f'{track}_rt_meta.json', 'w'), indent=2); print(meta)
