#!/usr/bin/env python3
"""بازسازی فایل‌های پروتکل از روی all_servers.txt پالایش‌شده."""
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ALL_SERVERS = "all_servers.txt"

def main():
    if not os.path.exists(ALL_SERVERS):
        logger.error(f"{ALL_SERVERS} not found!")
        return

    with open(ALL_SERVERS, "r", encoding="utf-8") as f:
        configs = sorted({line.strip() for line in f if line.strip()})

    # -- نگاشت نام‌های غیراستاندارد --
    PROTO_MAP = {
        "hy2": "hysteria2",
        "hysteria": "hysteria",      # بدون تغییر
        "tuic": "tuic",
        "juicity": "juicity",
        # اگر مورد دیگری بود اینجا اضافه کنید
    }

    protocols = {}
    for cfg in configs:
        if '://' not in cfg:
            proto = 'other'
        else:
            proto = cfg.split('://')[0].strip().lower()   # یکسان‌سازی حروف
            proto = PROTO_MAP.get(proto, proto)           # ترجمه نام‌های خاص

        protocols.setdefault(proto, []).append(cfg)

    for proto, items in protocols.items():
        fname = f"{proto}_servers.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write("\n".join(items) + "\n")
        logger.info(f"Rebuilt {fname} with {len(items)} configs")

if __name__ == "__main__":
    main()
