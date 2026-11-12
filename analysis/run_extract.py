"""Portable entry point for extraction. Leaves the frozen p0_extract.py untouched (its hash is in outputs/plan_freeze.json)
and only redirects its input and output folders.
Usage: python3 analysis/run_extract.py --raw-dir /path/to/folder/with/data_{en_es,es_en,fr_en}.tar.gz [--data-dir data]"""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p0_extract as p0
ap = argparse.ArgumentParser(); ap.add_argument('--raw-dir', required=True); ap.add_argument('--data-dir', default=str(p0.ROOT / 'data'))
ap.add_argument('--tracks', nargs='*', default=['en_es', 'es_en', 'fr_en']); a = ap.parse_args()
p0.RAW = Path(a.raw_dir); p0.DATA = Path(a.data_dir); p0.DATA.mkdir(parents=True, exist_ok=True); (p0.ROOT / 'outputs').mkdir(exist_ok=True)
out = {}
for t in a.tracks:
    tok, ex, sha = p0.parse_track(t); tok.to_pickle(p0.DATA / f'{t}_tokens.pkl'); ex.to_pickle(p0.DATA / f'{t}_exercises.pkl')
    out[t] = dict(sha256=sha, tokens=len(tok), exercises=len(ex), users=int(tok.user.nunique()), err_rate=float(tok.error.mean())); print(t, out[t], flush=True)
json.dump(out, open(p0.ROOT / 'outputs' / 'p0_extract_summary.json', 'w'), indent=2)
