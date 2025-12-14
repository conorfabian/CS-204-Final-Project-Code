# YouTube Adaptive Bitrate Streaming Analysis

**CS 204 Final Project - Conor Fabian**

## Overview

This project analyzes YouTube's adaptive bitrate (ABR) algorithm under controlled network stress. We run YouTube playback through a 135-second network trace (20 Mbps → 1.5 Mbps → 20 Mbps) and collect telemetry from Chrome DevTools to observe quality switches, buffer behavior, and adaptation timing. Key findings: YouTube takes 5-13 seconds to respond to bandwidth drops, triggers quality switches when buffer falls below ~20 seconds, and avoids rebuffering through conservative buffer management.

## How to Run

**Prerequisites:** macOS with Chrome installed, Python 3.7+

**Setup:**
```bash
pip install -r requirements.txt
```

**Run a trial (automated):**
```bash
# 1. Launch Chrome with debugging enabled
./scripts/collection/launch_chrome.sh

# 2. In the browser, navigate to the YouTube video and start playback
#    (The script will connect to this running Chrome instance)

# 3. Run data collection with network shaping (135 seconds)
python scripts/collection/auto_collect.py --trial 001 --with-shaping

# 4. Process the raw data
python scripts/analysis/process_trial.py 001

# 5. Generate timeline plot
python scripts/visualization/plot_timeline.py 001
```

**Reproduce full analysis (all 5 trials):**
```bash
# After collecting all trials (001-005), compute metrics and create comparison plots
python scripts/analysis/calculate_metrics.py
python scripts/visualization/plot_comparison.py
```

**Output:** Raw CSVs in `data/raw/`, processed timelines in `data/processed/`, figures in `figures/`

## Deliverables

- **Scripts:** Network control, data collection, analysis, visualization
- **Dataset:** 5 trials with quality/buffer timelines (raw + processed)
- **Figures:** Per-trial timelines, cross-trial comparison dashboard
- **Documentation:** Project proposal, observations, metrics summary
