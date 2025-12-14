import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from plot_config import *

def plot_metrics_comparison():
    df = pd.read_csv('data/processed/metrics_summary.csv')

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    axes[0, 0].bar(df['trial'], df['avg_bitrate_kbps'], color=COLORS['quality'])
    axes[0, 0].set_ylabel('Average Bitrate (kbps)')
    axes[0, 0].set_title('Average Video Bitrate')

    axes[0, 1].bar(df['trial'], df['quality_switches'], color=COLORS['network'])
    axes[0, 1].set_ylabel('Number of Switches')
    axes[0, 1].set_title('Quality Switches')

    axes[1, 0].bar(df['trial'], df['avg_buffer_seconds'], color=COLORS['buffer'])
    axes[1, 0].set_ylabel('Average Buffer (seconds)')
    axes[1, 0].set_title('Average Buffer Level')

    # find columns with quality time percentages
    quality_cols = []
    for col in df.columns:
        if 'time_at_' in col:
            quality_cols.append(col)

    if len(quality_cols) > 0:
        quality_data = df[['trial'] + quality_cols].set_index('trial')
        # rename columns to be shorter
        new_names = []
        for col in quality_data.columns:
            name = col.replace('time_at_', '')
            name = name.replace('p_percent', 'p')
            new_names.append(name)
        quality_data.columns = new_names
        quality_data.plot(kind='bar', stacked=True, ax=axes[1, 1])
        axes[1, 1].set_ylabel('Percentage (%)')
        axes[1, 1].set_title('Time at Each Quality')
        axes[1, 1].legend(title='Resolution', loc='upper right')

    save_figure(fig, 'metrics_comparison.png')
    plt.close()

def plot_bitrate_overlay():
    proc_dir = Path('data/processed')
    # get trial directories
    trial_dirs = []
    for d in proc_dir.iterdir():
        if d.is_dir() and d.name.startswith('trial_'):
            trial_dirs.append(d)
    trial_dirs = sorted(trial_dirs)

    fig, ax = plt.subplots(figsize=FIGURE_SIZE_WIDE)

    for trial_dir in trial_dirs:
        trial_num = trial_dir.name.split('_')[1]
        df = pd.read_csv(trial_dir / 'unified_timeline.csv')
        ax.plot(df['time_seconds'], df['bitrate_kbps'] / 1000, label=f'Trial {trial_num}', linewidth=2, alpha=0.7)

    ax.axvline(x=45, color='red', linestyle='--', alpha=0.5)
    ax.axvline(x=90, color='green', linestyle='--', alpha=0.5)
    ax.set_xlabel('Time (seconds)')
    ax.set_ylabel('Bitrate (Mbps)')
    ax.set_title('Bitrate Comparison')
    ax.legend()
    ax.grid(True, alpha=0.3)

    format_time_axis(ax)
    save_figure(fig, 'bitrate_overlay.png')
    plt.close()

if __name__ == "__main__":
    Path('figures').mkdir(exist_ok=True)
    plot_metrics_comparison()
    plot_bitrate_overlay()
