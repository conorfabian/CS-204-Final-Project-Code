from pathlib import Path

YOUTUBE_VIDEO_URL = "https://www.youtube.com/watch?v=KLlXCFG5TnA"
TOTAL_DURATION = 135

CHROME_DEBUGGING_PORT = 9222
CHROME_OPTIONS = [
    "--no-sandbox",
    "--disable-dev-shm-usage"
]

POLLING_INTERVAL = 1.5
MIN_EVENT_SPACING = 15

BITRATE_MAP = {
    (426, 240): 400,
    (640, 360): 800,
    (854, 480): 1200,
    (1280, 720): 2500,
    (1920, 1080): 4500
}

BUFFER_MILESTONES = [5, 10, 15, 20, 25, 30]

PHASE1_BANDWIDTH_KBPS = 20000
PHASE2_BANDWIDTH_KBPS = 1500
PHASE3_BANDWIDTH_KBPS = 20000
LATENCY_MS = 40

PHASE1_DURATION = 45
PHASE2_DURATION = 45
PHASE3_DURATION = 45

def get_trial_dir(trial_num):
    return Path(f'data/raw/trial_{trial_num}')

def get_test_dir():
    return Path('data/raw/trial_test')
