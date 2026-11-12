"""P3 — Figures for the Brief Report (planned matching; 170 mm wide; readable in greyscale via line style/marker)."""
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]; OUT = ROOT / 'outputs'; MS = ROOT / 'manuscript'
TRACKS = ['en_es', 'es_en', 'fr_en']
LABEL = {'en_es': 'English course (Spanish speakers)', 'es_en': 'Spanish course (English speakers)', 'fr_en': 'French course (English speakers)'}
RAW, ADJ = '#2f6db5', '#d1701c'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.edgecolor': '#666', 'axes.labelcolor': '#222', 'xtick.color': '#444', 'ytick.color': '#444'})


def row():
    fig, axes = plt.subplots(1, 3, figsize=(6.69, 2.75), sharey=True, sharex=True)
    for ax in axes[1:]: ax.tick_params(labelleft=False)
    fig.subplots_adjust(left=0.09, right=0.985, top=0.90, bottom=0.19, wspace=0.16)
    return fig, axes


def fig1():
    fig, axes = row()
    for ax, t in zip(axes, TRACKS):
        P = pd.read_csv(OUT / f'{t}_primary_profile.csv')
        for series, col, ls, lab in [('excess_raw', RAW, '-', 'Raw'), ('excess_adj', ADJ, '--', 'Item-difficulty adjusted')]:
            d = P[P.series == series].sort_values('position')
            for side in [d[d.position < 0], d[d.position > 0]]:
                ax.fill_between(side.position, side.lo_pp, side.hi_pp, color=col, alpha=.15, lw=0)
                ax.plot(side.position, side.mean_pp, color=col, ls=ls, lw=1.5, label=lab if side.position.min() < 0 else None)
        ax.axhline(0, color='#999', lw=.8); ax.axvspan(-0.5, 0.5, color='#ddd', lw=0)
        ax.text(0, -1.4, 'cluster\nexercise', ha='center', va='bottom', fontsize=6.5, color='#555')
        ax.set_title(LABEL[t], fontsize=7.8); ax.set_xticks([-20, -10, 10, 20]); ax.set_xlim(-20.5, 20.5); ax.set_ylim(-1.5, 6)
    axes[0].set_ylabel('Excess error, cluster minus\nmatched comparison (pp)')
    axes[0].legend(frameon=False, loc='upper left', fontsize=7.5)
    fig.supxlabel('Token position relative to the error-cluster exercise (−20…−1 before, +1…+20 after)', fontsize=8.5, y=0.02)
    fig.savefig(MS / 'Figure_1.png', dpi=600); fig.savefig(MS / 'Figure_1.pdf'); plt.close(fig)


def fig2():
    fig, axes = row(); doses = ['2', '3', '4+']; x = np.arange(3)
    for ax, t in zip(axes, TRACKS):
        d = pd.read_csv(OUT / f'{t}_primary_summary.csv'); d = d[d.analysis == 'dose'].set_index('quantity')
        for off, w, col, mk, lab in [(-.12, 'pre_ex', RAW, 'o', 'Before cluster (−20…−1)'), (.12, 'post_ex', ADJ, 's', 'After cluster (+1…+20)')]:
            m = [d.loc[f'{w}__{k}', 'mean_pp'] for k in doses]; lo = [d.loc[f'{w}__{k}', 'lo_pp'] for k in doses]; hi = [d.loc[f'{w}__{k}', 'hi_pp'] for k in doses]
            ax.errorbar(x + off, m, yerr=[np.subtract(m, lo), np.subtract(hi, m)], fmt=mk, color=col, ms=4.5, capsize=2, lw=1.1, label=lab)
        ax.axhline(0, color='#999', lw=.8); ax.set_xticks(x); ax.set_xticklabels(doses); ax.set_xlim(-0.5, 2.5); ax.set_ylim(-1, 5.4)
        ax.set_title(LABEL[t], fontsize=7.8)
    axes[0].set_ylabel('Excess error (pp)'); axes[0].legend(frameon=False, fontsize=7.5, loc='upper left')
    fig.supxlabel('Errors in the cluster exercise', fontsize=8.5, y=0.02)
    fig.savefig(MS / 'Figure_2.png', dpi=600); fig.savefig(MS / 'Figure_2.pdf'); plt.close(fig)


if __name__ == '__main__':
    fig1(); fig2(); print('figures written')
