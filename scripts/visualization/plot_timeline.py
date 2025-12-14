import pandas as pd
import matplotlib.pyplot as plt
import sys
from pathlib import Path
from plot_config import *

def plot_trial_timeline(trial_num):
    df = pd.read_csv(f'data/processed/trial_{trial_num}/unified_timeline.csv')

    fig, axes = plt.subplots(2, 1, figsize=FIGURE_SIZE, sharex=True)

    ax1 = axes[0]
    ax1.plot(df['time_seconds'], df['bitrate_kbps'] / 1000, linewidth=2, color=COLORS['quality'])
    ax1.axvline(x=45, color=COLORS['phase_marker'], linestyle='--', alpha=0.6)
    ax1.axvline(x=90, color=COLORS['recovery'], linestyle='--', alpha=0.6)
    ax1.set_ylabel('Bitrate (Mbps)')
    ax1.set_title(f'Trial {trial_num}: Quality and Buffer')
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    ax2.plot(df['time_seconds'], df['buffer_seconds'], linewidth=2, color=COLORS['buffer'])
    ax2.axvline(x=45, color=COLORS['phase_marker'], linestyle='--', alpha=0.6)
    ax2.axvline(x=90, color=COLORS['recovery'], linestyle='--', alpha=0.6)
    ax2.set_ylabel('Buffer (seconds)')
    ax2.set_xlabel('Time (seconds)')
    ax2.grid(True, alpha=0.3)

    format_time_axis(ax2)
    save_figure(fig, f'trial_{trial_num}_timeline.png')
    plt.close()

if __name__ == "__main__":
    Path('figures').mkdir(exist_ok=True)
    plot_trial_timeline(sys.argv[1])
