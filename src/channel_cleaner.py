# channel_cleaner.py
import requests, time
from pathlib import Path

INPUT = "channels.txt"
VALID = "channels_cleaned.txt"
INVALID = "invalid_channels.txt"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
TIMEOUT = 5

def main():
    if not Path(INPUT).exists():
        print(f"❌ {INPUT} not found")
        return
    with open(INPUT) as f:
        channels = [l.strip() for l in f if l.strip() and not l.startswith('#')]
    print(f"Checking {len(channels)} channels...")
    valid, invalid = [], []
    for i, ch in enumerate(channels, 1):
        url = f"https://t.me/s/{ch}"
        try:
            r = requests.head(url, headers={"User-Agent": UA}, timeout=TIMEOUT, allow_redirects=True)
            if r.status_code == 200:
                valid.append(ch)
            else:
                invalid.append(f"{ch} # HTTP {r.status_code}")
        except Exception as e:
            invalid.append(f"{ch} # {e}")
        if i % 50 == 0:
            print(f"  {i}/{len(channels)} checked...")
        time.sleep(0.2)  # مؤدبانه
    Path(VALID).write_text("\n".join(valid))
    Path(INVALID).write_text("\n".join(invalid))
    print(f"Done. Valid: {len(valid)}, Invalid: {len(invalid)}")

if __name__ == "__main__":
    main()
