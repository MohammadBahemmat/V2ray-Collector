#!/usr/bin/env python3
import asyncio
import aiohttp
import aiosqlite
import base64
import re
import os
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from tqdm import tqdm
import backoff
from typing import Dict, Optional, Set, List, Tuple
import binascii

# ============================
# ⚙️ بخش ۱: پیکربندی نهایی (ساعتی، توقف خودکار و ذخیره‌ی شاخه‌ها)
# ============================
CONFIG_DEFAULTS = {
    "SEARCH_PERIOD_DAYS": 1,            # فقط برای مرحله‌ی جستجو (پوشش اولیه)
       "REPO_SEARCH_PAGES": 1,
    "CODE_SEARCH_PAGES": 1,
    "EXTRA_UPDATED_REPO_PAGES": 1,
    "MAX_AGE_HOURS": 1,                 # 🆕 فیلتر ساعتی: فقط مخازنی که در ۱ ساعت گذشته push داشته‌اند

    "GENERAL_CONCURRENT_REQUESTS": 80,
    "SEARCH_API_CONCURRENCY": 3,
    "AIOHTTP_CONNECTION_LIMIT": 80,
    "BATCH_SIZE": 200,

    "TARGET_CORE_CONSUMPTION": 5000,
    "CORE_PER_REPO_ESTIMATE": 5,
    "MAX_DISCOVERED_REPOS_TO_SCAN": 800,
    "RATE_CHECK_MIN_INTERVAL": 20,
    "RATE_LOW_THRESHOLD": 10,
    "RATE_SLEEP_ON_LOW": 61,

    "MAX_RECURSION_DEPTH": 0,
    "MAX_FILE_BYTES": 2 * 1024 * 1024,
    "OUTPUT_FILE": "servers_collected.txt",
    "DB_FILE": "collector.db",
    "ENV_FILE": ".env",
    "CACHE_FILE": "collector_cache.json",
    "CACHE_EXPIRY_DAYS": 1,
    "CHECKPOINT_FILE": "checkpoint.json",
    "DISCOVERED_BRANCHES_FILE": "discovered_branches.json",
}

# ============================
# 🔎 بخش ۲: منابع و کوئری‌ها (کامل)
# ============================
COMMON_BRANCH_NAMES = [
    'main', 'master', 'dev', 'develop', 'v2', 'Master', 'The-Nodes-of-Clash&V2ray',
    'tutu', 'canary', 'mineuwu', 'Clash-and-V2ray', 'branch', 'manyuser', 'Main',
    'on', 'mian', 'v.-2.0', 'KangProxy', 'VPN', 'rm', '2.15.x', 'Config', 'up',
    'feat/initial-project-scaffold', '5.x', 'backup', 'proxies', 'nodes', 'gh-pages',
    'patch-1', 'release', 'latest', 'stable', 'beta', 'alpha', 'test', 'testing',
    'staging', 'production', 'prod', 'development', 'feature', 'hotfix', 'bugfix',
    'free', 'premium', 'iran', 'ir', 'global', 'world', 'all', 'full', 'complete',
    'update', 'new', 'latest-configs', 'daily', 'hourly', 'auto', 'automatic',
    'subscription', 'sub', 'config', 'configs', 'proxy', 'proxies', 'vless', 'vmess',
    'trojan', 'shadowsocks', 'hysteria', 'hysteria2', 'tuic', 'juicity', 'reality',
    'sing-box', 'clash', 'nekobox', 'nekoray', 'v2rayng', 'v2rayu', 'xray', 'singbox',
    'hiddify', 'warp', 'argo', 'cloudflare', 'cf', 'cdn', 'speed', 'fast', 'best',
    'premium-configs', 'free-nodes', 'paid', 'vip', 'exclusive', 'private', 'public',
    'mci', 'irancell', 'mokhaberat', 'rightel', 'asiatech', 'shatel', 'v2ray-iran',
    'pishgaman', 'hiweb', 'tci', 'parsonline', 'freeiran', 'iranfree', 'config-iran',
    'iran-proxy', 'persian', 'farsi', 'vless-reality-iran', 'hysteria2-iran',
    'singbox-iran', 'tuic-iran', 'juicity-iran', 'warp-iran', 'worker-iran',
    'protonvpn-next-dev', 'devin/1777224454-initial-app', 'v2-rewrite', 'no-reflow',
    'codex/anfisa-vpn-publish', 'init', 'Monad'
]

REPO_SEARCH_QUERIES = sorted(list(set([
    "v2ray", "proxy", "subscribe", "vless", "vmess", "trojan", "shadowsocks", "clash",
    "کانفیگ", "اشتراک", "رایگان", "لینک", "سرور", "节点分享", "免费vpn", "机场",
    "翻墙", "科学上网", "Бесплатные", "прокси", "vpn", "無料ノード", "cấu hình miễn phí",
    "بروكسي مجاني", "ücretsiz v2ray", "akun v2ray gratis", "VLESS REALITY", "VLESS TLS",
    "Trojan gRPC", "Clash meta subscription", "hysteria2 configs", "TUIC configs",
    "sing-box configs", "Clash-Meta configs", "Hysteria2 subscription", "TUIC subscription",
    "nekoray config", "nekobox subscription", "juicity configs", "Shadowrocket configs",
    "Surge proxy", "V2Ray-N configs", "v2ray subscription", "free vpn configs",
    "shadowsocks links", "proxy collector", "v2ray aggregator", "free proxy list",
    "ss subscription", "secure proxy subscription", "کانفیگ رایگان", "لینک اشتراک v2ray",
    "سرور vless", "کانفیگ vmess", "v2ray nodes", "бесплатные прокси", "v2ray github",
    "anti-censor proxy", "proxy provider", "proxy pool", "subconverter", "proxy provider list",
    "free nodes", "daily v2ray", "node list", "clash verge", "v2ray updated",
    "reality configuration", "hiddify", "hiddify-next", "VLESS over REALITY",
    "sing-box one-click script", "Hysteria2 协议", "Vless-reality, Vmess-ws, Vless-grpc,Hysteria2, Tuic5",
    "WARP Sing-Box Config Generator", "free proxy list updated", "v2ray-configs",
    "vless-reality", "vless reality iran", "trojan grpc tls", "hysteria2 subscription free",
    "tuic v5 configs", "free v2ray configs 2024", "v2ray panel", "v2ray subscriber",
    "v2ray core", "v2rayu", "xrayr", "geoip v2fly", "free v2ray", "v2ray free",
    "iran v2ray", "irancell v2ray", "mci v2ray", "mokhaberat v2ray", "asiatech v2ray",
    "rightel v2ray", "reality vless", "warp config", "argo tunnel vless", "cloudflare v2ray", "v2ray config",
    "ایرانسل", "همراه اول", "مخابرات", "رایتل", "آسیاتک", "شاتل", "های وب", "پیشگامان",
      "سرور ایران", "فیلترشکن", "وی پی ان", "پروکسی", "اشتراک رایگان", "اشتراک v2ray",
    "v2ray ایرانی", "v2ray ایران", "پروکسی ایران", "کانفیگ رایگان ایران",
     "hysteria2 ایران", "warp اینترنت رایگان", "فیلترشکن رایگان",
    "v2ray irancell", "v2ray mci", "v2ray mokhaberat", "v2ray rightel",
    "v2ray asiatech", "v2ray shatel", "v2ray hiweb", "v2ray iran 2025",
    "proxy iran free", "xray iran", "singbox iran", "reality iran",
    "juicity iran", "warp iran", "iran v2ray config",
    "iran free proxy", "iran subscription v2ray",
    "إيران بروكسي", "ایران vpn", "Иран v2ray", "İran v2ray ücretsiz"
])))

CODE_SEARCH_QUERIES = sorted(list(set([
    '"vless://" security=reality', '"vless://" type=grpc security=tls', '"trojan://" type=grpc',
    '"hysteria2://"', '"tuic://"', '"juicity://"', '"ss://"', '"ssr://"', '"hysteria://"',
    'filename:subscription reality', 'filename:clash tls', 'filename:all.txt "vless://"',
    'filename:proxy "vmess://"', 'filename:sub.json', 'filename:sub.txt "vless://"',
    'filename:proxies.yaml "trojan://"', 'filename:README.md "vless://"', 'filename:Dockerfile "vless://"',
    'filename:nekoray-config.json', 'filename:hysteria.json "outbounds"', 'extension:yaml "proxies:"',
    'extension:json "outbounds"', 'extension:txt "vmess://"', 'extension:yaml "proxy-providers"',
    'extension:json "REALITY-VLESS"', 'path:proxies', 'path:sub "trojan://"', 'path:data "vless"',
    'path:subscribe "https://"', 'path:subscribe vless', '"/api/v1/client/subscribe?token="',
    '"/api/v1/client/subscribe?token=" in:file', 'filetype:txt subscription', 'language:yaml "vless"',
    'language:json "outbounds"', 'language:yaml "proxy-groups:"', 'language:json "inbounds" "vless"',
    '"clash" "reality"', '"V2RAY" "CONFIG"', '"vless reality" OR "vmess reality"',
    'gist.github.com "vless://"', '"vless://" in:comments', 'sni:"dl.google.com" "vless://"',
    'sni:"www.speedtest.net"', '"proxies:" AND "server:" AND "port:" extension:yaml',
    '"trojan-go"', 'vless iran', 'Mokhaberat vless', '("vless" OR "vmess" OR "trojan") AND ("iran" OR "MCI" OR "irancell")',
    '("Mokhaberat" OR "Asiatech" OR "Rightel") AND "vless://"', '"vless://" "节点"', '"trojan://" "бесплатно"',
    'v2ray 無料', 'v2ray 무료 구독', '"cấu hình v2ray miễn phí"', '"ซับ v2ray" language:txt',
    'filename:hiddify.json', 'filename:sing-box.json "vless"', 'path:subs "vless"',
    '"Vless WebSocket"', 'extension:json "vless-reality"', 'extension:txt "vless-configs"',
    '"argo tunnel" "vless"', '"v2ray config"', '"free v2ray subscription"', '"v2rayNG config"',
    '"reality v2ray"', 'filename:config.yaml "outbounds"', 'filename:config.json "proxies"',
    'path:config "vless://"', 'path:subscription "vmess://"', 'filename:base64.txt', 'filename:encoded.txt',
    'extension:sub "vless://"', 'extension:txt "trojan://"', 'filename:links.txt "hysteria2://"',
    'filename:clash-meta.yaml "proxy-providers"', 'filename:sing-box.json "outbounds"', 'path:free "vless://"',
    'sni:"digikala.com"', 'sni:"aparat.com"', 'sni:"namasha.com"',
    'sni:"varzesh3.com"', 'sni:"snapp.ir"', 'sni:"tapsi.ir"',
    'sni:"alibaba.ir"', 'sni:"divar.ir"', 'sni:"bama.ir"', 'sni:"shahrefarang.com"',
    'sni:"filmio.ir"', 'sni:"telewebion.com"', 'sni:"anten.ir"',
    '"Irancell" "vless://"', '"MCI" "hysteria2://"', '"Mokhaberat" AND "vless://"',
    '"Rightel" "tuic://"', '"Asiatech" "reality"',
    'filename:iran.txt "vless://"', 'filename:config-iran.json',
    'path:iran "vless://"', 'path:persian "vmess://"',
    'extension:yaml "iran" "proxies"', 'extension:json "iran" "outbounds"',
    'language:fa "vless://"',
    '("iran" OR "mci" OR "irancell") "hysteria2://"',
    'sni:"speedtest.net" AND "iran"', 'sni:"www.google.com" AND "reality"'

])))

# --- کوئری‌های عمومی برای جستجوی تکمیلی با فیلتر updated (فقط ۱ صفحه) ---
EXTRA_UPDATED_REPO_QUERIES = [
    "v2ray", "proxy", "free v2ray", "vpn config", "iran v2ray", "reality", "iran v2ray",
    "فیلترشکن", "v2ray irancell", "reality iran", "hysteria2 iran", "sing-box iran",
    "tuic iran", "proxy iran", "free config iran", "iran subscription"
]

MANUAL_REPOS_TO_SCAN = sorted(list(set([
    ("mahdibland", "V2RayAggregator"), ("yebekhe", "V2Hub"), ("asgharkapk", "Sub-Config-Extractor"),
    ("freefq", "free"), ("Epodonios", "v2ray-configs"), ("ALIILAPRO", "v2rayNG-Config"),
    ("soroushmirzaei", "V2Ray-configs"), ("MortezaBashsiz", "CFScanner"), ("MrPooyaX", "V2rayAggregator"),
    ("iyarivky", "reality-configs"), ("V2RayRoot", "V2RayConfig"), ("M-Mashreghi", "Free-V2ray-Collector"),
    ("mahdibland", "Node-Collector"), ("kevin-hf", "v2ray-configs-collection"), ("Misaka-blog", "Misaka-V2ray-Sub"),
    ("tindy2013", "subconverter"), ("MetaCubeX", "meta-rules-dat"), ("pojiezhiyuanjun", "freev2"),
    ("yebekhe", "TelegramV2rayCollector"), ("sashalsk", "V2Ray"), ("wizora", "v2ray-configs"),
    ("KOP-XIAO", "v2ray-vless"), ("AzadNetCH", "V2Ray-configs"), ("ebrasha", "free-v2ray-public-list"),
    ("MatinGhanbari", "v2ray-configs"), ("Firmfox", "Proxify"), ("Joker-funland", "V2ray-configs"),
    ("hello-world-1989", "cn-news"), ("Mohammadgb0078", "IRV2ray"), ("SoliSpirit", "v2ray-configs"),
    ("mostafasadeghifar", "v2ray-config"), ("morteza-v2", "free-v2ray-irancell-config"), ("hans-thomas", "v2ray-subscription"),
    ("roosterkid", "openproxylist"), ("miladtahanian", "V2RayCFGDumper"), ("Surfboardv2ray", "TGParse"),
    ("miladtahanian", "V2RayScrapeByCountry"), ("skywrt", "v2ray-configs"), ("10ium", "V2ray-Config"),
    ("10ium", "V2rayCollector"), ("skywrt", "v2ray-Collector"), ("10ium", "V2RayAggregator"),
    ("10ium", "V2Hub3"), ("10ium", "multi-proxy-config-fetcher"), ("Abdulhossein", "Autov2rayLeecher"),
    ("Argh94", "V2RayAutoConfig"), ("Kwinshadow", "TelegramV2rayCollector"), ("MahsaNetConfigTopic", "config"),
    ("MhdiTaheri", "V2rayCollector"), ("Mosifree", "-FREE2CONFIG"), ("SamanGho", "v2ray_collector"),
    ("arshiacomplus", "v2rayExtractor"), ("azadiazinjamigzare", "Service"), ("coldwater-10", "V2ray-Config"),
    ("darknessm427", "Sub"), ("hamedp-71", "Trojan"), ("hamedp-71", "openproxylist"),
    ("itsyebekhe", "PSG"), ("mahdibland", "ShadowsocksAggregator"), ("youfoundamin", "V2rayCollector"),
    ("MortezaHajilou", "V2Ray-Configs"), ("im-hady", "V2RayAggregator"), ("NiREvil", "vless"),
    ("ircfspace", "V2ray-Configs"), ("yebekhe", "Config-Collector"), ("mrvcoder", "V2rayCollector"),
    ("Sepideh0", "V2ray-Configs-Iphone"), ("proxypal", "proxy-configs"), ("ircfspace", "V2ray-Configs-Store"),
    ("im-hady", "v2ray-configs"), ("proxifly", "v2ray-subscription"), ("Osivpn", "v2ray-configs"),
    ("ojovirtual", "v2ray-configs"), ("herospeed", "v2ray-config"), ("peasoft", "NoMoreWalls"),
    ("anaer", "Sub"), ("Zaeem20", "FREE_V2RAY_CONFIGS"), ("Pawdroid", "Free-V2Ray"),
    ("aiboboxx", "v2rayfree"), ("R-the-coder", "V2ray-configs"), ("GFW4Fun", "sing-box-yg-argo-reality-tuic-hysteria"),
    ("aleskxyz", "reality-ezpz"), ("Ptechgithub", "sing-box"), ("v2rayfree", "v2rayfree"),
    ("barry-far", "free-v2ray"), ("Epodonios", "free-proxies"), ("GetAConfig", "GetAConfig"),
    ("hrostami", "v2ray-configs"), ("vfarid", "v2ray-worker-sub"), ("v2rayNG-dist", "v2rayNG"),
    ("v2rayN-release", "v2rayN"), ("Xray-core", "Xray-core"), ("v2fly", "v2ray-core"),
    ("v2fly", "fhs-install-v2ray"), ("Project-V", "ProjectV"), ("v2rayA", "v2rayA"),
    ("v2rayN", "v2rayN"), ("v2rayN", "v2rayN-Releases"), ("v2rayN", "v2rayN-Configs"),
    ("v2rayN", "v2rayN-Subscription"), ("nikita29a", "FreeProxyList"), ("MrAbolfazlNorouzi", "iran-configs"),
    ("nyeinkokoaung404", "V2ray-Configs"), ("vungocbaobao", "v2ray-config-finder-tg-bot"), ("Danialsamadi", "v2go"),
    ("iboxz", "free-v2ray-collector"), ("gfpcom", "free-proxy-list"), ("V2RAYCONFIGSPOOL", "V2RAY_SUB"),
    ("mohammmdmdmkdmewof", "v2rayConfigsForYou"), ("Epodonios", "bulk-xray-v2ray-vless-vmess-...-configs"), 
    ("0xAbolfazl", "PyroConfig"), ("WLget", "V2Ray_configs_64"), ("sinavm", "SVM"), ("jackrun123", "v2ray_configs"),
    ("MahanKenway", "Freedom-V2Ray"), ("LuisF-92", "Freedom-V2Ray"), ("miladtahanian", "Config-Collector"),
    ("SoliSpirit", "SolVPN"), ("Shayanthn", "V2ray-Tester-Pro"), ("amirkma", "proxykma"), ("kasesm", "Free-Config"),
    ("hamedcode", "port-based-v2ray-configs"), ("Delta-Kronecker", "V2ray-Config"), ("gongchandang49", "TelegramV2rayCollector"),
    ("SoroushImanian", "BlackKnight"), ("swileran", "v2ray-config-collector"), ("barry-far", "V2ray-Config"),
    ("crackbest", "V2ray-Config"), ("jagger235711", "V2rayCollector"), ("mohamadfg-dev", "telegram-v2ray-configs-collector"),
    ("smakotta", "V2rey-cfg"), ("pornnewbee", "free-vless-VPN"), ("mostafanamv", "timetunnel"),
    ("therealaleph", "sni-spoofing-rust"), ("cool-cucumber-in-the-town", "v2ray-test-config"), ("Lego1997", "mac-proxy-sync"),
    ("PaPerseller", "chn-iplist"), ("Abobirec", "bezdelnicha-vpn0chek"), ("amirhosseinesmaeilnejadtanha-cloud", "vpn-"),
    ("Yan233th", "sub2nodes"), ("thisara0810", "V2Ray-Render"), ("alisadeghiaghili", "v2ray-finder"),
    ("Arsham1ho", "telegram-bale-proxy-agent"), ("jafarm83", "ConfigV2Ray"), ("liketolivefree", "kobabi"),
    ("akarezi", "V2auto"), ("SinorDev", "OV-Refiner"), ("jeet8200", "CDN-SNI-Scanner-PLUS-for-V2Ray-xray"),
    ("MahdiAshuori", "v2ma.apk"), ("rb360full", "V2Ray-Configs"), ("mehdirzfx", "v2ray-sub"),
    ("katvixlab", "xray-tlg"), ("MortezaAcm", "v2rayConfig"), ("Bllare", "V2ray-Configs"),
    ("smblue07", "my-v2ray-tools"), ("Doki-code-22", "Free-Internet-"), ("AzadNetCH", "Clash"),
    ("frank-vpl", "servers"), ("Amir603-o", "ELX"), ("penhandev", "AutoAiVPN"),
    ("DrFarhad2", "v2ray_configs_pools"), ("iaghapour", "v2ray-converter"), ("Abol007", "v2ray-config-hunter"),
    ("Ryan-PG", "ry-v2ray-config-extractor"), ("Hamed-Gharghi", "V2Ray-Checker"), ("Alireza-ALZ", "RayScout"),
    ("0xRadikal", "Telegram-Config-Extractor"), ("salmanclever", "v2rconfigfetcher"), ("iteride", "vpn"),
    ("amirali098-sys", "v2ray-sub"), ("mahdizynali", "jimbo-v2ray"), ("ByteTrue", "sub2mihomo"),
    ("cirosantilli", "china-dictatorship"), ("mRFWq7LwNPZjaVv5v6eo", "cihna-dictattorshrip-8"), ("cirosantilli", "china-dictatroship-7"),
    ("darkdoki69", "v2ray"), ("primeZdev", "Emergency-key"), ("Alireza533022", "v2ray-guide-free-v2ray-v2rayng-iran"),
    ("phpvortex", "php-v2ray-manager"), ("Lakyn80", "xray-manager"), ("dos2bang", "v2ray_config"),
    ("mohsenfaraj", "samir"), ("amirhosseinqaderifar-cell", "Amirkingtap1"), ("mehdikarimifa", "v2ray-config-finder-tg-bot"),
    ("mrmarzx", "SGV2RAY-TELEGRAM"), ("saTrx", "config"), ("NIKJOO", "Config_Over_SMS"),
    ("altyhydyrov", "https-github.com-altyhydyrov-Also-"), ("nckpln", "v2ray-conf"), ("qaderizadeh", "v2ray-docker-win"),
    ("ErfanElhamiMokhar", "v2rayConfig"), ("changsongyang", "V2ray-configs2"), ("loopaz", "V2ray-config-convet"),
    ("ramby066-pixel", "v2ray-configs"), ("proxystore11", "v2ray-config-collector"), ("officialmzstudio", "Python_Telegram_Bot"),
    ("ahMADASSadi", "We2Ray"), ("mydocker-repo", "v2ray"), ("H3mnz", "bug_vpn"),
    ("pouyawhite", "config"), ("onion108", "onion-v2ray-subscription-to-clash-converter"), ("Yikai-Liao", "v2ray-reverse-bridge-guide"),
    ("Givonar", "v2rayconfig2xrayjson"), ("A512-dev", "config-collector"), ("mrpauk", "singbox2link"),
    ("NamiraNet", "V2Configs"), ("gege-circle", ".github"), ("elf2017spring", "ConfigsHub"),
    ("shammay-PC", "Ay-v2Ray-Subscription"), ("corey11256", "v2ray-config_v5"), ("nichind", "v2ray2proxy"),
    ("decemberpei", "V2rayRunner"), ("ddmm1214", "node-config-converter"), ("MrArvand", "FreeRay"),
    ("F4RAN", "wolf-pack-watcher"), ("Amirali9687", "free_v2ray_config"), ("infinitymood", "config-bridge"),
    ("hooman1234567", "v2ray-sales-bot"), ("torguardvpn", "tgv2ray"), ("sahar-km", "aurora"),
    ("mehdi9097f", "Netopenbook"), ("sithu015", "Sub-mm"), ("Nullfill", "3x-pannel-and-bot"),
    ("arsph", "VPN-Check-Status"), ("kelvinxue1107", "v2ray_ansible"), ("ihossein", "v2ray-server-less"),
    ("WhoisNeon", "Config-To-QrCode"), ("ircfspace", "location"), ("Iranux", "TopSub"),
    ("Shjpr9", "Subs"), ("tunmerreclop", "Proxify-PWA"), ("xvolld", "xvolldv2rayserver"),
    ("llgelarall", "-TelegramV2RayConfigFetcher"), ("facksten", "V2rayScrapper"), ("mahan403", "v2ray"),
    ("DiamondTeamOfficial", "v2ray-zitel"), ("Ki4wn", "v2ray-sub-manager"), ("VQIVS", "MarzbanBot"),
    ("moeinomidali", "v2ray-proxy-service"), ("theemadd", "V2ray"), ("Mikita-ala", "MARZBAN-SETTINGS"),
    ("Arash-GJ", "v2ray-config-tester"), ("apolloadam31415926", "v2ray_config"), ("procrastinando", "mindbloat-bot"),
    ("mostaghimbot", "FreeV2rayConfig"), ("amirrezaalavi", "XrayConfigTester"), ("ALIILAPRO", "ProxyNest"),
    ("ThyArt-IsMurder", "Proxy-Test"), ("SAMURAI-007", "V2ray-shop-bot"), ("chaosone", "v2ray_config"),
    ("Ashrafty", "RAE-VPN"), ("Sajjad-Taghinezhad", "v2checker"), ("ColorfulChen", "v2rayStartupScript"),
    ("geek-spot", "Free-Config"), ("ItzGlace", "MistLink"), ("ADAX-3VI", "Configs"),
    ("1Shervin", "FreeShen"), ("AutoFTbot", "free"), ("gfw-killer", "Free-v2Ray-Nodes"),
    ("mkmark", "v2ray-config-python"), ("mehrdadmb2", "v2ray-telegram-collector"), ("Panini235", "update-v2ray-config-from-dynamodb"),
    ("1Shervin", "v2ray-skimmer"), ("runoneall", "netlify-v2ray2clash"), ("itpourya", "V2rayBot"),
    ("yoyoraya", "subgenerator"), ("Majholl", "Majholl"), ("mnr73", "v2ray-to-clash-converter"),
    ("Surfboardv2ray", "Trojan-worker"), ("molaei2000", "auto-import-config"), ("Trueaminm", "Majholl"),
    ("Surfboardv2ray", "v2ray-refiner"), ("Mohammad-Hossein-Dlt", "kc_vanguard_bot"), ("MrNbody16", "TvConfigViewer"),
    ("ircfspace", "updater"), ("ircfspace", "tester"), ("GitDev90", "V2ray-Config-Pool"),
    ("ARS-83", "v2ray-ConfigGenerator"), ("Surfboardv2ray", "replit-argo"), ("thefatedefeater", "V2ray-configs2"),
    ("vpnchi", "vpnchii"), ("Surfboardv2ray", "Config-Multiplier"), ("RealCuf", "VCG-Script"),
    ("kooloopoo", "TELEGRAM_PROXY_SUB"), ("ByteMysticRogue", "Ray2Box"), ("Net-Account", "Config"),
    ("Uryzen317", "V2ray-subscription-to-json"), ("PAIREN1383", "GVCA"), ("sinasims", "Free-V2ray-Config-"),
    ("AtlanticTeam", "V2rayClient"), ("iyarivky", "sing-ribet"), ("Mohammadtafakori01", "v2rayConfigAsBase64"),
    ("claxpoint", "xconfig"), ("limintara", "V2RAY_SUB"), ("fafa1121", "edaw3"),
    ("xingdawang", "load_balance"), ("saeed-54996", "V2CS-Bot"), ("ngathit7", "v2flare"),
    ("mahdi-turrkk", "x-ui-panel-manager"), ("thethtwe-dev", "v2flare"), ("mindcrunch4u", "v2ray-reloader"),
    ("wikm360", "fragmentbot"), ("EXE88", "v2ray-config-beautifier"), ("morawd", "jupyter"),
    ("V2rayking", "V2rayking"), ("wikm360", "Config-Detector"), ("selenanett", "v2ray-worker-sub"),
    ("eurus1", "V2Box-Client-Config-ios"), ("selenanett", "clash-worker"), ("boypt", "vmess2json"),
    ("Am7nRaz", "MoonLight"), ("MohammadQS", "QandShekan_Bot"), ("SiYaHP0sH", "vless"),
    ("KiyarashFarahani", "OmegaRay-legacy"), ("kltk", "v2ray-tools"), ("Sami4387", "TBot"),
    ("cloudwindy", "v2ray"), ("hellopoisonx", "v2rayConfig"), ("soheil1405", "generateV2ray"),
    ("aliasgharfathikhah", "v2rayse"), ("zszszszsz", ".config"), ("aalligithub", "automated-v2ray-manger"),
    ("vfarid", "clash-worker"), ("farengeyit", "V2Ray"), ("alireza-rou13", "daily-config-backend"),
    ("Creativveb", "v2configs"), ("jbasoft", "V2ray"), ("Soroushbolbolabady", "FreeInternet"),
    ("denizkaplanst", "openvpn-v2ray"), ("sinadalvand", "CFScanner"), ("mrunderline", "telegram_v2ray_sub"),
    ("noobj2", "Personal-Worker-Sub"), ("vfarid", "v2ray-worker-merge"), ("0xdolan", "v2ray_config_generator"),
    ("slandx", "v2rayGen"), ("KH4St3H", "PyCFScanner"), ("bitcoinvps", "singbox-vpn"),
    ("horapusa-lk", "V2ray-API"), ("yonggithub", "AutoCreateConfigScriptForV2R"), ("sh-sh-dev", "extract-v2ray-configs"),
    ("m9h4s", "V2Ray"), ("mofakhrpour", "v2ray-transparent-proxy-gateway"), ("iiTzIsh", "multi-v2ray"),
    ("MathNodes", "v2ray_configs"), ("harryhastam", "v2rayXUI"), ("rastgoo", "v2ray"),
    ("Daravai1234", "china-dictatorship"), ("amir1376", "v2raychecker"), ("b0LBwZ7r5HOeh6CBMuQIhVu3-s-random-fork", "PCL2"),
    ("zpc1314521", "PCL2"), ("panbinibn", "OpenPacketFix_"), ("0xZoomEye", "V2ray-tools"),
    ("scy1993", "v2ray"), ("volegris", "-v2ray"), ("fisabiliyusri", "XRAY-V2RAY-CUSTOM-SL"),
    ("JackLean", "v2ray-config"), ("re-f", "v2rays"), ("bruceluk", "v2rayM"),
    ("vcs6", "vinit"), ("shafiqsaaidin", "go-csv-to-mysql"), ("Annihilater", "caddy-v2ray-docker-config"),
    ("swordsmile", "v2ray"), ("krot357", "CN-v2ray-install"), ("nakululusatuva", "V2Switch"),
    ("webcirque", "v2studio"), ("MTDickens", "v2ray-config"), ("Benny0731", "v2ray"),
    ("whosy", "v2ray-config"), ("WhoJave", "ExternalConfig"), ("Nan3r", "v2ray-config"),
    ("xusos", "v2ray-config-online"), ("lance65", ".github-workflows-openwrt-ci.yml"), ("QZero233", "generateV2rayConfig"),
    ("edaoren", "v2ray-linux-chrome"), ("maskedeken", "v2ray-config"), ("rikaaa0928", "V2rayE"),
    ("Dinu-orjinl", "v2ray-config"), ("DomYY", "v2ray.config"), ("alexxyjiang", "v2ray-config-public"),
    ("ITXiaoPang", "v2raypro"), ("chenmoaaaa", "v2ray_configs"), ("DukeMehdi", "FreeList-V2ray-Configs")
])))

# ============================
# 🧰 بخش ۳: ابزارها، الگوها و BranchManager
# ============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("collector.log", "w", "utf-8"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

V2RAY_CONFIG_PATTERN = re.compile(
    r'(?:vless|vmess|trojan|ss|ssr|hysteria|hysteria2|tuic|juicity)://[^\s`\'"]+',
    flags=re.IGNORECASE
)
SUB_LINK_PATTERN = re.compile(
    r'https?://[^\s`\'"]+\.(?:txt|yaml|yml|json|conf)[^\s`\'"]*',
    flags=re.IGNORECASE
)

class BranchManager:
    def __init__(self, base_branches: list, file_path: str):
        self.file_path = file_path
        self.base_branches = set(base_branches)
        self.discovered_branches = set()
        self._lock = asyncio.Lock()
        self._load()

    def _load(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    if isinstance(saved, list):
                        self.discovered_branches = set(saved)
            except Exception as e:
                logger.warning(f"Could not load discovered branches: {e}")

    def _save(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.discovered_branches), f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save discovered branches: {e}")

    @property
    def active_branches(self) -> Set[str]:
        return self.base_branches | self.discovered_branches

    async def add(self, branch: str):
        if branch in self.base_branches or branch in self.discovered_branches:
            return
        async with self._lock:
            if branch not in self.base_branches and branch not in self.discovered_branches:
                self.discovered_branches.add(branch)
                self._save()
                logger.info(f"🌿 New branch saved: '{branch}' (will be used in future runs)")

branch_manager = BranchManager(COMMON_BRANCH_NAMES, CONFIG_DEFAULTS["DISCOVERED_BRANCHES_FILE"])
ACTIVE_BRANCHES = branch_manager.active_branches

# ============================
# 📊 بخش ۴: مدیریت Rate Limit (با پرچم توقف خودکار)
# ============================
RATE_STATE = {
    'search': {'remaining': 30, 'reset': 0.0, 'last_checked': 0.0, 'paused_until': 0.0},
    'core':   {'remaining': 5000, 'reset': 0.0, 'last_checked': 0.0, 'paused_until': 0.0},
}
TOTAL_CORE_USED = 0
CORE_LIMIT_REACHED = False
RATE_API_LOCK = asyncio.Lock()

async def check_rate_limit(session: aiohttp.ClientSession, headers: dict, resource_type: str = 'core', force: bool = False):
    global TOTAL_CORE_USED, RATE_STATE, CORE_LIMIT_REACHED
    now_ts = time.time()
    state = RATE_STATE[resource_type]
    min_interval = CONFIG_DEFAULTS["RATE_CHECK_MIN_INTERVAL"]

    if state['paused_until'] and now_ts < state['paused_until']:
        wait = state['paused_until'] - now_ts
        logger.warning(f"[RateLimit] {resource_type.upper()} Paused. Sleeping {int(wait)}s")
        await asyncio.sleep(wait)
        state['paused_until'] = 0.0
        return

    if not force and (now_ts - state['last_checked'] < min_interval):
        return

    async with RATE_API_LOCK:
        now_ts = time.time()
        if not force and (now_ts - state['last_checked'] < min_interval):
            return

        state['last_checked'] = now_ts
        try:
            async with session.get("https://api.github.com/rate_limit", headers=headers, timeout=15) as resp:
                if resp.status != 200:
                    logger.warning(f"[RateLimit] /rate_limit returned {resp.status}, sleep 65s")
                    await asyncio.sleep(65)
                    return

                data = await resp.json()
                resource = data.get('resources', {}).get(resource_type, {})
                remaining = resource.get('remaining')
                reset = resource.get('reset', 0)

                if remaining is None:
                    return

                if resource_type == 'core':
                    delta_used = state['remaining'] - remaining
                    if delta_used > 0:
                        TOTAL_CORE_USED += delta_used

                state['remaining'] = remaining
                state['reset'] = float(reset)

                logger.info(f"[RateLimit] {resource_type.upper()} Remaining: {remaining} | Total Core Used (Est): {TOTAL_CORE_USED}")

                threshold = CONFIG_DEFAULTS["RATE_LOW_THRESHOLD"] if resource_type == 'core' else 2
                is_low_remaining = remaining < threshold
                is_over_budget = (resource_type == 'core') and (TOTAL_CORE_USED >= CONFIG_DEFAULTS["TARGET_CORE_CONSUMPTION"])

                if is_low_remaining or is_over_budget:
                    if resource_type == 'core':
                        if not CORE_LIMIT_REACHED:
                            logger.warning("🛑 Core limit reached! Will stop scanning and finalize soon.")
                            CORE_LIMIT_REACHED = True
                        return
                    else:
                        wait_time = max(CONFIG_DEFAULTS["RATE_SLEEP_ON_LOW"], state['reset'] - now_ts + 5)
                        logger.warning(f"[RateLimit] Low SEARCH. Pausing {int(wait_time)}s")
                        state['paused_until'] = now_ts + wait_time
                        await asyncio.sleep(wait_time)
                        state['paused_until'] = 0.0
        except Exception as e:
            logger.error(f"[RateLimit] Error checking: {e}. Sleep 65s")
            await asyncio.sleep(65)

# ============================
# 💾 بخش ۵: پایگاه داده و کش (اصلاح‌شده)
# ============================
class CacheManager:
    def __init__(self, cache_file: str, expiry_days: int):
        self.cache_file = cache_file
        self.expiry_days = expiry_days
        self.cache: Dict[str, float] = self._load_cache()

    def _load_cache(self) -> Dict[str, float]:
        if not os.path.exists(self.cache_file):
            return {}
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                raw_cache = json.load(f)
            now_ts = datetime.now(timezone.utc).timestamp()
            expiry_limit_ts = (datetime.now(timezone.utc) - timedelta(days=self.expiry_days)).timestamp()
            cleaned = {url: ts for url, ts in raw_cache.items() if isinstance(ts, (int, float)) and ts >= expiry_limit_ts}
            if len(raw_cache) != len(cleaned):
                logger.info(f"Cache: Cleaned {len(raw_cache) - len(cleaned)} expired entries.")
            return cleaned
        except Exception:
            return {}

    def _save_cache(self):
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving cache: {e}")

    def is_cached(self, url: str) -> bool:
        return url in self.cache

    def add(self, url: str):
        self.cache[url] = datetime.now(timezone.utc).timestamp()

_db_connection = None

async def get_db():
    global _db_connection
    if _db_connection is None:
        _db_connection = await aiosqlite.connect(CONFIG_DEFAULTS["DB_FILE"])
        _db_connection.row_factory = aiosqlite.Row
        await _db_connection.execute("PRAGMA journal_mode=WAL")
        await _db_connection.execute("CREATE TABLE IF NOT EXISTS configs (config TEXT PRIMARY KEY)")
        await _db_connection.execute("CREATE TABLE IF NOT EXISTS urls (url TEXT PRIMARY KEY, processed_at REAL)")
        await _db_connection.execute("CREATE INDEX IF NOT EXISTS idx_urls_processed_at ON urls(processed_at)")
        await _db_connection.commit()
    return _db_connection

async def db_add_configs(configs: Set[str]) -> int:
    db = await get_db()
    added = 0
    for c in configs:
        try:
            await db.execute("INSERT OR IGNORE INTO configs (config) VALUES (?)", (c,))
            added += 1
        except Exception:
            pass
    await db.commit()
    return added

async def db_mark_url_processed(url: str):
    db = await get_db()
    await db.execute("INSERT OR REPLACE INTO urls (url, processed_at) VALUES (?, ?)", (url, time.time()))
    await db.commit()

async def db_is_url_processed(url: str, expiry_days: int) -> bool:
    db = await get_db()
    async with db.execute("SELECT processed_at FROM urls WHERE url = ?", (url,)) as cursor:
        row = await cursor.fetchone()
    if row:
        if expiry_days <= 0:
            return False
        processed_at_ts = row[0]
        expiry_limit_ts = (datetime.now(timezone.utc) - timedelta(days=expiry_days)).timestamp()
        return processed_at_ts >= expiry_limit_ts
    return False

async def db_get_all_configs() -> List[str]:
    db = await get_db()
    cursor = await db.execute("SELECT config FROM configs")
    rows = await cursor.fetchall()
    return [r[0] for r in rows]

# ============================
# 🧩 بخش ۶: مدیریت Checkpoint
# ============================
async def load_checkpoint() -> Dict:
    try:
        with open(CONFIG_DEFAULTS["CHECKPOINT_FILE"], "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"processed_urls": [], "searched_queries": [], "scanned_manual_repos": []}

async def save_checkpoint(processed_urls: set, searched_queries: set, scanned_manual: set):
    data = {
        "processed_urls": list(processed_urls),
        "searched_queries": list(searched_queries),
        "scanned_manual_repos": list(scanned_manual),
    }
    with open(CONFIG_DEFAULTS["CHECKPOINT_FILE"], "w") as f:
        json.dump(data, f)

# ============================
# 🌐 بخش ۷: توابع اصلی (با فیلتر ساعتی و توقف خودکار)
# ============================
def get_github_token() -> str:
    load_dotenv(dotenv_path=CONFIG_DEFAULTS["ENV_FILE"])
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        logger.error("GitHub token not found in .env file. Please add GITHUB_TOKEN.")
        raise SystemExit(1)
    return token

def get_time_filter_query(qualifier: str = 'pushed') -> str:
    search_days = CONFIG_DEFAULTS.get("SEARCH_PERIOD_DAYS", 0)
    if search_days <= 0:
        return ""
    time_filter_value = datetime.now(timezone.utc) - timedelta(days=search_days)
    return f" {qualifier}:>{time_filter_value.strftime('%Y-%m-%d')}"

@backoff.on_exception(backoff.expo, (aiohttp.ClientError, asyncio.TimeoutError), max_tries=2, max_time=120)
async def fetch_url_content(session: aiohttp.ClientSession, url: str, headers: dict, semaphore: asyncio.Semaphore) -> Optional[str]:
    is_core_api = "api.github.com" in url and "/search/" not in url
    if is_core_api:
        if CORE_LIMIT_REACHED:
            return None
        await check_rate_limit(session, headers, 'core')
    
    async with semaphore:
        try:
            async with session.get(url, headers=headers, timeout=10, allow_redirects=True) as response:
                if response.status == 200:
                    max_bytes = CONFIG_DEFAULTS["MAX_FILE_BYTES"]
                    size = 0
                    chunks = []
                    async for chunk in response.content.iter_chunked(16 * 1024):
                        chunks.append(chunk)
                        size += len(chunk)
                        if max_bytes > 0 and size > max_bytes:
                            logger.debug(f"Skipping oversize file: {url}")
                            return None
                    return b"".join(chunks).decode('utf-8', errors='ignore')
                elif response.status in (403, 429) and "api.github.com" in url:
                    logger.warning(f"Rate limit hit for {url}. Forcing check.")
                    await check_rate_limit(session, headers, 'core' if is_core_api else 'search', force=True)
                    raise aiohttp.ClientError(f"Rate limit: {response.status}")
                else:
                    return None
        except Exception as e:
            logger.debug(f"Fetch error {url}: {e}")
            raise

@backoff.on_exception(backoff.expo, (aiohttp.ClientError, asyncio.TimeoutError), max_tries=5, max_time=300)
async def search_github_api(session: aiohttp.ClientSession, query: str, search_type: str, headers: dict, max_pages: int, semaphore: asyncio.Semaphore, qualifier: str = 'pushed') -> Set:
    results = set()
    full_query = f"{query}{get_time_filter_query(qualifier)}".strip()

    async with semaphore:
        for page in range(1, max_pages + 1):
            await check_rate_limit(session, headers, 'search')
            params = {'q': full_query, 'sort': 'updated', 'order': 'desc', 'per_page': 100, 'page': page}
            try:
                async with session.get(f"https://api.github.com/search/{search_type}", headers=headers, params=params, timeout=25) as resp:
                    if resp.status in (403, 429):
                        await check_rate_limit(session, headers, 'search', force=True)
                        continue
                    if resp.status == 422:
                        logger.warning(f"[Search] Invalid query (422) for: {full_query[:100]}...")
                        break
                    resp.raise_for_status()
                    data = await resp.json()
                    items = data.get('items', [])
                    if not items:
                        break
                    for item in items:
                        if search_type == 'repositories' and 'full_name' in item:
                            try:
                                owner, repo = item['full_name'].split('/', 1)
                                results.add((owner, repo))
                            except Exception:
                                continue
                        elif search_type == 'code' and 'html_url' in item:
                            raw_url = item['html_url'].replace('https://github.com/', 'https://raw.githubusercontent.com/').replace('/blob/', '/')
                            results.add(raw_url)
                    if len(items) < 100:
                        break
            except Exception as e:
                logger.warning(f"Search error for '{query}': {e}")
                break
    return results

async def get_repo_metadata(session, owner, repo, headers, semaphore) -> Optional[dict]:
    if CORE_LIMIT_REACHED:
        return None
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    content = await fetch_url_content(session, api_url, headers, semaphore)
    if content:
        try:
            return json.loads(content)
        except Exception:
            pass
    return None

async def get_tree_for_branch(session, owner, repo, branch, headers, semaphore) -> Optional[dict]:
    if CORE_LIMIT_REACHED:
        return None
    tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    content = await fetch_url_content(session, tree_url, headers, semaphore)
    if content:
        try:
            data = json.loads(content)
            if 'tree' in data:
                return data
        except Exception:
            pass
    return None

async def get_repo_files(session, owner, repo, headers, semaphore) -> Set[str]:
    links = set()
    sub_max_kb = CONFIG_DEFAULTS.get("SUBSCRIPTION_MAX_SIZE_KB", 0) * 1024
    gen_max_bytes = CONFIG_DEFAULTS.get("GENERAL_FILE_MAX_SIZE_KB", 0) * 1024 or 0

    async def process_tree(tree_data, branch):
        for item in tree_data.get('tree', []):
            if item.get('type') != 'blob':
                continue
            path = item.get('path', '')
            path_lower = path.lower()
            if not path_lower.endswith(('.txt', '.yaml', '.yml', '.md', '.json', '.conf')):
                continue
            size = item.get('size', 0)
            limit = sub_max_kb if path_lower.endswith(('.txt', '.yaml', '.yml')) else gen_max_bytes
            if limit > 0 and size > limit:
                continue
            links.add(f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}")

    repo_data = await get_repo_metadata(session, owner, repo, headers, semaphore)
    actual_branch = None
    if repo_data:
        actual_branch = repo_data.get("default_branch")

    if actual_branch:
        tree = await get_tree_for_branch(session, owner, repo, actual_branch, headers, semaphore)
        if tree:
            await process_tree(tree, actual_branch)
            if actual_branch not in ACTIVE_BRANCHES:
                logger.info(f"[BRANCH DISCOVERY] {owner}/{repo} uses '{actual_branch}'")
                await branch_manager.add(actual_branch)
        if links:
            return links

    branches_to_check = set(ACTIVE_BRANCHES)
    if actual_branch:
        branches_to_check.discard(actual_branch)
    for branch in branches_to_check:
        if CORE_LIMIT_REACHED:
            break
        tree = await get_tree_for_branch(session, owner, repo, branch, headers, semaphore)
        if tree:
            await process_tree(tree, branch)
            if links:
                break
    return links

async def check_and_scan_repo(session, owner, repo, headers, semaphores, url_set):
    """
    اسکن یک مخزن فقط در صورتی که در MAX_AGE_HOURS ساعت گذشته push داشته باشد.
    """
    if CORE_LIMIT_REACHED:
        return
    repo_data = await get_repo_metadata(session, owner, repo, headers, semaphores['fetch'])
    if not repo_data:
        return

    # فیلتر ساعتی دقیق
    max_hours = CONFIG_DEFAULTS.get("MAX_AGE_HOURS", 0)
    if max_hours > 0:
        pushed_at_str = repo_data.get("pushed_at") or repo_data.get("updated_at")
        if pushed_at_str:
            try:
                pushed_at = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_hours)
                if pushed_at < cutoff_time:
                    return  # قدیمی است
            except Exception:
                pass

    files = await get_repo_files(session, owner, repo, headers, semaphores['fetch'])
    if files:
        url_set.update(files)

# ============================
# 🔍 بخش ۸: پردازش URL و استخراج نهایی
# ============================
async def process_url(session, url, headers, processed_urls_session, cache, semaphore, depth=0):
    if depth > CONFIG_DEFAULTS["MAX_RECURSION_DEPTH"] or url in processed_urls_session:
        return
    processed_urls_session.add(url)

    if cache.is_cached(url) or await db_is_url_processed(url, CONFIG_DEFAULTS["CACHE_EXPIRY_DAYS"]):
        return

    content = await fetch_url_content(session, url, headers, semaphore)
    if not content:
        cache.add(url)
        await db_mark_url_processed(url)
        return

    found_configs = set()
    try:
        found_configs.update(V2RAY_CONFIG_PATTERN.findall(content))
    except Exception:
        pass

    try:
        stripped = content.strip()
        if 16 <= len(stripped) <= 200000 and re.fullmatch(r'^[A-Za-z0-9_\-=\s/]+$', stripped[:2000]):
            padding = (4 - len(stripped) % 4) % 4
            decoded = base64.urlsafe_b64decode(stripped + '=' * padding).decode('utf-8', errors='ignore')
            found_configs.update(V2RAY_CONFIG_PATTERN.findall(decoded))
    except Exception:
        pass

    if found_configs:
        await db_add_configs(found_configs)

    cache.add(url)
    await db_mark_url_processed(url)

    if depth + 1 <= CONFIG_DEFAULTS["MAX_RECURSION_DEPTH"]:
        sub_links = SUB_LINK_PATTERN.findall(content)
        tasks = [process_url(session, sub, headers, processed_urls_session, cache, semaphore, depth+1)
                 for sub in sub_links if sub not in processed_urls_session]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

# ============================
# 🚀 بخش ۹: تابع اصلی (هماهنگ با فیلتر ساعتی)
# ============================
async def main():
    logger.info("🚀 Starting Optimized Collector (Hourly Filter + Auto-Stop)")
    start_time = time.time()

    token = get_github_token()
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
        "User-Agent": "OptimizedCollector/2.4"
    }

    cache = CacheManager(CONFIG_DEFAULTS["CACHE_FILE"], CONFIG_DEFAULTS["CACHE_EXPIRY_DAYS"])
    fetch_semaphore = asyncio.Semaphore(CONFIG_DEFAULTS["GENERAL_CONCURRENT_REQUESTS"])
    search_semaphore = asyncio.Semaphore(CONFIG_DEFAULTS["SEARCH_API_CONCURRENCY"])

    checkpoint = await load_checkpoint()
    processed_urls_session = set(checkpoint.get("processed_urls", []))
    searched_queries = set(checkpoint.get("searched_queries", []))
    scanned_manual_repos = set(checkpoint.get("scanned_manual_repos", []))

    connector = aiohttp.TCPConnector(limit=CONFIG_DEFAULTS["AIOHTTP_CONNECTION_LIMIT"])
    async with aiohttp.ClientSession(connector=connector) as session:

        await check_rate_limit(session, headers, 'core', force=True)
        core_remaining = RATE_STATE['core']['remaining']
        core_budget_for_scan = core_remaining - (CONFIG_DEFAULTS["TARGET_CORE_CONSUMPTION"] * 0.3)
        dynamic_max_scan = max(0, int(core_budget_for_scan / CONFIG_DEFAULTS["CORE_PER_REPO_ESTIMATE"]))
        final_max_scan = min(CONFIG_DEFAULTS["MAX_DISCOVERED_REPOS_TO_SCAN"], dynamic_max_scan)
        logger.info(f"Core Remaining: {core_remaining}. Max scan: {final_max_scan}")

        # --- Stage 1: Search ---
        logger.info("--- Stage 1: GitHub Search (pushed + updated) ---")
        search_tasks = []
        for q in REPO_SEARCH_QUERIES:
            if q not in searched_queries:
                search_tasks.append(asyncio.create_task(
                    search_github_api(session, q, 'repositories', headers, CONFIG_DEFAULTS["REPO_SEARCH_PAGES"], search_semaphore, qualifier='pushed')
                ))
        for q in CODE_SEARCH_QUERIES:
            if q not in searched_queries:
                search_tasks.append(asyncio.create_task(
                    search_github_api(session, q, 'code', headers, CONFIG_DEFAULTS["CODE_SEARCH_PAGES"], search_semaphore, qualifier='updated')
                ))
        for q in EXTRA_UPDATED_REPO_QUERIES:
            search_tasks.append(asyncio.create_task(
                search_github_api(session, q, 'repositories', headers, CONFIG_DEFAULTS["EXTRA_UPDATED_REPO_PAGES"], search_semaphore, qualifier='updated')
            ))

        logger.info(f"Total search tasks: {len(search_tasks)}")
        search_results = []
        for fut in tqdm(asyncio.as_completed(search_tasks), total=len(search_tasks), desc="[Stage 1] Searches"):
            try:
                res = await fut
                search_results.append(res)
            except Exception as e:
                logger.warning(f"Search task error: {e}")

        for q in REPO_SEARCH_QUERIES:
            searched_queries.add(q)
        for q in CODE_SEARCH_QUERIES:
            searched_queries.add(q)

        discovered_repo_tuples = {item for res in search_results for item in res if isinstance(item, tuple)}
        discovered_code_urls = {item for res in search_results for item in res if isinstance(item, str)}
        logger.info(f"Discovered {len(discovered_repo_tuples)} repos, {len(discovered_code_urls)} code URLs.")

        # اگر Core تمام شده، مستقیماً به Stage 3 برو
        if CORE_LIMIT_REACHED:
            logger.warning("Core limit reached before scanning. Skipping Stage 2.")
            source_urls = set(discovered_code_urls)
        else:
            # --- Stage 2: Scan repos with hourly filter ---
            logger.info("--- Stage 2: Scanning Repos (Hourly Filter Active) ---")
            source_urls = set(discovered_code_urls)
            semaphores = {'fetch': fetch_semaphore, 'search': search_semaphore}

            manual_to_scan = [(o, r) for o, r in MANUAL_REPOS_TO_SCAN if f"{o}/{r}" not in scanned_manual_repos]
            if manual_to_scan and not CORE_LIMIT_REACHED:
                manual_tasks = [asyncio.create_task(check_and_scan_repo(session, o, r, headers, semaphores, source_urls)) for o, r in manual_to_scan]
                for fut in tqdm(asyncio.as_completed(manual_tasks), total=len(manual_tasks), desc="[Stage 2] Manual Repos"):
                    try:
                        await fut
                    except Exception as e:
                        logger.warning(f"Manual repo error: {e}")
                    if CORE_LIMIT_REACHED:
                        logger.warning("Core limit reached during manual scan.")
                        break
                for o, r in manual_to_scan:
                    scanned_manual_repos.add(f"{o}/{r}")

            discovered_only = discovered_repo_tuples - set(MANUAL_REPOS_TO_SCAN)
            repos_to_scan = list(discovered_only)[:final_max_scan]
            if repos_to_scan and not CORE_LIMIT_REACHED:
                logger.info(f"Scanning {len(repos_to_scan)} discovered repos")
                repo_tasks = [asyncio.create_task(check_and_scan_repo(session, o, r, headers, semaphores, source_urls)) for o, r in repos_to_scan]
                for fut in tqdm(asyncio.as_completed(repo_tasks), total=len(repo_tasks), desc="[Stage 2] Discovered Repos"):
                    try:
                        await fut
                    except Exception as e:
                        logger.warning(f"Discovered repo error: {e}")
                    if CORE_LIMIT_REACHED:
                        logger.warning("Core limit reached during discovered scan.")
                        break

            await save_checkpoint(processed_urls_session, searched_queries, scanned_manual_repos)

        logger.info(f"Total source URLs (before filtering): {len(source_urls)}")

        # --- Stage 3: Process URLs ---
        logger.info("--- Stage 3: Processing URLs ---")
        urls_to_process = []
        for u in source_urls:
            if 'github.com' not in u and 'raw.githubusercontent.com' not in u:
                continue
            if u in processed_urls_session:
                continue
            if cache.is_cached(u) or await db_is_url_processed(u, CONFIG_DEFAULTS["CACHE_EXPIRY_DAYS"]):
                continue
            urls_to_process.append(u)

        logger.info(f"New URLs to process: {len(urls_to_process)}")
        batch_size = CONFIG_DEFAULTS["BATCH_SIZE"]
        for i in range(0, len(urls_to_process), batch_size):
            batch = urls_to_process[i:i+batch_size]
            tasks = [asyncio.create_task(process_url(session, url, headers, processed_urls_session, cache, fetch_semaphore, 0))
                     for url in batch]
            for fut in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"[Stage 3] Batch {i//batch_size + 1}"):
                try:
                    await fut
                except Exception as e:
                    logger.debug(f"Process error: {e}")
            await save_checkpoint(processed_urls_session, searched_queries, scanned_manual_repos)

    # --- Stage 4: Final Export ---
    logger.info("--- Stage 4: Final Export ---")
    cache._save_cache()
    all_configs = await db_get_all_configs()
    unique_configs = {c.strip() for c in all_configs if c.strip()}
    logger.info(f"✅ Total unique configs: {len(unique_configs)}")
    if unique_configs:
        with open(CONFIG_DEFAULTS["OUTPUT_FILE"], "w", encoding="utf-8") as f:
            for c in sorted(unique_configs)[:1000]:
                f.write(c + "\n")
        logger.info(f"Saved to '{CONFIG_DEFAULTS['OUTPUT_FILE']}'")
    else:
        logger.warning("⚠️ No configs found.")

    if CORE_LIMIT_REACHED:
        logger.warning("⛔ Script finished early because Core limit was reached.")
    else:
        logger.info("✅ Script completed normally without hitting Core limit.")

    # دیگر Checkpoint را پاک نکن تا اجراهای بعدی Stage 1 را تکرار نکنند
    # if os.path.exists(CONFIG_DEFAULTS["CHECKPOINT_FILE"]):
    #     os.remove(CONFIG_DEFAULTS["CHECKPOINT_FILE"])
    logger.info(f"--- Finished in {int(time.time() - start_time)}s ---")
    logger.info(f"Estimated Core used: {TOTAL_CORE_USED}")

if __name__ == "__main__":
    if os.name == 'nt':
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted. Progress saved in checkpoint.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
