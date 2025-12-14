import pandas as pd
from pathlib import Path

def validate_trial(trial_num):
    unified_file = Path(f'data/processed/trial_{trial_num}/unified_timeline.csv')
    if not unified_file.exists():
        print(f"Trial {trial_num}: not found")
        return False

    df = pd.read_csv(unified_file)
    print(f"Trial {trial_num}: {len(df)} rows, ", end="")

    if len(df) != 136:
        print(f"expected 136")
        return False

    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"{missing} missing values")
        return False

    print("OK")
    return True

def validate_all():
    proc_dir = Path('data/processed')
    trial_dirs = sorted([d for d in proc_dir.iterdir() if d.is_dir() and d.name.startswith('trial_')])

    valid = sum(validate_trial(d.name.split('_')[1]) for d in trial_dirs)
    print(f"\n{valid}/{len(trial_dirs)} trials valid")

if __name__ == "__main__":
    validate_all()
