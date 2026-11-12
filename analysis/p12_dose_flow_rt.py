"""P12 — POST HOC (November 2026). (a) Dose contrast: group sizes behind the planned contrast and a within-learner
version restricted to learners with clusters of both sizes. (b) Sample flow. (c) Exercise durations on complete cases.
Usage: python3 p12_dose_flow_rt.py <track>"""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_symmetric as p1, p5_rt_session as p5
warnings.simplefilter('ignore')
if __name__ == '__main__':
    track = sys.argv[1]; groups, meta = p1.load(track); recs, _ = p1.estimate(groups, track)
    ref = json.load(open(p1.OUT / f'{track}_primary_meta.json')); assert len(recs) == ref['n_events']
    rows = []
    # (a) dose
    recs['dose'] = pd.cut(recs.n_errors, [1, 2, 3, np.inf], labels=['2', '3', '4+']).astype(str)
    L = recs.groupby(['user', 'dose'])[['ev_pre', 'ev_post', 'c_pre', 'c_post', 'ev_pre_a', 'ev_post_a', 'c_pre_a', 'c_post_a']].mean()
    did = ((L.ev_post - L.c_post) - (L.ev_pre - L.c_pre)).unstack('dose'); did_a = ((L.ev_post_a - L.c_post_a) - (L.ev_pre_a - L.c_pre_a)).unstack('dose')
    both = did[['2', '4+']].dropna()
    D = pd.DataFrame({'did_4plus_minus_2_within': both['4+'] - both['2'], 'did_2_common': both['2'], 'did_4plus_common': both['4+'],
                      'did_a_4plus_minus_2_within': (did_a['4+'] - did_a['2']).reindex(both.index)})
    mean, reps = p1.boot_means(D.to_numpy(float)); lo, hi = p1.ci(reps)
    for i, q in enumerate(D.columns): rows.append(dict(track=track, tag='dose_within', analysis='posthoc', quantity=q, n_learners=len(D), n_events=np.nan, mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100))
    dose_n = dict(n_learners_dose2=int(did['2'].notna().sum()), n_learners_dose3=int(did['3'].notna().sum()), n_learners_dose4plus=int(did['4+'].notna().sum()), n_learners_both_2_and_4plus=len(both),
                  n_clusters_dose2=int((recs.dose == '2').sum()), n_clusters_dose3=int((recs.dose == '3').sum()), n_clusters_dose4plus=int((recs.dose == '4+').sum()))
    # (b) flow
    ncl = nwin = 0
    for user, g, x in groups:
        n = len(g); e = x.errors.to_numpy() >= 2; ncl += int(e.sum()); nwin += int((e & (x.end.to_numpy() + 20 < n) & (x.start.to_numpy() >= 20)).sum())
    raw = json.load(open(p1.OUT / 'p0_extract_summary.json'))[track]
    flow = dict(raw_learner_records=raw['users'], raw_tokens=raw['tokens'], retained_learner_records=meta['n_users'], retained_tokens=meta['n_tokens'],
                clusters_total=ncl, clusters_without_complete_windows=ncl - nwin, clusters_with_complete_windows=nwin,
                clusters_without_matched_comparison=nwin - len(recs), clusters_matched=len(recs), learners_contributing=int(recs.user.nunique()))
    # (c) durations, complete cases
    rt, _ = p5.rt_table(track); r = p5.run(groups, rt, track, False); assert len(r) == len(recs)
    cols = [c for c in r.columns if c.startswith(('ev_', 'c_'))]; Lr = r.groupby('user')[cols].mean()
    pre = lambda p: Lr[[f'{p}_-3', f'{p}_-2', f'{p}_-1']].mean(axis=1); post = lambda p: Lr[[f'{p}_1', f'{p}_2', f'{p}_3']].mean(axis=1)
    R = pd.DataFrame({'rt_pre_ex_cc': pre('ev') - pre('c'), 'rt_post_ex_cc': post('ev') - post('c')}).dropna(); R['rt_did_cc'] = R.rt_post_ex_cc - R.rt_pre_ex_cc
    mean, reps = p1.boot_means(R.to_numpy(float)); lo, hi = p1.ci(reps)
    for i, q in enumerate(R.columns): rows.append(dict(track=track, tag='rt_complete_case', analysis='posthoc', quantity=q, n_learners=len(R), n_events=len(r), mean_pp=mean[i] * 100, lo_pp=lo[i] * 100, hi_pp=hi[i] * 100))
    pd.DataFrame(rows).to_csv(p1.OUT / f'{track}_dose_rt_posthoc_summary.csv', index=False)
    json.dump(dict(track=track, dose=dose_n, flow=flow), open(p1.OUT / f'{track}_flow.json', 'w'), indent=2)
    print(pd.DataFrame(rows).round(2).to_string()); print(dose_n); print(flow)
