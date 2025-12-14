import time
import sys
import csv
import socket
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from collector_config import *

class VideoDataCollector:
    def __init__(self, trial_num, duration, is_test=False):
        self.trial_num = trial_num
        self.duration = duration
        self.is_test = is_test

        if is_test:
            self.output_dir = get_test_dir()
        else:
            self.output_dir = get_trial_dir(trial_num)

        self.driver = None
        self.quality_events = []
        self.buffer_events = []

        self.last_width = None
        self.last_height = None
        self.last_buffer_milestone = -1
        self.last_forced_record = -1

    def verify_chrome_connection(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', CHROME_DEBUGGING_PORT))
        sock.close()
        return result == 0

    def connect_to_chrome(self):
        print(f"Connecting to Chrome on port {CHROME_DEBUGGING_PORT}...")

        if not self.verify_chrome_connection():
            print(f"Error: Cannot connect to Chrome on port {CHROME_DEBUGGING_PORT}")
            print("Please run: ./scripts/collection/launch_chrome.sh")
            return False

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_DEBUGGING_PORT}")
        for opt in CHROME_OPTIONS:
            chrome_options.add_argument(opt)

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            print("Connected successfully")
            return True
        except WebDriverException as e:
            print(f"Error connecting to Chrome: {e}")
            return False

    def wait_for_video(self, retries=3):
        print("Loading YouTube video...")
        self.driver.get(YOUTUBE_VIDEO_URL)

        for attempt in range(retries):
            time.sleep(3)
            js_code = "return document.querySelector('video') !== null;"
            if self.driver.execute_script(js_code):
                width = self.driver.execute_script("return document.querySelector('video').videoWidth;")
                height = self.driver.execute_script("return document.querySelector('video').videoHeight;")
                if width > 0 and height > 0:
                    print(f"Video loaded: {width}x{height}")
                    return True

        print("Error: Video failed to load after 3 retries")
        return False

    def click_play_button(self):
        js_code = """
        const video = document.querySelector('video');
        if (video && video.paused) {
            const playButton = document.querySelector('.ytp-play-button');
            if (playButton) {
                playButton.click();
                return 'clicked';
            }
            return 'no_button';
        }
        return 'already_playing';
        """
        result = self.driver.execute_script(js_code)
        if result == 'clicked':
            print("Clicked play button")
            time.sleep(1)
        elif result == 'already_playing':
            print("Video already playing")
            time.sleep(0.5)
        else:
            time.sleep(0.5)

    def countdown(self, seconds=5):
        trial_label = "test" if self.is_test else self.trial_num
        print(f"Trial {trial_label} ready. Starting collection in {seconds} seconds...")
        for i in range(seconds, 0, -1):
            print(f"{i}...", end=" ", flush=True)
            time.sleep(1)
        print("Collecting")

    def extract_video_data(self):
        js_code = """
        const video = document.querySelector('video');
        if (!video) return null;
        return {
            width: video.videoWidth,
            height: video.videoHeight,
            buffer: video.buffered.length > 0 ?
                    video.buffered.end(0) - video.currentTime : 0,
            currentTime: video.currentTime
        };
        """
        return self.driver.execute_script(js_code)

    def detect_quality_change(self, width, height):
        if self.last_width is None or self.last_height is None:
            return True
        return (width, height) != (self.last_width, self.last_height)

    def detect_buffer_milestone(self, buffer_seconds):
        current_milestone = int(buffer_seconds // 5) * 5
        if current_milestone > self.last_buffer_milestone and current_milestone in BUFFER_MILESTONES:
            return True
        return False

    def estimate_bitrate(self, width, height):
        return BITRATE_MAP.get((width, height), 1200)

    def enable_network_throttling(self, download_kbps, upload_kbps, latency_ms):
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False,
            'downloadThroughput': download_kbps * 1024 / 8,
            'uploadThroughput': upload_kbps * 1024 / 8,
            'latency': latency_ms
        })

    def disable_network_throttling(self):
        self.driver.execute_cdp_cmd('Network.emulateNetworkConditions', {
            'offline': False,
            'downloadThroughput': -1,
            'uploadThroughput': -1,
            'latency': 0
        })

    def apply_network_phase(self, phase):
        if phase == 1 or phase == 3:
            self.enable_network_throttling(PHASE1_BANDWIDTH_KBPS, PHASE1_BANDWIDTH_KBPS, LATENCY_MS)
            print(f"[Phase {phase}] Network: 20 Mbps, 40ms latency")
        elif phase == 2:
            self.enable_network_throttling(PHASE2_BANDWIDTH_KBPS, PHASE2_BANDWIDTH_KBPS, LATENCY_MS)
            print(f"[Phase {phase}] Network: 1.5 Mbps, 40ms latency")

    def record_quality_event(self, timestamp, width, height, note=""):
        bitrate = self.estimate_bitrate(width, height)
        self.quality_events.append([timestamp, width, height, bitrate, note])
        self.last_width = width
        self.last_height = height

    def record_buffer_event(self, timestamp, buffer_seconds, note=""):
        self.buffer_events.append([timestamp, round(buffer_seconds, 1), note])
        current_milestone = int(buffer_seconds // 5) * 5
        if current_milestone > self.last_buffer_milestone:
            self.last_buffer_milestone = current_milestone

    def write_csv_files(self):
        print("Writing CSV files...")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        quality_file = self.output_dir / 'quality_timeline.csv'
        with quality_file.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time_seconds', 'resolution_width', 'resolution_height', 'bitrate_kbps', 'notes'])
            for event in self.quality_events:
                writer.writerow(event)

        buffer_file = self.output_dir / 'buffer_timeline.csv'
        with buffer_file.open('w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['time_seconds', 'buffer_seconds', 'notes'])
            for event in self.buffer_events:
                writer.writerow(event)

        trial_label = "test" if self.is_test else self.trial_num
        print(f"Saved: {quality_file} ({len(self.quality_events)} events)")
        print(f"Saved: {buffer_file} ({len(self.buffer_events)} events)")
        print(f"Collection complete: trial_{trial_label}")

    def collect(self, enable_shaping=False):
        if not self.connect_to_chrome():
            return False

        if not self.wait_for_video():
            self.driver.quit()
            return False

        self.click_play_button()

        if enable_shaping:
            self.apply_network_phase(1)

        self.countdown()

        start_time = time.time()
        last_status_print = 0
        current_phase = 1

        data = self.extract_video_data()
        if data:
            self.record_quality_event(0, data['width'], data['height'], "startup")
            self.record_buffer_event(0, data['buffer'], "startup")

        while True:
            elapsed = time.time() - start_time

            if enable_shaping:
                if elapsed >= 90 and current_phase == 2:
                    self.apply_network_phase(3)
                    current_phase = 3
                elif elapsed >= 45 and current_phase == 1:
                    self.apply_network_phase(2)
                    current_phase = 2

            if elapsed >= self.duration:
                data = self.extract_video_data()
                if data:
                    self.record_quality_event(int(elapsed), data['width'], data['height'], "end")
                    self.record_buffer_event(int(elapsed), data['buffer'], "end")
                break

            data = self.extract_video_data()
            if not data:
                time.sleep(POLLING_INTERVAL)
                continue

            timestamp = int(elapsed)
            width = data['width']
            height = data['height']
            buffer_seconds = data['buffer']

            quality_changed = self.detect_quality_change(width, height)
            buffer_milestone = self.detect_buffer_milestone(buffer_seconds)
            force_record = timestamp - self.last_forced_record >= MIN_EVENT_SPACING

            if quality_changed:
                self.record_quality_event(timestamp, width, height, "quality_change")

            if buffer_milestone:
                self.record_buffer_event(timestamp, buffer_seconds, "buffer_milestone")

            if force_record and not quality_changed:
                self.record_quality_event(timestamp, width, height, "periodic")
                if not buffer_milestone:
                    self.record_buffer_event(timestamp, buffer_seconds, "periodic")
                self.last_forced_record = timestamp

            if timestamp - last_status_print >= 15:
                bitrate = self.estimate_bitrate(width, height)
                print(f"[{timestamp}s] Quality: {width}x{height} ({bitrate} kbps), Buffer: {buffer_seconds:.1f}s")
                last_status_print = timestamp

            time.sleep(POLLING_INTERVAL)

        print(f"[{self.duration}s] Collection complete")

        if enable_shaping:
            self.disable_network_throttling()

        self.driver.quit()
        self.write_csv_files()
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python auto_collect.py --trial XXX [--duration N] [--with-shaping]")
        print("       python auto_collect.py --test [--duration N]")
        sys.exit(1)

    trial_num = None
    duration = TOTAL_DURATION
    is_test = False
    enable_shaping = False

    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--trial':
            trial_num = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--duration':
            duration = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--test':
            is_test = True
            trial_num = 'test'
            i += 1
        elif sys.argv[i] == '--with-shaping':
            enable_shaping = True
            i += 1
        else:
            i += 1

    if trial_num is None:
        print("Error: Must specify --trial XXX or --test")
        sys.exit(1)

    collector = VideoDataCollector(trial_num, duration, is_test)
    success = collector.collect(enable_shaping=enable_shaping)

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
