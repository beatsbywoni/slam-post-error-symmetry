"""P1 — Symmetric pre/post windows around error clusters, item-difficulty adjusted.

Specified in docs/OSF_ADDENDUM_2026-09-23_EN.md before execution. Reuses the
matching logic of the 18 September estimator (reanalyse.estimate) and adds:
pre windows for both anchor types, leave-one-learner-out item difficulty,
dose (cluster size), lag (position) and session-gap decompositions.

Usage: python3 p1_symmetric.py <track> [--window 20] [--k 2] [--history none|prior|symmetric] [--tag name]
"""
from pathlib import Path
import sys, json, time
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
OUT = ROOT / 'outputs'; OUT.mkdir(exist_ok=True)
SEED = 20260923
BOOT = 2000
MIN_OTHER = 20      # minimum other-learner occurrences for token-level difficulty
SESSION_GAP_MIN = 30
EXMETA = {}


def load(track):
    tok = pd.read_pickle(DATA / f'{track}_tokens.pkl')
    ex = pd.read_pickle(DATA / f'{track}_exercises.pkl')
    global EXMETA
    EXMETA = {c: ex.set_index('ex_id')[c] for c in ['session', 'client']}
    tok = tok.merge(ex[['ex_id', 'days', 'format']], on='ex_id', validate='many_to_one')
    assert not tok.duplicated(['user', 'pos_idx']).any()
    stats = tok.groupby('user').error.agg(['size', 'sum'])
    keep = stats[(stats['size'] >= 200) & (stats['sum'] >= 20)].index
    tok = tok[tok.user.isin(keep)].sort_values(['user', 'pos_idx']).reset_index(drop=True)
    assert (tok.groupby('user').days.diff().dropna() >= 0).all(), 'Unsorted source chronology'
    tok['freq_bin'] = pd.qcut(tok.token_freq, 4, labels=False, duplicates='drop').astype(int)
    # --- leave-one-learner-out item difficulty (within course, on included learners) ---
    tw = tok.groupby('token').error.agg(T_n='size', T_e='sum')
    uw = tok.groupby(['user', 'token']).error.agg(u_n='size', u_e='sum').reset_index()
    uw = uw.merge(tw, left_on='token', right_index=True)
    uw['other_n'] = uw.T_n - uw.u_n; uw['other_e'] = uw.T_e - uw.u_e
    tp = tok.groupby('pos').error.agg(P_n='size', P_e='sum')
    up = tok.groupby(['user', 'pos']).error.agg(p_n='size', p_e='sum').reset_index()
    up = up.merge(tp, left_on='pos', right_index=True)
    up['pother_n'] = up.P_n - up.p_n; up['pother_e'] = up.P_e - up.p_e
    tok = tok.merge(uw[['user', 'token', 'other_n', 'other_e']], on=['user', 'token'], how='left')
    tok = tok.merge(up[['user', 'pos', 'pother_n', 'pother_e']], on=['user', 'pos'], how='left')
    tok_ok = tok.other_n >= MIN_OTHER
    d_tok = np.where(tok_ok, tok.other_e / tok.other_n.where(tok.other_n > 0, 1), np.nan)
    d_pos = np.where(tok.pother_n > 0, tok.pother_e / tok.pother_n.where(tok.pother_n > 0, 1), tok.error.mean())
    tok['difficulty'] = np.where(np.isfinite(d_tok), d_tok, d_pos)
    tok['fallback_pos'] = ~tok_ok
    tok['adj'] = tok.error - tok.difficulty
    tok = tok.sort_values(['user', 'pos_idx']).reset_index(drop=True)
    diffmeta = dict(track=track, n_users=int(tok.user.nunique()), n_tokens=len(tok),
                    share_pos_fallback=float(tok.fallback_pos.mean()),
                    difficulty_mean=float(tok.difficulty.mean()), error_mean=float(tok.error.mean()))
    groups = []
    for u, g in tok.groupby('user', sort=True):
        g = g.reset_index(drop=True)
        x = g.groupby('ex_id', sort=False).agg(start=('pos_idx', 'min'), end=('pos_idx', 'max'), days=('days', 'first'),
                                                fmt=('format', 'first'), n=('error', 'size'), errors=('error', 'sum'),
                                                freq=('freq_bin', 'median'), diff=('difficulty', 'mean'))
        x = x.sort_values('start').reset_index()
        assert np.array_equal(g.pos_idx.to_numpy(), np.arange(len(g)))
        x['daybin'] = pd.cut(x.days, [0, 7, 14, 30], labels=False, include_lowest=True).astype(int)
        x['lenbin'] = np.searchsorted([2, 4, 7], x.n, side='left')
        # POST HOC (added 23 Sept after internal review): position within session, sessions split at gaps >= 30 min
        gapmin = x.days.diff().fillna(np.inf) * 1440.0
        ses = (gapmin >= SESSION_GAP_MIN).cumsum()
        x['sespos'] = x.groupby(ses).cumcount() + 1
        x['sesbin'] = np.searchsorted([4, 9, 16, 29], x.sespos, side='right')   # 1-3, 4-8, 9-15, 16-28, 29+
        # POST HOC (November 2026): further session descriptors used only by p8_diagnostics.py
        x['ses'] = ses.to_numpy()
        x['seslen'] = np.searchsorted([9, 16, 29], x.groupby('ses').ex_id.transform('size'), side='right')  # 1-8, 9-15, 16-28, 29+
        x['sestype'] = x.ex_id.map(EXMETA['session']).to_numpy(); x['client'] = x.ex_id.map(EXMETA['client']).to_numpy()
        groups.append((u, g[['error', 'adj', 'days']].copy(), x))
    return groups, diffmeta


def estimate(groups, track, window=20, k=2, history='none', seed=SEED, sesmatch=False):
    """Per-event records with symmetric windows; matching identical to the 18 Sept estimator
    except that both anchor types must also have a complete pre window."""
    rng = np.random.default_rng(seed)
    recs = []; prof = []  # prof: per-learner position sums
    for user, g, x in groups:
        y = g.error.to_numpy(float); a = g.adj.to_numpy(float); days = g.days.to_numpy(); n = len(y)
        start = x.start.to_numpy(); end = x.end.to_numpy(); errs = x.errors.to_numpy()
        event_all = end[errs >= k]
        previous = np.searchsorted(event_all, end, side='right') - 1
        prevdist = np.where(previous >= 0, end - event_all[np.maximum(previous, 0)], np.inf) if len(event_all) else np.full(len(x), np.inf)
        prior = np.searchsorted(event_all, end, side='left') - 1
        prior_dist = np.where(prior >= 0, end - event_all[np.maximum(prior, 0)], np.inf) if len(event_all) else np.full(len(x), np.inf)
        available = (end + window < n) & (start >= window)
        evmask = (errs >= k) & available
        plmask = (errs < k) & available
        if history == 'prior':      # 18 Sept rule: comparisons not within `window` tokens after a prior event
            plmask &= prevdist > window
        elif history == 'symmetric':  # both anchor types free of any prior event within `window` tokens
            plmask &= prevdist > window; evmask &= prior_dist > window
        elif history != 'none':
            raise ValueError(history)
        keys = list(zip(x.daybin, x.fmt, x.lenbin, x.freq, x.sesbin)) if sesmatch else list(zip(x.daybin, x.fmt, x.lenbin, x.freq))
        pools = {}
        for j in np.flatnonzero(plmask): pools.setdefault(keys[j], []).append(j)
        pre_off = np.arange(-window, 0); post_off = np.arange(1, window + 1)
        E = np.zeros((2, 2 * window)); C = np.zeros((2, 2 * window)); cnt = 0
        for j in np.flatnonzero(evmask):
            pool = pools.get(keys[j], [])
            if not pool: continue
            chosen = np.asarray(pool) if len(pool) <= 3 else rng.choice(pool, 3, replace=False)
            ep_pre = start[j] + pre_off; ep_post = end[j] + post_off
            cp_pre = start[chosen, None] + pre_off[None, :]; cp_post = end[chosen, None] + post_off[None, :]
            assert ep_pre.min() >= 0 and ep_post.max() < n and cp_pre.min() >= 0 and cp_post.max() < n
            ev = np.concatenate([y[ep_pre], y[ep_post]]); ea = np.concatenate([a[ep_pre], a[ep_post]])
            cv = np.concatenate([y[cp_pre].mean(0), y[cp_post].mean(0)]); ca = np.concatenate([a[cp_pre].mean(0), a[cp_post].mean(0)])
            E[0] += ev; E[1] += ea; C[0] += cv; C[1] += ca; cnt += 1
            gap_min = (days[end[j] + 1] - days[end[j]]) * 1440.0
            w = window
            recs.append(dict(
                track=track, user=user, ex_id=int(x.ex_id.iloc[j]), n_errors=int(errs[j]), n_tokens=int(x.n.iloc[j]),
                surprise=float(x['diff'].iloc[j]), gap_min=float(gap_min), day=float(x.days.iloc[j]),
                ev_pre=ev[:w].mean(), ev_post=ev[w:].mean(), c_pre=cv[:w].mean(), c_post=cv[w:].mean(),
                ev_pre_a=ea[:w].mean(), ev_post_a=ea[w:].mean(), c_pre_a=ca[:w].mean(), c_post_a=ca[w:].mean(),
                ev_m5=ev[w-5:w].mean(), c_m5=cv[w-5:w].mean(), ev_m5_a=ea[w-5:w].mean(), c_m5_a=ca[w-5:w].mean(),
                ev_p1=ev[w], c_p1=cv[w], ev_p1_a=ea[w], c_p1_a=ca[w],
                ev_p2_5=ev[w+1:w+5].mean(), c_p2_5=cv[w+1:w+5].mean(), ev_p2_5_a=ea[w+1:w+5].mean(), c_p2_5_a=ca[w+1:w+5].mean(),
                ev_p6_20=ev[w+5:].mean(), c_p6_20=cv[w+5:].mean(), ev_p6_20_a=ea[w+5:].mean(), c_p6_20_a=ca[w+5:].mean(),
            ))
        if cnt:
            prof.append(dict(user=user, n_events=cnt, E_raw=E[0] / cnt, E_adj=E[1] / cnt, C_raw=C[0] / cnt, C_adj=C[1] / cnt))
    return pd.DataFrame(recs), prof


def boot_means(M, seed=SEED, boot=BOOT):
    """M: learners x quantities (NaN allowed). Returns point means and bootstrap replicate means."""
    rng = np.random.default_rng(seed); n = len(M)
    idx = rng.integers(0, n, (boot, n))
    reps = np.stack([np.nanmean(M[ix], axis=0) for ix in idx])
    return np.nanmean(M, axis=0), reps


def ci(reps): return np.nanquantile(reps, [.025, .975], axis=0)


def summarise(recs, prof, track, tag, window):
    pp = 100.0
    # ---- learner-level means of all per-event quantities ----
    cols = [c for c in recs.columns if c.startswith(('ev_', 'c_'))]
    L = recs.groupby('user')[cols].mean(); nL = len(L)
    def derived(df):
        d = pd.DataFrame(index=df.index)
        for s in ['', '_a']:
            d['pre_ex' + s] = df['ev_pre' + s] - df['c_pre' + s]
            d['post_ex' + s] = df['ev_post' + s] - df['c_post' + s]
            d['did' + s] = d['post_ex' + s] - d['pre_ex' + s]
            d['ev_did' + s] = df['ev_post' + s] - df['ev_pre' + s]
            d['c_did' + s] = df['c_post' + s] - df['c_pre' + s]
            d['m5_ex' + s] = df['ev_m5' + s] - df['c_m5' + s]
            d['p1_ex' + s] = df['ev_p1' + s] - df['c_p1' + s]
            d['p2_5_ex' + s] = df['ev_p2_5' + s] - df['c_p2_5' + s]
            d['p6_20_ex' + s] = df['ev_p6_20' + s] - df['c_p6_20' + s]
            d['lag_p1_minus_m5' + s] = d['p1_ex' + s] - d['m5_ex' + s]
        return d
    D = derived(L)
    mean, reps = boot_means(D.to_numpy(float))
    lo, hi = ci(reps)
    rows = [dict(track=track, tag=tag, analysis='primary', quantity=q, n_learners=nL, n_events=len(recs),
                 mean_pp=mean[i] * pp, lo_pp=lo[i] * pp, hi_pp=hi[i] * pp) for i, q in enumerate(D.columns)]
    # share explained by item difficulty (post excess and pre excess)
    j_raw = list(D.columns).index('post_ex'); j_adj = list(D.columns).index('post_ex_a')
    share = 1 - reps[:, j_adj] / reps[:, j_raw]; share_pt = 1 - mean[j_adj] / mean[j_raw]
    rows.append(dict(track=track, tag=tag, analysis='primary', quantity='share_post_explained_by_item_difficulty', n_learners=nL, n_events=len(recs),
                     mean_pp=share_pt * 100, lo_pp=np.quantile(share, .025) * 100, hi_pp=np.quantile(share, .975) * 100))
    j_raw = list(D.columns).index('pre_ex'); j_adj = list(D.columns).index('pre_ex_a')
    share = 1 - reps[:, j_adj] / reps[:, j_raw]; share_pt = 1 - mean[j_adj] / mean[j_raw]
    rows.append(dict(track=track, tag=tag, analysis='primary', quantity='share_pre_explained_by_item_difficulty', n_learners=nL, n_events=len(recs),
                     mean_pp=share_pt * 100, lo_pp=np.quantile(share, .025) * 100, hi_pp=np.quantile(share, .975) * 100))
    # ---- dose ----
    recs['dose'] = pd.cut(recs.n_errors, [1, 2, 3, np.inf], labels=['2', '3', '4+']).astype(str)
    Ld = recs.groupby(['user', 'dose'])[cols].mean()
    Dd = derived(Ld).reset_index()
    wide = Dd.pivot(index='user', columns='dose', values=['did', 'did_a', 'post_ex', 'post_ex_a', 'pre_ex', 'pre_ex_a']).reindex(L.index)
    wide.columns = [f'{a}__{b}' for a, b in wide.columns]
    mean, reps = boot_means(wide.to_numpy(float)); lo, hi = ci(reps)
    for i, q in enumerate(wide.columns):
        dose = q.split('__')[1]
        rows.append(dict(track=track, tag=tag, analysis='dose', quantity=q, n_learners=int(wide[q].notna().sum()),
                         n_events=int((recs.dose == dose).sum()), mean_pp=mean[i] * pp, lo_pp=lo[i] * pp, hi_pp=hi[i] * pp))
    for s in ['', '_a']:
        if f'did{s}__4+' not in wide.columns or f'did{s}__2' not in wide.columns: continue
        a_ = list(wide.columns).index(f'did{s}__4+'); b_ = list(wide.columns).index(f'did{s}__2')
        diff = reps[:, a_] - reps[:, b_]
        rows.append(dict(track=track, tag=tag, analysis='dose', quantity=f'did{s}__4+_minus_2', n_learners=int(wide.iloc[:, [a_, b_]].notna().all(1).sum()),
                         n_events=np.nan, mean_pp=(mean[a_] - mean[b_]) * pp, lo_pp=np.quantile(diff, .025) * pp, hi_pp=np.quantile(diff, .975) * pp))
    # ---- session gap (exploratory) ----
    recs['gap'] = np.where(recs.gap_min < SESSION_GAP_MIN, 'same', 'break')
    Lg = recs.groupby(['user', 'gap'])[cols].mean(); Dg = derived(Lg).reset_index()
    wide = Dg.pivot(index='user', columns='gap', values=['post_ex', 'post_ex_a', 'did', 'did_a', 'p1_ex_a']).reindex(L.index)
    wide.columns = [f'{a}__{b}' for a, b in wide.columns]
    mean, reps = boot_means(wide.to_numpy(float)); lo, hi = ci(reps)
    for i, q in enumerate(wide.columns):
        gp = q.split('__')[1]
        rows.append(dict(track=track, tag=tag, analysis='session_gap', quantity=q, n_learners=int(wide[q].notna().sum()),
                         n_events=int((recs.gap == gp).sum()), mean_pp=mean[i] * pp, lo_pp=lo[i] * pp, hi_pp=hi[i] * pp))
    # ---- surprise tertiles (exploratory) ----
    recs['surprise_t'] = pd.qcut(recs.surprise, 3, labels=['hard', 'mid', 'easy'][::-1]).astype(str)  # low difficulty = easy = surprising
    Ls = recs.groupby(['user', 'surprise_t'])[cols].mean(); Ds = derived(Ls).reset_index()
    wide = Ds.pivot(index='user', columns='surprise_t', values=['did', 'did_a', 'post_ex_a', 'pre_ex_a']).reindex(L.index)
    wide.columns = [f'{a}__{b}' for a, b in wide.columns]
    mean, reps = boot_means(wide.to_numpy(float)); lo, hi = ci(reps)
    for i, q in enumerate(wide.columns):
        st = q.split('__')[1]
        rows.append(dict(track=track, tag=tag, analysis='surprise', quantity=q, n_learners=int(wide[q].notna().sum()),
                         n_events=int((recs.surprise_t == st).sum()), mean_pp=mean[i] * pp, lo_pp=lo[i] * pp, hi_pp=hi[i] * pp))
    # ---- position profile (learner-weighted means and bootstrap bands) ----
    P = {key: np.stack([p[key] for p in prof]) for key in ['E_raw', 'E_adj', 'C_raw', 'C_adj']}
    ex_raw = P['E_raw'] - P['C_raw']; ex_adj = P['E_adj'] - P['C_adj']
    positions = list(range(-window, 0)) + list(range(1, window + 1))
    profile = []
    for name, M in [('event_raw', P['E_raw']), ('comparison_raw', P['C_raw']), ('event_adj', P['E_adj']), ('comparison_adj', P['C_adj']), ('excess_raw', ex_raw), ('excess_adj', ex_adj)]:
        mean, reps = boot_means(M); lo, hi = ci(reps)
        for i, pos in enumerate(positions):
            profile.append(dict(track=track, tag=tag, series=name, position=pos, mean_pp=mean[i] * pp, lo_pp=lo[i] * pp, hi_pp=hi[i] * pp))
    return pd.DataFrame(rows), pd.DataFrame(profile)


def main():
    track = sys.argv[1]
    window = int(sys.argv[sys.argv.index('--window') + 1]) if '--window' in sys.argv else 20
    k = int(sys.argv[sys.argv.index('--k') + 1]) if '--k' in sys.argv else 2
    history = sys.argv[sys.argv.index('--history') + 1] if '--history' in sys.argv else 'none'
    tag = sys.argv[sys.argv.index('--tag') + 1] if '--tag' in sys.argv else 'primary'
    sesmatch = '--sesmatch' in sys.argv
    t0 = time.time()
    groups, meta = load(track); print('loaded', meta, f'{time.time()-t0:.0f}s', flush=True)
    recs, prof = estimate(groups, track, window=window, k=k, history=history, sesmatch=sesmatch)
    print('events', len(recs), 'learners', recs.user.nunique(), f'{time.time()-t0:.0f}s', flush=True)
    recs.to_csv(OUT / f'{track}_{tag}_events.csv', index=False)
    rows, profile = summarise(recs, prof, track, tag, window)
    rows.to_csv(OUT / f'{track}_{tag}_summary.csv', index=False)
    profile.to_csv(OUT / f'{track}_{tag}_profile.csv', index=False)
    meta.update(tag=tag, window=window, k=k, history=history, sesmatch=sesmatch, n_events=len(recs), n_learners=int(recs.user.nunique()),
                seed=SEED, boot=BOOT, seconds=round(time.time() - t0))
    json.dump(meta, open(OUT / f'{track}_{tag}_meta.json', 'w'), indent=2)
    print(rows[rows.analysis == 'primary'].to_string(), flush=True)
    print('DONE', f'{time.time()-t0:.0f}s', flush=True)


if __name__ == '__main__':
    main()
