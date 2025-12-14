import pandas as pd
import sys
from pathlib import Path

def process_trial(trial_num):
    raw_dir = Path(f'data/raw/trial_{trial_num}')
    proc_dir = Path(f'data/processed/trial_{trial_num}')
    proc_dir.mkdir(parents=True, exist_ok=True)

    quality = pd.read_csv(raw_dir / 'quality_timeline.csv')
    buffer = pd.read_csv(raw_dir / 'buffer_timeline.csv')

    timeline = pd.DataFrame({'time_seconds': range(0, 136)})

    timeline = timeline.merge(
        quality[['time_seconds', 'resolution_width', 'resolution_height', 'bitrate_kbps']],
        on='time_seconds', how='left'
    )
    timeline[['resolution_width', 'resolution_height', 'bitrate_kbps']] = \
        timeline[['resolution_width', 'resolution_height', 'bitrate_kbps']].ffill()

    timeline = timeline.merge(
        buffer[['time_seconds', 'buffer_seconds']],
        on='time_seconds', how='left'
    )
    timeline['buffer_seconds'] = timeline['buffer_seconds'].interpolate()

    timeline['network_phase'] = 'phase1_high'
    timeline.loc[(timeline['time_seconds'] >= 45) & (timeline['time_seconds'] < 90), 'network_phase'] = 'phase2_low'
    timeline.loc[timeline['time_seconds'] >= 90, 'network_phase'] = 'phase3_high'

    timeline['network_bandwidth_mbps'] = 20.0
    timeline.loc[(timeline['time_seconds'] >= 45) & (timeline['time_seconds'] < 90), 'network_bandwidth_mbps'] = 1.5

    timeline.to_csv(proc_dir / 'unified_timeline.csv', index=False)
    print(f"Processed trial {trial_num}")

if __name__ == "__main__":
    process_trial(sys.argv[1])
