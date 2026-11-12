"""P2 — POST HOC (added after primary results were seen, 23 Sept 2026).

Question raised by the primary results: is the symmetric excess around error
clusters carried by re-presentations of the same word forms (learner-specific
item knowledge) rather than by a learner state? For each anchor exercise
(event or comparison) we split window tokens into those whose surface form
occurs in the anchor exercise ("repeat") and those that do not ("non-repeat"),
and recompute pre/post excess on non-repeat tokens only. Same matching and seed
as p1 (history='none'), so the matched sets are identical.
"""
from pathlib import Path
import sys, json, time
import numpy as np
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs'


def load_tokens(track):
    tok = pd.read_pickle(p1.DATA / f'{track}_tokens.pkl')
    ex = pd.read_pickle(p1.DATA / f'{track}_exercises.pkl')
    tok = tok.merge(ex[['ex_id', 'days']], on='ex_id')
    stats = tok.groupby('user').error.agg(['size', 'sum'])
    keep = stats[(stats['size'] >= 200) & (stats['sum'] >= 20)].index
    tok = tok[tok.user.isin(keep)].sort_values(['user', 'pos_idx'])
    return {u: g.token.to_numpy() for u, g in tok.groupby('user', sort=True)}


def estimate(groups, tokens, track, window=20, k=2, seed=p1.SEED):
    rng = np.random.default_rng(seed); recs = []
    pre_off = np.arange(-window, 0); post_off = np.arange(1, window + 1)
    for user, g, x in groups:
        y = g.error.to_numpy(float); a = g.adj.to_numpy(float); n = len(y); T = tokens[user]; assert len(T) == n
        start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy()
        available = (end + window < n) & (start >= window)
        evmask = (errs >= k) & available; plmask = (errs < k) & available
        keys = list(zip(x.daybin, x.fmt, x.lenbin, x.freq)); pools = {}
        for j in np.flatnonzero(plmask): pools.setdefault(keys[j], []).append(j)
        for j in np.flatnonzero(evmask):
            pool = pools.get(keys[j], [])
            if not pool: continue
            chosen = np.asarray(pool) if len(pool) <= 3 else rng.choice(pool, 3, replace=False)
            def win(i):
                pre = start[i] + pre_off; post = end[i] + post_off
                anchor = set(T[start[i]:end[i] + 1])
                rp_pre = np.array([t in anchor for t in T[pre]]); rp_post = np.array([t in anchor for t in T[post]])
                return pre, post, rp_pre, rp_post
            ep, eq, er_pre, er_post = win(j)
            rec = dict(track=track, user=user, ex_id=int(x.ex_id.iloc[j]), n_errors=int(errs[j]),
                       ev_rep_share_pre=er_pre.mean(), ev_rep_share_post=er_post.mean())
            # event: non-repeat and repeat token means (raw and adjusted)
            for lab, m_pre, m_post in [('non', ~er_pre, ~er_post), ('rep', er_pre, er_post)]:
                rec[f'ev_pre_{lab}'] = y[ep][m_pre].mean() if m_pre.any() else np.nan
                rec[f'ev_post_{lab}'] = y[eq][m_post].mean() if m_post.any() else np.nan
                rec[f'ev_pre_{lab}_a'] = a[ep][m_pre].mean() if m_pre.any() else np.nan
                rec[f'ev_post_{lab}_a'] = a[eq][m_post].mean() if m_post.any() else np.nan
            cvals = {f'c_{w}_{lab}{s}': [] for w in ['pre', 'post'] for lab in ['non', 'rep'] for s in ['', '_a']}
            cshare = []
            for c in chosen:
                cp, cq, cr_pre, cr_post = win(c); cshare.append((cr_pre.mean(), cr_post.mean()))
                for lab, m_pre, m_post in [('non', ~cr_pre, ~cr_post), ('rep', cr_pre, cr_post)]:
                    cvals[f'c_pre_{lab}'].append(y[cp][m_pre].mean() if m_pre.any() else np.nan)
                    cvals[f'c_post_{lab}'].append(y[cq][m_post].mean() if m_post.any() else np.nan)
                    cvals[f'c_pre_{lab}_a'].append(a[cp][m_pre].mean() if m_pre.any() else np.nan)
                    cvals[f'c_post_{lab}_a'].append(a[cq][m_post].mean() if m_post.any() else np.nan)
            for kk, v in cvals.items(): rec[kk] = np.nanmean(v) if np.isfinite(v).any() else np.nan
            rec['c_rep_share_pre'] = np.mean([s[0] for s in cshare]); rec['c_rep_share_post'] = np.mean([s[1] for s in cshare])
            recs.append(rec)
    return pd.DataFrame(recs)


def summarise(recs, track):
    cols = [c for c in recs.columns if c.startswith(('ev_', 'c_'))]
    L = recs.groupby('user')[cols].mean()
    D = pd.DataFrame(index=L.index)
    for lab in ['non', 'rep']:
        for s in ['', '_a']:
            D[f'pre_ex_{lab}{s}'] = L[f'ev_pre_{lab}{s}'] - L[f'c_pre_{lab}{s}']
            D[f'post_ex_{lab}{s}'] = L[f'ev_post_{lab}{s}'] - L[f'c_post_{lab}{s}']
            D[f'did_{lab}{s}'] = D[f'post_ex_{lab}{s}'] - D[f'pre_ex_{lab}{s}']
    for w in ['pre', 'post']:
        D[f'rep_share_{w}_event'] = L[f'ev_rep_share_{w}']; D[f'rep_share_{w}_comparison'] = L[f'c_rep_share_{w}']
    mean, reps = p1.boot_means(D.to_numpy(float)); lo, hi = p1.ci(reps)
    rows = [dict(track=track, tag='repeats_posthoc', analysis='repeats', quantity=q, n_learners=int(D[q].notna().sum()), n_events=len(recs),
                 mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100) for i, q in enumerate(D.columns)]
    return pd.DataFrame(rows)


if __name__ == '__main__':
    track = sys.argv[1]; t0 = time.time()
    groups, meta = p1.load(track); tokens = load_tokens(track)
    recs = estimate(groups, tokens, track)
    ref = pd.read_csv(OUT / f'{track}_primary_events.csv')
    assert len(recs) == len(ref) and (recs.ex_id.to_numpy() == ref.ex_id.to_numpy()).all(), 'matched sets differ from primary'
    recs.to_csv(OUT / f'{track}_repeats_events.csv', index=False)
    rows = summarise(recs, track); rows.to_csv(OUT / f'{track}_repeats_summary.csv', index=False)
    rows['est'] = rows.apply(lambda r: f"{r.mean_pp:.2f} [{r.lo_pp:.2f}, {r.hi_pp:.2f}]", axis=1)
    print(rows[['quantity', 'n_learners', 'est']].to_string()); print('DONE', f'{time.time()-t0:.0f}s')
