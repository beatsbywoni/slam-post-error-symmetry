"""Post hoc C1 corrections. Originals are read only; see ../ANALYSIS_PLAN.md."""
from pathlib import Path
import sys, json, hashlib, platform
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parents[1]
DER=ROOT.parent/'03_analysis/derived'
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
SEED=20260918
BOOT=2000

def load(track):
    tok=pd.read_parquet(DER/f'{track}_tokens.parquet')
    ex=pd.read_parquet(DER/f'{track}_exercises.parquet')
    tok=tok.merge(ex[['ex_id','days','format']],on='ex_id',validate='many_to_one')
    assert not tok.duplicated(['user','pos_idx']).any()
    stats=tok.groupby('user').error.agg(['size','sum'])
    keep=stats[(stats['size']>=200)&(stats['sum']>=20)].index
    tok=tok[tok.user.isin(keep)].sort_values(['user','pos_idx'])
    assert (tok.groupby('user').days.diff().dropna()>=0).all(), 'Unsorted source chronology'
    tok['freq_bin']=pd.qcut(tok.token_freq,4,labels=False,duplicates='drop').astype(int)
    groups=[]
    for u,g in tok.groupby('user',sort=True):
        g=g.reset_index(drop=True)
        x=g.groupby('ex_id',sort=False).agg(start=('pos_idx','min'),end=('pos_idx','max'),days=('days','first'),fmt=('format','first'),n=('error','size'),errors=('error','sum'),freq=('freq_bin','median'))
        x=x.sort_values('start').reset_index()
        assert np.array_equal(g.pos_idx.to_numpy(),np.arange(len(g)))
        x['daybin']=pd.cut(x.days,[0,7,14,30],labels=False,include_lowest=True).astype(int)
        x['lenbin']=np.searchsorted([2,4,7],x.n,side='left')
        groups.append((u,g[['error','days','ex_id','token']].copy(),x))
    return groups,dict(track=track,n_users=len(groups),n_tokens=len(tok))

def estimate(groups,track,window=20,k=2,split=None,block=100,cut=None,seed=SEED):
    rng=np.random.default_rng(seed); rows=[]; diagnostic=[]
    early_freq=None
    if cut is not None:
        words=pd.concat([g.loc[g.days<=cut,'token'] for _,g,_ in groups],ignore_index=True)
        freq=words.value_counts(); bins=pd.qcut(words.map(freq),4,labels=False,duplicates='drop')
        early_freq=dict(zip(words,bins))
    # Every window is represented by its original token indices; membership asserts
    # below protect event AND comparison observations, including reused comparisons.
    for user,g,x0 in groups:
        x=x0.copy(); y=g.error.to_numpy(); days=g.days.to_numpy(); n=len(y)
        if early_freq is not None:
            early=g[g.days<=cut].copy();early['fb']=early.token.map(early_freq)
            med=early.groupby('ex_id').fb.median();x['freq']=x.ex_id.map(med)
        if split=='block': seg=(x.start.to_numpy()//block).astype(int)
        elif split=='temporal': seg=(np.arange(len(x))>=len(x)/2).astype(int)
        else: seg=np.zeros(len(x),dtype=int)
        halves=seg%2 if split=='block' else seg
        token_seg=np.repeat(seg,x.n.to_numpy())
        event_all=x.end.to_numpy()[x.errors.to_numpy()>=k]
        previous=np.searchsorted(event_all,x.end.to_numpy(),side='right')-1
        prevdist=np.where(previous>=0,x.end.to_numpy()-event_all[np.maximum(previous,0)],np.inf) if len(event_all) else np.full(len(x),np.inf)
        available=x.end.to_numpy()+window<n
        if cut is not None:
            available &= x.days.to_numpy()<=cut
            available &= days[np.minimum(x.end.to_numpy()+window,n-1)]<=cut
        available &= token_seg[np.minimum(x.end.to_numpy()+window,n-1)]==seg
        evmask=(x.errors.to_numpy()>=k)&available
        plmask=(x.errors.to_numpy()<k)&available&(prevdist>window)
        keys=list(zip(x.daybin,x.fmt,x.lenbin,x.freq,halves))
        pools={}
        for j in np.flatnonzero(plmask): pools.setdefault(keys[j],[]).append(j)
        vals={}; counts={}; difflen={}; difffreq={}; evrates={}; plrates={}; pres={}
        used=[set(),set()]
        for j in np.flatnonzero(evmask):
            pool=pools.get(keys[j],[])
            if not pool: continue
            chosen=np.asarray(pool) if len(pool)<=3 else rng.choice(pool,3,replace=False)
            end=int(x.end.iloc[j]); ep=np.arange(end+1,end+window+1)
            pp=x.end.to_numpy()[chosen,None]+np.arange(1,window+1)[None,:]
            h=int(halves[j]); assert np.all(token_seg[ep]==seg[j])
            assert np.all((token_seg[pp]%2 if split=='block' else token_seg[pp])==h)
            if cut is not None: assert np.all(days[ep]<=cut) and np.all(days[pp]<=cut)
            if split:
                used[h].update(ep.tolist()); used[h].update(pp.ravel().tolist())
            ec=y[ep]; pc=y[pp].mean(0); d=ec-pc
            vals.setdefault(h,[]).append(d);evrates.setdefault(h,[]).append(ec);plrates.setdefault(h,[]).append(pc)
            counts[h]=counts.get(h,0)+1
            difflen.setdefault(h,[]).append(float(x.n.iloc[j]-x.n.iloc[chosen].mean()))
            difffreq.setdefault(h,[]).append(float(x.freq.iloc[j]-x.freq.iloc[chosen].mean()))
            start=int(x.start.iloc[j]); pre=y[start-window:start] if start>=window else None
            if pre is not None: pres.setdefault(h,[]).append(float(ec.mean()-pre.mean()))
        if split: assert not used[0].intersection(used[1]),'Cross-half raw token reuse'
        for h,v in vals.items():
            v=np.asarray(v); ev=np.asarray(evrates[h]); pl=np.asarray(plrates[h]); c=v.mean(0)
            row=dict(track=track,user=user,half=h,n_events=counts[h],auc=c.mean(),depth=c[:min(5,window)].mean(),completeness=c[-5:].mean(),event_error=ev.mean(),placebo_error=pl.mean(),prepost=np.mean(pres[h]) if h in pres else np.nan,length_difference=np.mean(difflen[h]),frequency_bin_difference=np.mean(difffreq[h]))
            row.update({f'd{z+1}':float(q) for z,q in enumerate(c)});rows.append(row)
        diagnostic.append(dict(user=user,eligible_events=int(evmask.sum()),matched_events=sum(counts.values()),eligible_controls=int(plmask.sum()),cross_half_token_overlap=0))
    return pd.DataFrame(rows),pd.DataFrame(diagnostic)

def interval_mean(a,seed=SEED):
    a=np.asarray(a);a=a[np.isfinite(a)];rng=np.random.default_rng(seed)
    vals=[np.mean(a[rng.integers(0,len(a),len(a))]) for _ in range(BOOT)]
    return [float(np.mean(a)),*np.quantile(vals,[.025,.975]).tolist()]

def reliability(df,track,kind):
    out=[]
    eligible=df[df.n_events>=5]
    for axis in ['auc','depth']:
        z=eligible.pivot(index='user',columns='half',values=axis).dropna()
        if z.shape[1]!=2 or len(z)<3: continue
        a=z.to_numpy();r=float(spearmanr(a[:,0],a[:,1]).statistic)
        rng=np.random.default_rng(SEED);boot=[]
        for _ in range(BOOT):
            b=a[rng.integers(0,len(a),len(a))];rr=spearmanr(b[:,0],b[:,1]).statistic
            boot.append(rr)
        lo,hi=np.nanquantile(boot,[.025,.975]);sb=lambda q:2*q/(1+q)
        out.append(dict(track=track,split=kind,axis=axis,n=len(a),r=r,r_lo=lo,r_hi=hi,sb=sb(r),sb_lo=sb(lo),sb_hi=sb(hi)))
    return out

def outcomes(groups,cut):
    out=[]
    for u,g,x in groups:
        early=g[g.days<=cut];late=g[g.days>cut]
        if len(late)==0 or len(early)==0: continue
        a=x[x.days>cut];acc=1-a.errors/a.n
        slope=np.polyfit(a.days,acc,1)[0] if len(a)>=10 and a.days.nunique()>=3 else np.nan
        out.append(dict(user=u,early_acc=1-early.error.mean(),n_early=len(early),out_acc=1-late.error.mean(),n_out=len(late),out_slope=slope))
    return pd.DataFrame(out)

def regress(df,scope,cut,axis,outcome,controls):
    cols=[outcome,axis,'base_acc','n_out','n_early','early_acc']
    d=df.dropna(subset=cols).copy();n=len(d)
    if n<20:return {}
    xs=[d.base_acc.to_numpy()]
    if controls=='original':xs.append(np.log(d.n_out.to_numpy()))
    else:xs.extend([d.early_acc.to_numpy(),np.log(d.n_early.to_numpy())])
    if d.track.nunique()>1:xs.extend([(d.track==t).to_numpy(float) for t in sorted(d.track.unique())[1:]])
    C=np.column_stack([np.ones(n)]+xs); X=np.column_stack([C,d[axis].to_numpy()]);y=d[outcome].to_numpy()
    def fit(c,x,y):
        b=np.linalg.lstsq(x,y,rcond=None)[0];bc=np.linalg.lstsq(c,y,rcond=None)[0]
        beta=b[-1]*x[:,-1].std(ddof=1)/y.std(ddof=1)
        delta=(((y-c@bc)**2).sum()-((y-x@b)**2).sum())/((y-y.mean())**2).sum()
        return beta,delta
    beta,delta=fit(C,X,y);rng=np.random.default_rng(SEED);bs=[]
    for _ in range(BOOT):
        ix=rng.integers(0,n,n);bs.append(fit(C[ix],X[ix],y[ix])[0])
    lo,hi=np.quantile(bs,[.025,.975])
    # Fixed five folds, balanced across tracks; all rows are distinct track-user pairs.
    folds=np.empty(n,dtype=int)
    for tr in d.track.unique():
        ix=np.flatnonzero((d.track==tr).to_numpy());rng.shuffle(ix);folds[ix]=np.arange(len(ix))%5
    p0=np.empty(n);p1=np.empty(n)
    for f in range(5):
        train=folds!=f;test=~train
        p0[test]=C[test]@np.linalg.lstsq(C[train],y[train],rcond=None)[0]
        p1[test]=X[test]@np.linalg.lstsq(X[train],y[train],rcond=None)[0]
    den=((y-y.mean())**2).sum();r0=1-((y-p0)**2).sum()/den;r1=1-((y-p1)**2).sum()/den
    return dict(scope=scope,cut=cut,axis=axis,outcome=outcome,controls=controls,n=n,beta=beta,lo=lo,hi=hi,delta_r2=delta,cv_r2_base=r0,cv_r2_full=r1,cv_delta_r2=r1-r0)

def main(track):
    groups,meta=load(track);print('loaded',meta,flush=True)
    main,diag=estimate(groups,track);main.to_csv(OUT/f'{track}_axes.csv',index=False);diag.to_csv(OUT/f'{track}_matching.csv',index=False)
    summary=dict(meta,matched_users=len(main),eligible_events=int(diag.eligible_events.sum()),matched_events=int(diag.matched_events.sum()),auc=interval_mean(main.auc),depth=interval_mean(main.depth),prepost=interval_mean(main.prepost),max_abs_user_length_difference=float(main.length_difference.abs().max()))
    json.dump(summary,open(OUT/f'{track}_summary.json','w'),indent=2)
    print('main',summary,flush=True)
    rel=[]
    for split,block in [('block',100),('temporal',100),('block',60),('block',200)]:
        tab,dg=estimate(groups,track,split=split,block=block)
        name=f'{split}{block}' if split=='block' else split
        tab.to_csv(OUT/f'{track}_{name}_halves.csv',index=False)
        rr=reliability(tab,track,name);rel.extend(rr);print('reliability',rr,flush=True)
    pd.DataFrame(rel).to_csv(OUT/f'{track}_reliability.csv',index=False)
    sens=[]
    for w,k in [(10,2),(30,2),(20,3)]:
        tab,dg=estimate(groups,track,window=w,k=k)
        for axis in ['auc','depth']:
            m,l,h=interval_mean(tab[axis]);sens.append(dict(track=track,window=w,k=k,axis=axis,n=len(tab),mean=m,lo=l,hi=h,events=int(dg.matched_events.sum())))
    pd.DataFrame(sens).to_csv(OUT/f'{track}_sensitivity.csv',index=False)
    for cut in [10,12]:
        tab,dg=estimate(groups,track,cut=cut)
        tab=tab.merge(outcomes(groups,cut),on='user',validate='one_to_one');tab['base_acc']=1-tab.placebo_error
        tab['included']=(tab.n_events>=10)&(tab.n_out>=50)
        tab.to_csv(OUT/f'{track}_prediction_cut{cut}.csv',index=False)
    print('DONE',track,flush=True)

def combine():
    rows=[]
    for cut in [10,12]:
        d=pd.concat([pd.read_csv(OUT/f'{t}_prediction_cut{cut}.csv') for t in ['en_es','es_en','fr_en']],ignore_index=True);d=d[d.included]
        for scope in ['pooled','en_es','es_en','fr_en']:
            s=d if scope=='pooled' else d[d.track==scope]
            for axis in ['auc','depth']:
                for outcome in ['out_acc','out_slope']:
                    for controls in ['original','early_strict']:
                        rows.append(regress(s,scope,cut,axis,outcome,controls))
            print('regression complete',cut,scope,flush=True)
    pd.DataFrame(rows).to_csv(OUT/'prediction_models.csv',index=False)
    pd.concat([pd.read_csv(OUT/f'{t}_reliability.csv') for t in ['en_es','es_en','fr_en']]).to_csv(OUT/'reliability.csv',index=False)
    manifest={'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,'seed':SEED,'bootstrap':BOOT,'source_hashes':{}}
    for p in sorted(DER.glob('*.parquet')):
        if 'smoke' not in p.name:manifest['source_hashes'][p.name]=hashlib.sha256(p.read_bytes()).hexdigest()
    manifest['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    json.dump(manifest,open(OUT/'manifest.json','w'),indent=2)

def predict_only(track):
    groups,_=load(track)
    for cut in [10,12]:
        tab,dg=estimate(groups,track,cut=cut)
        tab=tab.merge(outcomes(groups,cut),on='user',validate='one_to_one');tab['base_acc']=1-tab.placebo_error
        tab['included']=(tab.n_events>=10)&(tab.n_out>=50)
        tab.to_csv(OUT/f'{track}_prediction_cut{cut}.csv',index=False)
    print('prediction rebuilt using early-only token frequencies',track,flush=True)

if __name__=='__main__':
    if sys.argv[1]=='combine':combine()
    elif sys.argv[1]=='predict':predict_only(sys.argv[2])
    else:main(sys.argv[1])
