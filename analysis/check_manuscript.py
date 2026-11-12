"""Check word counts and that every 'x [lo, hi]' triple in the manuscript matches an output CSV."""
import re, sys, glob, pandas as pd
f = sys.argv[1]; s = open(f).read()
def sec(a, b): return s[s.index(f'## {a}'):s.index(f'## {b}')]
def wc(t): return len(re.sub(r'^#.*$', '', t, flags=re.M).split())
parts = [('Abstract','Significance statement'),('Significance statement','Keywords'),('Introduction','Method'),('Method','Results'),('Results','Discussion'),('Discussion','List of abbreviations')]
for a,b in parts: print(a, wc(sec(a,b)))
print('MAIN BODY', sum(wc(sec(a,b)) for a,b in parts[2:]), '| incl. headings', sum(len(sec(a,b).replace('#','').split()) for a,b in parts[2:]))
S = pd.concat([pd.read_csv(x) for x in glob.glob('outputs/*_summary.csv')])
trip = set()
for _, r in S.iterrows():
    for d in (2, 0): trip.add((round(r.mean_pp, d), round(r.lo_pp, d), round(r.hi_pp, d)))
txt = s.replace('−', '-').replace('%', '')
found = re.findall(r'(-?\d+\.?\d*) \[(-?\d+\.?\d*), (-?\d+\.?\d*)\]', txt)
bad = [x for x in found if (float(x[0]), float(x[1]), float(x[2])) not in trip]
print(len(found), 'triples;', len(bad), 'unmatched:', bad)
if bad: raise SystemExit(1)
print('em-dashes:', s.count('—'), '| " we ":', len(re.findall(r'\b[Ww]e\b', s)))
