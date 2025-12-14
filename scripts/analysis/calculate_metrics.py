import pandas as pd
from pathlib import Path

def calculate_trial_metrics(trial_num):
    unified_file = Path(f'data/processed/trial_{trial_num}/unified_timeline.csv')
    if not unified_file.exists():
        return None

    df = pd.read_csv(unified_file)
    metrics = {'trial': trial_num, 'duration_seconds': len(df)}

    if 'bitrate_kbps' in df.columns:
        metrics['avg_bitrate_kbps'] = df['bitrate_kbps'].mean()
        metrics['max_bitrate_kbps'] = df['bitrate_kbps'].max()
        metrics['min_bitrate_kbps'] = df['bitrate_kbps'].min()
        metrics['stddev_bitrate_kbps'] = df['bitrate_kbps'].std()
        # count quality switches
        switches = 0
        prev_bitrate = df['bitrate_kbps'].iloc[0]
        for i in range(1, len(df)):
            if df['bitrate_kbps'].iloc[i] != prev_bitrate:
                switches += 1
                prev_bitrate = df['bitrate_kbps'].iloc[i]
        metrics['quality_switches'] = switches

    if 'buffer_seconds' in df.columns:
        metrics['avg_buffer_seconds'] = df['buffer_seconds'].mean()
        metrics['min_buffer_seconds'] = df['buffer_seconds'].min()
        metrics['max_buffer_seconds'] = df['buffer_seconds'].max()
        metrics['buffer_empty_count'] = (df['buffer_seconds'] <= 0).sum()

    if 'resolution_height' in df.columns:
        for height in [360, 480, 720, 1080]:
            metrics[f'time_at_{height}p_percent'] = round((df['resolution_height'] == height).sum() / len(df) * 100, 2)

    # phase 1: 0-45s
    phase1_df = df[(df['time_seconds'] >= 0) & (df['time_seconds'] < 45)]
    if 'bitrate_kbps' in phase1_df.columns:
        metrics['phase1_avg_bitrate'] = phase1_df['bitrate_kbps'].mean()
    if 'buffer_seconds' in phase1_df.columns:
        metrics['phase1_avg_buffer'] = phase1_df['buffer_seconds'].mean()

    # phase 2: 45-90s
    phase2_df = df[(df['time_seconds'] >= 45) & (df['time_seconds'] < 90)]
    if 'bitrate_kbps' in phase2_df.columns:
        metrics['phase2_avg_bitrate'] = phase2_df['bitrate_kbps'].mean()
    if 'buffer_seconds' in phase2_df.columns:
        metrics['phase2_avg_buffer'] = phase2_df['buffer_seconds'].mean()

    # phase 3: 90-136s
    phase3_df = df[(df['time_seconds'] >= 90) & (df['time_seconds'] < 136)]
    if 'bitrate_kbps' in phase3_df.columns:
        metrics['phase3_avg_bitrate'] = phase3_df['bitrate_kbps'].mean()
    if 'buffer_seconds' in phase3_df.columns:
        metrics['phase3_avg_buffer'] = phase3_df['buffer_seconds'].mean()

    return metrics

def calculate_all_trials():
    proc_dir = Path('data/processed')
    trial_dirs = sorted([d for d in proc_dir.iterdir() if d.is_dir() and d.name.startswith('trial_')])

    all_metrics = []
    for trial_dir in trial_dirs:
        trial_num = trial_dir.name.split('_')[1]
        metrics = calculate_trial_metrics(trial_num)
        if metrics:
            all_metrics.append(metrics)

    summary = pd.DataFrame(all_metrics)
    summary.to_csv(proc_dir / 'metrics_summary.csv', index=False)
    print(summary[['trial', 'avg_bitrate_kbps', 'quality_switches', 'avg_buffer_seconds']].to_string(index=False))

if __name__ == "__main__":
    calculate_all_trials()
