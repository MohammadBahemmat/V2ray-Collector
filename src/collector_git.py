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
    
]

REPO_SEARCH_QUERIES = sorted(list(set([

])))

CODE_SEARCH_QUERIES = sorted(list(set([

])))

EXTRA_UPDATED_REPO_QUERIES = [

]

MANUAL_REPOS_TO_SCAN = sorted(list(set([
    ("mostafanamv", "timetunnel"), ("pornnewbee", "free-vless-VPN"), ("smakotta", "V2rey-cfg"),
    ("PaPerseller", "chn-iplist"), ("asgharkapk", "Sub-Config-Extractor"), ("anaer", "Sub"),
    ("MahsaNetConfigTopic", "config"), ("10ium", "V2ray-Config"), ("v2fly", "v2ray-core"),
    ("MetaCubeX", "meta-rules-dat"), ("10ium", "V2rayCollector"), ("LoneKingCode", "free-proxy-db"),
    ("skka3134", "Free-servers"), ("abueyad2017", "railway-vless-vpn"), ("v2raynnodes", "v2raynnodes.github.io"),
    ("v2raynnodes", "v2rayclash"), ("joestonecodes", "drinaxian-regency-dashboard"), ("v2raynnodes", "clashnode"),
    ("emberuh", "Code-iuxgqjwdkc-Java"), ("Chocolate4U", "Iran-v2ray-rules"), ("Mou7s", "spacex-calendar"),
    ("flclash-us", "clash-router-openwrt"), ("Mmaduabuchi", "foodboxNG"), ("legiz-ru", "mihomo-rule-sets"),
    ("type-one", "PublishSubscribeESP32"), ("moshesteiner", "VisualNode"), ("Tenejakin", "sound-clash"),
    ("pf123120", "clash-rules-txt-to-mrs"), ("ProgrammerLiSichen", "mental-icd-cn"), ("nikkinikki-org", "OpenWrt-nikki"),
    ("ermaozi", "get_subscribe"), ("AgungHari", "aaagang"), ("emberuh", "Code-jrhjmrtvmq-Java"),
    ("opensa13-bot", "MTProto"), ("othyn", "go-calendar"), ("ninggee", "clash_to_hosts"),
    ("opensa13-bot", "MTProto-Yurich"), ("JacksonJiangxh", "Clash-Rule"), ("haandiiong", "yp7.net"),
    ("justinritchie", "clash-of-clans-mcp"), ("noahkostesku", "ferroflow"), ("ripaojiedian", "freenode"),
    ("chatgpt-helper-tech", "airport-access"), ("Robin1128", "VPN"), ("kirito201711", "Shadowsocks-go"),
    ("Thordata", "awesome-free-proxy-list"), ("HenryChiao", "MIHOMO_YAMLS"), ("Loischsiy", "server-subscribers"),
    ("QuixoticHeart", "rule-set"), ("jinghengLi", "clash"), ("MCC12138", "Clash_Rules"),
    ("bskinn", "cpython-release-feed"), ("2dust", "v2rayN-core-bin"), ("VPSDance", "ai-proxy-rules"),
    ("VictorMaxWang", "childcare-smart"), ("Latticect", "V2ray-Rules-Dat-SwitchyOmega"), ("dctxmei", "v2ray-china-list"),
    ("7-yearsold", "clash-rules"), ("linzjian666", "chromego_extractor"), ("Use4Free", "breakfree"),
    ("ChiaoYenta", "mihomo_yamls"), ("uykb", "clash-proxy-cleaner"), ("KaringX", "karing"),
    ("zz-want2sleep", "daily-gist"), ("codeking-ai", "cligate"), ("namtonthat", "apple-health-data"),
    ("kidddr", "CEO-Clash"), ("Latticect", "clash-rule-set"), ("weiguangchao", "Clash"),
    ("mehrancardtr-cpu", "ReMIX"), ("YUTING0907", "SubscribePapers"), ("yeemelya77", "Servers"),
    ("hotseo123", "shida-jichang-tuijian"), ("Hotinosin", "clash-rule"), ("JessyeKessia", "MessageHub"),
    ("raidal", "v2ray-rules"), ("CMON1975", "is-gamepass-worth"), ("SeanXuCn", "ClashVergeTrafficLedger"),
    ("YY-China", "Clash"), ("rankalpha", "v2ray_sub"), ("clashv2rayu", "clashv2rayu.github.io"),
    ("Ruk1ng001", "freeSub"), ("BrandonPerez915", "CineList"), ("SuperNG6", "clash-ruleset"),
    ("ASGDB", "SubconverterACL"), ("Vincentkeio", "probe-nodes-list"), ("qRuWGQ", "rules"),
    ("eswar7216", "TreeListWithMultiNode"), ("flclash-us", "clash-linux-cli-config"), ("flclash-us", "vps-proxy-deploy-guide"),
    ("laosan-xx", "my-v2ray-geodata"), ("v2rayA", "dist-v2ray-rules-dat"), ("ByteMysticRogue", "Hiddify-Warp"),
    ("ruabbit233", "clash-config-manager"), ("xOS", "Config"), ("kan996", "clashini"),
    ("awesome-vpn", "awesome-vpn"), ("soapbucket", "sbproxy"), ("mrdear", "my-clash-rules"),
    ("xilakg515", "cheap-residential-proxy-alternatives"), ("xituimao", "spider-clash"), ("djck7231", "dataimpulse-vs-smartproxy"),
    ("DeepJH", "fuck-sb-qzxy-ad"), ("Hit-Mickey", "clash-for-linux"), ("gdhdhgdhxg78-bit", "v2ray_404-sub"),
    ("freeclashn", "freeclashn.github.io"), ("clashformac", "clashformac.github.io"), ("bvxwtfmq", "dataimpulse-vs-webshare"),
    ("yuanwangokk-1", "clash-converter"), ("clash-nyanpasu", "clash-nyanpasu.github.io"), ("clash-s", "clash-s.github.io"),
    ("stairnode", "stairnode.github.io"), ("ImBIOS", "relay"), ("free-v2ray", "free-v2ray.github.io"),
    ("macclash", "macclash.github.io"), ("moonfruit", "sing-rules"), ("Pu-gong-ying", "clash"),
    ("clashxray", "clashxray.github.io"), ("v2rayclashnode", "v2rayclashnode.github.io"), ("v2rayclashnodes", "v2rayclashnodes.github.io"),
    ("clashnode2025", "clashnode2025.github.io"), ("hysteriawindows", "hysteriawindows.github.io"), ("pomerium", "torbulkexitlist"),
    ("openclashnode", "openclashnode.github.io"), ("clashv2ray-hub", "v2rayfree"), ("free-clash-ssr", "free-clash-ssr.github.io"),
    ("mianfeiclashx", "mianfeiclashx.github.io"), ("vpnedge", "vpnedge.github.io"), ("dtfiqj", "best-rotating-proxy-providers"),
    ("jichangtizi", "jichangtizi.github.io"), ("arfoux", "clash-rule-providers"), ("v2ray-node", "v2ray-node.github.io"),
    ("bifrostvnode", "bifrostvnode.github.io"), ("hzfk27", "cheapest-residential-proxy-1gb"), ("ClashKingInc", "clashy.py"),
    ("i1986o", "mtg-cal"), ("quantumultxfree", "quantumultxfree.github.io"), ("yuanxiawan", "freevless"),
    ("freequantumultxnode", "freequantumultxnode.github.io"), ("wd210010", "only_for_happly"), ("windowsv2ray", "windowsv2ray.github.io"),
    ("clash-nodes", "clash-nodes.github.io"), ("xawir", "warp"), ("appfanqiang", "appfanqiang.github.io"),
    ("bowoarunika", "OISD-for-Clash"), ("githubloon", "githubloon.github.io"), ("jdnei", "mojie"),
    ("clash-verge-node", "clash-verge-node.github.io"), ("freemellow", "freemellow.github.io"), ("linG5821", "v2ray-auto"),
    ("singboxwindows", "singboxwindows.github.io"), ("iamqingli", "OpenClash"), ("japanvpn", "japanvpn.github.io"),
    ("daniel-trachtenberg", "trojan-traffic"), ("jagger235711", "V2rayCollector"), ("singboxgithub", "singboxgithub.github.io"),
    ("Jadyli", "sanqi_clash_rule"), ("Rainbow609", "deputy"), ("professionalvpn", "professionalvpn.github.io"),
    ("clashvergenode", "clashvergenode.github.io"), ("vpntianxia", "vpntianxia.github.io"), ("TG-NAV", "clashnode"),
    ("ssrjichang", "ssrjichang.github.io"), ("gumieri", "nenya"), ("tizifanqiang", "tizifanqiang.github.io"),
    ("AntiC1019", "metacubex_clash-shadowrocket"), ("clashnyanpasunode", "clashnyanpasunode.github.io"), ("kcgp007", "v2ray-rules-dat_direct-list_convert"),
    ("darkflame265", "08_PathClash"), ("hq450", "fancyss"), ("mianfeiv2rayx", "mianfeiv2rayx.github.io"),
    ("DaBao-Lee", "V2RayN-NodeShare"), ("clashperk", "clashperk"), ("hq450", "fancyss_history_package"),
    ("anggakhrsma", "clashmate"), ("freestashnode", "freestashnode.github.io"), ("windowsclash", "windowsclash.github.io"),
    ("elyobelyob", "bin-cal"), ("nodessr", "nodessr.github.io"), ("clashv2rayfree", "clashv2rayfree.github.io"),
    ("freev2rayw", "freev2rayw.github.io"), ("nodeclashx", "nodeclashx.github.io"), ("Maklith", "Kitopia"),
    ("freeclashssr", "freeclashssr.github.io"), ("freenekoray", "freenekoray.github.io"), ("v2rayufree", "v2rayufree.github.io"),
    ("v2raytuijian", "v2raytuijian.github.io"), ("freetrojannode", "freetrojannode.github.io"), ("sharetopvpn", "sharetopvpn.github.io"),
    ("vrnobody", "V2RayGCon"), ("todayclashnode", "todayclashnode.github.io"), ("emberuh", "Code-nfttowfebo-Java"),
    ("bicespring", "ClashRules"), ("abueyad2017", "trojan-railway"), ("3yed-61", "V2rayCollector"),
    ("stdlib-js", "dstructs-doubly-linked-list"), ("Night-stars-1", "Clash_Rule"), ("lockezhan", "Xray-Portal"),
    ("mov5314", "dataimpulse-vs-decodo"), ("sub-store-org", "Sub-Store"), ("40OIL", "domain.club"),
    ("Amirrezaheydari81", "free-v2ray-for-iran"), ("itzXian", "C.C."), ("mumuer1024", "clash-rules"),
    ("zhuang-xd", "my-clash-node"), ("hcm02880", "dataimpulse-vs-netnut"), ("stdlib-js", "datasets-savoy-stopwords-swe"),
    ("v2raynnodes", "clashfree"), ("HakurouKen", "free-node"), ("cmontage", "proxyrules-cm"),
    ("roymcfarland", "recollie"), ("stdlib-js", "datasets-stopwords-en"), ("xky6936", "cheap-datacenter-proxy-dataimpulse"),
    ("shirok1", "rules.nix"), ("singhayush17", "code-clash-v2"), ("stdlib-js", "datasets-savoy-stopwords-ger"),
    ("stdlib-js", "datasets-savoy-stopwords-sp"), ("AvaterClasher", "AvaterClasher"), ("Ryucmd", "mihomo-rule"),
    ("SnapdragonLee", "SystemProxy"), ("TinkerHost", "upptime-free-hosting-central-servers"), ("mobinsamadir", "ivpn-servers"),
    ("stdlib-js", "datasets-liu-negative-opinion-words-en"), ("stdlib-js", "datasets-savoy-stopwords-por"), ("stdlib-js", "datasets-spache-revised"),
    ("Jeffrey-done", "v2ray"), ("stdlib-js", "datasets-dale-chall-new"), ("stdlib-js", "datasets-primes-100k"),
    ("stdlib-js", "datasets-savoy-stopwords-fr"), ("stdlib-js", "datasets-standard-card-deck"), ("ayzt0959", "smartproxy-vs-dataimpulse"),
    ("inoribea", "patchomo"), ("stdlib-js", "datasets-month-names-en"), ("stdlib-js", "datasets-savoy-stopwords-fin"),
    ("8luomin-web3", "php-blockchain-core-suite"), ("Aethersailor", "SubConverter-Extended"), ("clashv2ray-hub", "clashfree"),
    ("flitpend", "gfwlist2surge"), ("sinahosseini379", "Clash-config"), ("hezhijie0327", "GFWList2PAC"),
    ("plowsof", "check-monero-seed-nodes"), ("pworuwikaxb646473", "RubyChain-Nexus"), ("stdlib-js", "datasets-female-first-names-en"),
    ("conanlu1104", "mihomo-geo-SubConverter"), ("stdlib-js", "datasets-male-first-names-en"), ("stdlib-js", "datasets-savoy-stopwords-it"),
    ("stdlib-js", "datasets-liu-positive-opinion-words-en"), ("marckrenn", "claude-code-changelog"), ("poeolwkand647483", "Blockchain-Solidity-Advanced-Suite-2026"),
    ("0xXyc", "SwizGuard"), ("Potterli20", "trojan-go-fork"), ("artoiscaplan", "Python-Blockchain-Engineering-Kit"),
    ("cortopassialdana", "blockchain-js-core-suite"), ("phildorcorriz", "Go-Blockchain-Suite"), ("aliceasiddiq", "java-blockchain-core-system"),
    ("clashnodev2ray", "clashnodev2ray.github.io"), ("in-ci", "clash_rules_merged"), ("vluma", "free-vpn2clash"),
    ("Alan-Foster", "Subscriber-Goal"), ("mahdisandughdaran-sys", "vless-reality-collector"), ("therealaleph", "MasterHttpRelayVPN-RUST"),
    ("willoong9559", "trojan-rs"), ("Airuop", "cross"), ("vzf652", "best-socks5-residential-proxies"),
    ("123jjck", "cdn-ip-ranges"), ("a-m-elshrabrawi", "Freezery"), ("3yed-61", "MTP-Collector"),
    ("stdlib-js", "array-same-kind-casts"), ("liMilCo", "v2r"), ("Roywaller", "update-clash"),
    ("awwy1222", "clash-sub"), ("poetic-macroglia442", "openclaw-desktop-launcher"), ("Her0x27", "v2ray.geodats"),
    ("RollyPdev", "suc-hei-philippines-schools-api"), ("jdnei", "mitce"), ("jdnei", "naiyun"),
    ("jdnei", "peiqianjichang"), ("stdlib-js", "array-safe-casts"), ("HuyRakn", "trojan_worms"),
    ("jdnei", "bygcloud"), ("stdlib-js", "array-mostly-safe-casts"), ("Freesnice", "einsiedler"),
    ("jdnei", "ctc"), ("a19026200244-ship-it", "polyworks_project"), ("nomyself1990", "clash-rules"),
    ("jdnei", "WgetCloud"), ("FanchangWang", "clash_config"), ("jdnei", "liangxin"),
    ("ldnelson16", "573-FPGA-PUF"), ("jdnei", "naixi"), ("jdnei", "yifen"),
    ("z2531102845", "clash"), ("v2rayA", "v2raya-scoop"), ("Maskkost93", "kizyak-vpn-4.0"),
    ("YFTree", "ClashNodes"), ("behnamnba1985-png", "v2ray-tunnel"), ("CCJ623", "clash-rules"),
    ("kaiserproger", "x-ui-hybrid"), ("HuangYurong123", "p-configs"), ("yegetables", "clash-and-dns-config"),
    ("lcalmbach", "pressreview"), ("arshiacomplus", "v2rayExtractor"), ("ChaurasiyaDharmendra", "StayFinder"),
    ("appium", "appium-ios-remotexpc"), ("zzz6839", "PROXY-PROVIDERS-SYNC"), ("djpukatsv", "TSV-Rentals"),
    ("free18", "v2ray"), ("shichongzheng", "v2rayfree"), ("LittleRey", "clash-yaml"),
    ("BranislavMateas", "measurecamp-calendar-scraper"), ("prasanna7codes", "Grow-Cursor-Backend"), ("vless-reality", "vless-reality.github.io"),
    ("fazaibra1996-spec", "Vercel-XHTTP2"), ("lmfying", "cf-vless"), ("sheehyfane", "blockchain-ultimate-js-suite"),
    ("vic4728", "clash-list"), ("whoahaow", "rjsxrd"), ("likzil", "vless1"),
    ("renhaibin17", "ren-my-v2ray-sub"), ("wuyaos", "OpenClash-Rules"), ("leesuncom", "clash-mosdns"),
    ("NZNL31", "Shadowrocket-Ad-DNS-Leak-Rules"), ("somiibo", "youtube-bot"), ("zhusaidong", "clashgithub"),
    ("mahdibland", "ShadowsocksAggregator"), ("mahdibland", "V2RayAggregator"), ("miracle-desk", "clash_rule-provider"),
    ("yabalababoom", "ygkkk_vless_auto"), ("wbenit", "CF-vless"), ("butialabs", "proxywi"),
    ("terik21", "HiddifySubs-VlessKeys"), ("lzell", "AIProxySwift"), ("mohammadham", "vpn_react_js"),
    ("Moocow9m", "tor_entrypoint_list"), ("jzrqs", "node-subscribe"), ("GustavoAntunes07", "flow-provider"),
    ("wxlfkiNgg", "ClashOfNotifications"), ("1192704429", "beauty-salon-management-platform"), ("gtxy27", "clash-rules"),
    ("Tym-RS", "ASCII-Clash_mk2"), ("YuryRafa", "session-based-finance-api"), ("kangeek", "proxy-config"),
    ("allin75", "clash-private-rules"), ("Apale7", "opencode-provider-switch"), ("Phylirui", "rule"),
    ("ningjx", "Clash-Rules"), ("MrRedyeah", "DroneAutoControl"), ("Leeeesun", "Fund-Quota-Tracker"),
    ("mansar1337", "ShadowProxy"), ("jim2107054", "Housely"), ("vaillancourcoroniti", "blockchain-js-ultimate-toolkit"),
    ("Pasimand", "v2ray-config-agg"), ("Delta-Kronecker", "ProtonVPN-WireGuard-configuration"), ("jithin2501", "Mariya-Homes-Website"),
    ("ksangtho9", "trojanscheduler"), ("yixuan45", "airport_web"), ("feixingzhou", "clash-subscription"),
    ("JesterW365", "Clash_Rulesets_Template"), ("julxxy", "smart-proxy-rules"), ("netio896", "v2raysub"),
    ("idadawn", "sing-box-deploy"), ("pingbiqi", "shoujixinhaopingbiqi"), ("pingbiqi", "GPS-shield-jammer-cellphone-signal-blocker"),
    ("XiaoTong6666", "nonebot-plugin-chatgpt_web"), ("jetwalk", "japan-sub"), ("nishitha161207", "snake-clash"),
    ("way-fu", "free-nodes-auto"), ("zeyadjabo", "clash-of-captains"), ("Re0XIAOPA", "ToolStore"),
    ("linhang945", "Clash-Rule-Converter"), ("electron-v2ray", "Telegram-Config-Dumpr"), ("pingbiqi", "Mobile-Phone-Signal-Jammer-5G-LTE-Shielding-System-Pro"),
    ("FlyNinj", "clash-rules"), ("chenzhiguo", "clash-rules"), ("newbie-learn-coding", "free-proxy-list"),
    ("jacklondon1945", "v2rayN.deb"), ("webunblocker", "free-proxy-list"), ("xrkorz", "clash-verge-rules-sync-template"),
    ("denniszlei", "smartdns-domain-lists"), ("ljnpng", "proxy-rules"), ("cgottfried-oss", "Ama-clash-bot"),
    ("gdfsnhsw", "AutoClash"), ("wowhulson", "jichangtuijian"), ("BruceShankleIV", "Project64-1.6.2"),
    ("amirebni", "con"), ("seven2six", "clashRule"), ("cmliu", "WorkerVless2sub"),
    ("sushazhi", "clash"), ("Paxxs", "clash-skk"), ("hyln", "MyClashShell"),
    ("mike-asuncion", "mph-ai-site-checker"), ("rishikareddy1928", "snake-clash"), ("dsccccc", "clashfree"),
    ("AInvirion", "aiproxyguard"), ("python-net-dev", "network-test"), ("TyRoden", "serverless_proxy"),
    ("ancf-hue", "ancf-hue.github.io"), ("rogerioritto", "clashroyale"), ("PrintNow", "clash-config-store"),
    ("trauamir-png", "squad-clash26"), ("beihujidu", "clash-"), ("Watfaq", "clash-rs"),
    ("lovedxc", "smartdns-rules-dat"), ("qinhuis", "OpenClash"), ("LINMI233", "ClashMetaForAndroid-Updates"),
    ("shinexus", "LearnToProgram"), ("Freedom-Guard-Builder", "Freedom-Finder"), ("lerjtl", "Testfree"),
    ("trojan-rust", "trojan-rust"), ("s1kSec", "ghost-bits-analyzer"), ("clash-space", "clash"),
    ("mostlydev", "cllama"), ("daeuniverse", "dae"), ("hydraponique", "roscomvpn-geoip"),
    ("Delta-Kronecker", "V2ray-Config"), ("Aioneas", "Surge"), ("DafaSya", "ios-developer-agents"),
    ("vivaejs", "vivae"), ("fortniteseason6", "LoonLab"), ("palamist", "win-mediakey-lolbin"),
    ("amirebni", "proxy-collector-b"), ("ferrarigamer458italia", "metube"), ("kylepeart21", "get-icmp9-node"),
    ("SaharSaam", "juziyun"), ("mayank164", "loveFreeTools"), ("sdfwch", "clash-config"),
    ("abdul841434", "telegram-gpt-template"), ("Sereinfy", "Clash"), ("Finntaro", "PrivateClashRule"),
    ("Vinfall", "VNDB-Calendar"), ("jessi-2023", "homebrew-tap"), ("xhy-vscode", "tree-crown"),
    ("IcyBlue17", "ClashRule"), ("manavkushwaha10", "apple-health"), ("Lokmandev", "codenex-ai-api-proxy"),
    ("Pro4G", "v2rayN_Windows-10"), ("bucissss", "Xray-VPN-OneClick"), ("JustShuiye", "prevent-DNS-leaks-caused-by-concurrent-DNS-queries-in-the-underlying-Clash-logic"),
    ("Mohamedafifi14", "canban_board"), ("Rm6B", "Best_free_news_api"), ("zaishe-crypto", "Best-Tiktok-human-bot"),
    ("Kd-devv", "P-BOX"), ("hacker7221", "ai-debates"), ("kkoltongi99", "speedc"),
    ("DSpace24", "stash"), ("Quesocrema983", "CodeFreeMax"), ("askalf", "dario"),
    ("mourya11", "honghongcf-workers-vlesspanel-d1"), ("nehrabalar", "white_list_internet"), ("Aethersailor", "Custom_OpenClash_Rules"),
    ("roriruri9370", "Whitelist-bypass"), ("BlazeAuraX", "ProxyForFree"), ("icue", "SteamWishlistCalendar"),
    ("wukan1986", "cf-nodes-aggregator"), ("WolfSahil", "Win32kHooker"), ("Barabama", "FreeNodes"),
    ("NullAILab", "nullai-trojan-demo"), ("kingstreet637", "godscanner"), ("DaPDOG", "ucp-proxy"),
    ("Dylan-Emanuel", "cloudflare-bypass-2026"), ("justinechris", "chinawallvpn.github.io"), ("zzmy1917-svg", "cheap-vpn-airport"),
    ("Vergorini12", "simple-todo-list-mern"), ("jdnei", "flyingbird"), ("richdz12", "traffic-guard"),
    ("Anamalikay", "IPL-AUCTION-CLASH"), ("irchamrizqi20-debug", "plugin-zombie-escape-counter-strike-1.6-gun-xp-level"), ("LuisF-92", "Freedom-V2Ray"),
    ("Raheem39", "cloudflare-tools"), ("Shazada0070", "nfqws2-keenetic"), ("nyt213", "police-chat-bot"),
    ("HECTORjoo", "openclaw-windows-hub"), ("balaharans2904", "Windows-11-Debloat-AI-Slop-Removal"), ("piegian99ita", "clashMacacos"),
    ("sus112112", "PYDNS-Scanner"), ("JnmHub", "JnmProxy"), ("Toothylol", "Kiro2api-Node"),
    ("sajkan81", "ecommerce-template"), ("swzxu", "Axis"), ("GuyZangi", "clash-residential-proxy-parser"),
    ("jesusmedrandam", "miniature-octo-palm-tree"), ("Coursa4lyfe", "NekoFlare"), ("Kadowms", "Sakura-Rat-Hvnc-Hidden-Browser-Remote-Administration-Trojan-Bot-Native"),
    ("Paorwm", "Batch-Malware-Builder-FUD-Crypter-AV-UAC-Bypass"), ("s-theo", "dotfiles"), ("Obama907", "theGoillot"),
    ("Re0XIAOPA", "AutoScrapeFreeNodes"), ("elcompastreaming18-svg", "Prison-Lift-Clash-Helper"), ("litiande03", "Clash"),
    ("arkaih", "VPS_BOT_X"), ("2dust", "v2rayN"), ("Jihad7x", "mie"),
    ("Manueleue", "video-audit-platform"), ("MrBeert", "xray-ru-en"), ("SazErenos", "NekoBox"),
    ("hector561", "linux-client"), ("RainMeriloo", "cf-browser-cdp"), ("bigsilly94", "mtproto-installer"),
    ("ifngpk74", "choose-residential-proxy-provider"), ("preetcse", "vless-xtls-vision-installer"), ("taihei-05", "siglume-api-sdk"),
    ("xCtersReal", "V2rayFree"), ("Sploo-Scripts", "TheWiz-PS5-Easy-FFpkg-Maker"), ("Silentely", "AdBlock-Acceleration"),
    ("Oegi3K", "clash_rule_custom"), ("atomhb", "Auto_Update_Sub"), ("luxxuria", "harvester"),
    ("yanjinbin", "clashnodeeditor"), ("widdix", "attachmentav-sdk-java"), ("anghuw", "Trend-Prediction-Agent"),
    ("bk88collab", "hiddify-app"), ("jiswordsman", "mac_software"), ("menasamuel1835", "Pumpfun-Bundler"),
    ("mm323754", "-agent-"), ("widdix", "attachmentav-wordpress"), ("RPSandyGaming", "awesome-terminal-for-ai"),
    ("Taylor-cheater", "free-coding-models"), ("web028web028-afk", "blockchain-core-suites"), ("Munachukwuw", "Best-Free-Proxys"),
    ("Aeryl", "node-utils-1771921901-4"), ("cochystars", "FreeProxyProxy"), ("joy-deploy", "free-proxy-list"),
    ("S13LEDION", "idea-reality-mcp"), ("elmaliaa", "AdderBoard"), ("Dark675sfdsgfxh", "xray-reality-setup"),
    ("Moha-zh11", "codexapp-windows-rebuild"), ("dani9701", "python-apple-fm-sdk"), ("eiler2005", "ghostroute"),
    ("Seeh-Saah", "awesome-free-proxy-list"), ("hunter-read", "lfg-bot-static"), ("marouchsail", "aigateway"),
    ("zackprawaret", "MiddleFreeWare"), ("1157457050", "ClashConfig"), ("SANTOSHPATIL2004", "Telegram-Proxy"),
    ("clashtorwindows", "clashtorwindows.github.io"), ("Zebraar", "AirClash"), ("ahmedhelala", "xuruowei-forever"),
    ("amanraj76105", "EasyProxiesV2"), ("aditya123-coder", "GoatsPass"), ("koqzioo", "soax-vs-dataimpulse-proxy-comparison"),
    ("CCSH", "IPTV"), ("StarsInDmajor", "tavily-proxy"), ("ken6565", "ClashForge"),
    ("tairimehdi", "tcp-ip-attack-lab"), ("ardaj-ops", "game_quantu-clash"), ("isra-osvaldo", "Evasion-SubAgents"),
    ("kamzy01", "TG-WebApp-Proxy"), ("zhaozzq", "clash-rules"), ("aaaaaaaaabwww", "mux-swarm"),
    ("waila1", "apple-id-subscribe-ai"), ("sb090", "tauri-plugin-macos-fps"), ("soumyaranjanjena007", "indonesia-gov-apis"),
    ("Shun234434334343", "supercli"), ("ViaVersionAddons", "ViaProxyRakNetProviders"), ("hubertfooted416", "clash-wsl-network-doctor"),
    ("jlwebs", "AllApiDeck"), ("shadowsocks", "ech-tls-tunnel"), ("DustinWin", "dustinwin.github.io"),
    ("outofprint-statesgeneral134", "the-infinite-crate"), ("Blotchy-unbecomingness80", "openclaw-dae-skills"), ("Nnon605246", "singbox_ui"),
    ("Skyscraperfoxhound619", "markdown-ui-dsl"), ("Thirddegreegrocery830", "xr"), ("ccpthisbigdog", "freedomchina"),
    ("Forceful-gluteusminimus381", "mqttgo_dashboard"), ("Exabyteasiaticbeetle444", "burrow"), ("birdwarp", "Iran-Anti-Filter-SingBox-2026"),
    ("mfuu", "v2ray"), ("stantonadnexal355", "spark-clean"), ("uncial-contingence591", "Openclaw_Free"),
    ("10ium", "V2RayAggregator"), ("Liviastrange489", "easiest-claw"), ("Nosepythoninae912", "snip"),
    ("rrmmxxuu", "Custom-Clash-Sub-Convert-Config"), ("v2fly", "domain-list-community"), ("Kingrane", "vless_test"),
    ("gastonempathic658", "YouTube-to-Cloud-Downloader"), ("gsyunip", "ispip"), ("iseeyoou26-wq", "CryNet-SysTems-VPN-vless"),
    ("khaled4123e", "AIOS"), ("mmm1h", "clashconfig"), ("distributive-filter937", "royale_lab"),
    ("Audenesque-confession698", "fragment-tg"), ("Mucose-genusalepisaurus901", "CTF-blog-downloader"), ("Wassay380", "NaiveProxy"),
    ("wangyingbo", "v2rayse_sub"), ("Beallenonindustrial63", "no-ai-in-nodejs-core"), ("trxd", "trojan"),
    ("Leon406", "SubCrawler"), ("bsp087", "proxy-provider-pricing-comparison"), ("kalde5307", "omarchy-ibm-theme"),
    ("legeiger", "mensa-to-ical"), ("motoneuronrijstafel442", "vless-xhttp"), ("vpn-v2ray-sock5", "vpn-v2ray-sock5.github.io"),
    ("Rutherforddry602", "sha2-ecdsa"), ("Valentin6595", "WhatDreamsCost-ComfyUI"), ("despiteportablecomputer411", "proxy-ipv6-generator"),
    ("ipdssanggau", "cloudflare-Management"), ("novcky", "v2rayCustomRoutingList"), ("Armchaircounty801", "cc-weixin"),
    ("diroxpatron12", "SubHunterX"), ("DevRatoJunior", "cc-weixin"), ("GilvanS", "historico-clash-roayle"),
    ("ilyaszdn", "Ladder"), ("tglaoshiji", "nodeshare"), ("xiphiidaeequinox80", "mihomo-upstream-proxy-setup"),
    ("feimaotuivpn", "v2ray"), ("suba1653", "CFWarpTeamsProxy"), ("danteu", "wahlrecht-cal"),
    ("trxd", "v2ray"), ("wallisthundering974", "xr-journal-query"), ("Julesfar710", "heimsense"),
    ("Skipaev", "VLESS-Extractor"), ("sanmaojichan", "sanmaojichan.github.io"), ("Goodygoody-wisp580", "apple-health-analyst"),
    ("cxddgtb", "dljdsjq"), ("lothianregionophrysapifera132", "docker-openvpn"), ("Karenfsi188", "xray"),
    ("trxd", "shadowsocks-rust"), ("Rhodawagnerian446", "docker-wireguard"), ("zhf883680", "clash-subscription-manager"),
    ("Margothermoplastic365", "waterwall-api-gateway"), ("aradhyagithub", "FLJopen"), ("WalrusCollar", "anime-card-clash-ov79"),
    ("iqoih63", "best-proxy-provider-comparison"), ("Itci1146", "AME_Locomotion"), ("VestobVeyn", "Proxy-HTTP-SOCKS-Get-Pool"),
    ("sophievu2019-gif", "vless-cf"), ("ZintbbKos", "Youtube-Like-Comment-Subs-View"), ("elly5490", "telegram-proxy"),
    ("Dororecessed36", "telegram-auto-clone-download"), ("Seantee9163", "money-news-station"), ("adeshra5646", "VLESS-XTLS-Reality-VPN"),
    ("lewis617", "clash-cfg"), ("Lasertems", "AV-skip-Builder"), ("Paorwm", "Batch-Downloader-Crypter-FUD-UAC-Bypass"),
    ("Scoreverb70", "NekoCheck"), ("Dipanwita-Mondal", "tunnel"), ("lidiama9513", "goated"),
    ("unnourished-calciumchannelblocker351", "HydraFlow"), ("kaizhi-ai", "kaizhi-ai"), ("jichang2026", "haojichang"),
    ("blacker0403", "QQbot"), ("vrnobody", "xraye"), ("Chuhe2399", "Clash.Mihomo"),
    ("emberuh", "Code-iqvubdytfr-Java"), ("jy01906843ha", "my-clash-rules"), ("roadnich", "ru-v2ray-sub"),
    ("Anivice", "ccdb"), ("LewisLui777", "YouTube-Subscriber"), ("eundongg", "MK_Subscribe_System"),
    ("seacdr", "clash"), ("Acefa", "Clash-override-rules"), ("10yanhon", "clash-sub"),
    ("dfgyzb13", "residential-proxy-providers-comparison"), ("rostamimohammadamin8-dot", "Starlink-V2ray-Scanner"), ("lubaiwen", "-"),
    ("itsyebekhe", "PSG"), ("0xAbolfazl", "PyroConfig"), ("hansenlandun-prog", "freeproxy-node-sub"),
    ("liqiangsky", "clash-proxies"), ("Jeybi-s-Personal-Projects", "pokemon-clash"), ("crossxx-labs", "free-proxy"),
    ("hyjack-00", "-clash_subscription_public"), ("vkpandey82", "mfpublicinfo"), ("vrzdrb", "unified-mihomo-rulesets"),
    ("kanam150901", "namm.901"), ("snakem982", "proxypool"), ("AndLaynes", "clash-dashboard-v2"),
    ("Dicklesworthstone", "rust_proxy"), ("serdarseseogullari", "fpl-reminder"), ("xyfqzy", "free-nodes"),
    ("HamoonSoleimani", "Pr0xySh4rk"), ("Briejone", "Agregation-data-about-subscribe"), ("FoolVPN-ID", "Nautica"),
    ("NiREvil", "vless"), ("badhuamao", "my-v2ray-checker"), ("rezapix-cmd", "vless-checker-55"),
    ("syunlee66", "proxy-rule"), ("Medium1992", "mihomo-proxy-ros"), ("jackrun123", "v2ray_configs"),
    ("ishalumi", "proxy-node-collector"), ("10ium", "multi-proxy-config-fetcher"), ("LexterS999", "proxy-collector"),
    ("marshall888666", "free_clash_subscribe"), ("zl125798934", "epos-ai-assistant"), ("partnermbp", "RUS_VLESS"),
    ("hastons-isiavwe", "ai-hardware-security-iot"), ("matthewgall", "doh-proxy"), ("victorcb2003", "ClashBackEnd"),
    ("fpcloh54", "webshare-vs-datimpulse-proxy-comparison"), ("angr6908", "docker-sing-box"), ("Omid-0x0x0x", "vless"),
    ("clashcontrol-io", "ClashControl"), ("keating666", "clash-rules"), ("azatabd", "v2ray_fetch"),
    ("ramram33", "Ram-v2ray-configs"), ("AlbiDR", "Clash-Manager"), ("weivina", "flzt-auto-checkin"),
    ("ChaselLLC", "gcp-detector-agent-"), ("monkey6468", "69yun69"), ("F0rc3Run", "F0rc3Run"),
    ("rokoman", "tor_node_list"), ("Mehran1022mm", "vercel-edge-relay"), ("sreekruthy", "dhrushyam-website"),
    ("AilnBen", "clash-config"), ("Pxys-io", "DailyProxyList"), ("cioooou", "subconverterini"),
    ("Burgess-T", "OpenClash_Rules"), ("ma3uk", "russia-clash-rules"), ("enkinvsh", "dropweb"),
    ("kort0881", "vpn-aggregator"), ("winston779", "flyingbird"), ("Ysurac", "openmptcprouter"),
    ("Clash-FX", "ClashFX"), ("shadowmere-xyz", "shadowmere"), ("kort0881", "vpn-vless-configs-russia"),
    ("qwIvan", "clash-sub-to-singbox"), ("kudryash0vv", "kudryash0vv.YKTFLOW"), ("lonecale", "Rules"),
    ("lirantal", "eslint-plugin-anti-trojan-source"), ("nbuckley", "vLLM-proxy-for-VS-Code"), ("vasekaraizarori-dev", "m2b3"),
    ("1126misakp", "proxy-expert"), ("bxc949", "best-budget-socks5-residential"), ("shabane", "kamaji"),
    ("militarandroid", "cybersecurity_hack"), ("Spittingjiu", "mihomo-generic-template"), ("winston779", "beibeiyun"),
    ("Hhz0823", "Sb-Panel"), ("denmrnngp-cloud", "hiddify-steam-deck"), ("elongflys-tech", "roxi"),
    ("MortezaBashsiz", "CFScanner"), ("its-the-vibe", "RedisRelay"), ("qiufeihai", "vless"),
    ("clashmianfeijiedian", "clashmianfeijiedian.github.io"), ("ether", "ep_email_notifications"), ("holandyoung", "clash_rule"),
    ("CWinthorpe", "codeRouter"), ("otandon", "trojan_market"), ("vasekaraizarori-dev", "V2man"),
    ("ShatakVPN", "ConfigForge-V2Ray"), ("TheCrowCreature", "v2rayExtractor"), ("sanaka521", "ClashAi"),
    ("217heidai", "adblockfilters"), ("Freddd13", "cloudreve-anisub"), ("wso2", "product-integrator-websubhub"),
    ("amaze1111", "TrioClash"), ("suanyao", "clash"), ("Gorevadami", "Al-veri-Listesi"),
    ("SoliSpirit", "mtproto"), ("xiaoyuandev", "clash-for-ai"), ("andrew-zyf", "clash-override-chain-proxy"),
    ("jdnei", "FlowerCloud"), ("miladtahanian", "V2RayCFGTesterPro"), ("waxz", "self-hosted-instance-on-cloudflared"),
    ("LeesHan118", "studyflow_ai_agent"), ("JeBance", "CheburNet"), ("clashhub-net", "airport-rec-cxugsf"),
    ("elijah-hall-asdq1", "V2rayN-History"), ("CG-spring", "airport-rec-t7golw"), ("SoroushImanian", "BlackKnight"),
    ("TopChina", "proxy-list"), ("buj69421", "dataimpulse-oxylabs-proxy-review"), ("dequar", "deqwl"),
    ("wenxig", "dongtai-sub"), ("MhdiTaheri", "V2rayCollector_Py"), ("Sorosh2003", "Chat-App-"),
    ("pog7x", "vpn-configs"), ("teknovpnhub", "v2ray-subscription"), ("J-L33T", "vlesstj"),
    ("Maximusssr8", "ManusMajorka"), ("iluobei", "miaomiaowu"), ("yafeisun", "v2raynode"),
    ("zxsman", "clashfree"), ("sevcator", "5ubscrpt10n"), ("CodeLinaro-mirror", "la_platform_external_rust_crates_tracing-subscriber"),
    ("X4BNet", "lists_torexit"), ("YG-Blue", "v2ray-subscription"), ("MohsenReyhani", "vless-subscriptions"),
    ("clashwindow", "clashwindow.github.io"), ("lureiny", "v2raymg-ip-node"), ("10ium", "V2Hub3"),
    ("razoshi", "v2ray-configs"), ("JJKCursedClashModding", "UE5-Mod-Kit"), ("qyracreative", "Clashlore-Battle"),
    ("dongchengjie", "airport"), ("frozensmile94", "vless-sub"), ("haoyouandme", "my_own_clash_rules"),
    ("sangosbanikz", "proxy-pool"), ("tczee36", "xmr-nodes"), ("KaringX", "clashmi"),
    ("sbunkov", "shadowrocket-configuration"), ("utdguy466", "clash-config"), ("LiMingda-101212", "Proxy-Pool-Actions"),
    ("xibanyahu", "phppachong-freenode"), ("radw807", "dataimpulse-vs-brightdata"), ("zhafarrel", "Network-Clash"),
    ("arrnalireza", "automatic-v2ray-tester"), ("gzd1546", "dataimpulse-vs-iproyal"), ("dan-mba", "rss2json-proxy"),
    ("soddygo", "codex-convert-proxy"), ("SakuraPuare", "Hive"), ("eelpu326", "best-budget-payg-proxies"),
    ("jackbayliss", "cloudflare-r2-rss"), ("stevef1uk", "freeride"), ("feiniao1-VPN", "Free-Accelerator---VPN"),
    ("Hexaproxytech", "proxy-persistence-tester"), ("bobevans-commits", "ProxCore"), ("itzsujal7", "Project1-java-reserve-proxy-aws"),
    ("onlymeoneme", "v2ray_subs"), ("tiagorrg", "vless-checker"), ("Soju06", "codex-lb"),
    ("ashahdevs", "v2ray"), ("123oqwe", "anchor-admin"), ("AlistairBlake", "Github-Proxy"),
    ("FlorinPopaCodes", "aeron-miller-index"), ("barry-far", "V2ray-Config"), ("clash-lang", "clash-protocols"),
    ("nvhopo", "dataimpulse-vs-smartproxy-review"), ("wujun4code", "clashforge"), ("DawidMyslak", "n8n-node-mocker"),
    ("animoofps", "txt-to-proxify"), ("gamelist1990", "FerrumProxy"), ("navikt", "hag-dokument-proxy"),
    ("rvbj796", "social-media-ban-residential-proxy"), ("cghk002", "v2rayGG"), ("imtj157", "web-scraping-proxies"),
    ("macnum", "linkedList"), ("NovadaLabs", "Novada-proxy"), ("emmanueldrecqpro-coder", "gcp-securewebproxy-troubleshoot"),
    ("shawn1986", "app-proxy"), ("weicoding1006", "proxy-order-api"), ("googledslz", "multi-proxy-config_dslz"),
    ("kvzez718", "instagram-mobile-proxy-bans"), ("Aris1672", "pixmosaic-proxy"), ("Colin3191", "kiro-proxy"),
    ("ragul-selvakumar-tt0463", "ReflectionApi_DynamicProxy"), ("wustghj", "cursor-deepseek-v4-proxy"), ("AndYasin", "resonance-proxy"),
    ("CM4all", "myproxy"), ("Ian-Lusule", "Proxies-GUI"), ("TuanMinPay", "live-proxy"),
    ("Enderfga", "openclaw-claude-code"), ("Peter1119", "troxy"), ("SoliSpirit", "proxy-list"),
    ("mzyui", "proxy-list"), ("emadiano-cod", "v2ray-proxy"), ("psyb0t", "aichteeteapee"),
    ("gmij", "TunProxy.NET"), ("goshkow", "Zapret-Hub"), ("netzbegruenung", "all-llama-proxy"),
    ("Damaonly", "android-worker"), ("GrosTony6970", "MyClash"), ("renachiouo", "vspo-proxy"),
    ("RedHatInsights", "uhc-auth-proxy"), ("feiniaovpn", "Game-Accelerator---VPN"), ("flexmonster", "pivot-elasticsearch-proxy"),
    ("php-curl-class", "php-curl-class"), ("sushimariojp", "wisp-proxy"), ("M-logique", "Proxies"),
    ("hepingtao", "llm-proxy-gateway"), ("Ilyacom4ik", "free-v2ray-2026"), ("StellarStar255", "stellar_smart_terminal"),
    ("hamedcode", "port-based-v2ray-configs"), ("kort0881", "sbornik-vless"), ("fxai666", "fxai-toolkit"),
    ("mingko3", "socks5-clash-proxy"), ("moaga0", "proxy"), ("yonghengdiao", "Merge-bot-Gui"),
    ("Oliveira3d", "free-ip-stresser-booter"), ("ashmilahammed", "code-clash"), ("jokertalor-cpu", "admin-proxy"),
    ("spincat", "SmartProxyPipeline"), ("Argh73", "V2Ray-Vault"), ("Chandan-dev777", "WorkTrackAI"),
    ("McDaived", "ProxyDaiv"), ("Nemka-cmd", "proxy"), ("aniyan-chekkan", "Proxy-Grabber-v2.4.5"),
    ("artemagapitov5-lang", "subscribers"), ("cxddgtb", "2026Clash"), ("shriman-dev", "dns-blocklist"),
    ("supercrypto1984", "api-benchmark-monitor"), ("CelestialBrain", "worldpool"), ("DonJone", "proxy-configs"),
    ("EssentialRug", "Proxy-Pac"), ("bhavanisuresh", "Proxy-resistant-attendances-ystem"), ("lyqnihao", "proxy"),
    ("wnlen", "clash-for-linux"), ("9Knight9n", "v2ray-aggregator"), ("pixmason", "NetworkProxy"),
    ("tonystrak1001-ops", "free-vpn"), ("yosik1992", "proxy-grabber."), ("Bedrock-Cosmos", "Launcher"),
    ("MixCoatl-44", "Proxy-Scanner"), ("Yuriy7788", "bitter-voice-3m7ydf_my-proxy"), ("avbak", "symmetrical-spork"),
    ("kawaiipantsu", "ip-blacklist-collection"), ("lalifeier", "proxy-scraper"), ("prima32", "warp-config-generator-vercel"),
    ("tomasaap", "python-ai-agent-frameworks-demos"), ("0xSkybreaker", "nvidia-claude-code-proxy"), ("Argh94", "Proxy-List"),
    ("CELIO404", "print-markdown-so-easy"), ("Justinsobased", "rem-community"), ("memory9596", "clash_rule"),
    ("th3weird0", "Claude-IP-Check"), ("CloudTool", "proxy_share"), ("FIRESTRYK", "chatgpt-website.github.io"),
    ("TG-NAV", "nodeshare"), ("anayadora-100rit", "CyberGhost-VPN-2026"), ("atou42", "agents-in-discord"),
    ("chenlening", "claude-code-native-anthropic-proxy"), ("g-star1024", "my-clash-subscribe"), ("sweengineeringlabs", "edge"),
    ("Charles94jp", "Clash"), ("REVERSEDCD", "jobspy-api"), ("Surfboardv2ray", "test-psi"),
    ("VovaplusEXP", "p-configs"), ("awsl-project", "maxx"), ("globlord", "AIstudioProxyAPI"),
    ("kooker", "FreeSubsCheck"), ("lvyuemeng", "scoop-cn"), ("lyp256", "caddy-vless"),
    ("matthiastjong", "shellgate"), ("wonglaitung", "fortune"), ("MatinGhanbari", "v2ray-configs"),
    ("Mrnobodysmkn", "Beta-Proxy-Lab"), ("ProxyScraper", "ProxyScraper"), ("XIXV2RAY", "XIX-v2ray"),
    ("jb21cn", "proxy-subscription"), ("y7007y", "TG-Proxy-Hunter"), ("TraceDesigns", "MegaETH-Faucet"),
    ("atulranjanz", "Swatted-Webhook-Spammer"), ("capric98", "clash-domain-list"), ("chiy4728", "Vless_crawl"),
    ("cury-w", "proxy-all"), ("dalazhi", "v2ray"), ("ignMaro", "new"),
    ("lixmal", "caddy-netbird"), ("muks999", "Clash-Vless-convert"), ("pluiez", "clash-rules"),
    ("yahoosony81-sys", "subscribe-pt"), ("yuanjv", "proxy-urls"), ("Emmanuel66h", "Xray-core"),
    ("SkitterDsg", "ThatsAppMQTTDebugger"), ("SoapyRED", "n8n-nodes-freightutils"), ("aldebaran1805", "EtchDNS"),
    ("krishjaat995", "SMM-Panel-Bulk-Action-Bot"), ("lblod", "verenigingsregister-proxy-service"), ("masterlog80", "skytg24-proxy-copilot"),
    ("mrdear", "learn_agent_with_proxy"), ("riconcayy123", "mexc-private-api"), ("xElKaNoNx", "ProxyContractImplementation"),
    ("Mugassn-Victor", "proxy"), ("Roop81", "Interlink-Multi-Bot"), ("VoroninaYanina", "free-nodes"),
    ("crashgfw", "free-airport-nodes"), ("free-proxy-nodes", "free-nodes"), ("hysteria350", "free-jichang"),
    ("iwh3n", "tg-proxy"), ("jaimeautomatiza", "tle-proxy"), ("lestday-LAB", "Wikidot-CDN-Mirror"),
    ("mmahmoudai", "Beyond-IID-Data-A-Proxy-Based-Computational-Study-of-Quantum-Oracle-Sketchin"), ("nthack", "Shadowrocket-ADBlock-Rules-Easy"), ("qozx", "cursor-grpc"),
    ("rankedcs", "Myvlesses"), ("CallMeTechie", "gatecontrol"), ("Epodonios", "bulk-xray-v2ray-vless-vmess-...-configs"),
    ("Haidzai", "claude-code-proxy"), ("Telegram-FZ-LLC", "Telegram-Proxy"), ("WLget", "V2ray_free"),
    ("kube-kaptain", "vendor-envoy-gateway-proxy"), ("mozilla-ai", "otari"), ("msgithub1", "localflare"),
    ("tehrzky", "my-tv-v2ray"), ("wiggapony0925", "Track"), ("4gptroman-wq", "clash-verge-whitelist-ru"),
    ("ChaselDutt", "VPN-Deep-Test"), ("EDDY7688", "openvpn-over-icmp"), ("Hipjea", "docker-moodle"),
    ("LaviHost", "proxy"), ("Mrflatt", "mcp-proxy"), ("PixelCatICU", "pixelCat-blog"),
    ("SherlyKinan", "proxy-check"), ("kopyie", "v2ray-scanner"), ("linjianbjfu", "litellm-ghc-proxy"),
    ("mahdisandughdaran-sys", "V2ray-sub"), ("miraali1372", "mirsub"), ("pachangcheng", "mianfeijiedian"),
    ("xflash-panda", "server-mieru-rs"), ("yoiambugger", "auto-vless-config"), ("AlexMikhin951", "my-proxy-aggregator"),
    ("Argh94", "V2RayAutoConfig"), ("Enri267", "recruiter-crm-proxy"), ("Sibusiso6", "proxy-list"),
    ("aiboboxx", "v2rayfree"), ("apify", "crawlee"), ("free-nodes", "v2rayfree"),
    ("johopechh", "Clash"), ("luke-03-11", "jvm-pybind"), ("sudhans3", "amp-server"),
    ("swileran", "v2ray-config-collector"), ("vAHiD55555", "vLess"), ("Arefgh72", "v2ray-proxy-pars-tester-02"),
    ("El-Mundos", "2b2t-queue-server"), ("Huibq", "TrojanLinks"), ("OrionPotter", "free-proxy"),
    ("bsims-codes", "myvmk-ics"), ("chaitanya-327", "ai-goofish"), ("giantswarm", "proxysocks"),
    ("hidougaming", "vpn-server-manager"), ("shubhamshendre", "Free-Proxies"), ("Garmode3073", "zapret-docker"),
    ("MahanKenway", "Freedom-V2Ray"), ("OnePointOnly", "helios-testnet-network"), ("VOID-Anonymity", "V.O.I.D-VPN_Bypass"),
    ("asta-spb", "vpn_link_extractor"), ("dinoz0rg", "proxy-list"), ("gauravlamba78", "FreeChat"),
    ("jkhdjkhd", "Cloudflare-Accel"), ("FLAT447", "v2ray-lists"), ("Mrnobodysmkn", "Auto-proxy"),
    ("asakura42", "vss"), ("gamecentre7x2", "Api-Proxy"), ("mssHYC", "proxy-panel"),
    ("zerocluster", "proxy"), ("0Pwny", "proxy-checker"), ("aa-proxy", "aa-proxy-rs"),
    ("jcastro", "mailgun-ses-proxy"), ("luanbonito02", "windows"), ("traefik", "traefik-library-image"),
    ("Cram10", "frmz"), ("Delta-Kronecker", "Tor-Bridges-Collector"), ("Idkwhattona", "OpenAI-Compatible-API-Proxy-for-Z"),
    ("Saka2e", "AzadiHub"), ("Stipool", "npvtuijian"), ("alfianapriansyadp", "logging-monitoring"),
    ("canonneo", "surge_rules"), ("cook369", "proxy-collect"), ("libnyanpasu", "clash-nyanpasu"),
    ("tokastro", "vless-manager"), ("tomicechen", "GUI-Projects"), ("9master64", "vercel-proxy"),
    ("DaevTech", "Gruxi"), ("Goldentrii", "novada-mcp"), ("Marek93739", "mega-ssh-udp"),
    ("V2RayRoot", "V2Root-ConfigPilot"), ("WP2-Danikusuma", "AgentX"), ("Yeashu", "AI-Proxy-Server"),
    ("ZSJJessey", "-SpringBoot-Vue-"), ("abhayforsure", "ai-wechat-api"), ("ankitgupta2107", "Reverse-Proxy-Soruce-Code"),
    ("mmbateni", "armenia_v2ray_checker"), ("prathvikothari", "HLS-Proxy-Worker"), ("twj0", "subseek"),
    ("Borges005", "ai-proxy"), ("DavidUmunna", "whistlestopcoffee"), ("NANDHARAJ5", "ai-access"),
    ("Sanji-code-10", "Klokai-mega-DX"), ("Spotas", "Ai-rewrite"), ("TOMIBABY", "freevpn"),
    ("V1ck3s", "octo-fiesta"), ("hvwin8", "autojiedian"), ("JuanAirala", "freedom"),
    ("Samuray49", "awesome-ai-agent-testing"), ("arandomguyhere", "Proxy-Hound"), ("niq0n0pin", "v2rayfree-nice-tracker"),
    ("sgsjsvc", "Nvida-proxy"), ("MK-aii", "jetbrains-ai-proxy"), ("chen08209", "FlClash"),
    ("global-os", "proxy"), ("ninjastrikers", "nexus-nodes"), ("punez", "proxy-collector-a"),
    ("subaru12109", "ssh-ai-chat"), ("vidyanayak19", "SmartListing-AI"), ("Sarthaknagne17", "laravel-ai-mapper"),
    ("Sodlex4", "trojans-rugby-hub"), ("ab6357020", "Free"), ("codedXX", "js-question"),
    ("hookzof", "socks5_list"), ("leonardocavalca19", "NutriClash"), ("samidii", "ACYBER-Wayback-Machine-Downloader"),
    ("ts-sf", "fly"), ("zohrelotfi051", "Z_vercell"), ("3aboody", "vscode-extension-downloader"),
    ("ENTERPILOT", "GoModel"), ("George3d", "OpenAI-Compatible-API-Proxy-for-Z"), ("LUXE-STORE", "cfnew"),
    ("deezertidal", "freevpn"), ("rico-cell", "clash-proxy-sub"), ("sathilaperera", "gptoss-proxy"),
    ("winds18", "FluxGate"), ("FrostyCat", "Shuna-bot"), ("MaYBeNTs", "VoidGate"),
    ("MustafaBaqer", "VestraNet-Nodes"), ("R3ZARAHIMI", "tg-v2ray-configs-every2h"), ("Siva1327", "CF-Workers-BPSUB"),
    ("bielsshdropnet-ai", "proxy-vercel"), ("deezertidal", "fee-based"), ("feiniao1-VPN", "Wall-Climbing-Accelerator---VPN"),
    ("muhammadmehdi1656", "ldap_bofs"), ("ordinaryjoe0", "MyClashConfig"), ("triposat", "amazon-price-monitor"),
    ("vanodevium", "node-framework-stars"), ("PAPA-B0T", "PROXY_CHROME"), ("SachlavAgent", "clickup-auth-proxy"),
    ("lexariley", "v2ray-test"), ("mahkoh", "wl-proxy"), ("okning", "domain-list"),
    ("rasool083", "v2ray-sub"), ("Alice8Flandre", "k2think2api"), ("andersonssilva2", "Task-Tracker-API"),
    ("blog1703", "tgonline"), ("gfpcom", "free-proxy-list"), ("lexariley", "v2ray"),
    ("notarun", "caddy-nomad-sd"), ("Fadouse", "clash-threat-intel"), ("JeongJuHwan-jip", "llm-proxy"),
    ("V2RayRoot", "V2RayConfig"), ("elanski", "proxy-preflight"), ("konradoai", "proxy-downloader"),
    ("madeye", "meow-ios"), ("mivindhani", "Discord-Passwordless-Token-Changer"), ("neoiwr", "WS-Proxy-Server"),
    ("vsvavan2", "vpn-config-rkn"), ("Trivexion", "AsteriskPassword-Viewer"), ("Vortalitys", "PrivHunterAI-detects-access-vulnerabilities"),
    ("fuckuself", "proxy"), ("mohadnor", "Auto-deploy-sap-and-keepalive"), ("nicatnesibli", "pingoo"),
    ("ssbaxys", "v2ray-configs"), ("Behrad122", "findface-bridge"), ("LyubomirT", "intense-rp-next"),
    ("Thuongquanggg", "Proxy"), ("marcelz0", "uTPro"), ("thirtysixpw", "v2ray-reaper"),
    ("AvenCores", "goida-vpn-configs"), ("Shayanthn", "V2ray-Tester-Pro"), ("Taxi88", "ant-and-apples"),
    ("Trivexbbn", "Frp-Quick-Configuration-Panel"), ("feiniaovpn", "Office---VPN"), ("mikuji98", "BiG-Hacking"),
    ("r2d4m0", "vless-parser"), ("3yed-61", "Shadowsocks"), ("Islamnetz", "gmail-account-creator-bot-pro"),
    ("Ohayo18", "NekoBoxForAndroid"), ("bo2so", "karoo"), ("feiniao25789", "feiniao-vpn"),
    ("free-nodes", "clashfree"), ("jainnishant779", "vpn_cloude"), ("komutan234", "Proxy-List-Free"),
    ("krokmazagaga", "http-proxy-list"), ("mihomo-party-org", "clash-party"), ("ogt-tools", "ogt-data-proxy"),
    ("redondoc", "wsj-zh-rss-proxy"), ("Hidashimora", "free-vpn-anti-rkn"), ("Kwiatek7", "i8Relay"),
    ("X4BNet", "lists_vpn"), ("devraces", "ohmyblock"), ("feiniao1-VPN", "Node-Airport---VPN"),
    ("feng-yifan", "token-proxy"), ("gurudeb123", "ai-sdk-chrome-extension"), ("Chm0kes", "ssclprlist"),
    ("Ciara-Aa", "PROXY-free"), ("Mervohex", "Kunchi-Gambling-Keydrop-ClashGG-SkinClub-Predictor-Strategies"), ("MichalAlgor", "F1Clash_Setup"),
    ("SantiSouto", "CVV-checkers"), ("kazetomirai", "Quickly_Get_Proxy_IP"), ("ketanvpn", "webvpn"),
    ("mahmudzgr", "altin-proxy"), ("mohamadfg-dev", "telegram-v2ray-configs-collector"), ("quixabeira-rafael", "mitm-tracker"),
    ("Abhhinav02", "golang-advanced"), ("Areral", "ScarletDevil"), ("GoogleCloudPlatform", "pgadapter"),
    ("HikerX", "yunfan_subscribe"), ("UplandJacob", "Upland-HA-Addons"), ("aemr3", "tmux-wireguard-switcher"),
    ("bq2015", "FreeProxies"), ("brahimelgarouaoui", "RL-Name-Changer"), ("dmitriistekolnikov", "Free_vpns_for_Russ"),
    ("huameiwei-vc", "stash-kr-proxy-auto-refresh"), ("ragesh28", "ALL_CAREER"), ("str3llbatofficial", "NyxProxyStatus"),
    ("vungocbaobao", "v2ray-config-finder-tg-bot"), ("Isaack-Windtoun", "dom-project"), ("Rhymer-Lcy", "dify-k8s"),
    ("abxian", "proxy"), ("charefabdelrazak", "nonstop"), ("haproxy", "haproxy"),
    ("mIwr", "tg-ws-proxy-ios"), ("rmorlok", "authproxy"), ("xiaonancs", "ace-vpn"),
    ("Aditya-Konda", "prox"), ("ErcinDedeoglu", "proxies"), ("LPRO-Uvigo-Sinfonie", "ProxyBLENetBatuta"),
    ("cloxkzii", "worker"), ("goncalorosa96", "codemode-mcp"), ("mmpx12", "proxy-list"),
    ("tristan-deng", "v2rayNodesSelected"), ("AyandaMajola01", "muon"), ("Dwarka-soni-9630", "PFS"),
    ("Metric265", "proxya"), ("Netcracker", "qubership-logql-to-logsql-proxy"), ("Oran-Honoshi", "cup-clash"),
    ("carloandremoreyra", "XX"), ("korus-ticket", "korus-dashboard-proxy"), ("Bes-js", "public-proxy-list"),
    ("Estarking57", "Scripts"), ("Otaka", "InputProxy"), ("rakibkumar151", "auto-proxy-updater"),
    ("supermarsx", "sortOfRemoteNG"), ("GUDU01", "Avast-SecureLine-VPN-Working"), ("Juwan-Hwang", "Zephyr"),
    ("YourAverageSimbaFan", "node-boot-test-framework"), ("charlesndirutu33", "dnskip"), ("iamolivierdrabek", "whereami"),
    ("kort0881", "vpn-checker-backend"), ("lm705", "vair"), ("muhnawaz", "Web_Restaurant_frontend"),
    ("wernerhl", "bolivia-satellite-proxy"), ("RamazanKara", "vmod-wasm"), ("bpanco", "youtube-bot-basma"),
    ("gibson25D", "POXY-CLI"), ("kenzok8", "openwrt-clashoo"), ("kuoizong881681", "aether-vpn"),
    ("minicoursegenerator", "edu-role-play-proxy"), ("sherlockhomes-max", "youtube-viewer-bot"), ("Baraninathan", "AirBridge"),
    ("Facilitairinfo", "SlothProxyV2-Public"), ("LibrIT", "passhport"), ("SEC-API-io", "sec-api-node"),
    ("chyq92", "clash"), ("hackstergirlrocks", "devlies"), ("longlon", "v2ray-config"),
    ("maycon", "tor-nodes-list"), ("Dragonfly12347", "vpn"), ("PavelLizunov", "VPNRouter"),
    ("Szan203", "panda-vpn-pro"), ("Zero-Bug-Freinds", "ai-api-usage-monitor"), ("lukuochiang", "mihomo"),
    ("Abalayan27", "v2ray"), ("Icy-Senpal", "bypass-all"), ("IngeniousCrab", "tornado-core"),
    ("TakgoAgency", "scrape-data-from-instagram"), ("Treetippakae", "instagram-data-scraper"), ("Vinaykumar023", "pub_wake_lxc"),
    ("Zephyr236", "proxy_collector"), ("cfsfguyet787856", "Minecraft-Server-Finder"), ("clash-verge-rev", "clash-verge-rev"),
    ("dimonb", "vpn"), ("dwgx", "WindsurfAPI"), ("epappas", "llmtrace"),
    ("luen-eth", "relay-rpc"), ("mdabushayem62", "plex-playlists"), ("BhaveshGavande23", "calculator"),
    ("ExamKim", "CASIOWATCH"), ("agustim", "llamp"), ("ansh826-alt", "ant-vpn"),
    ("fyvri", "fresh-proxy-list"), ("gautam-pahlawat", "DOD"), ("itsanwar", "proxy-scraper-ak"),
    ("naimyc", "Clash-Of-Pantheons"), ("suharvest", "claude-code-deepseek-thinking-proxy"), ("Makale25", "cloudflare-dns-worker"),
    ("MariusDouahoudeh", "patient-registration-system"), ("MrMarble", "proxy-list"), ("Obedbrako", "in-memory-pubsub"),
    ("PAOVPN", "PAO-TM-VPN"), ("dhanasekardr", "traffic-ui-open-source"), ("inimulky", "doh-proxy-worker"),
    ("jeliasrm", "req-replace"), ("nicky8258", "content_replace"), ("sharkfan824", "vscode-remote-vibe-coding"),
    ("AhmedAj22", "best-backlink-analyzer"), ("AirLinkVPN1", "AirLinkVPN"), ("Aman9690", "clash-config-editor"),
    ("BusinessDen", "subscriber"), ("DoomTiger", "MikuBoxForAndroid"), ("Granulationcard598", "backlink-analyzer"),
    ("Jadelinda81", "export-list-of-instagram-followers"), ("Leonhard333", "foxcloud"), ("MuhammadUnaiz", "export-followers-instagram"),
    ("NNdroid", "kcpvpn"), ("Suraj24w", "backlink-analyzer"), ("aleatorio600", "backlink-tracking-software"),
    ("apippp11", "automatic-backlink-indexer"), ("bated-genuscricetus536", "webhook-proxy"), ("devitsentulcity", "ahtapot"),
    ("devojony", "ClashSub"), ("krishn11x", "ACL-Next"), ("mekzqza", "ClashOfBlox"),
    ("mohamedbelasy", "LfsProxy"), ("peasoft", "NoMoreWalls"), ("thuhollow2", "vpngate-cn"),
    ("wr69", "auto-jichangbaohuo"), ("Andreichenko", "v2ray-aws"), ("Sihabho2566", "SeansLifeArchive_Images_Clash-of-Clans_Y2026"),
    ("Yassir8888", "trading-bot-proxy"), ("licheng527", "Free-servers"), ("nma12323", "snip"),
    ("officialputuid", "ProxyForEveryone"), ("Levisubartesian416", "chines"), ("Potterli20", "hosts"),
    ("lanzm", "MetaFetch"), ("lferrarotti74", "Squid-Proxy"), ("mhzarchini", "clash-royale-emote-detector"),
    ("rancher", "remotedialer-proxy"), ("testbebranin-prog", "v2node"), ("thuhollow2", "vpngate"),
    ("Zangadze1101", "Convert"), ("adsikramlink", "proxy"), ("andreabranca", "Telegram-Downloader-Tools"),
    ("antivpn-7", "Vpn"), ("ayushgoyal-a11y", "proxy-server"), ("fastasfuck-net", "VPN-List"),
    ("goauthentik", "authentik"), ("mahazoualedji595", "secure_multisite_vpn"), ("mehdihoore", "TestVpnGateServers"),
    ("notfaj", "ester"), ("Alex123Aaaaaa", "windows"), ("Chondrinvolubility888", "Privacy-Relay-System"),
    ("MohammadBahemmat", "V2ray-Collector"), ("UVA-Course-Explorer", "course-data"), ("alireza-rezaee", "tor-nodes"),
    ("ilya-120", "vpn-tester"), ("kort0881", "telegram-proxy-collector"), ("mheidari98", ".proxy"),
    ("muazzamhussain0914", "Job_Portal_Website_-MERN-"), ("seyeddex", "proxy"), ("southpart302", "vless-wizard"),
    ("Eibwen", "podcast-proxy"), ("Fewgenusdendroaspis337", "v2rayN"), ("armanridho", "ProxyJson-toYaml"),
    ("aws", "mcp-proxy-for-aws"), ("cysurigao", "LRFtoMP4"), ("maurice2k", "ab-proxy"),
    ("mohammmdmdmkdmewof", "v2rayConfigsForYou"), ("shivangsharma270", "proxylysis"), ("thaikhan9717", "3x-ui"),
    ("venkatkrishna07", "caddy-mcp"), ("wr69", "auto-jichangqiandao"), ("SherlockChiang", "Maodie-Launcher"),
    ("TheSpeedX", "PROXY-List"), ("Tom-Riddle09", "proxy_server"), ("VampXDH", "MyProxy"),
    ("Vepashka94", "vpngate_web"), ("dr-andytseng", "afl-calendar-feeds"), ("xiaoji235", "airport-free"),
    ("Access-At", "proxy-scraping"), ("Anthon3284", "IKESS"), ("Fatherless-costusoil269", "ProxyMod"),
    ("Lutiancheng1", "lingma-ipc-proxy"), ("MhdiTaheri", "V2rayCollector"), ("TheAirBlow", "Turnable"),
    ("alihusains", "sstp-vpn"), ("datastax", "starlight-for-rabbitmq"), ("fmjnax", "dynamic-proxy"),
    ("g-hunter-g", "awesome-vpn"), ("huha-create", "TikTok-VPN-"), ("investidorbot-del", "dashbot-proxy"),
    ("jdxj", "sing-box-config"), ("parsamrrelax", "auto-warp-config"), ("realrolfje", "podfix"),
    ("shaoyouvip", "free"), ("Lonnory", "Exchenged-Client"), ("Mr-Meshky", "vify"),
    ("Phamtuandat", "responses-proxy"), ("RaineMtF", "v2rayse"), ("Surfboardv2ray", "TGParse"),
    ("akbarali123A", "proxy_scraper"), ("claudianus", "clco-proxy"), ("elijah-hall-asdq1", "Clash-Verge-Rev-History"),
    ("jasgues", "nodejs-proxy-server2"), ("wenxig", "free-nodes-sub"), ("Flexvent", "AioProx"),
    ("Garminado", "claude-affinity-proxy"), ("Hjsosn", "FireWall-Blocks"), ("MaskaBOG", "clash-vless-auto"),
    ("ZhurinDanil", "clash-sub"), ("kanokphol3013", "RSN"), ("keizno", "vod_stream_proxy"),
    ("sakata114", "work"), ("sandyemousy17", "wireguard-hook"), ("yiohoohoo2026", "format-proxy"),
    ("Denrox", "ui-apt-mirror"), ("JHC000abc", "ProxyParseForSing-box"), ("ThomaKust", "ai-proxy"),
    ("lingga1997", "full-stack-proxy-nginx-n8n-for-everyone-with-docker-compose"), ("maxstev72", "Zero-Trust-Auth-Service"), ("mhghco", "v2ray-hub"),
    ("onl35461-debug", "Accelerator-node-ladder---VPN"), ("oscarshrek9", "Cloud-Native-Load-Balancer"), ("szymonrychu", "oauth2-proxy-admission-controller"),
    ("zlylong", "proxygw"), ("Danialsamadi", "v2go"), ("Durgaa17", "cf-sg-proxies"),
    ("LalatinaHub", "Mineral"), ("PodoroznikVPN", "PodoroznikVPN_bot"), ("YimitKEQ", "TFTClash"),
    ("ferrofluidd", "Corporate-Clash-Cog-Viewer"), ("gaoyi1020-web", "proxy-bundle"), ("henrijaime", "Flutter-Awesome-Dialogs"),
    ("idkdevoo", "intercept-wave-upstream"), ("tranhoanganh2002", "aws-proxy-keys"), ("tudo123112312", "wireguard"),
    ("Argh94", "ProxyProwler"), ("Argh94", "telegram-proxy-scraper"), ("Cat-Ling", "sing-box"),
    ("DIGYXL", "venom"), ("Filterrr", "AdBlock_Rule_For_Clash"), ("Jer-y", "copilot-proxy"),
    ("Surfboardv2ray", "TGProto"), ("ThinkWatchProject", "ThinkWatch"), ("adesh777", "axios"),
    ("arunsakthivel96", "proxyBEE"), ("bach999-vamous", "Kimi-K2"), ("einyx", "tkr"),
    ("gtaiv005", "PublicProxyList"), ("gwindev", "vpn-client-api"), ("hiztin", "VLESS-PO-GRIBI"),
    ("jaatji261019-alt", "voxify-frontend"), ("jnjal", "v2ray"), ("josebormey", "render-eltoque-proxy"),
    ("massimoalbertoli-arch", "school-calendar-proxy"), ("nextrizon", "Vless-Hysteria-OpenWrt"), ("touhedulislam", "k8s-proxy"),
    ("veritynoob", "clash_ext"), ("Hash-Ag", "libsocks"), ("Mide-IT", "cdn-ip-ranges"),
    ("debian-professional", "debian-vpn-gateway"), ("disscript-id", "openai-proxy"), ("kiri11uk", "Clash-rule"),
    ("neshat73", "proxycache"), ("onl35461-debug", "Free-ladder---VPN"), ("pete731", "sati"),
    ("shaa2020", "V2Ray-Automator"), ("sinavm", "SVM"), ("trio666", "proxy-checker"),
    ("xteamlyer", "opera-proxy"), ("Arama120517", "scoop-proxy-cn"), ("CB-X2-Jun", "Free-v2ray-node"),
    ("ErTmannobom", "terraform-aws-vpc-peering"), ("FusionSync", "cli-agent-proxy"), ("OrbisProxy", "proxy"),
    ("RKPchannel", "RKP_bypass_configs"), ("ReliablyObserve", "Loki-VL-proxy"), ("Rusl2023", "vpn-alive-check"),
    ("WLget", "V2Ray_configs_64"), ("anutmagang", "Free-HighQuality-Proxy-Socks"), ("ar4kiara", "proxy"),
    ("arseniy700", "vpn-sub"), ("esmelimited23", "Cloud-Native-Load-Balancer"), ("nikita29a", "FreeProxyList"),
    ("rachelkuo8888-blip", "nova-api"), ("Chiuhum", "Clash"), ("Kotlas23412", "proxy-checker"),
    ("SHAHBBBB", "V2ray-collector"), ("T3stAcc", "V2Ray"), ("YangLang116", "auto_gen"),
    ("gongchandang49", "TelegramV2rayCollector"), ("igareck", "vpn-configs-for-russia"), ("jbaranski", "majorleaguesoccer-today"),
    ("mrkpjc", "castari-proxy"), ("nagelboi", "DDOS47"), ("nodesfree", "clashnode"),
    ("nodesfree", "v2raynode"), ("skalover32-a11y", "vlf-chrome-proxy"), ("yespresso80", "yespresso-proxy"),
    ("7c", "torfilter"), ("ALIILAPRO", "Proxy"), ("DukeMehdi", "FreeList-V2ray-Configs"),
    ("LoneKingCode", "panbox"), ("Lumimojjav", "Chibi-Clash-Crypto-Game-Token-Api"), ("Pawdroid", "Free-servers"),
    ("RealFascinated", "PIA-Servers"), ("ahmedzaik", "Pi-Hole-Setup"), ("ali13788731", "vpn"),
    ("amirkma", "proxykma"), ("idtheo", "V2Ray-CleanIPs-Servers"), ("junjun266", "FreeProxyGo"),
    ("maiyulao", "ResoHub"), ("milchee", "vless_subs"), ("openproxyhub", "proxy-exports"),
    ("roosterkid", "openproxylist"), ("toml66l", "fanqiang"), ("wubozh", "clash-sub-pages"),
    ("wxglenovo", "1AdGuardHome-Rules-AutoMerge-"), ("VP01596", "vless-top15"), ("feiniao1-VPN", "VPN-service"),
    ("proxifly", "free-proxy-list"), ("svpjohji", "NECHAEV_VPN_AGGREGATOR"), ("3nerg0n", "vless-parser"),
    ("AlterSolutions", "tornodes_lists"), ("Mr-Spect3r", "fad"), ("OpenNetCN", "clash"),
    ("SoliSpirit", "SolVPN"), ("V2RAYCONFIGSPOOL", "TELEGRAM_PROXY_SUB"), ("WOLFIEEEE", "scrape"),
    ("Zover1337", "vless-free-whtielist"), ("Casper-Tech-ke", "casper-free-proxies"), ("Firmfox", "Proxify"),
    ("Garmask", "SilverRAT-FULL-Source-Code"), ("ThandarLin2026", "v2ray-topup"), ("Xnuvers007", "free-proxy"),
    ("amnezia-vpn", "amnezia-client"), ("brother2050", "Proxyium"), ("mapleafgo", "clash-for-flutter"),
    ("mullvad", "mullvadvpn-app"), ("Sidoah2", "ProxyCar"), ("bin1site1", "V2rayFree"),
    ("cstreit03", "CoC-Stats"), ("denysg001", "zabbix-unified-installer"), ("liaohch3", "claude-tap"),
    ("miladtahanian", "V2RayScrapeByCountry"), ("therealaleph", "Iran-configs"), ("tobileng", "vless-ws-cdn-tunnel-setup"),
    ("Therealwh", "MTPproxyLIST"), ("ember-01", "Clash-Aggregator"), ("hamedp-71", "N_sub_cheker"),
    ("monosans", "proxy-list"), ("naseem499379", "mihomo_yamls"), ("sakha1370", "OpenRay"),
    ("takonorik", "flare-proxy"), ("tis24dev", "NordVPN-Easy-OpenWrt"), ("IsaacDSC", "proxy"),
    ("LustPriest", "proxy"), ("Skillter", "ProxyGather"), ("cimiacybersecurity", "danti"),
    ("Juno-Yi", "JunoYi"), ("Niekeisha", "business-gemini-pool"), ("wasimeahmed98-coder98", "clash-converter"),
    ("CJackHwang", "ds2api"), ("Jha0rahul", "Business-OpenAPI"), ("SoliSpirit", "v2ray-configs"),
    ("conoro", "reddit-rss-proxy"), ("4n0nymou3", "multi-proxy-config-fetcher"), ("BlackKillrt", "config_for_V2Ray"),
    ("FiligranHQ", "xtm-hub"), ("heimian0722-hash", "clashrule"), ("luigibarretta", "wallet-aggregator"),
    ("mzwaterski", "calendar-subscribe-feed"), ("nathanieljulien-a11y", "garden-calendar-proxy"), ("nobodysclown", "clash-rules"),
    ("nyeinkokoaung404", "multi-proxy-config-fetcher"), ("peptang12", "pingap-docker-provider"), ("proxygenerator1", "ProxyGenerator"),
    ("woshishiq1", "my-clash-sync"), ("xrkorz", "codex-proxyman-auto-replay"), ("child9527", "clash-latest"),
    ("feiniao25789", "vpn"), ("Au1rxx", "free-vpn-subscriptions"), ("ThaminduDisnaZ", "Esena-News-Github-Bot"),
    ("XigmaDev", "cf2tg"), ("chukwu-patrick", "five-worker"), ("docmirror", "dev-sidecar"),
    ("luizbizzio", "tailscale-mtu"), ("miladtahanian", "Config-Collector"), ("VPSLabCloud", "VPSLab-Free-Proxy-List"),
    ("Vanic24", "VPN"), ("bluenviron", "mediamtx"), ("qindinp", "keypool"),
    ("showmaker9", "clash-rule"), ("steam-100", "free-proxy-sub"), ("vtrixye", "vpn-shop"),
    ("Vann-Dev", "proxy-list"), ("chengaopan", "AutoMergePublicNodes"), ("feiniao1-VPN", "Node-based-VPN"),
    ("gitrecon1455", "fresh-proxy-list"), ("onl35461-debug", "Node-climbing-wall-ladder---VPN"), ("reminis0509-cyber", "llm-trace-lens"),
    ("sdfnh", "fanqiang"), ("Snishil", "Fisch-Script"), ("bg-grira53", "sql-server-security-audit"),
    ("crolankawasaki", "Goida26-Clash"), ("danmaifu", "mianfeijiedian"), ("hendrikbgr", "Free-Proxy-Repo"),
    ("infinitexlks", "linkhub"), ("likzid", "vless2"), ("netbirdio", "netbird"),
    ("Alvin9999-newpac", "fanqiang"), ("CodingButter", "snapcap-native"), ("PuddinCat", "BestClash"),
    ("REIJI007", "AdBlock_Rule_For_Clash"), ("RostislavKis", "4eburNet"), ("Veid09", "vless-list"),
    ("YawStar", "Proxy-Hunter"), ("ali13788731", "proxy"), ("hmcts", "crime-mcp-register"),
    ("runetfreedom", "russia-v2ray-rules-dat"), ("vmheaven", "VMHeaven.io-Free-Proxy-List"), ("Bails309", "strata-client"),
    ("MrAbolfazlNorouzi", "iran-configs"), ("TarekBN", "luci-app-ech-workers"), ("Zaeem20", "FREE_PROXIES_LIST"),
    ("airhorns", "shopify-draft-proxy"), ("ebrasha", "free-v2ray-public-list"), ("liangshengyong", "LanWan"),
    ("qopq1366", "VlessConfig"), ("Alisina7", "aleftaya-ios-proxy"), ("Hubaio", "Reverse-Proxy-Soruce-Code"),
    ("Mohammedcha", "ProxRipper"), ("OmniLLM", "omnillm"), ("PatNei", "esport-ics"),
    ("R0mb0", "LexiClash_Street_Edition"), ("matrixsy", "cf_ech_worker"), ("video05", "vpn-qr"),
    ("xuerake", "my-clash-sync"), ("ENAHSIN", "mqttstuff"), ("Frozoewn", "S500-RAT-HVNC-HAPP-HIdden-BROWSER-HRDP-REVERSE-PROXY-CRYPTO-MONITOR"),
    ("harismy", "BotVPN"), ("nyeinkokoaung404", "V2ray-Configs"), ("onl35461-debug", "Wall-climbing-ladder-VPN"),
    ("rtwo2", "FastNodes"), ("vovan046kursk-stack", "vless-list1"), ("zloi-user", "hideip.me"),
    ("Arefgh72", "v2ray-proxy-pars-tester"), ("Grifexdev", "CR-aiogram-bot"), ("Silvester13-SOS", "clash-war-analytics"),
    ("abrar699979", "Fortnite-Mobile-SSL-Bypass"), ("avion121", "V2RayDaily"), ("crackbest", "V2ray-Config"),
    ("feiniao1-VPN", "Airport-node-VPN"), ("maxvipon", "la-status"), ("neisii", "weather-proxy"),
    ("parserpp", "ip_ports"), ("Babaproates", "php-text-validator-lib"), ("NavyStack", "ipranges"),
    ("RasputinofThrace", "VerDix"), ("XigmaDev", "proxy"), ("bonymalomalo", "vless-auto-update"),
    ("caryyu0306", "proxy-list"), ("dadododojo", "clash-leaderboard"), ("divanniyanalityc-eng", "vpn101"),
    ("dorrin-sot", "V2RAY_CONFIGS_POOL-Processor"), ("hello-world-1989", "cn-news"), ("iplocate", "free-proxy-list"),
    ("onl35461-debug", "Node-Airport---VPN"), ("spider1605", "cf-workflow-rollback"), ("taurinexd", "shopify-ga4-app"),
    ("watchttvv", "free-proxy-list"), ("wisebobo", "clashNodes"), ("MRISOON", "instagram-comments-replies-and-subscribers-scraper-no-cookie"),
    ("WillyMS21", "Cloudflare-Bybass-CDP-Chromium"), ("elliottophellia", "proxylist"), ("nandapoxy", "proxy-server"),
    ("raphaelgoetter", "clash"), ("sigcli", "sigcli"), ("themiralay", "Proxy-List-World"),
    ("theriturajps", "proxy-list"), ("thorkx", "hockey-proxy"), ("Epodonios", "v2ray-configs"),
    ("RioMMO", "ProxyFree"), ("Wind7077", "yml-vless"), ("alexanderersej", "fanqiang"),
    ("linuxhobby", "autoinstallv2ray"), ("miladtahanian", "V2RayCFGDumper"), ("qq547820639", "tiktok-ad-video-skill"),
    ("A-K-6", "v2ray_scrapper_repo"), ("SHADOWWINGZ69", "ECH-CF"), ("Surfboardv2ray", "Proxy-sorter"),
    ("TheFlipper-spec", "VPNMY"), ("andigwandi", "free-proxy"), ("cheo87", "vless-all-in-one"),
    ("databay-labs", "free-proxy-list"), ("entur", "anshar"), ("kasesm", "Free-Config"),
    ("mauricegift", "free-proxies"), ("raffaeler", "mindthegap"), ("ArtemAfonasyev", "hentai-goida-subscription"),
    ("HankNovic", "ProxyClean"), ("Reid-Vin", "OpenClash_Custom_Rules_for_ios_rule_script"), ("SukrithTripathii", "ThreadPoolExecChain"),
    ("claude89757", "free_https_proxies"), ("dpangestuw", "Free-Proxy"), ("infzo", "TrajProxy"),
    ("kuciybes", "vpn-clash-rules"), ("michaelf-design", "sf-proxy"), ("partnermbp", "VLESS_RUS"),
    ("vomw", "AvenCores-goida-vpn-configs"), ("wildoaksapothecaryadmin", "squarespace-api-proxy"), ("wuqb2i4f", "xray-config-toolkit"),
    ("Anonym0usWork1221", "Free-Proxies"), ("PrabashSapkota", "proxyformywebsite"), ("RSSaltea", "DL-Clashfinder"),
    ("Siiingularity", "ClashOfMinds"), ("Swift-tunnel", "swifttunnel-app"), ("Wyr-Hub", "WyrVPN-Lite"),
    ("alphaa1111", "proxyscraper"), ("iboxz", "free-v2ray-collector"), ("jester4411", "amnezia-vpn"),
    ("navikt", "entra-proxy"), ("v2raynnodes", "v2rayfree"), ("vpn3288", "Chained-Proxy"),
    ("Andrejewild", "myvpn"), ("V2RAYCONFIGSPOOL", "V2RAY_SUB"), ("akshaymishra78600", "proxy-gem"),
    ("envoyproxy", "envoy"), ("expressalaki", "ExpressVPN"), ("gslege", "CloudflareIP"),
    ("pg-sharding", "spqr"), ("plsn1337", "white-vless"), ("pnv06", "betterclaude-workers"),
    ("purpletigerlzhlcgg", "ethereum-event-tracker"), ("qolbudr", "proxy-checker"), ("r00tee", "Proxy-List"),
    ("sozu-proxy", "sozu"), ("stormsia", "proxy-list"), ("youfoundamin", "V2rayCollector"),
    ("Khate-Tire", "CF-IP-Scanner"), ("adaskitkleilrociftey", "solidity-proxy-upgrade"), ("arasongiyvymjlndejkkhcbay", "evm-storage-layout-analyzer")
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

    # --- خواندن حالت اجرا فقط یک بار ---
    run_mode = os.getenv("RUN_MODE", "daily")

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

        # --- Stage 3: Process URLs ---
        logger.info("--- Stage 3: Processing URLs ---")
        urls_to_process = []
        for u in source_urls:
            if 'github.com' not in u and 'raw.githubusercontent.com' not in u:
                continue
            if run_mode in ("hourly", "frequent"):
                # در مد ساعتی و ۱۵دقیقه‌ای URLهای تکراری هم باید دوباره دانلود شوند
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
    unique_configs = sorted({c.strip() for c in all_configs if c.strip()})
    logger.info(f"✅ Total unique configs in DB: {len(unique_configs)}")

    if unique_configs:
        if run_mode == "hourly":
            daily_file = "daily_servers.txt"
            hourly_file = "hourly_servers.txt"

            daily_configs = set()
            if os.path.exists(daily_file):
                with open(daily_file, "r", encoding="utf-8") as f:
                    daily_configs = {line.strip() for line in f if line.strip()}
                logger.info(f"📄 Loaded {len(daily_configs)} configs from {daily_file}")
            else:
                logger.warning(f"⚠️ {daily_file} not found. All current configs will be treated as new.")

            new_configs = [c for c in unique_configs if c not in daily_configs]
            logger.info(f"🆕 New configs not in daily file: {len(new_configs)}")

            if new_configs:
                with open(hourly_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_configs))
                logger.info(f"💾 Saved {len(new_configs)} new configs to '{hourly_file}'")
            else:
                logger.info("👍 No new configs found. hourly_servers.txt will not be created/updated.")

        elif run_mode == "frequent":
            daily_file = "daily_servers.txt"
            hourly_file = "hourly_servers.txt"
            frequent_file = "frequent_servers.txt"

            daily_configs = set()
            if os.path.exists(daily_file):
                with open(daily_file, "r", encoding="utf-8") as f:
                    daily_configs = {line.strip() for line in f if line.strip()}
                logger.info(f"📄 Loaded {len(daily_configs)} configs from {daily_file}")

            hourly_configs = set()
            if os.path.exists(hourly_file):
                with open(hourly_file, "r", encoding="utf-8") as f:
                    hourly_configs = {line.strip() for line in f if line.strip()}
                logger.info(f"📄 Loaded {len(hourly_configs)} configs from {hourly_file}")

            base_configs = daily_configs | hourly_configs
            new_configs = [c for c in unique_configs if c not in base_configs]
            logger.info(f"🆕 Configs not in daily or hourly: {len(new_configs)}")

            if new_configs:
                with open(frequent_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_configs))
                logger.info(f"💾 Saved {len(new_configs)} configs to '{frequent_file}'")
            else:
                logger.info("No new configs for frequent.")

        else:
            # حالت روزانه: ذخیره‌ی کل خروجی در daily_servers.txt
            output_file = "daily_servers.txt"
            with open(output_file, "w", encoding="utf-8") as f:
                f.write("\n".join(unique_configs))
            logger.info(f"💾 Saved {len(unique_configs)} configs to '{output_file}'")
    else:
        logger.warning("⚠️ No configs found.")

    if CORE_LIMIT_REACHED:
        logger.warning("⛔ Script finished early because Core limit was reached.")
    else:
        logger.info("✅ Script completed normally without hitting Core limit.")

    logger.info(f"--- Finished in {int(time.time() - start_time)}s ---")
    logger.info(f"Estimated Core used: {TOTAL_CORE_USED}")
    os._exit(0)

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
