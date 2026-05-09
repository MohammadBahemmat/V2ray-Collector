#!/usr/bin/env python3
import os
import sys
import asyncio
import aiohttp
import aiosqlite
import base64
import re
import json
import logging
import time
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from tqdm import tqdm
import backoff
from typing import Dict, Optional, Set, List, Tuple

# ============================
# ⚙️ بخش ۱: پیکربندی نهایی (ساعتی، توقف خودکار و ذخیره‌ی شاخه‌ها)
# ============================
CONFIG_DEFAULTS = {
    "SEARCH_PERIOD_DAYS": 0,
    "REPO_SEARCH_PAGES": 0,
    "CODE_SEARCH_PAGES": 0,
    "EXTRA_UPDATED_REPO_PAGES": 0,
    "MAX_AGE_HOURS": 1,

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
    "MAX_FILE_BYTES": 10 * 1024 * 1024,
    "OUTPUT_FILE": "servers_collected.txt",
    "DB_FILE": "collector.db",
    "ENV_FILE": ".env",
    "CACHE_FILE": "collector_cache.json",
    "CACHE_EXPIRY_DAYS": 1,
    "CHECKPOINT_FILE": "checkpoint.json",
    "DISCOVERED_BRANCHES_FILE": "discovered_branches.json",
}

# ============================
# 🔎 بخش ۲: منابع و کوئری‌ها
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
'codex/anfisa-vpn-publish', 'init', 'Monad', 'claude/apartment-listing-monitor-2U2yQ',
'UwU', 'SeansLifeArchive_Images_Clash-of-Clans_Y2026_Main-dev'
]

REPO_SEARCH_QUERIES = sorted(list(set([

])))

CODE_SEARCH_QUERIES = sorted(list(set([

])))

EXTRA_UPDATED_REPO_QUERIES = [

]

MANUAL_REPOS_TO_SCAN = sorted(list(set([
("DoomTiger", "MikuBoxForAndroid"),
("Makale25", "cloudflare-dns-worker"),
("SiddanthEmani", "kyros"),
("Suraj24w", "backlink-analyzer"),
("jeliasrm", "req-replace"),
("mohamedbelasy", "LfsProxy"),
("MuhammadUnaiz", "export-followers-instagram"),
("apippp11", "automatic-backlink-indexer"),
("bated-genuscricetus536", "webhook-proxy"),
("nma12323", "snip"),
("Sihabho2566", "SeansLifeArchive_Images_Clash-of-Clans_Y2026"),
("noxi401", "vpn-server-provider"),
("Levisubartesian416", "chines"),
("Likely-kinsman623", "Bitscoper_SSTV_Icecast_Broadcaster"),
("Omid-0x0x0x", "vless"),
("azatabd", "v2ray_fetch"),
("mahazoualedji595", "secure_multisite_vpn"),
("Alex123Aaaaaa", "windows"),
("Zangadze1101", "Convert"),
("weivina", "flzt-auto-checkin"),
("Chondrinvolubility888", "Privacy-Relay-System"),
("Filterrr", "AdBlock_Rule_For_Clash"),
("gooseteam-hackers", "GooseVPN"),
("monkey6468", "69yun69"),
("southpart302", "vless-wizard"),
("Fewgenusdendroaspis337", "v2rayN"),
("Loaila1680", "parse-sse"),
("thaikhan9717", "3x-ui"),
("Fatherless-costusoil269", "ProxyMod"),
("Thunderous-cauliflower413", "DeSSyPHER"),
("abdallahhaytham", "AbdallahHaytham"),
("amberpepper", "ProxyWeave"),
("cmepthuklolka1", "vpn-bot"),
("fmjnax", "dynamic-proxy"),
("genyleap", "GenyConnect"),
("kort0881", "proxy-auto-checker"),
("rokoman", "tor_node_list"),
("rtwo2", "FastNodes"),
("zaiyin", "metaclsh-scraper"),
("Anthon3284", "IKESS"),
("Daneslack455", "ESP8266-DHT22-SSD1306-OLED-Temperature-Humidity-Monitor-MicroPython-"),
("crossxx-labs", "free-proxy"),
("cys92096", "python-xray-argo"),
("ENTERPILOT", "GoModel"),
("F0rc3Run", "F0rc3Run"),
("Flexvent", "AioProx"),
("Hjsosn", "FireWall-Blocks"),
("codonaft", "broadcastr"),
("johncenadududu", "pytorch-simsiam-contrastive-ssl"),
("kanokphol3013", "RSN"),
("mock-server", "mockserver-monorepo"),
("sakata114", "work"),
("sandyemousy17", "wireguard-hook"),
("Davoyan", "xray-routing"),
("Potterli20", "trojan-go-fork"),
("Stefen-io", "n9r-dockerized-deployment"),
("bien000", "the-watcher-ssr"),
("thorkx", "hockey-proxy"),
("SAQLAINComsats", "the-watcher-ssr"),
("Vepashka94", "vpngate-mirror"),
("henrijaime", "Flutter-Awesome-Dialogs"),
("lingga1997", "full-stack-proxy-nginx-n8n-for-everyone-with-docker-compose"),
("DIGYXL", "venom"),
("NASEER-MAX", "ssSign.github.io"),
("SimoneErrigo", "Janus"),
("bach999-vamous", "Kimi-K2"),
("cgy530627", "Proton-VPN"),
("folksreptilian850", "SSM-PC"),
("gtaiv005", "PublicProxyList"),
("idkdevoo", "intercept-wave-upstream"),
("tosayn386-dotcom", "ai-news-proxy"),
("touhedulislam", "k8s-proxy"),
("tudo123112312", "wireguard"),
("Hash-Ag", "libsocks"),
("LeiyuG", "Clash"),
("Mide-IT", "cdn-ip-ranges"),
("Parth3199", "10ssoonBase"),
("adesh777", "axios"),
("diflow95400", "x-evolution"),
("ma3uk", "russia-clash-rules"),
("neshat73", "proxycache"),
("Alexander-vecos", "ssmt"),
("SPARTAN2006", "is-in-ssh"),
("pete731", "sati"),
("ErTmannobom", "terraform-aws-vpc-peering"),
("Nancykharbanda", "ssh-tutorial-fr"),
("Roberto7771", "sso-ui-cdn"),
("kort0881", "vpn-aggregator"),
("lchw1", "my-proxy-sub"),
("mrkpjc", "castari-proxy"),
("nagelboi", "DDOS47"),
("petrpstepanov-svg", "kp-ssd"),
("ahmedzaik", "Pi-Hole-Setup"),
("apindipsi22", "Securing-SSH-Access-on-Proxmox-VE-9"),
("eyaorganization", "To-do-App"),
("learnodishahelp-cmd", "sscdash"),
("werea4947-sys", "day_ss"),
("afr0700", "ProxyList"),
("anooshali201", "CryptoLens"),
("ngthdong", "vpn"),
("Filterrr", "FlClash"),
("Stepan2222000", "clash-rulesets"),
("AlxVoropaev", "informer_bot"),
("BlacKSnowDot0", "Proxy-Pulse"),
("nyeinkokoaung404", "multi-proxy-config-fetcher"),
("sckang76", "SSU_CODE"),
("tobileng", "vless-ws-cdn-tunnel-setup"),
("saqi9912", "homelab-vpn-journey"),
("tokenpak", "tokenpak"),
("Harinavalona-web", "XWan"),
("LuisBraLo", "PPHAS_SIS_SSR"),
("YawStar", "Proxy-Hunter"),
("ahmedmagdy0000", "NORD"),
("danielfree19", "proxydock"),
("jlintvet", "SSTv2"),
("mfuu", "v2ray"),
("naseem499379", "mihomo_yamls"),
("Niekeisha", "business-gemini-pool"),
("Raffyn2", "python-api-base"),
("adan202", "Abelssoft-SSD-Fresh-Latest-Patch"),
("lhhkuki", "deepseek-proxy-manager"),
("wardnet", "wardnet"),
("wasimeahmed98-coder98", "clash-converter"),
("4n0nymou3", "multi-proxy-config-fetcher"),
("AJlv420", "VPN-BlackBox-Checker"),
("Arefgh72", "v2ray-proxy-pars-tester"),
("DeepakMudili", "cf-ssl-check"),
("Preethamvarma007", "privacy-first-network"),
("Pxys-io", "DailyProxyList"),
("Pxys-io", "proxylistdaily"),
("giuseppefabiani78-hash", "mepa-rdo-proxy"),
("Jha0rahul", "Business-OpenAPI"),
("clerzg", "quick-argo-xray"),
("lonecale", "Rules"),
("peptang12", "pingap-docker-provider"),
("qist", "xray-ui"),
("treasonking", "Capstone_Design"),
("chukwu-patrick", "five-worker"),
("braenmendes", "ssf"),
("jeric765", "wireguard"),
("Nemu-x", "privWL-clash"),
("aloplus", "AloPlusVPN"),
("sodardyjiber", "DailyProxyCheck"),
("Hill-1024", "simpleUI"),
("Sabariranil", "nashvpn"),
("Snishil", "Fisch-Script"),
("bg-grira53", "sql-server-security-audit"),
("envoyproxy", "envoy"),
("shabane", "kamaji"),
("xq25478", "OpenProxyRouter"),
("Dmitriy190424", "instruction"),
("S8Y", "mullvad-pac"),
("XXX5X", "iptables"),
("akshaymishra78600", "proxy-gem-noload"),
("bytedecode", "bytesflows"),
("patel-Asan", "SSC1"),
("Fishin09", "GodzillaNodeJsPayload"),
("TarekBN", "luci-app-ech-workers"),
("ThongLuc2k3", "Prompt-Guided-XRay-Segmentation"),
("alimalik122", "chest-xray-covid19-classification"),
("igikukik59", "Proxy-Google-Checker"),
("matrixsy", "cf_ech_worker"),
("xxx3-lab", "ahiteo-vpn"),
("Rislinstiligo23", "sss"),
("kongkong7777", "github-enterprise-ai-proxy"),
("pogiako123pak", "go-ssh"),
("5a5ehw1-star", "ssq"),
("ENAHSIN", "mqttstuff"),
("Faateemaa", "SnippetForge"),
("Grifexdev", "CR-aiogram-bot"),
("RasputinofThrace", "VerDix"),
("heinhtetzaw346", "sshu"),
("sacreations", "Proxy-Monitor"),
("AYMANE-GYM", "mise-setup-verification-action"),
("Azarscientist", "ssi-protocol-oss"),
("abrar699979", "Fortnite-Mobile-SSL-Bypass"),
("mano4now", "plant-protect"),
("Babaproates", "php-text-validator-lib"),
("MRISOON", "instagram-comments-replies-and-subscribers-scraper-no-cookie"),
("TuanMinPay", "live-proxy"),
("iseeyoou26-wq", "CryNet-SysTems-VPN-vless"),
("mzyui", "proxy-list"),
("spider1605", "cf-workflow-rollback"),
("Ahmdrady", "CloudLab"),
("NodePassProject", "Anywhere"),
("WillyMS21", "Cloudflare-Bybass-CDP-Chromium"),
("ahlembnhsn", "An0m0s-VPN"),
("alexanderersej", "fanqiang"),
("bcst17", "proxy-manage"),
("libnyanpasu", "clash-nyanpasu"),
("SHADOWWINGZ69", "ECH-CF"),
("SukrithTripathii", "ThreadPoolExecChain"),
("TheCrowCreature", "v2rayExtractor"),
("cheo87", "vless-all-in-one"),
("linuxhobby", "autoinstallv2ray"),
("linuxhobby", "xray-v2ray-install"),
("suiyuebaobao", "raypilot-xray-panel"),
("Swift-tunnel", "swifttunnel-app"),
("DafaSya", "ios-developer-agents"),
("camer1111", "ss.com-vacancy-search-python"),
("pnv06", "betterclaude-workers"),
("BrandonPerez915", "CineList"),
("KaringX", "clashmi"),
("moinugare19", "ssh-client-mcp"),
("noob-master-cell", "Gatekeeper"),
("Abdelmalik9", "microservices-lab"),
("fortniteseason6", "LoonLab"),
("palamist", "win-mediakey-lolbin"),
("colhoes1337", "local-ssl-automate"),
("dinoz0rg", "proxy-list"),
("ferrarigamer458italia", "metube"),
("kylepeart21", "get-icmp9-node"),
("Michigan5", "oports"),
("Nopekszz", "mssh"),
("SaharSaam", "juziyun"),
("haha123BC52", "SOCKS5-Proxies"),
("mayank164", "loveFreeTools"),
("pero082", "wg-orchestrator"),
("LukePham163", "docker-compose-servarr-with-gluetun"),
("abdul841434", "telegram-gpt-template"),
("jqmzfj", "wg-clash-admin"),
("zenjan1", "sshs"),
("MichaelPaddon", "aloha"),
("Munna89", "homelab-horizon"),
("jessi-2023", "homebrew-tap"),
("Phogapro", "cloud-phone-config"),
("arshveer1208", "ssh-brute-force-splunk"),
("hcd233", "aris-proxy-api"),
("manavkushwaha10", "apple-health"),
("Lokmandev", "codenex-ai-api-proxy"),
("bucissss", "Xray-VPN-OneClick"),
("Freddd13", "cloudreve-anisub"),
("Kineki07", "tuicr"),
("ada20204", "clash-override-chain-proxy"),
("217heidai", "adblockfilters"),
("Jaymarenad", "aws-api-gateway-tools"),
("Mohamedafifi14", "canban_board"),
("Rm6B", "Best_free_news_api"),
("VersaVin", "CF-Workers-UsagePanel"),
("macosta88", "Splunk-Dashboard-for-SSH-Logs"),
("realbabafingo", "gatepath-threat-model"),
("zaishe-crypto", "Best-Tiktok-human-bot"),
("Kd-devv", "P-BOX"),
("hacker7221", "ai-debates"),
("kkoltongi99", "speedc"),
("tentangsaya78", "ssdc-theme"),
("DSpace24", "stash"),
("Ian-Lusule", "Proxies"),
("Pritz96", "sosa-ssn-ontology-editors-edition-subclass-diagram"),
("Tusked", "IPcheck-workers"),
("mourya11", "honghongcf-workers-vlesspanel-d1"),
("nehrabalar", "white_list_internet"),
("BlazeAuraX", "ProxyForFree"),
("coffeegrind123", "awg-easy-rs"),
("shaoyouvip", "free"),
("DoraOtari", "slipstream"),
("FLAVIO3333", "ProxyForFree"),
("Rohit-Virkar", "DDoSSCAN"),
("WolfSahil", "Win32kHooker"),
("officialputuid", "ProxyForEveryone"),
("2dust", "v2rayNG"),
("blsdncn", "MCFuzz"),
("estebanbkk-glitch", "switch"),
("kingstreet637", "godscanner"),
("wuqb2i4f", "xray-config-toolkit"),
("Aplikasi-Berbasis-Platform-S1IF-11-04", "Pertemuan-3"),
("DaPDOG", "ucp-proxy"),
("Dylan-Emanuel", "cloudflare-bypass-2026"),
("Infisical", "agent-vault"),
("UMVERTH", "ssz-lensing"),
("justinechris", "chinawallvpn.github.io"),
("skycoin", "skywire"),
("stacksjs", "rpx"),
("Vergorini12", "simple-todo-list-mern"),
("Anamalikay", "IPL-AUCTION-CLASH"),
("CB-X2-Jun", "proxy-lists"),
("LiMingda-101212", "Proxy-Pool-Actions"),
("hanteng", "ACM-article-SSbD-MVB"),
("pepitopere666", "WireTapper"),
("richdz12", "traffic-guard"),
("HECTORjoo", "openclaw-windows-hub"),
("LuisF-92", "Freedom-V2Ray"),
("MilanMishutushkin", "tailscale"),
("Raheem39", "cloudflare-tools"),
("Shazada0070", "nfqws2-keenetic"),
("moriela1", "zero"),
("nyt213", "police-chat-bot"),
("quesoXD12", "nordvpn-wg"),
("tczee36", "xmr-nodes"),
("y-Adrian", "db-proxy"),
("LeonFH2005", "wireguard"),
("balaharans2904", "Windows-11-Debloat-AI-Slop-Removal"),
("connecting001", "blas-base-ssyr2"),
("denmrnngp-cloud", "hiddify-steam-deck"),
("denmrnngp-cloud", "hiddify-steam-deck-vpn"),
("paul86Wilson", "ssdjis8aorobertsusan43271"),
("sajkan81", "ecommerce-template"),
("sus112112", "PYDNS-Scanner"),
("theMavionx", "Clash"),
("DanybossGDpro", "router-vpn"),
("Fggp09", "mullvad-connection-status"),
("GuyZangi", "clash-residential-proxy-parser"),
("QuiteAFancyEmerald", "InvisiProxy"),
("Racc2006", "RealityGhost"),
("ThaminduDisnaZ", "Esena-News-Github-Bot"),
("Toothylol", "Kiro2api-Node"),
("jesusmedrandam", "miniature-octo-palm-tree"),
("llaravell", "clash-rules"),
("mukeshkannan18", "SSHBot"),
("rowdy-ff", "javid-mask"),
("Coursa4lyfe", "NekoFlare"),
("VPJayasinghe", "Proxymaze1"),
("canmi21", "vane"),
("Obama907", "theGoillot"),
("Watfaq", "clash-rs"),
("arkaih", "VPS_BOT_X"),
("elcompastreaming18-svg", "Prison-Lift-Clash-Helper"),
("Manueleue", "video-audit-platform"),
("Tsprnay", "Proxy-lists"),
("judawu", "nsx"),
("partout-io", "partout"),
("125jkop", "SSD_BABP"),
("AHANOV-CORPORATION", "ljg-skill-xray-paper"),
("Aldemirps", "ArrSuite-Guide"),
("Ilyacom4ik", "free-v2ray-2026"),
("Jihad7x", "mie"),
("yourssu", "ssufid-sites"),
("MrBeert", "xray-ru-en"),
("SazErenos", "NekoBox"),
("Zhao242", "ShanYangProxyApps"),
("bitesk782-wq", "ljg-skill-xray-book"),
("hector561", "linux-client"),
("imegabiz", "DPI-Phantom"),
("mauricegift", "free-proxies"),
("tetratorus", "llm-proxy"),
("yrteresr", "ljg-skill-xray-article"),
("RainMeriloo", "cf-browser-cdp"),
("Sploo-Scripts", "TheWiz-PS5-Easy-FFpkg-Maker"),
("bigsilly94", "mtproto-installer"),
("dmitriistekolnikov", "Free_vpns_for_Russ"),
("feiniao1-VPN", "Free-Accelerator---VPN"),
("feiniaovpn", "Free-Airport---VPN"),
("feiniaovpn", "Office---VPN"),
("halc8312", "SStory"),
("ludivor", "ssiptv"),
("preetcse", "vless-xtls-vision-installer"),
("sholdee", "caddy-proxy-cloudflare"),
("xCtersReal", "V2rayFree"),
("ShatakVPN", "ConfigForge-V2Ray"),
("feiniaovpn", "Shared-VPN"),
("HikerX", "yunfan_subscribe"),
("NiceVPN123", "NiceVPN"),
("Spellinfo", "sstop"),
("darklord-end", "-Graphene-VPN"),
("feiniaovpn", "Free-VPN"),
("Cellxv7", "testflight-lower-install"),
("Kirillo4ka", "eavevpn-configs"),
("MFSGA", "Chimera"),
("RealDefenderSqueeze", "Hamachi-Pro-Crack-Windows-2026"),
("Wind7077", "yml-vless"),
("elliottophellia", "proxylist"),
("iwh3n", "tg-proxy"),
("theriturajps", "proxy-list"),
("Centaurbenpulse", "Mullvad-VPN-Premium-Windows-2026"),
("MdSadiqMd", "TraceZero"),
("Sequen0", "ssd-dispatch-tracker"),
("alberti12345", "pfopn-convert"),
("andigwandi", "free-proxy"),
("fanshuiyu", "invisix"),
("hamedcode", "port-based-v2ray-configs"),
("CubeCashierCleanse", "NordVPN-License-2026"),
("DisplayAdvance", "UrbanVPN-New-Crack-2026"),
("MAHDI-143", "proxy-checker"),
("Yam3DLife", "vpn-subscriptions"),
("ayon-ssp", "ayon-ssp"),
("kasesm", "Free-Config"),
("menasamuel1835", "Pumpfun-Bundler"),
("mingko3", "socks5-clash-proxy"),
("mohameddorgham32", "open-wire"),
("plsn1337", "white-vless"),
("sjtlehbie", "meow-ssh"),
("supercrypto1984", "api-benchmark-monitor"),
("Anna4355", "aws-physical-server-hybrid-backup-architecture"),
("Argh73", "V2Ray-Vault"),
("Epodonios", "v2ray-configs"),
("GunnerInflate", "SSE-Pandora-Behaviour-Engine-Plus"),
("Innerplonote", "Mullvad-VPN-Premium-2026"),
("Nemka-cmd", "proxy"),
("RPSandyGaming", "awesome-terminal-for-ai"),
("SniperGoal", "mac-media-stack-advanced"),
("Taylor-cheater", "free-coding-models"),
("Telegram-FZ-LLC", "Telegram-Proxy"),
("bk88collab", "hiddify-app"),
("koteshwr-ra", "linux-mac"),
("logoministerroad", "Windscribe-VPN-2026-ba"),
("relc112885", "aws-tally-backup-fsx-hybrid-architecture"),
("spincat", "SmartProxyPipeline"),
("sumanrio", "mcp-atlassian-extended"),
("2cydg", "knot"),
("Alexey71", "opera-proxy"),
("Amith7721", "Cognitive_Claw"),
("Anonym0usWork1221", "Free-Proxies"),
("Boss-venkatesh", "Gost-Tunnel-Manager"),
("Munachukwuw", "Best-Free-Proxys"),
("TechSpiritSS", "TechSpiritSS"),
("XIXV2RAY", "XIX-v2ray"),
("alireza-rezaee", "tor-nodes"),
("googledslz", "multi-proxy-config_dslz"),
("rankedcs", "Myvlesses"),
("shriman-dev", "dns-blocklist"),
("Aeryl", "node-utils-1771921901-4"),
("Paul236", "node-utils-1771917038-1"),
("Potterli20", "hosts"),
("Thiago12097", "gluetun-webui"),
("badhuamao", "FasterVPN-Auto"),
("cochystars", "FreeProxyProxy"),
("lalifeier", "proxy-scraper"),
("mheidari98", ".proxy"),
("vasavibusetty", "DyberVPN"),
("S13LEDION", "idea-reality-mcp"),
("SSSSGGAAMMIINNGG", "devcontainer"),
("adsikramlink", "proxy"),
("dani9701", "python-apple-fm-sdk"),
("elmaliaa", "AdderBoard"),
("kort0881", "telegram-proxy-collector"),
("notfaj", "ester"),
("rico-cell", "clash-proxy-sub"),
("tonystrak1001-ops", "free-vpn"),
("yosik1992", "proxy-grabber."),
("Dark675sfdsgfxh", "xray-reality-setup"),
("ExteriorSerf17", "Linken-Sphere-2-Crack-2026"),
("KaWaIDeSuNe", "xingjiabijichang"),
("Keliz271", "Lantern"),
("Moha-zh11", "codexapp-windows-rebuild"),
("Seeh-Saah", "awesome-free-proxy-list"),
("UplandJacob", "Upland-HA-Addons"),
("aljihadhasan220", "ssstiktok"),
("feiniao1-VPN", "Wall-Climbing-Accelerator---VPN"),
("jingjiangy", "SsPlatform"),
("marouchsail", "aigateway"),
("mohammmdmdmkdmewof", "v2rayConfigsForYou"),
("shervinofpersia", "VPN-client-last-releases"),
("ssbanerje", "ssbanerje"),
("triposat", "amazon-price-monitor"),
("zackprawaret", "MiddleFreeWare"),
("9Knight9n", "v2ray-aggregator"),
("Argh94", "V2RayAutoConfig"),
("Epodonios", "bulk-xray-v2ray-vless-vmess-...-configs"),
("Hamedzah", "vpn_config"),
("Micky203", "zenproxy"),
("MixCoatl-44", "Proxy-Scanner"),
("SANTOSHPATIL2004", "Telegram-Proxy"),
("Youth787", "SSAFY_Algorithm_Study"),
("dr-andytseng", "afl-calendar-feeds"),
("feiniaovpn", "feiniao-VPN"),
("ssaaaammm", "ssaaaammm"),
("Cepreu54", "vless-clean"),
("GpuLieutenantView", "UrbanVPN-Crack-Latest-2026"),
("Jethro94", "nats-server"),
("Luisveloza", "api-manager"),
("SeizeSummonerTouch", "Kaspersky-Premium-2026"),
("Splitkraedge", "Windscribe-VPN-2026-ts"),
("VampXDH", "MyProxy"),
("Vepashka94", "vpngate_web"),
("mazda4940original", "PortWorld"),
("yesh2002", "fastapi-presearch"),
("AniketPaul44", "lextex-homelab"),
("Dapperdan1956", "GeminiOS"),
("MhdiTaheri", "V2rayCollector"),
("Mr-Meshky", "vify"),
("Tharindu-Nimsara", "proxymaze-cyphersentinels"),
("aditya123-coder", "GoatsPass"),
("ahmedhelala", "xuruowei-forever"),
("amanraj76105", "EasyProxiesV2"),
("annacriativars2", "synapse-protocol"),
("elanski", "proxy-preflight"),
("moksharth77", "mcp-remnawave"),
("mysistoken", "ghost-complete"),
("parsamrrelax", "auto-warp-config"),
("qitry", "Qimi-API"),
("vanodevium", "node-framework-stars"),
("Access-At", "proxy-scraping"),
("Alex-010101", "raspberry-pi-media-stack"),
("AliEgeErzin", "ssaju"),
("LinkPrinceLaud", "Windscribe-VPN-2026"),
("Moatasemmofadal", "ssd"),
("Sobobo32", "cli-proxy-API-Center"),
("TrippyDawg", "tg-ws-proxy"),
("alihusains", "sstp-vpn"),
("g-star1024", "my-clash-subscribe"),
("lexariley", "v2ray-test"),
("saliniarjun", "EvilAP"),
("skyvictordolmen", "Opera-VPN-2026"),
("tairimehdi", "tcp-ip-attack-lab"),
("volondsespel-png", "vpn-key-collector"),
("wenxig", "free-nodes-sub"),
("Chainsholaud", "McAfee-Total-Protection-2026"),
("Danialsamadi", "v2go"),
("Davi111776", "Overlord"),
("Jayysofficial", "redpill"),
("Maximusssr8", "ManusMajorka"),
("NiCkLP76667", "Halt.rs"),
("RaineMtF", "v2rayse"),
("Surfboardv2ray", "TGParse"),
("TG-NAV", "nodeshare"),
("TellerPiazza", "UrbanVPN-Crack-2026"),
("ZhurinDanil", "clash-sub"),
("anayadora-100rit", "CyberGhost-VPN-2026"),
("gamecentre7x2", "Api-Proxy"),
("jasgues", "nodejs-proxy-server2"),
("kooker", "FreeSubsCheck"),
("larsontrey720", "gemma-retry-proxy"),
("mhghco", "v2ray-hub"),
("myPOSpk", "whitelist_obhod"),
("ppap54088", "ProxMO-RL"),
("DJOUD3148", "browser-extension"),
("JHC000abc", "ProxyParseForSing-box"),
("Kelvin295", "cloakpipe"),
("adop1344-bot", "LetoVPN_free"),
("armoralbatrossstir", "Opera-VPN-Windows-2026"),
("bluereaper-2125", "max-list"),
("funcra", "vg-mirror"),
("gfpcom", "free-proxy-list"),
("isra-osvaldo", "Evasion-SubAgents"),
("kamzy01", "TG-WebApp-Proxy"),
("lhbbingzi", "clash-rules"),
("lvyuemeng", "scoop-cn"),
("yuanjv", "proxy-urls"),
("Mrnobodysmkn", "Beta-Proxy-Lab"),
("SAILFISH-PTE-LTD", "MetroVPN-Windows"),
("jb21cn", "proxy-subscription"),
("noon21000", "Pure-VPN-Crack-2026"),
("sb090", "tauri-plugin-macos-fps"),
("soumyaranjanjena007", "indonesia-gov-apis"),
("waila1", "apple-id-subscribe-ai"),
("y7007y", "TG-Proxy-Hunter"),
("AndrewImm-OP", "vpn-configs"),
("Beatrisadecisive305", "whoami"),
("Love-AronaPlana", "Automatic-VPN-Aggregation"),
("MatinGhanbari", "v2ray-configs"),
("ProxyScraper", "ProxyScraper"),
("Shun234434334343", "supercli"),
("SoftEtherVPN", "SoftEtherVPN"),
("bananasminecraftroblox192-glitch", "DEPI-SSIS-ETL-DWH-Project"),
("chiy4728", "Vless_crawl"),
("cury-w", "proxy-all"),
("hubertfooted416", "clash-wsl-network-doctor"),
("kenshin-arch", "Meta-Business-Suite-SSL-Pinning-Bypass"),
("mummerfleshwound733", "sputniq"),
("r4sso", "r4sso"),
("ryryss2-dev", "vpn-iperf-monitor"),
("Bean5789", "bbd2api"),
("Frostbound-northsea978", "api2cursor"),
("LineShogunSlat", "Proton-VPN-Crack-Latest"),
("Mugassn-Victor", "proxy"),
("Str3akoner", "UltraHiT"),
("Straightedgeheathaster783", "NanoProxy"),
("THEzombiePL", "Anti-VPN-List"),
("TeALO36", "ProxyInHA"),
("Vanic24", "VPN"),
("cariconjugal320", "deepseek-claude-proxy"),
("dmvait8534", "claude2api-deploy"),
("igareck", "vpn-configs-for-russia"),
("ksenkovsolo", "HardVPN-bypass-WhiteLists-"),
("marcusc9", "Clara-sStories"),
("outofprint-statesgeneral134", "the-infinite-crate"),
("poetic-macroglia442", "openclaw-desktop-launcher"),
("seejanm9990", "dynamo-shield"),
("syamsul18782", "xray2026"),
("toleuranus332", "KiteAI"),
("wenxig", "dongtai-sub"),
("xscosa400-wq", "universal-flutter-ssl-pinning"),
("Axillaryfossaprize786", "github_copilot_openai_api_wrapper"),
("Blotchy-unbecomingness80", "openclaw-dae-skills"),
("BreezeBoulderMap", "Mullvad-VPN-Premium-Last-Version"),
("Catoptric-genusplatanthera273", "2-api"),
("ImJustSkilled", "porta"),
("Nnon605246", "singbox_ui"),
("Simprint", "simprint"),
("adoptiongenuslemmus722", "chatgpt-creator"),
("dequar", "deqwl"),
("harmonic-desire485", "nebula"),
("jaimeautomatiza", "tle-proxy"),
("lestday-LAB", "Wikidot-CDN-Mirror"),
("mmaksim9191", "my-vpn-configs"),
("tehrzky", "my-tv-v2ray"),
("tepo18", "online-sshmax98"),
("toyonakibirthtrauma50", "env-runner"),
("warm-mannalichen723", "qclaw-skip-invite"),
("Chipsotrellis", "Proton-VPN-Crack-2026"),
("Davidsonencyclical885", "Nova-Os"),
("FrostChateau", "Windscribe-VPN-2026-go"),
("Lore-Hex", "quill-router"),
("MhdiTaheri", "V2rayCollector_Py"),
("Sean-Vibes", "NYSvibes_news_SS"),
("Skyscraperfoxhound619", "markdown-ui-dsl"),
("Surfboardv2ray", "TGProto"),
("Thirddegreegrocery830", "xr"),
("WLget", "V2ray_free"),
("keerthimamidipaka", "college-discovery"),
("masx200", "feiniu-os-ssh-security-analysis"),
("nthack", "Shadowrocket-ADBlock-Rules-Easy"),
("piqueriastrongbreeze520", "claude-and-codex-website"),
("pog7x", "vpn-configs"),
("selfconjurerrelease", "Hamachi-Pro-Crack-2026"),
("snowluwu", "droute"),
("subscribey48-code", "my-vpn-mirror"),
("xq1337", "proxy-list1337"),
("Ariedeclivitous630", "vecgate"),
("BrinkPrivate", "Surfshark-VPN-Crack-2026"),
("Excellenceehoist", "Mullvad-VPN-Premium-2026"),
("Forceful-gluteusminimus381", "mqttgo_dashboard"),
("Jacky-Yeeo", "Shadowroclet-Rules"),
("Julk8200", "Illuminate"),
("Orthostatic-cassava481", "crypto-security-toolkit"),
("Phantriy4065", "ai-cost-optimizer"),
("SherlyKinan", "proxy-check"),
("VOID-Anonymity", "V.O.I.D-VPN_Bypass"),
("aiboboxx", "v2rayfree"),
("free-nodes", "v2rayfree"),
("gameoplight-lgtm", "FlowSet"),
("gongchandang49", "TelegramV2rayCollector"),
("kopyie", "v2ray-scanner"),
("mahdisandughdaran-sys", "V2ray-sub"),
("pandemic-xanthicacid21", "mcp-time-travel"),
("skibiditoilet12341912-eng", "connaxis"),
("AlexMikhin951", "my-proxy-aggregator"),
("AndyYuenOk", "airport-summary"),
("Exabyteasiaticbeetle444", "burrow"),
("OrionPotter", "free-proxy"),
("UIngarsoe", "SSISM_Intel_Sentinel"),
("ad1239g", "token-saver"),
("amdevelopment-scripts", "my-sveltekit-template"),
("cxv-drift220", "mythic_tailscale"),
("edwinvizcarra1234591-max", "tg-ws-proxy-ANDROID"),
("evanyou0411-design", "zalo-agent-cli"),
("horoshiyvpn-rus", "smart-vpn-sub"),
("kingorza2011-ctrl", "vpngate-servers"),
("malfy-driller", "vpn-builder-"),
("mamun1978", "__2026_03_14_chihlee_gemini__"),
("miraali1372", "mirsub"),
("mlagifts2809", "ssa-my-social-security-browser-automation"),
("stantonadnexal355", "spark-clean"),
("uncial-contingence591", "Openclaw_Free"),
("vAHiD55555", "vLess"),
("Arefgh72", "v2ray-proxy-pars-tester-02"),
("Kingslywilling46", "ssbu-less-lag"),
("Liviastrange489", "easiest-claw"),
("MahanKenway", "Freedom-V2Ray"),
("Nosepythoninae912", "snip"),
("YG-Blue", "v2ray-subscription"),
("andreasvesaliusfringedpolygala893", "codex-manager"),
("brandicoital992", "Awesome-Minecraft"),
("gastonempathic658", "YouTube-to-Cloud-Downloader"),
("hamdanalk3biii-ux", "kyprox"),
("jimmyk9573", "openwebui-ollama-proxy"),
("khaled4123e", "AIOS"),
("koagaroon", "ssaHdrify-tauri"),
("lureiny", "v2raymg-ip-node"),
("sarthakGudwani200", "Lucid-Subnet"),
("0Pwny", "proxy-checker"),
("Basidiomycetespanamaniancapital403", "workerd"),
("Firmfox", "Proxify"),
("MohsenReyhani", "vless-subscriptions"),
("NiREvil", "vless"),
("ShapeRepresentative", "Error-0x80072ee7-Solutions-Windows"),
("Shootp5044", "gemini-mac-pilot"),
("SpriteStudio", "SSPlayerForGodot"),
("Tod-weenieroast366", "coding-plan-mask"),
("asakura42", "vss"),
("constanceintrauterine625", "MySearch-Proxy"),
("daktil888", "ocp"),
("distributive-filter937", "royale_lab"),
("kingorza2011-ctrl", "vpn-sub"),
("matiassppeed-stack", "gemini-watermark-remover-editghost"),
("maycon", "tor-nodes-list"),
("milliammeterfamilyalligatoridae52", "fly-vpn"),
("netbursarlead", "Opera-VPN-Latest"),
("tideakatsukiendure", "Mullvad-VPN-Premium-Latest"),
("Albertarevolutionary289", "any-auto-register"),
("Analgesiamisuse629", "AntiDetection-ProxyBrowser-2026"),
("AnixOps", "AnixOps-xray-install"),
("Audenesque-confession698", "fragment-tg"),
("Beallenonindustrial63", "no-ai-in-nodejs-core"),
("Gr00ss", "Gr00ss"),
("Mucose-genusalepisaurus901", "CTF-blog-downloader"),
("Shiovann2991", "ProtoCMiner"),
("V2RayRoot", "V2Root-ConfigPilot"),
("Wassay380", "NaiveProxy"),
("absolutethresholdhsvii920", "mpp-proxy"),
("acquainted-marsh585", "BackupX"),
("bollywoodhymanrickover646", "zoro"),
("commercesehoga", "ssc"),
("moni-SST", "sst-ams"),
("nikita29a", "FreeProxyList"),
("30nilupulthisaranga-bit", "aegis"),
("Arama120517", "scoop-proxy"),
("Au1rxx", "free-vpn-subscriptions"),
("Djawedc7304", "gea"),
("ErcinDedeoglu", "proxies"),
("Evangelinchichi158", "Proxy-Scraper-2026-GUI"),
("LaviHost", "proxy"),
("Mrnobodysmkn", "Auto-proxy"),
("OfficeDev", "Office-Addin-TaskPane-SSO-JS"),
("cook369", "proxy-collect"),
("divisible-stretcherparty41", "Predict-Fun-Farming-Bot"),
("kalde5307", "omarchy-ibm-theme"),
("kort0881", "vpn-vless-configs-russia"),
("motoneuronrijstafel442", "vless-xhttp"),
("qindinp", "keypool"),
("sternepenitentiary330", "google"),
("Karlczernyvaporisation476", "S2A-Manager"),
("Micaelachesty584", "Citadel"),
("Rutherforddry602", "sha2-ecdsa"),
("ZORfree", "proxy_pool_wasmer"),
("despiteportablecomputer411", "proxy-ipv6-generator"),
("lolandegrenadian150", "IntelliHybrid"),
("platonic-gaelic239", "Emby-In-One"),
("sdsdsdsdsdsihdkjsdjl", "cursoride2api"),
("swargaseemasalesteam-ux", "swargaseema-sss-cab-booking-portal"),
("Bes-js", "public-proxy-list"),
("Decreasingmonotonic-openendwrench955", "proxy-turn-vk-android"),
("Jayant2007", "Mimir"),
("Maxierepresentational96", "YaCV"),
("NJMathwig", "qiaomu-markdown-proxy"),
("Phillippcarboniferous312", "My-Brain-Is-Full-Crew"),
("V2RAYCONFIGSPOOL", "TELEGRAM_PROXY_SUB"),
("aarnold-livefront", "IoTSpy"),
("avbak", "symmetrical-spork"),
("diroxpatron12", "SubHunterX"),
("dmeshechkov", "vpn-subscriptions"),
("ebrasha", "cidr-ip-ranges-by-country"),
("geometric-detection287", "Socat-Network-Operations-Manager"),
("injustice4934", "GitHub-Copilot-Free"),
("ipdssanggau", "cloudflare-Management"),
("partitive-comma396", "nayuyyyu"),
("roderigoambiguous332", "MicroWARP"),
("zbxhaha", "go-task-scheduler"),
("Adamoktora", "imperium"),
("CROSS-T", "Linux.do-Accelerator"),
("DevRatoJunior", "cc-weixin"),
("Esethu1974", "sgproxy"),
("SaloniSS", "SaloniSS"),
("ilyaszdn", "Ladder"),
("mmbateni", "armenia_v2ray_checker"),
("ra7701", "aulite"),
("sunny9577", "proxy-scraper"),
("xiphiidaeequinox80", "mihomo-upstream-proxy-setup"),
("Aline001xx", "turk-arr-bridge"),
("Trillion-pinkandwhiteeverlasting354", "MyDVLD"),
("ahmafadli73-design", "ssukaltim"),
("foliageSea", "ssh_tool"),
("kiet50524", "My-TW-Coverage"),
("ljrdominic-png", "misakaReborn"),
("ninjastrikers", "nexus-nodes"),
("proxygenerator1", "ProxyGenerator"),
("skinned-italianpeninsula990", "weclaw-proxy"),
("suba1653", "CFWarpTeamsProxy"),
("xtrcode", "ovpn.com-ip-grabber"),
("Julesfar710", "heimsense"),
("Kelsibenzoic800", "sshtoolkit"),
("Muhammad4822", "freezeauto"),
("abdallahLokmene", "teamclaude"),
("lordi2809", "agent-infra-security"),
("mmpx12", "proxy-list"),
("mukeshk3272", "Smart-Routing-Butler-for-OpenClaws"),
("vivianalaced749", "vk-calls-tunnel"),
("wallisthundering974", "xr-journal-query"),
("Denchic-2009", "xray-checked-configs"),
("hati4100", "oag"),
("masseuseherpetology481", "keygate"),
("Buint1504", "Predict-Fun-Farming-Bot"),
("Goodygoody-wisp580", "apple-health-analyst"),
("Rimaglottidisspacewalk319", "claude-meter"),
("broken-osmund815", "Polymarket-Trade-Bot"),
("fluxflapping699", "factory-cursor-bridge"),
("lishi0105", "frp-automic"),
("lothianregionophrysapifera132", "docker-openvpn"),
("swagsiamese37", "GVRT-Trading-Bot"),
("BielGodoi", "3LayersPersistence"),
("Grassmacoun146", "CPA-OPEN"),
("KRYYYYYYYYYYYYYYYYYYY", "xray-uuid-checker"),
("Karenfsi188", "xray"),
("Rhodawagnerian446", "docker-wireguard"),
("arandomguyhere", "Proxy-Hound"),
("chmoralla-code", "cynework-ai-proxy"),
("dongchengjie", "airport"),
("hardcopycortex461", "worker-bridge"),
("ilamafascista615", "kyma"),
("revenantguttaperchatree773", "Onvoyage-Ai-Testnet-farm"),
("vsvavan2", "vpn-config-rkn"),
("Margothermoplastic365", "waterwall-api-gateway"),
("Minded-nakuru841", "headscale-install"),
("Zohuko71", "ferrox"),
("anniet5664", "webclaw-tls"),
("aradhyagithub", "FLJopen"),
("magicspellnosejob374", "flaregun"),
("onlymeoneme", "v2ray_subs"),
("ritchiearistotelian98", "docker-headscale"),
("Maklith", "Kitopia"),
("Malvaceaefries86", "NetSniffer"),
("bayvapourisable154", "Stratum"),
("explorative-largemagellaniccloud775", "MF.Radius"),
("fadh24434", "webarsenal"),
("lqdflying", "cursorProxy"),
("xuanranran", "rely"),
("Fadouse", "clash-threat-intel"),
("HSG4338", "springboot-oauth2-sso-example"),
("Itci1146", "AME_Locomotion"),
("Nonpregnant-loss29", "not-claude-code-emulator"),
("abidi556", "doge-code"),
("devojony", "ClashSub"),
("elly5490", "telegram-proxy"),
("esanacore", "SSH_DeviceManager"),
("mayerhany32", "litchi_claude_code"),
("yahoosony81-sys", "subscribe-pt"),
("3yed-61", "Shadowsocks"),
("Asaza366", "iron-proxy"),
("Claudiasinusoidal818", "OffensiveSET"),
("Dororecessed36", "telegram-auto-clone-download"),
("Holdkradesignate", "TotalAV-Pro-Activator-Crack"),
("Lowering-mechanism250", "ns"),
("eiler2005", "ghostroute"),
("epicentr", "aerodrome-ical-proxy"),
("feiniao25789", "vpn"),
("fyvri", "fresh-proxy-list"),
("madeye", "BaoLianDeng"),
("rorafiftysix26", "First"),
("ssbaxys", "v2ray-configs"),
("vilage777", "my-vpn-su"),
("Delta-Kronecker", "Downloader"),
("Elkraz", "ccxray"),
("Eloco", "free-proxy-raw"),
("Foul-plastique636", "CC-Router"),
("Lasertems", "AV-skip-Builder"),
("Leos573", "node-curl-impersonate"),
("Scoreverb70", "NekoCheck"),
("T3stAcc", "V2Ray"),
("Thuongquanggg", "Proxy"),
("adeshra5646", "VLESS-XTLS-Reality-VPN"),
("bellasachs4-bit", "wiregui"),
("ogt-tools", "ogt-data-proxy"),
("Competent-genuscanella687", "openclaw-billing-proxy"),
("DarkRoyalty", "shnajder-vpn-configs"),
("Dipanwita-Mondal", "tunnel"),
("EngangAman", "GptCrate"),
("Jasperuric559", "Supervisor.skill"),
("VP01596", "vless-top15"),
("addadi", "aws-vpn-saml"),
("alixblae550", "SecureTunnel"),
("epigraphcommissioner131", "ai-one-click-beauty"),
("feiniao1-VPN", "Node-Airport---VPN"),
("gitrecon1455", "fresh-proxy-list"),
("jonascolditz3-dot", "SSC-Database-Gen-Tool"),
("lidiama9513", "goated"),
("niq0n0pin", "v2rayfree-nice-tracker"),
("tylero5029", "MasterDnsVPN-AndroidGG"),
("unnourished-calciumchannelblocker351", "HydraFlow"),
("Andy7152", "luci-app-minigate"),
("Bpcod8422", "Facebook-SSL-Pinning-Bypass-NonRoot"),
("Dldigisof3283", "copilot-api"),
("Ealasaidstupid494", "VeilScrape"),
("Manans999", "ChromiumManager"),
("Robbynjazzy512", "opencode-local-provider"),
("mahmudzgr", "altin-proxy"),
("proud-persiangulf507", "ripgrep-node"),
("punez", "proxy-collector-a"),
("sanasa-bank-baddegama", "nod"),
("scriptzteam", "AirVPNWatch"),
("zhou-jian-qq", "Clash-Hub"),
("Amy7007", "VPN-Detector"),
("Arjun99291", "telemt-panel"),
("Lumimojjav", "Chibi-Clash-Crypto-Game-Token-Api"),
("Mervohex", "Kunchi-Gambling-Keydrop-ClashGG-SkinClub-Predictor-Strategies"),
("SoliSpirit", "proxy-list"),
("Trivexion", "AsteriskPassword-Viewer"),
("V2RAYCONFIGSPOOL", "SLIPNET_SUB"),
("Vortalitys", "PrivHunterAI-detects-access-vulnerabilities"),
("aaron4605", "context-optimizer"),
("davitaalliaceous7299", "FalixNodes"),
("ernestaweak8629", "yourvpndead"),
("gsamuele78", "R-studioConf"),
("onl35461-debug", "Node-climbing-wall-ladder---VPN"),
("parserpp", "ip_ports"),
("ron33tui", "clash-merger"),
("scriptzteam", "NordVPNWatch"),
("shreyanxNova", "RKNHardering"),
("teraka3109", "hls-restream-proxy"),
("ts-sf", "fly"),
("tullextraterrestrial3175", "ClaudeCode-Model-Rotator"),
("Gmsher5817", "domloggerpp-caido"),
("MrMarble", "proxy-list"),
("Shayanthn", "V2ray-Tester-Pro"),
("child9527", "clash-latest"),
("cybelleweak1220", "green-campus-tracker"),
("feiniaovpn", "--VPN"),
("jannasweetened9049", "SwizGuard"),
("steam-100", "free-proxy-sub"),
("vakhov", "fresh-proxy-list"),
("wxglenovo", "1AdGuardHome-Rules-AutoMerge-"),
("youkatalo123-star", "ComfyUI_RH_VoxCPM"),
("Biologicaltimemistral1034", "nodris"),
("Paorwm", "Batch-Downloader-Crypter-FUD-UAC-Bypass"),
("Prasadchelated435", "windows-telegram-bot"),
("Rr3511167", "snix"),
("Scarecrowish-shoat5968", "ByeByeVPN"),
("Sprokitz", "all-deploy"),
("Teodoorpenal672", "baiqi-GhostReg"),
("Tuchit893", "social-fixed-ip-guide"),
("Zaeem20", "FREE_PROXIES_LIST"),
("kravchenkosaveliy27-crypto", "my-vpn"),
("lucas01feh", "oss-security-audit"),
("thirtysixpw", "v2ray-reaper"),
("twj0", "subseek"),
("video05", "vpn-qr"),
("virgiliomaxillary918", "cfnb"),
("Armillary-italy713", "Smart-Config-Kit"),
("Doryeightsided72", "adblock-rust-manager"),
("Islamnetz", "gmail-account-creator-bot-pro"),
("Jeffreycommon553", "HA-Optimizer"),
("Paorwm", "Batch-Malware-Builder-FUD-Crypter-AV-UAC-Bypass"),
("Remyix123", "PiHole-Cloud-Wireguard-VPN-Orchestrator"),
("VovaplusEXP", "p-configs"),
("bgpeer", "icons"),
("jhosuemiscanvilchez", "ssh-api"),
("krokmazagaga", "http-proxy-list"),
("mariadelapazj2155", "nginx-proxy-manager-api"),
("rainwatershilling272", "Fortnite-Premium-External"),
("saltplainjobaction503", "sub-store-workers"),
("shitless-secretor385", "ahr999-dataset"),
("sonic0jd", "MasterHttpRelayVPN"),
("svpjohji", "NECHAEV_VPN_AGGREGATOR"),
("tranhailong012", "windsurf-tools"),
("vievieng761", "AJAS"),
("0funct0ry", "xwebs"),
("Alexgood321", "my-proxy-raw-link-for-all"),
("CB-X2-Jun", "https-proxy"),
("Gerryoverlooking665", "Blooket-Bot-Flooder"),
("Hidashimora", "free-vpn-anti-rkn"),
("Kadowms", "Sakura-Rat-Hvnc-Hidden-Browser-Remote-Administration-Trojan-Bot-Native"),
("Lgutier9249", "SNI-XHTTP-V1.1"),
("Memooaren7891", "VSoft.AnsiConsole"),
("Tieazide1959", "DNSly"),
("Unified-rosinbag197", "gh-relay"),
("Vadim287", "free-proxy"),
("Wheelernormandy677", "CF-IP-Scanner"),
("amuck-tie267", "SNI-XHTTP"),
("balaji-cse15", "gemi"),
("chantalunsupportable7191", "mhr-cfw"),
("deezertidal", "fee-based"),
("deezertidal", "freevpn"),
("feiniao1-VPN", "VPN-service"),
("greenlandspinel496", "FlowDriver"),
("grimvpn", "clash-convertor"),
("kirtim8895", "awesome-privacy-tools"),
("komutan234", "Proxy-List-Free"),
("l610128078", "sssss"),
("muskd79", "proxy-manager-telebot"),
("r2d4m0", "vless-parser"),
("spayed-turkmen6590", "netlify-relay"),
("ssplash65", "sspl"),
("xenmate", "mon-ss"),
("AvenCores", "goida-vpn-configs"),
("FLEXIY0", "matryoshka-vpn"),
("Intermolecular-sirdar532", "v2node"),
("Secondary-offer942", "hamid-mahdavi-client"),
("SevenworksDev", "proxy-list"),
("Unopposable-starting193", "chatgpt-bridge"),
("XigmaDev", "cf2tg"),
("arfahmahmud", "codex-context-editor-proxy"),
("batus5678", "mhr-ggate"),
("chengaopan", "AutoMergePublicNodes"),
("fleetstreetremit109", "Post-X-Premium.com-Automated-Post-Publishing"),
("iplocate", "free-proxy-list"),
("massimoalbertoli-arch", "school-calendar-proxy"),
("olympiangamesgenussynchytrium730", "dokploy-tailscale-webhook-relay"),
("onl35461-debug", "Node-Airport---VPN"),
("redondoc", "wsj-zh-rss-proxy"),
("trabict", "my-vpn-configs"),
("Mohammedcha", "ProxRipper"),
("feiniao25789", "feiniao-vpn"),
("yoshikanguyen", "BTVN_SS12"),
("Neamul09", "sstu-bot"),
("R3ZARAHIMI", "tg-v2ray-configs-every2h"),
("arunsakthivel96", "proxyBEE"),
("huameiwei-vc", "stash-kr-proxy-auto-refresh"),
("kort0881", "vpn-checker-backend"),
("malfy-driller", "vpn-builderV2"),
("shaa2020", "V2Ray-Automator"),
("v0id9", "vpn-configs"),
("vovan046kursk-stack", "vless-list1"),
("wyattowalsh", "proxywhirl"),
("AxLeRage10", "noteapp"),
("CB-X2-Jun", "Free-v2ray-node"),
("Surfboardv2ray", "Proxy-sorter"),
("apify", "crawlee"),
("arseniy700", "vpn-sub"),
("onl35461-debug", "Free-ladder---VPN"),
("rlaeodn1015-oss", "ssnim-request-landing"),
("Ciara-Aa", "PROXY-free"),
("RioMMO", "ProxyFree"),
("bonymalomalo", "vless-auto-update"),
("jeongwoo1020", "SST-electricity_Risk_Management"),
("mfonectrl-bit", "rss-proxy"),
("r5r3", "s32p-proxy"),
("strikersam", "local-llm-server"),
("tiagorrg", "vless-checker"),
("83646uguh", "Git-proxy"),
("daneb255", "pkggate"),
("feiniaovpn", "Accelerator-Node---VPN"),
("longlon", "v2ray-config"),
("xuerake", "my-clash-sync"),
("Areral", "ScarletDevil"),
("REIJI007", "AdBlock_Rule_For_Clash"),
("SenumiCosta", "proxymaze26"),
("free-nodes", "clashfree"),
("Durgaa17", "cf-sg-proxies"),
("Zephyr236", "proxy_collector"),
("Zero-Bug-Freinds", "ai-api-usage-monitor"),
("amantestingforbugs", "sslscannerv4"),
("bin1site1", "V2rayFree"),
("feiniao1-VPN", "Free-ladder---VPN"),
("onl35461-debug", "Wall-climbing-ladder-VPN"),
("shekelstrong", "vpn_bot"),
("9xN", "auto-ovpn"),
("Frozoewn", "S500-RAT-HVNC-HAPP-HIdden-BROWSER-HRDP-REVERSE-PROXY-CRYPTO-MONITOR"),
("Hubaio", "Reverse-Proxy-Soruce-Code"),
("M-logique", "Proxies"),
("liangshengyong", "LanWan"),
("mayday151", "douban-proxy"),
("scriptzteam", "AzireVPNWatch"),
("tonykslee", "ClashCookies"),
("wonglaitung", "fortune"),
("Garmask", "SilverRAT-FULL-Source-Code"),
("RedHatInsights", "uhc-auth-proxy"),
("anutmagang", "Free-HighQuality-Proxy-Socks"),
("hvwin8", "autojiedian"),
("peasoft", "NoMoreWalls"),
("tomaasz", "litellm-free-models-proxy"),
("wr69", "auto-jichangbaohuo"),
("Reid-Vin", "OpenClash_Custom_Rules_for_ios_rule_script"),
("Xnuvers007", "free-proxy"),
("crolankawasaki", "Goida26-Clash"),
("licheng527", "Free-servers"),
("raphaelgoetter", "clash"),
("7c", "torfilter"),
("ALIILAPRO", "Proxy"),
("Argh94", "Proxy-List"),
("LoneKingCode", "panbox"),
("Pawdroid", "Free-servers"),
("RealFascinated", "PIA-Servers"),
("Scully34", "sscoe-dashboard"),
("amirkma", "proxykma"),
("canadice", "ssl-index"),
("claudianus", "clco-helper"),
("claudianus", "clco-proxy"),
("codeking-ai", "cligate"),
("fastasfuck-net", "VPN-List"),
("junjun266", "FreeProxyGo"),
("jy02739245", "ssh_tools"),
("kiyo-astro", "SSDL-SatPass-Notification"),
("lanzm", "MetaFetch"),
("maiyulao", "ResoHub"),
("mehdihoore", "TestVpnGateServers"),
("miladtahanian", "Config-Collector"),
("milchee", "vless_subs"),
("mohamadfg-dev", "telegram-v2ray-configs-collector"),
("roosterkid", "openproxylist"),
("socks5-proxy", "socks5-proxy.github.io"),
("toml66l", "fanqiang"),
("watchttvv", "free-proxy-list"),
("AlterSolutions", "tornodes_lists"),
("TheSpeedX", "PROXY-List"),
("Tom-Riddle09", "proxy_server"),
("armanridho", "ProxyJson-toYaml"),
("bq2015", "FreeProxies"),
("itsanwar", "proxy-scraper-ak"),
("nandapoxy", "proxy-server"),
("qolbudr", "proxy-checker"),
("sweengineeringlabs", "edge"),
("wr69", "auto-jichangqiandao"),
("Casper-Tech-ke", "casper-free-proxies"),
("OpenNetCN", "clash"),
("OxiBelt", "OxiBelt"),
("SoliSpirit", "SolVPN"),
("elijah-hall-asdq1", "Clash-Verge-Rev-History"),
("g-hunter-g", "awesome-vpn"),
("xiaoji235", "airport-free"),
("ArtemAfonasyev", "hentai-goida-subscription"),
("Daysema", "xRay-visual"),
("HasithaErandika", "proxy-maze"),
("MaskaBOG", "clash-vless-auto"),
("Master-Mind-007", "Auto-Parse-Proxy"),
("akbarali123A", "proxy_scraper"),
("captianzo", "School-Management"),
("feiniao1-VPN", "Node-based-VPN"),
("gbagliesi", "cms-sst-report"),
("maxstev72", "Zero-Trust-Auth-Service"),
("trio666", "proxy-checker"),
("yiohoohoo2026", "format-proxy"),
("LalatinaHub", "Mineral"),
("Silvester13-SOS", "clash-war-analytics"),
("crackbest", "V2ray-Config"),
("feiniaovpn", "Node-Airport-VPN"),
("hiztin", "VLESS-PO-GRIBI"),
("lm705", "vair"),
("oscarshrek9", "Cloud-Native-Load-Balancer"),
("sdfnh", "fanqiang"),
("ttblstr", "sslv-telegram-monitor"),
("yunusalemu", "Proxy-Manager"),
("A-K-6", "v2ray_scrapper_repo"),
("Cat-Ling", "sing-box"),
("GilvanS", "historico-clash-roayle"),
("I-r-a-j", "proxy"),
("Ian-Lusule", "Proxies-GUI"),
("Leavend", "SSO_Kali"),
("Surfboardv2ray", "test-psi"),
("atajanofficila", "vpn-server-list"),
("jnjal", "v2ray"),
("josebormey", "render-eltoque-proxy"),
("ljhq553", "OpenClash-Setup"),
("rakibkumar151", "auto-proxy-updater"),
("stormsia", "proxy-list"),
("thomaswetzler", "vLLM-Sleep-Proxy"),
("woshishiq1", "my-clash-sync"),
("Access-At", "proxy-list"),
("Argh94", "ProxyProwler"),
("Argh94", "telegram-proxy-scraper"),
("JeBance", "CheburNet"),
("KiryaScript", "white-lists"),
("SoroushImanian", "BlackKnight"),
("Zover1337", "vless-free-whtielist"),
("daffwt221", "homelab-raspberry-network-stack"),
("elijah-hall-asdq1", "V2rayN-History"),
("fdciabdul", "Vpngate-Scraper-API"),
("goauthentik", "authentik"),
("ilya-120", "vpn-tester"),
("ircfspace", "XrayRefiner"),
("mikealmeida1721", "SSEE"),
("miladtahanian", "V2RayScrapeByCountry"),
("nomadturk", "vpn-adblock"),
("theavel", "free-vless-proxy"),
("yashlatiwal", "ssc-reddit-monitor"),
("Bd-Mutant7", "SSRF_Vulnerable_Lab"),
("NishaMax", "ProxyMaze"),
("ShadowException", "VPN"),
("Skillter", "ProxyGather"),
("SriSathyaSaiVidyaVahini", "SSSVV-landing"),
("TopChina", "proxy-list"),
("WLget", "V2Ray_configs_64"),
("ar4kiara", "proxy"),
("esmelimited23", "Cloud-Native-Load-Balancer"),
("feiniao1-VPN", "Airport-node-VPN"),
("lexariley", "v2ray"),
("miladtahanian", "V2RayCFGTesterPro"),
("therealaleph", "Iran-configs"),
("topsuperv", "ss"),
("wisebobo", "clashNodes"),
("Chunlion", "VPS-Optimize"),
("MarcoYou", "open-proxy-mcp"),
("XigmaDev", "proxy"),
("arseniy700", "MSC-VPN"),
("dorrin-sot", "V2RAY_CONFIGS_POOL-Processor"),
("jackbayliss", "cloudflare-r2-rss"),
("kenzok8", "openwrt-clashoo"),
("kokulanK", "ProxyMaze-26"),
("lyc-aon", "codex-session-manager"),
("robintw", "sse_powercuts"),
("sinavm", "SVM"),
("teknovpnhub", "v2ray-subscription"),
("ChaselDutt", "VPN-Deep-Test"),
("Maskkost93", "kizyak-vpn-4.0"),
("MrAbolfazlNorouzi", "iran-configs"),
("MustafaBaqer", "VestraNet-Nodes"),
("balookrd", "outline-ws-rust"),
("bondarevaamelya", "token_ss"),
("conoro", "reddit-rss-proxy"),
("cstreit03", "CoC-Stats"),
("ember-01", "Clash-Aggregator"),
("handeveloper1", "DailyProxy---Auto-Update-List"),
("idtheo", "V2Ray-CleanIPs-Servers"),
("imegabiz", "Anonymous-ir-proxy-configs"),
("mzwaterski", "calendar-subscribe-feed"),
("nodesfree", "clashnode"),
("nodesfree", "v2raynode"),
("FLAT447", "v2ray-lists"),
("SHAHBBBB", "V2ray-collector"),
("SoliSpirit", "v2ray-configs"),
("YangLang116", "auto_gen"),
("YoulianBoshi", "vpn"),
("barry-far", "V2ray-Config"),
("caryyu0306", "proxy-list"),
("ebrasha", "abdal-proxy-hub"),
("hello-world-1989", "cn-news"),
("mingcheng", "faure.sh"),
("mizmazegt1-design", "auto-vpngate-configs"),
("nyeinkokoaung404", "V2ray-Configs"),
("sibur1703-alt", "my-auto-vpn"),
("surdebmalya", "baud-news-ss"),
("CharlesPikachu", "freeproxy"),
("J-L33T", "vlesstj"),
("PatNei", "esport-ics"),
("TheFlipper-spec", "VPNMY"),
("acymz", "AutoVPN"),
("blog1703", "tgonline"),
("dpsserver", "VPNCONFIG"),
("gslege", "CloudflareIP"),
("huangjunyin991-art", "ak-proxy"),
("mmalmi", "nostr-vpn"),
("muks999", "Clash-Vless-convert"),
("scriptzteam", "IVPNWatch"),
("zxsman", "clashfree"),
("Argh73", "VpnConfigCollector"),
("DukeMehdi", "FreeList-V2ray-Configs"),
("Katrinaannija", "ss.lv"),
("RayanAhmadKhan", "PRISM"),
("Therealwh", "MTPproxyLIST"),
("databay-labs", "free-proxy-list"),
("ebrasha", "free-v2ray-public-list"),
("khbmgh", "clasher"),
("kringemega", "VlessParser"),
("rasool083", "v2ray-sub"),
("sevcator", "5ubscrpt10n"),
("ssg-create", "ssg-dashboard-data"),
("Kotlas23412", "proxy-checker"),
("PuddinCat", "BestClash"),
("Rusl2023", "vpn-alive-check"),
("ali13788731", "vpn"),
("atou42", "agents-in-discord"),
("dpangestuw", "Free-Proxy"),
("feiniaovpn", "Game-Accelerator---VPN"),
("kuciybes", "vpn-clash-rules"),
("nuggetenak", "Nugget-Nihongo-SSW-Konstruksi"),
("pjrpjr9003-svg", "SSS"),
("proxifly", "free-proxy-list"),
("scriptzteam", "PrivateInternetAccessWatch"),
("AirLinkVPN1", "AirLinkVPN"),
("Delta-Kronecker", "Tor-Bridges-Collector"),
("V2RayRoot", "V2RayConfig"),
("Yo0l0", "ssss"),
("monosans", "proxy-list"),
("razoshi", "v2ray-configs"),
("sengshinlee", "hosts"),
("3nerg0n", "vless-parser"),
("Alvin9999-newpac", "fanqiang"),
("AutumnVN", "ssleaderboard"),
("Dimasssss", "free_telemt_servers"),
("FL-Penly", "proxy-gate"),
("HankNovic", "ProxyClean"),
("NoTalkTech", "xrayctl"),
("Veid09", "vless-list"),
("Wyr-Hub", "WyrVPN-Lite"),
("ali13788731", "proxy"),
("anatolykoptev", "oxpulse-partner-edge"),
("avion121", "V2RayDaily"),
("hamedp-71", "N_sub_cheker"),
("iboxz", "free-v2ray-collector"),
("jester4411", "amnezia-vpn"),
("sakha1370", "OpenRay"),
("vahid162", "proxy-address-mining"),
("vmheaven", "VMHeaven.io-Free-Proxy-List"),
("wildoaksapothecaryadmin", "squarespace-api-proxy"),
("TheHotCodes", "HotVpn"),
("V2RAYCONFIGSPOOL", "V2RAY_SUB"),
("Vann-Dev", "proxy-list"),
("adaskitkleilrociftey", "solidity-proxy-upgrade"),
("alphaa1111", "proxyscraper"),
("expressalaki", "ExpressVPN"),
("fugary", "simple-boot-mock-server"),
("onl35461-debug", "Accelerator-node-ladder---VPN"),
("qopq1366", "VlessConfig"),
("themiralay", "Proxy-List-World"),
("Amiin-key", "ssm2027"),
("MrViSiOn", "ssha"),
("ZEPO228", "Vortex-vpn"),
("alialieghar-b", "proxy"),
("arasongiyvymjlndejkkhcbay", "evm-storage-layout-analyzer"),
("claude89757", "free_https_proxies"),
("j0rd1s3rr4n0", "api"),
("purpletigerlzhlcgg", "ethereum-event-tracker"),
("solovyov-jenya2004", "all_subs"),
("waiswadaniel24", "ssewasswa-api"),
("zloi-user", "hideip.me"),
("zoreu", "proxyssl"),
("Andrejewild", "myvpn"),
("chen08209", "FlClash"),
("kort0881", "sbornik-vless"),
("sotashimozono", "obsidian-remote-ssh"),
("crashed6767", "tor-proxy")
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
# 📊 بخش ۴: مدیریت Rate Limit
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
# 💾 بخش ۵: پایگاه داده و کش
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

    max_hours = CONFIG_DEFAULTS.get("MAX_AGE_HOURS", 0)
    if max_hours > 0:
        pushed_at_str = repo_data.get("pushed_at") or repo_data.get("updated_at")
        if pushed_at_str:
            try:
                pushed_at = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_hours)
                if pushed_at < cutoff_time:
                    return
            except Exception:
                pass

    files = await get_repo_files(session, owner, repo, headers, semaphores['fetch'])
    if files:
        url_set.update(files)

# ============================
# 🔍 بخش ۸: پردازش URL و استخراج نهایی
# ============================
async def process_url(session, url, headers, processed_urls_session, cache, semaphore, depth=0, repo_stats: dict = None):
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
        # استخراج owner/repo از URL و به‌روزرسانی آمار
        if repo_stats is not None:
            parts = url.split('/')
            if len(parts) >= 5 and parts[2] == 'raw.githubusercontent.com':
                owner, repo = parts[3], parts[4]
                key = f"({owner}, {repo})"
                repo_stats[key] = repo_stats.get(key, 0) + len(found_configs)

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

    # --- خواندن حالت اجرا فقط یک بار ---
    run_mode = os.getenv("RUN_MODE", "daily")
    max_age_env = os.getenv("MAX_AGE_HOURS")
    if max_age_env is not None:
        CONFIG_DEFAULTS["MAX_AGE_HOURS"] = float(max_age_env)
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

    # در اجرای ساعتی و ۱۵‌دقیقه‌ای، مخازن دستی هر بار دوباره بررسی شوند
    if run_mode in ("hourly", "frequent"):
        scanned_manual_repos = set()

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

            # ذخیره‌ی کش لینک‌های raw برای استفاده در اجراهای بعدی (فقط در روزانه)
            if run_mode == "daily":
                with open("raw_urls_cache.json", "w") as f:
                    json.dump(list(source_urls), f)
                logger.info(f"💾 Saved {len(source_urls)} raw URLs to raw_urls_cache.json")

        logger.info(f"Total source URLs (before filtering): {len(source_urls)}")

        # --- برای آمار مخازن ---
        repo_stats: Dict[str, int] = {}

        # --- Stage 3: Process URLs ---
        logger.info("--- Stage 3: Processing URLs ---")
        urls_to_process = []
        for u in source_urls:
            if 'github.com' not in u and 'raw.githubusercontent.com' not in u:
                continue
            if run_mode in ("hourly", "frequent"):
                pass
            else:
                if u in processed_urls_session:
                    continue
                if cache.is_cached(u) or await db_is_url_processed(u, CONFIG_DEFAULTS["CACHE_EXPIRY_DAYS"]):
                    continue
            urls_to_process.append(u)

        logger.info(f"New URLs to process: {len(urls_to_process)}")
        batch_size = CONFIG_DEFAULTS["BATCH_SIZE"]
        for i in range(0, len(urls_to_process), batch_size):
            batch = urls_to_process[i:i+batch_size]
            tasks = [asyncio.create_task(process_url(session, url, headers, processed_urls_session, cache, fetch_semaphore, 0, repo_stats))
                     for url in batch]
            for fut in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"[Stage 3] Batch {i//batch_size + 1}"):
                try:
                    await fut
                except Exception as e:
                    logger.debug(f"Process error: {e}")
            await save_checkpoint(processed_urls_session, searched_queries, scanned_manual_repos)

        # --- بروزرسانی گزارش مخازن ---
        repo_report_file = "repo_report.txt"   # در ریشهٔ پروژه
        repo_history = {}
        if os.path.exists(repo_report_file):
            with open(repo_report_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    key, counts = line.split(':', 1)
                    key = key.strip()
                    counts = [c.strip() for c in counts.split(',') if c.strip().isdigit()]
                    repo_history[key] = counts

        for key, count in repo_stats.items():
            if key in repo_history:
                repo_history[key].append(str(count))
            else:
                prev_len = len(next(iter(repo_history.values()))) if repo_history else 0
                repo_history[key] = ['0'] * prev_len + [str(count)]

        for key in repo_history:
            if key not in repo_stats:
                repo_history[key].append('0')

        with open(repo_report_file, "w", encoding="utf-8") as f:
            f.write(f"GitHub Repo Report — last update: {datetime.now(timezone.utc).isoformat()}\n\n")
            for key in sorted(repo_history.keys()):
                counts_str = ", ".join(repo_history[key])
                f.write(f"{key}: {counts_str}\n")
        logger.info(f"📊 گزارش مخازن در {repo_report_file} بروز شد.")

    # --- Stage 4: Final Export ---
    logger.info("--- Stage 4: Final Export ---")
    cache._save_cache()
    all_configs = await db_get_all_configs()
    unique_configs = sorted({c.strip() for c in all_configs if c.strip()})
    logger.info(f"✅ Total unique configs in DB: {len(unique_configs)}")
    
    if CORE_LIMIT_REACHED:
        logger.warning("⛔ Script finished early because Core limit was reached.")
    else:
        logger.info("✅ Script completed normally without hitting Core limit.")

    # --- مرحله نهایی: ادغام و تفکیک پروتکل‌ها ---
    await finalize_output()

    logger.info(f"--- Finished in {int(time.time() - start_time)}s ---")
    logger.info(f"Estimated Core used: {TOTAL_CORE_USED}")
    os._exit(0)

# ============================
# 🗂️ بخش ۱۰: ذخیره‌سازی هوشمند و تفکیک پروتکل‌ها (جدید)
# ============================
async def finalize_output():
    """فقط all_servers.txt را با کانفیگ‌های جدید بازنویسی می‌کند."""
    logger.info("--- Finalizing Output: Writing new configs to all_servers.txt ---")
    
    output_file = "all_servers.txt"
    existing_configs = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            existing_configs = {line.strip() for line in f if line.strip()}

    new_configs = set(await db_get_all_configs())
    added_configs = new_configs - existing_configs
    logger.info(f"🆕 Truly new configs this run: {len(added_configs)}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sorted(added_configs)) + "\n")
    logger.info(f"💾 Saved {len(added_configs)} new configs to '{output_file}'")

    logger.info("✅ Output finalized successfully.")
    
if __name__ == "__main__":
    if os.name == 'nt':
        try:
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        except Exception:
            pass
    exit_code = 0
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Interrupted. Progress saved in checkpoint.")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        exit_code = 1
    finally:
        sys.exit(exit_code)
