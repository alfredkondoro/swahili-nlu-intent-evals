"""Evaluation, visualisation and LaTeX generation utilities for SwahiliNLU."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def per_domain_pivot(domain_results, test_df, task='Intent'):
    """
    Build a model × domain Macro-F1 pivot table.

    Args:
        domain_results: list of per-domain result dicts from train_classifier
        test_df:        test split DataFrame
        task:           'Intent' or 'Tone'

    Returns:
        DataFrame with domains as rows, models + test_n as columns
    """
    df   = pd.DataFrame([r for r in domain_results if r['task'] == task])
    piv  = df.pivot_table(index='domain', columns='model', values='macro_f1').round(4)
    sizes = (test_df['source_file']
             .str.replace('.csv', '', regex=False)
             .str.replace('_', ' ').str.title()
             .value_counts().rename('test_n'))
    return piv.join(sizes).sort_values('test_n', ascending=False)


def plot_per_domain(pivot, title='Per-Domain Macro-F1'):
    """Bar chart of per-domain Macro-F1 for each model."""
    models = [m for m in ['mBERT', 'XLM-R', 'AfroXLMR'] if m in pivot.columns]
    colors = ['#534AB7', '#1D9E75', '#E8593C']
    x      = np.arange(len(pivot))
    width  = 0.25

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, (m, c) in enumerate(zip(models, colors)):
        ax.bar(x + i * width, pivot[m], width, label=m,
               color=c, alpha=0.85, edgecolor='white')

    ax.set_xticks(x + width)
    ax.set_xticklabels(pivot.index, rotation=35, ha='right', fontsize=9)
    ax.set_ylabel('Macro-F1')
    ax.set_ylim(0, 1.0)
    ax.set_title(title, fontweight='bold')
    ax.legend()
    plt.tight_layout()
    plt.show()
    plt.close(fig)


def plot_summary(all_results):
    """Three-panel summary chart: Intent, Tone, Slot Filling."""
    tasks   = ['Intent', 'Tone', 'Slot Filling']
    metrics = ['macro_f1', 'macro_f1', 'slot_f1']
    colors  = ['#534AB7', '#1D9E75', '#E8593C']

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    for ax, task, met, col in zip(axes, tasks, metrics, colors):
        sub = all_results[all_results['task'] == task].copy()
        if met not in sub.columns:
            continue
        sub[met] = pd.to_numeric(sub[met], errors='coerce')
        sub = sub.dropna(subset=[met])
        bars = ax.bar(sub['model'], sub[met], color=col, alpha=0.85, edgecolor='white')
        for bar, val in zip(bars, sub[met]):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.005,
                    f'{val:.3f}', ha='center', va='bottom', fontsize=8)
        ax.set_title(task, fontweight='bold')
        ax.set_ylim(0, 1.05)
        ax.set_ylabel('Score')
        ax.tick_params(axis='x', rotation=25)

    plt.suptitle('SwahiliNLU Baseline Results', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.show()
    plt.close(fig)


def build_latex_tables(all_results, slot_results):
    """
    Generate LaTeX source for Table 3 (classification) and Table 4 (slots).

    Returns:
        tuple (table3_str, table4_str)
    """
    clf    = all_results[all_results['task'].isin(['Intent', 'Tone'])]
    ft     = clf[clf['model'].isin(['mBERT', 'XLM-R', 'AfroXLMR'])]
    zs     = clf[~clf['model'].isin(['mBERT', 'XLM-R', 'AfroXLMR'])]
    best_i = ft[ft['task'] == 'Intent']['macro_f1'].max()
    best_t = ft[ft['task'] == 'Tone']['macro_f1'].max()
    best_zi = zs[zs['task'] == 'Intent']['macro_f1'].max()
    best_zt = zs[zs['task'] == 'Tone']['macro_f1'].max()

    def bold(val, best):
        return f'\\textbf{{{val}}}' if str(val) == str(best) else str(val)

    lines3 = [
        '\\begin{table}[t]',
        '\\caption{Classification results. Bold~=~best per task per category.}',
        '\\label{tab:clf}\\setlength{\\tabcolsep}{3pt}\\small',
        '\\begin{tabular}{llccc}\\toprule',
        '\\textbf{Model} & \\textbf{Task} & \\textbf{Acc.} & '
        '\\textbf{Mac-F1} & \\textbf{Wt-F1} \\\\',
        '\\midrule\\multicolumn{5}{l}{\\textit{Fine-tuned models}} \\\\'
    ]
    for _, r in ft.iterrows():
        b = best_i if r['task'] == 'Intent' else best_t
        lines3.append(
            f"  {r['model']} & {r['task']} & {r['accuracy']} & "
            f"{bold(r['macro_f1'], b)} & {r['weighted_f1']} \\\\"
        )
    lines3 += ['\\midrule\\multicolumn{5}{l}{\\textit{Zero-shot LLMs}} \\\\']
    for _, r in zs.iterrows():
        b = best_zi if r['task'] == 'Intent' else best_zt
        lines3.append(
            f"  {r['model']} & {r['task']} & {r['accuracy']} & "
            f"{bold(r['macro_f1'], b)} & --- \\\\"
        )
    lines3 += ['\\bottomrule\\end{tabular}\\end{table}']

    sdf    = pd.DataFrame(slot_results)
    best_s = sdf['slot_f1'].max()
    lines4 = [
        '\\begin{table}[t]',
        '\\caption{Slot filling results (seqeval Macro-F1).}',
        '\\label{tab:slots}\\small',
        '\\begin{tabular}{lc}\\toprule',
        '\\textbf{Model} & \\textbf{Slot F1} \\\\',
        '\\midrule'
    ]
    for _, r in sdf.iterrows():
        b = '\\textbf{' if r['slot_f1'] == best_s else ''
        e = '}'         if r['slot_f1'] == best_s else ''
        lines4.append(f'  {b}{r["model"]}{e} & {b}{r["slot_f1"]}{e} \\\\')
    lines4 += ['\\bottomrule\\end{tabular}\\end{table}']

    return '\n'.join(lines3), '\n'.join(lines4)
