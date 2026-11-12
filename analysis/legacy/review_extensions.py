"""Additional post hoc checks requested in pre-submission review, 2026-09-18.
No new confirmatory hypotheses. Reuses the corrected matching realization exactly.
"""
from pathlib import Path
import sys,json,time,hashlib
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
import reanalyse as a
R=a.ROOT; O=a.OUT; TRACKS=['en_es','es_en','fr_en']; SEED=a.SEED; BOOT=a.BOOT

def instrument():
    # Instrument a copy of the estimator without changing the primary selection/RNG.
    import inspect
    s=inspect.getsource(a.estimate).replace('def estimate(', 'def detailed(').replace('seed=SEED):','seed=SEED,symmetric=False):')
    s=s.replace("evmask=(x.errors.to_numpy()>=k)&available", "prior=np.searchsorted(event_all,x.end.to_numpy(),side='left')-1\n        prior_dist=np.where(prior>=0,x.end.to_numpy()-event_all[np.maximum(prior,0)],np.inf) if len(event_all) else np.full(len(x),np.inf)\n        evmask=(x.errors.to_numpy()>=k)&available\n        if symmetric: evmask &= prior_dist>window")
    s=s.replace('used=[set(),set()]', 'used=[set(),set()]; eu=[set(),set()]; pu=[set(),set()]; anchors=[[],[]]; extras={}')
    s=s.replace('ec=y[ep]; pc=y[pp].mean(0); d=ec-pc', '''eu[h].update(ep.tolist());pu[h].update(pp.ravel().tolist());anchors[h].extend(chosen.tolist())
            ec=y[ep]; pc=y[pp].mean(0); d=ec-pc
            es=int(x.start.iloc[j]); cs=x.start.to_numpy()[chosen]
            extra=dict(day_difference=float(x.days.iloc[j]-x.days.iloc[chosen].mean()),log_frequency_difference=float(x.logfreq.iloc[j]-x.logfreq.iloc[chosen].mean()))
            if es>=window and np.all(cs>=window):
                extra.update(event_pre=float(y[es-window:es].mean()),comparison_pre=float(np.mean([y[int(q)-window:int(q)].mean() for q in cs])),event_post_common=float(ec.mean()),comparison_post_common=float(pc.mean()))
            extras.setdefault(h,[]).append(extra)''')
    s=s.replace("row.update({f'd{z+1}'", "row.update(unique_event_tokens=len(eu[h]),unique_comparison_tokens=len(pu[h]),comparison_draws=len(anchors[h]),unique_comparison_anchors=len(set(anchors[h])),comparison_reuse_rate=1-len(set(anchors[h]))/len(anchors[h]))\n            for key in ['day_difference','log_frequency_difference','event_pre','comparison_pre','event_post_common','comparison_post_common']:\n                vv=[q[key] for q in extras[h] if key in q];row[key]=np.mean(vv) if vv else np.nan\n            row['n_pre_events']=sum('event_pre' in q for q in extras[h])\n            row.update({f'd{z+1}'")
    ns=dict(a.__dict__);exec(s,ns);return ns['detailed']
detailed=instrument()

def dist(v):
    v=np.asarray(v);v=v[np.isfinite(v)]
    if not len(v):return dict(n=0,min=np.nan,q1=np.nan,median=np.nan,q3=np.nan,max=np.nan)
    return dict(n=len(v),min=v.min(),q1=np.quantile(v,.25),median=np.median(v),q3=np.quantile(v,.75),max=v.max())

def corr_ci(x,y):
    if len(x)<3 or np.std(x)==0 or np.std(y)==0:return [np.nan]*3
    x=np.asarray(x);y=np.asarray(y);r=spearmanr(x,y).statistic;rng=np.random.default_rng(SEED)
    bs=[]
    for _ in range(BOOT):
        ix=rng.integers(0,len(x),len(x));bs.append(spearmanr(x[ix],y[ix]).statistic)
    return [r,*np.nanquantile(bs,[.025,.975])]

def track(t):
    started=time.monotonic();groups,meta=a.load(t)
    tok=pd.read_parquet(a.DER/f'{t}_tokens.parquet');ex=pd.read_parquet(a.DER/f'{t}_exercises.parquet')
    logfreq=tok.groupby('ex_id').token_freq.apply(lambda v:np.log1p(v).mean())
    for u,g,x in groups:x['logfreq']=x.ex_id.map(logfreq)
    allstat=tok.groupby('user').error.agg(['size','sum'])
    flow=[dict(track=t,stage='Raw training records',n=len(allstat)),dict(track=t,stage='At least 200 tokens',n=int((allstat['size']>=200).sum())),dict(track=t,stage='Also at least 20 errors',n=len(groups))]
    main,diag=detailed(groups,t);old=pd.read_csv(O/f'{t}_axes.csv')
    np.testing.assert_allclose(main[old.select_dtypes('number').columns],old.select_dtypes('number'),equal_nan=True,atol=1e-12)
    main.to_csv(O/f'{t}_detailed_main.csv',index=False)
    flow += [dict(track=t,stage='Complete event window',n=int((diag.eligible_events>0).sum())),dict(track=t,stage='At least one matched event',n=len(main))]
    quantities=[];components=[]
    for split in ['block','temporal']:
        name='block100' if split=='block' else split
        tab,dg=detailed(groups,t,split=split);old=pd.read_csv(O/f'{t}_{name}_halves.csv')
        np.testing.assert_allclose(tab[old.select_dtypes('number').columns],old.select_dtypes('number'),equal_nan=True,atol=1e-12)
        tab.to_csv(O/f'{t}_{name}_detailed.csv',index=False)
        for minimum in [5,10,20]:
            z=tab[tab.n_events>=minimum];ids=z.groupby('user').size();ids=ids[ids==2].index;z=z[z.user.isin(ids)]
            if minimum==5:flow.append(dict(track=t,stage=name+' at least 5 per half (branch)',n=len(ids)))
            for axis in ['event_error','placebo_error','auc']:
                w=z.pivot(index='user',columns='half',values=axis).reindex(columns=[0,1]).dropna();r,lo,hi=corr_ci(w[0],w[1]);components.append(dict(track=t,split=name,min_events=minimum,axis=axis,n=len(w),r=r,lo=lo,hi=hi))
            for half in [0,1]:
                for var in ['n_events','unique_event_tokens','unique_comparison_tokens','comparison_draws','unique_comparison_anchors','comparison_reuse_rate']:
                    quantities.append(dict(track=t,split=name,min_events=minimum,half=half,variable=var,**dist(z.loc[z.half==half,var])))
        print(t,name,'done',flush=True)
    pd.DataFrame(quantities).to_csv(O/f'{t}_information.csv',index=False);pd.DataFrame(components).to_csv(O/f'{t}_components.csv',index=False)
    sy,dg=detailed(groups,t,symmetric=True);sy.to_csv(O/f'{t}_symmetric_axes.csv',index=False);dg.to_csv(O/f'{t}_symmetric_matching.csv',index=False)
    summ=[]
    for axis in ['depth','auc','event_pre','comparison_pre','event_post_common','comparison_post_common']:
        m,l,h=a.interval_mean(sy[axis]);summ.append(dict(track=t,axis=axis,n=int(sy[axis].notna().sum()),events=int(sy.n_events.sum()),mean=m,lo=l,hi=h))
    pd.DataFrame(summ).to_csv(O/f'{t}_symmetric_summary.csv',index=False)
    # Prospective selection branches start again at full-record inclusion.
    desc=[]
    for cut in [10,12]:
        pred=pd.read_csv(O/f'{t}_prediction_cut{cut}.csv')
        early,ed=detailed(groups,t,cut=cut)
        flow += [dict(track=t,stage=f'Day {cut} complete early event window (branch)',n=int((ed.eligible_events>0).sum())),dict(track=t,stage=f'Day {cut} any early matched event',n=len(early)),dict(track=t,stage=f'Day {cut} at least 10 early matched events',n=int((early.n_events>=10).sum())),dict(track=t,stage=f'Day {cut} also at least 50 later tokens',n=int(pred.included.sum())),dict(track=t,stage=f'Day {cut} also slope outcome conditions',n=int((pred.included&pred.out_slope.notna()).sum()))]
        ids=set(pred.loc[pred.included,'user']);ev=dict(zip(pred.user,pred.n_events))
        for u,g,x in groups:
            if u not in ids:continue
            row=dict(track=t,user=u,cut=cut,n_events=ev[u])
            for name,mask in [('early',g.days<=cut),('late',g.days>cut)]:
                q=g[mask];xx=x[x.ex_id.isin(q.ex_id)]
                row.update({name+'_tokens':len(q),name+'_exercises':len(xx),name+'_days_min':q.days.min(),name+'_days_max':q.days.max(),name+'_span':q.days.max()-q.days.min(),name+'_distinct_times':q.days.nunique(),name+'_error':q.error.mean()})
            desc.append(row)
    pd.DataFrame(flow).to_csv(O/f'{t}_flow.csv',index=False);pd.DataFrame(desc).to_csv(O/f'{t}_cohort_descriptives.csv',index=False)
    json.dump(dict(track=t,seconds=time.monotonic()-started,primary_matches_unchanged=True),open(O/f'{t}_extension_checks.json','w'),indent=2)
    print(t,'complete',time.monotonic()-started,flush=True)

def prediction():
    d=pd.concat([pd.read_csv(O/f'{t}_prediction_cut10.csv') for t in TRACKS]);d=d[d.included].reset_index(drop=True);assert len(d)==1105 and not d.user.duplicated().any()
    # Preserve the original primary fold realization: advance by exactly its bootstrap draws.
    n=len(d);rng=np.random.default_rng(SEED)
    for _ in range(BOOT):rng.integers(0,n,n)
    def folds(rng):
        f=np.empty(n,int)
        for t in d.track.unique():
            ix=np.flatnonzero((d.track==t).to_numpy());rng.shuffle(ix);f[ix]=np.arange(len(ix))%5
        return f
    fixed=folds(rng);y=d.out_acc.to_numpy();den=((y-y.mean())**2).sum();deviation=d.auc.to_numpy();out=[];cv=[];vifs=[]
    repeated=[fixed]+[folds(np.random.default_rng(SEED+10000+i)) for i in range(1,101)]
    pd.DataFrame({'track':d.track,'user':d.user,**{f'repeat_{i}':f for i,f in enumerate(repeated)}}).to_csv(O/'prediction_folds.csv',index=False)
    for name,early_acc,early_volume in [('M1',False,False),('M2',False,True),('M3',True,False),('M4',True,True)]:
        xs=[d.base_acc.to_numpy()];names=['comparison_accuracy']
        if early_acc:xs.append(d.early_acc.to_numpy());names.append('overall_early_accuracy')
        xs.append(np.log(d.n_early if early_volume else d.n_out).to_numpy());names.append('log_early_volume' if early_volume else 'log_later_volume')
        for t in sorted(d.track.unique())[1:]:xs.append((d.track==t).to_numpy(float));names.append(t)
        C=np.column_stack([np.ones(n)]+xs);X=np.column_stack([C,deviation]);names=['intercept']+names+['deviation']
        def fit(ix):
            c=C[ix];x=X[ix];yy=y[ix];b=np.linalg.lstsq(x,yy,rcond=None)[0];bc=np.linalg.lstsq(c,yy,rcond=None)[0];dd=((yy-yy.mean())**2).sum()
            return b[-1]*x[:,-1].std(ddof=1)/yy.std(ddof=1),1-((yy-c@bc)**2).sum()/dd,1-((yy-x@b)**2).sum()/dd
        beta,r0,r1=fit(np.arange(n));rng=np.random.default_rng(SEED);bs=[fit(rng.integers(0,n,n))[0] for _ in range(BOOT)];lo,hi=np.quantile(bs,[.025,.975])
        cc=[]
        for repeat,f in enumerate(repeated):
            p0=np.empty(n);p1=np.empty(n)
            for k in range(5):
                tr=f!=k;te=~tr;p0[te]=C[te]@np.linalg.lstsq(C[tr],y[tr],rcond=None)[0];p1[te]=X[te]@np.linalg.lstsq(X[tr],y[tr],rcond=None)[0]
            c0=1-((y-p0)**2).sum()/den;c1=1-((y-p1)**2).sum()/den;cc.append(c1-c0);cv.append(dict(model=name,repeat=repeat,base_r2=c0,full_r2=c1,delta_r2=c1-c0))
        first=cv[-len(repeated)];out.append(dict(model=name,n=n,beta=beta,lo=lo,hi=hi,base_r2=r0,full_r2=r1,delta_r2=r1-r0,cv_base=first['base_r2'],cv_full=first['full_r2'],cv_delta=first['delta_r2'],repeat_median=np.median(cc[1:]),repeat_lo=np.quantile(cc[1:],.025),repeat_hi=np.quantile(cc[1:],.975)))
        for j in range(1,X.shape[1]):
            z=X[:,j];other=np.delete(X,j,axis=1);res=z-other@np.linalg.lstsq(other,z,rcond=None)[0];vif=((z-z.mean())**2).sum()/(res**2).sum();vifs.append(dict(model=name,variable=names[j],vif=vif))
    pd.DataFrame(out).to_csv(O/'factorial_prediction.csv',index=False);pd.DataFrame(cv).to_csv(O/'repeated_cv.csv',index=False);pd.DataFrame(vifs).to_csv(O/'prediction_vif.csv',index=False)
    d[['auc','base_acc','early_acc']].corr().to_csv(O/'prediction_correlations.csv')
    old=pd.read_csv(O/'prediction_models.csv');old=old[(old.scope=='pooled')&(old.cut==10)&(old.axis=='auc')&(old.outcome=='out_acc')]
    for name,control in [('M1','original'),('M4','early_strict')]:
        q=next(z for z in out if z['model']==name);r=old[old.controls==control].iloc[0];np.testing.assert_allclose([q['beta'],q['cv_delta']],[r.beta,r.cv_delta_r2],atol=1e-12)
    print(pd.DataFrame(out).to_string(index=False),flush=True)

def combine():
    for name in ['information','components','symmetric_summary','flow','cohort_descriptives']:
        pd.concat([pd.read_csv(O/f'{t}_{name}.csv') for t in TRACKS]).to_csv(O/f'{name}.csv',index=False)
    z=pd.read_csv(O/'cohort_descriptives.csv');r=[]
    for (t,cut),g in z.groupby(['track','cut']):
        for col in g.select_dtypes('number').columns.drop('cut'):r.append(dict(track=t,cut=cut,variable=col,**dist(g[col])))
    pd.DataFrame(r).to_csv(O/'cohort_distribution.csv',index=False)
    r=[]
    for t in TRACKS:
        g=pd.read_csv(O/f'{t}_detailed_main.csv')
        for col in ['length_difference','day_difference','log_frequency_difference','frequency_bin_difference']:
            r.append(dict(track=t,variable=col,mean=g[col].mean(),**dist(g[col])))
    pd.DataFrame(r).to_csv(O/'continuous_matching.csv',index=False)

if __name__=='__main__':
    if sys.argv[1]=='prediction':prediction()
    elif sys.argv[1]=='combine':combine()
    else:track(sys.argv[1])
