import sys
import os
import logging
import json
import base64
import re
from collections import Counter
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

# --- تنظیمات ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def safe_base64_decode(s):
    s = s.strip()
    return base64.b64decode(s + '=' * (-len(s) % 4))

def _normalize_vmess(link: str) -> str:
    """
    نرمال‌سازی پیشرفته VMess:
    - دیکود JSON، حذف فیلد 'ps'، استانداردسازی مقادیر کلیدی، بازسازی JSON مرتب.
    """
    try:
        if "://" in link:
            b64_data = link.split("://")[1]
        else:
            b64_data = link
        json_bytes = safe_base64_decode(b64_data)
        config = json.loads(json_bytes.decode('utf-8', errors='ignore'))
        
        to_lower_keys = ['add', 'host', 'sni', 'id', 'net', 'type', 'tls', 'scy']
        cleaned_config = {}
        for k, v in config.items():
            if k.lower() in ['ps', 'remark']:
                continue
            if k == 'port':
                cleaned_config[k] = str(v)
            elif k in to_lower_keys and isinstance(v, str):
                cleaned_config[k] = v.strip().lower()
            else:
                cleaned_config[k] = v
        normalized_json = json.dumps(cleaned_config, sort_keys=True, separators=(',', ':'))
        normalized_b64 = base64.b64encode(normalized_json.encode('utf-8')).decode('utf-8').rstrip("=")
        return f"vmess://{normalized_b64}"
    except Exception:
        return link

def _normalize_shadowsocks(parsed: object) -> str:
    """
    نرمال‌سازی Shadowsocks (SS):
    - مدیریت فرمت‌های قدیمی و جدید (SIP002)
    - کوچک کردن متد (method) اما حفظ بزرگی/کوچکی پسورد (password) برای جلوگیری از حذف اشتباه.
    """
    try:
        if '@' in parsed.netloc:
            credentials, host_port = parsed.netloc.rsplit('@', 1)
            host_port = host_port.lower()
            try:
                decoded_creds = safe_base64_decode(credentials).decode('utf-8')
                if ':' in decoded_creds:
                    method, password = decoded_creds.split(':', 1)
                    # فقط متد کوچک می‌شود
                    credentials = f"{method.lower()}:{password}"
            except:
                pass
            final_netloc = f"{credentials}@{host_port}"
        else:
            try:
                decoded = safe_base64_decode(parsed.netloc).decode('utf-8')
                if '@' in decoded:
                    creds, hp = decoded.rsplit('@', 1)
                    hp = hp.lower()
                    final_netloc = f"{creds}@{hp}"
                else:
                    final_netloc = parsed.netloc
            except:
                final_netloc = parsed.netloc
        return urlunparse((parsed.scheme.lower(), final_netloc, parsed.path, parsed.params, parsed.query, ''))
    except Exception:
        return urlunparse(parsed)

def _normalize_generic(parsed: object) -> str:
    """
    نرمال‌سازی عمومی برای VLESS, Trojan, Tuic, Hysteria, Socks, Juicity و غیره.
    - کوچک کردن UUID (برای vless/trojan)، مرتب‌سازی پارامترهای Query، حذف Fragment.
    """
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc
    if '@' in netloc:
        user_info, host_port = netloc.rsplit('@', 1)
        host_port = host_port.lower()
        if scheme in ['vless', 'trojan']:
            user_info = user_info.lower()
        final_netloc = f"{user_info}@{host_port}"
    else:
        final_netloc = netloc.lower()
        
    query_params = parse_qs(parsed.query, keep_blank_values=True)
    sorted_params = []
    safe_to_lower_values = ['type', 'security', 'fp', 'alpn', 'sni', 'flow', 'encryption', 'headerType']
    for key, values in query_params.items():
        if key.lower() in ['remark', 'alias', 'name']:
            continue
        for v in values:
            if key.lower() in safe_to_lower_values:
                v = v.lower()
            sorted_params.append((key, v))
    sorted_params.sort()
    normalized_query = urlencode(sorted_params)
    return urlunparse((scheme, final_netloc, parsed.path, parsed.params, normalized_query, ''))

def get_canonical_form(link: str) -> str:
    """تابع اصلی تشخیص و نرمال‌سازی لینک"""
    link = link.strip()
    if not link:
        return None
    try:
        parsed = urlparse(link)
        scheme = parsed.scheme.lower()
        if not scheme:
            return None
        if scheme == 'vmess':
            return _normalize_vmess(link)
        elif scheme in ['ss', 'shadowsocks']:
            return _normalize_shadowsocks(parsed)
        # پشتیبانی کامل از تمام پروتکل‌های رایج
        elif scheme in ['vless', 'trojan', 'socks', 'socks5', 'tuic', 'hysteria', 'hysteria2', 'hy2', 'juicity']:
            return _normalize_generic(parsed)
        else:
            return _normalize_generic(parsed)
    except Exception:
        return None

def process_servers(input_path, output_path):
    logger.info(f"Processing {input_path}")
    if not os.path.exists(input_path):
        logger.error("Input file not found.")
        return
    unique_map = {}
    stats = Counter()
    invalid = 0
    with open(input_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    for line in lines:
        raw_link = line.strip()
        if not raw_link or raw_link.startswith('#'):
            continue
        proto = raw_link.split('://')[0].lower() if '://' in raw_link else 'unknown'
        canonical = get_canonical_form(raw_link)
        if canonical:
            if canonical not in unique_map:
                unique_map[canonical] = raw_link
                stats[proto] += 1
        else:
            invalid += 1
    sorted_links = sorted(unique_map.values())
    with open(output_path, 'w', encoding='utf-8') as f:
        for link in sorted_links:
            f.write(link + '\n')
    logger.info(f"Input: {len(lines)}, Invalid: {invalid}, Output: {len(sorted_links)}")
    for p, c in stats.most_common():
        logger.info(f"{p}: {c}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python dedup_configs.py <filename>")
        sys.exit(1)
    input_file = sys.argv[1]
    output_file = input_file + ".tmp"
    process_servers(input_file, output_file)
    os.replace(output_file, input_file)
    print(f"Dedup completed. Unique configs written to {input_file}")

if __name__ == "__main__":
    main()
