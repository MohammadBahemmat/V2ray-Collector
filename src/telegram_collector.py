#!/usr/bin/env python3
# src/telegram_collector.py
import requests
import re
import sqlite3
import time
import logging
from pathlib import Path
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----- تنظیمات -----
CHANNELS_FILE = "channels.txt"       # فایل حاوی شناسه کانال‌ها
DB_FILE = "collector.db"             # همان دیتابیس اصلی پروژه
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
SLEEP_BETWEEN_CHANNELS = 1.5         # تاخیر بین واکشی کانال‌ها (حفظ ادب در scraping)

# ----- الگوی استخراج کانفیگ -----
V2RAY_PATTERN = re.compile(
    r'(?:vless|vmess|trojan|ss|ssr|hysteria|hysteria2|tuic|juicity)://[^\s`\'"<>]+',
    flags=re.IGNORECASE
)

def load_channels(filepath):
    """بارگذاری لیست کانال‌ها از فایل (هر خط یک شناسه)."""
    path = Path(filepath)
    if not path.exists():
        logger.error(f"فایل {filepath} پیدا نشد. یک فایل با شناسه کانال‌ها بسازید.")
        return []
    with open(path, 'r', encoding='utf-8') as f:
        channels = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    logger.info(f"{len(channels)} کانال از {filepath} بارگذاری شد.")
    return channels

def fetch_page(channel):
    """دریافت HTML صفحه t.me/s با مدیریت خطا."""
    url = f"https://t.me/s/{channel}"
    try:
        headers = {"User-Agent": USER_AGENT}
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"خطا در واکشی {channel}: {e}")
        return ""

def extract_configs(html):
    """استخراج لینک‌های V2Ray از HTML دریافتی."""
    return set(V2RAY_PATTERN.findall(html))

def save_to_db(configs):
    """ذخیره کانفیگ‌های یکتا در دیتابیس collector.db."""
    conn = sqlite3.connect(DB_FILE)
    try:
        with conn:
            conn.executemany(
                "INSERT OR IGNORE INTO configs (config) VALUES (?)",
                [(c,) for c in configs]
            )
        logger.info(f"{len(configs)} کانفیگ جدید به دیتابیس اضافه شد.")
    except Exception as e:
        logger.error(f"خطا در ذخیره‌سازی دیتابیس: {e}")
    finally:
        conn.close()

def main():
    logger.info("🚀 شروع جمع‌آوری کانفیگ‌های تلگرام...")
    channels = load_channels(CHANNELS_FILE)
    if not channels:
        return

    channel_results = []  # برای گزارش نهایی
    all_configs = set()
    for idx, ch in enumerate(channels, 1):
        logger.info(f"📡 [{idx}/{len(channels)}] واکشی کانال: {ch}")
        html = fetch_page(ch)
        if html:
            found = extract_configs(html)
            logger.info(f"   ↳ {len(found)} کانفیگ استخراج شد.")
            all_configs.update(found)
            channel_results.append((ch, len(found)))
        else:
            channel_results.append((ch, 0))

        if idx < len(channels):
            time.sleep(SLEEP_BETWEEN_CHANNELS)

    if all_configs:
        save_to_db(all_configs)
    else:
        logger.warning("هیچ کانفیگی یافت نشد.")

    # --- ذخیره گزارش عملکرد کانال‌ها ---
    report_file = "channel_report.txt"
    history = {}
    if Path(report_file).exists():
        with open(report_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or ':' not in line:
                    continue
                parts = line.split(':', 1)
                if len(parts) != 2:
                    continue
                ch, counts = parts
                ch = ch.strip()
                counts = [c.strip() for c in counts.split(',') if c.strip().isdigit()]
                history[ch] = counts

    for ch, count in channel_results:
        if ch in history:
            history[ch].append(str(count))
        else:
            history[ch] = [str(count)]

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(f"Telegram Channel Report — last update: {datetime.now(timezone.utc).isoformat()}\n\n")
        for ch in sorted(history.keys()):
            counts_str = ", ".join(history[ch])
            f.write(f"{ch}: {counts_str}\n")

    logger.info("📊 تاریخچه‌ی کانال‌ها در channel_report.txt بروز شد.")

    logger.info("✅ پایان جمع‌آوری تلگرام.")

if __name__ == "__main__":
    main()
