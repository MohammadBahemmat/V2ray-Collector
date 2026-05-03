#!/usr/bin/env python3
import os, sys, asyncio, aiohttp, re, json, logging, base64
from collections import Counter

# ---------- پیکربندی ----------
DAILY_FILE = "daily_servers.txt"
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

    # بارگذاری کانفیگ‌های روزانه (مبنا)
    daily_configs = set()
    if os.path.exists(DAILY_FILE):
        with open(DAILY_FILE) as f:
            daily_configs = {line.strip() for line in f if line.strip()}
        logger.info(f"Loaded {len(daily_configs)} configs from {DAILY_FILE}")
    else:
        logger.warning(f"{DAILY_FILE} not found, all found configs will be output.")

    sem = asyncio.Semaphore(MAX_CONCURRENT)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url, sem) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    new_configs = set()
    for content in results:
        if not content or isinstance(content, Exception):
            continue
        try:
            # تلاش برای decode محتوای base64
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

    # فقط کانفیگ‌های جدید نسبت به روزانه
    truly_new = [c for c in new_configs if c not in daily_configs]
    logger.info(f"Found {len(truly_new)} new configs (out of {len(new_configs)} total)")

    if truly_new:
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(truly_new))
        logger.info(f"Saved to {OUTPUT_FILE}")
    else:
        logger.info("No new configs, output file not created.")

if __name__ == "__main__":
    asyncio.run(main())
