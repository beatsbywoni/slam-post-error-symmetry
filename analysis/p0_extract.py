"""P0 — Re-extract SLAM train partitions into pickled token/exercise streams.

Mirrors 03_analysis/c1_01_extract.py (same parsing rules) so that token counts,
user counts and pos_idx match the archived derived parquet files. Output format
is pickle (pyarrow is unavailable in this environment). Also stores the
exercise-level `time` field (response time, seconds; may be null) and the
per-token surface/POS/morphology needed for difficulty adjustment.
"""
import sys, tarfile, io, hashlib, json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = Path('/mnt/user-data/uploads/_shared_data/slam')
DATA = ROOT / 'data'
STAMP = '20190204'
EXPECTED = json.load(open(RAW.parent.parent / 'c1_recall_error_recovery/09_acp_theory_revision/outputs/manifest.json')) if False else None


def parse_track(track):
    path = RAW / f'data_{track}.tar.gz'
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    tf = tarfile.open(path, 'r:gz')
    member = next(m for m in tf.getmembers() if m.name == f'{track}.slam.{STAMP}.train')
    f = io.TextIOWrapper(tf.extractfile(member), encoding='utf-8')
    tok_rows, ex_rows = [], []
    ex_id = -1
    user = days = fmt = session = client = rt = None
    for line in f:
        if line.startswith('# user:'):
            ex_id += 1
            meta = dict(p.split(':', 1) for p in line[2:].split() if ':' in p)
            user = meta['user']
            days = float(meta.get('days', 'nan'))
            fmt = meta.get('format', '')
            session = meta.get('session', '')
            client = meta.get('client', '')
            t = meta.get('time')
            rt = None if t in (None, 'null') else int(t)
            ex_rows.append((ex_id, user, days, fmt, session, client, rt))
        elif line.startswith('#'):
            continue
        else:
            cols = line.split()
            if len(cols) >= 3 and cols[-1] in ('0', '1'):
                # token_id surface POS morph dep head label
                tok_rows.append((ex_id, user, cols[1].lower(), cols[2], cols[3] if len(cols) > 3 else '', int(cols[-1])))
    tok = pd.DataFrame(tok_rows, columns=['ex_id', 'user', 'token', 'pos', 'morph', 'error'])
    ex = pd.DataFrame(ex_rows, columns=['ex_id', 'user', 'days', 'format', 'session', 'client', 'rt'])
    tok['pos_idx'] = tok.groupby('user').cumcount()
    freq = tok['token'].value_counts()
    tok['token_freq'] = tok['token'].map(freq)
    return tok, ex, sha


if __name__ == '__main__':
    out = {}
    for track in sys.argv[1:] or ['en_es', 'es_en', 'fr_en']:
        tok, ex, sha = parse_track(track)
        tok.to_pickle(DATA / f'{track}_tokens.pkl')
        ex.to_pickle(DATA / f'{track}_exercises.pkl')
        out[track] = dict(sha256=sha, tokens=len(tok), exercises=len(ex), users=int(tok.user.nunique()), err_rate=float(tok.error.mean()))
        print(track, out[track], flush=True)
    json.dump(out, open(ROOT / 'outputs' / 'p0_extract_summary.json', 'w'), indent=2)
