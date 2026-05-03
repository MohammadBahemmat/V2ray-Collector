#!/usr/bin/env python3
import os
import asyncio
import aiohttp
import re
import json
import logging
import base64

# ---------- پیکربندی ----------
DAILY_FILE = "daily_servers.txt"
HOURLY_FILE = "hourly_servers.txt"
OUTPUT_FILE = "frequent_servers.txt"
CACHE_FILE = "raw_urls_cache.json"
MAX_CONCURRENT = 80
MAX_BYTES = 10 * 1024 * 1024

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

V2RAY_PATTERN = re.compile(
    r'(?:vless|vmess|trojan|ss|ssr|hysteria|hysteria2|tuic|juicity)://[^\s`\'"]+',
    flags=re.IGNORECASE
)

async def fetch(session, url, sem):
    async with sem:
        try:
            async with session.get(url, timeout=10) as resp:
                if resp.status == 200:
                    size = 0
                    chunks = []
                    async for chunk in resp.content.iter_chunked(16*1024):
                        chunks.append(chunk)
                        size += len(chunk)
                        if size > MAX_BYTES:
                            logger.debug(f"Skipping large file: {url}")
                            return None
                    return b"".join(chunks).decode('utf-8', errors='ignore')
        except Exception:
            return None

async def main():
    if not os.path.exists(CACHE_FILE):
        logger.error(f"{CACHE_FILE} not found. Exiting.")
        return

    with open(CACHE_FILE) as f:
        urls = json.load(f)
    logger.info(f"Loaded {len(urls)} URLs from cache")

    # بارگذاری کانفیگ‌های مبنا از daily و hourly
    base_configs = set()
    for base_file in (DAILY_FILE, HOURLY_FILE):
        if os.path.exists(base_file):
            with open(base_file) as f:
                base_configs.update(line.strip() for line in f if line.strip())
            logger.info(f"Loaded configs from {base_file}")
    if not base_configs:
        logger.warning("No daily or hourly configs found; all found configs will be considered new.")

    sem = asyncio.Semaphore(MAX_CONCURRENT)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, sem) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    new_configs = set()
    for content in results:
        if not content or isinstance(content, Exception):
            continue
        try:
            # بررسی محتوای base64
            stripped = content.strip()
            if 16 <= len(stripped) <= 200000 and re.fullmatch(r'^[A-Za-z0-9_\-=\s/]+$', stripped[:2000]):
                padding = (4 - len(stripped) % 4) % 4
                try:
                    decoded = base64.urlsafe_b64decode(stripped + '=' * padding).decode('utf-8', errors='ignore')
                    new_configs.update(V2RAY_PATTERN.findall(decoded))
                except:
                    pass
            new_configs.update(V2RAY_PATTERN.findall(content))
        except:
            pass

    # فقط کانفیگ‌های جدید (نه در daily و نه در hourly)
    truly_new = [c for c in new_configs if c not in base_configs]
    logger.info(f"Found {len(truly_new)} configs not in daily or hourly (out of {len(new_configs)} total)")

    if truly_new:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(truly_new))
        logger.info(f"Saved to {OUTPUT_FILE}")
    else:
        logger.info("No new configs, output file not created.")

if __name__ == "__main__":
    asyncio.run(main())
