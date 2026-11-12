"""P9 — POST HOC (November 2026): is the excess around a cluster local, or a property of the whole session?
For each matched cluster and its comparison anchors (pre-specified matching, same seed as p1), the
"rest-of-session" error rate is the error rate of all tokens in the anchor's session that lie more than 20
tokens before the anchor exercise or more than 20 tokens after it (at least 20 such tokens required).
Rest-of-session excess = event minus comparison. Local excess = window excess minus rest-of-session excess.
Usage: python3 p9_session_background.py <track>
"""
from pathlib import Path
import sys, warnings
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1
warnings.simplefilter('ignore'); W = 20

if __name__ == '__main__':
    track = sys.argv[1]; groups, _ = p1.load(track); rng = np.random.default_rng(p1.SEED); recs = []
    for user, g, x in groups:
        y = g.error.to_numpy(float); n = len(y); cs = np.concatenate([[0], np.cumsum(y)])
        start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy(); ses = x.ses.to_numpy()
        s_first = pd.Series(start).groupby(ses).min().reindex(ses).to_numpy(); s_last = pd.Series(end).groupby(ses).max().reindex(ses).to_numpy()
        available = (end + W < n) & (start >= W)
        evmask = (errs >= 2) & available; plmask = (errs < 2) & available
        keys = list(zip(x.daybin, x.fmt, x.lenbin, x.freq)); pools = {}
        for j in np.flatnonzero(plmask): pools.setdefault(keys[j], []).append(j)
        def rest(i):
            a0, a1 = s_first[i], max(s_first[i], start[i] - W)          # tokens [a0, a1) before the window
            b0, b1 = min(s_last[i] + 1, end[i] + W + 1), s_last[i] + 1  # tokens [b0, b1) after the window
            cnt = (a1 - a0) + (b1 - b0)
            return (cs[a1] - cs[a0] + cs[b1] - cs[b0]) / cnt if cnt >= 20 else np.nan
        def win(i): return y[start[i] - W:start[i]].mean(), y[end[i] + 1:end[i] + W + 1].mean()
        for j in np.flatnonzero(evmask):
            pool = pools.get(keys[j], [])
            if not pool: continue
            chosen = np.asarray(pool) if len(pool) <= 3 else rng.choice(pool, 3, replace=False)
            er = rest(j); cr = [rest(c) for c in chosen]
            if np.isnan(er) or np.all(np.isnan(cr)): continue
            ok = [c for c, r in zip(chosen, cr) if not np.isnan(r)]
            cw = np.array([win(c) for c in ok]); ew = win(j)
            recs.append(dict(user=user, ev_rest=er, c_rest=np.nanmean(cr), ev_pre=ew[0], ev_post=ew[1], c_pre=cw[:, 0].mean(), c_post=cw[:, 1].mean()))
    R = pd.DataFrame(recs); L = R.groupby('user').mean(numeric_only=True); D = pd.DataFrame(index=L.index)
    D['rest_ex'] = L.ev_rest - L.c_rest; D['pre_ex'] = L.ev_pre - L.c_pre; D['post_ex'] = L.ev_post - L.c_post
    D['pre_local'] = D.pre_ex - D.rest_ex; D['post_local'] = D.post_ex - D.rest_ex; D['did'] = D.post_ex - D.pre_ex
    mean, reps = p1.boot_means(D.to_numpy(float)); lo, hi = p1.ci(reps)
    out = pd.DataFrame([dict(track=track, tag='session_background', analysis='diag', quantity=q, n_learners=len(D), n_events=len(R),
                             mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100) for i, q in enumerate(D.columns)])
    out.to_csv(p1.OUT / f'{track}_sessionbg_summary.csv', index=False)
    out['est'] = out.apply(lambda r: f"{r.mean_pp:.2f} [{r.lo_pp:.2f}, {r.hi_pp:.2f}]", axis=1); print(track, len(R)); print(out[['quantity', 'est']].to_string())
