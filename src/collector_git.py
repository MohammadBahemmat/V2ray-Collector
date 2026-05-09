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
("LoneKingCode", "free-proxy-db"),
("skka3134", "Free-servers"),
("morooi", "homebrew-xray"),
("pleme-io", "aresta"),
("marcusc9", "Clara-sStories"),
("vb197701", "clash-rules-mrs"),
("simonwei999", "clash"),
("PhoenixxZ2023", "XRAY2026"),
("Lluciocc", "sspm-viewver"),
("Psikuvit", "CashClash"),
("gumieri", "nenya"),
("soga11", "clash-"),
("MahmoudEl-Gohary", "xray_report_gen"),
("xteamlyer", "opera-proxy"),
("mowei-ie", "router-vpn"),
("doitnow40", "sst"),
("villarrealed", "node-services-hub"),
("jpassick", "ig-follower-proxy"),
("ATropichev", "WinPublicIP-cpp"),
("floppy007", "floppyguard"),
("Chocolate4U", "Iran-v2ray-rules"),
("superchaospc", "xray-relay"),
("MaksimPchelka", "Flingway"),
("ameyukisora", "Clash-Rule"),
("ThomaKust", "ai-proxy"),
("Daysema", "xRay-visual"),
("Elias201478", "32Xstyizxernide.exe"),
("legiz-ru", "mihomo-rule-sets"),
("pf123120", "clash-rules-txt-to-mrs"),
("okning", "domain-list"),
("MFSGA", "Chimera"),
("nodesfree", "nodesfree.github.io"),
("mozilla-ai", "otari"),
("vadic1218", "VPN"),
("clash-verge-rev", "clash-verge-rev"),
("nikkinikki-org", "OpenWrt-nikki"),
("clashv2ray-hub", "clashv2ray-hub.github.io"),
("ripaojiedian", "freenode"),
("wellborgmann", "HoxManager"),
("Taekwonnie", "claude-task-router"),
("ermaozi", "ermao.net"),
("ermaozi", "get_subscribe"),
("pomerium", "torbulkexitlist"),
("othyn", "go-calendar"),
("ninggee", "clash_to_hosts"),
("nightcrawler42", "Xray-core"),
("clashv2ray-hub", "clashv2rayshare"),
("sselimabdelrhman-byte", "sselimabdelrhman-byte.github.io"),
("supabase", "supabase-js"),
("JacksonJiangxh", "Clash-Rule"),
("AnixOps", "AnixOps-xray-install"),
("Mundo-Connect", "FlClash-FOSS"),
("Woody4618", "feature-gate-tracker"),
("DomainWarrior", "Practice"),
("Thordata", "awesome-free-proxy-list"),
("mplaczek99", "xrayview"),
("Homas", "vpn007"),
("QuixoticHeart", "rule-set"),
("qist", "xray"),
("HenryChiao", "MIHOMO_YAMLS"),
("bskinn", "cpython-release-feed"),
("tglaoshiji", "aa"),
("YeonSeong-Lee", "sseuregi-king"),
("deverzh", "ai-api-proxy-list"),
("ganlinte", "VPN"),
("DavidFerreira21", "ssm-patch"),
("Latticect", "V2ray-Rules-Dat-SwitchyOmega"),
("unexpear", "chipblocks"),
("yuezk", "GlobalProtect-openconnect"),
("aws", "mcp-proxy-for-aws"),
("envoyproxy", "envoy"),
("youbin777", "clash"),
("kort0881", "sbornik-vless"),
("7-yearsold", "clash-rules"),
("dctxmei", "v2ray-china-list"),
("linzjian666", "chromego_extractor"),
("Daneslack455", "ESP8266-DHT22-SSD1306-OLED-Temperature-Humidity-Monitor-MicroPython-"),
("firezone", "firezone"),
("zz-want2sleep", "daily-gist"),
("Use4Free", "breakfree"),
("ChiaoYenta", "mihomo_yamls"),
("LitchiCherry", "Clash"),
("uykb", "clash-proxy-cleaner"),
("kklouzal", "Docker_Proxy"),
("mrdear", "learn_agent_with_proxy"),
("AgungHari", "aaagang"),
("Anivice", "ccdb"),
("simonzhang316", "clash-verge-ip-guard"),
("stevengiguere1993-coder", "h2.0"),
("ikaiguang", "go-kit"),
("xiaofeng0503", "lightning-proxy"),
("Freddd13", "cloudreve-anisub"),
("clashwindow", "clashwindow.github.io"),
("Latticect", "clash-rule-set"),
("supernovaria", "triq-calendar"),
("namtonthat", "apple-health-data"),
("ermaozi", "pyjichang.com"),
("woaim65", "proxy-pool"),
("shriman-dev", "dns-blocklist"),
("YUTING0907", "SubscribePapers"),
("superchaospc", "hysteria2-relay"),
("sixg0000d-copr", "v2ray-rules-dat"),
("IvanKorney", "code_clash"),
("Pritz96", "sosa-ssn-ontology-editors-edition-subclass-diagram"),
("raidal", "v2ray-rules"),
("heximao", "rule_provider"),
("rankalpha", "v2ray_sub"),
("EasyTier", "EasyTier"),
("10ium", "VpnClashFaCollector"),
("wutipongmoph16-stack", "ssj-duty"),
("Mihik04", "Dwellio"),
("Clashsoft", "Clashsoft"),
("Ruk1ng001", "freeSub"),
("Valiant-Cat", "LTX2-ICEdit-Insight"),
("rmorlok", "authproxy"),
("sparshTatiya", "ssl-scraper"),
("xwall60", "bajie"),
("SuperNG6", "clash-ruleset"),
("qRuWGQ", "rules"),
("Awenforever", "CoDeepSeedeX"),
("Vincentkeio", "probe-nodes-list"),
("baisysquant", "BAISYS_QUANT"),
("laosan-xx", "my-v2ray-geodata"),
("Ba3ilik", "rus-rules"),
("songxiaohuo", "clash-rules"),
("ByteMysticRogue", "Hiddify-Warp"),
("s-theo", "dotfiles"),
("Medium1992", "mihomo-proxy-ros"),
("iluobei", "miaomiaowu"),
("moaga0", "proxy"),
("philmillman", "M0SSFlash"),
("xOS", "Config"),
("xenmate", "mon-ss"),
("DailySleepy", "SSE-Cloud-Service"),
("TG-NAV", "clashnode"),
("awesome-vpn", "awesome-vpn"),
("batonogov", "terraform-provider-threexui"),
("mrdear", "my-clash-rules"),
("xituimao", "spider-clash"),
("217heidai", "adblockfilters"),
("passeway", "Snell"),
("sigcli", "sigcli"),
("tailscale", "tailscale"),
("xiaoyuandev", "clash-for-ai"),
("xrayian", "xrayian"),
("average-joe44", "Python-PoC-RAT"),
("menhera-org", "menhera-ssg"),
("papapapapdelesia", "Emilia"),
("LexterS999", "proxy-collector"),
("Aldemirps", "ArrSuite-Guide"),
("ghangelini", "xrays_evaluation"),
("Phogapro", "cloud-phone-config"),
("lovejg", "codeXray"),
("g-star1024", "my-clash-subscribe"),
("3yed-61", "Shadowsocks"),
("clashv2ray-hub", "v2rayfree"),
("jun763", "openClash"),
("PinguuSS", "PinguuSS"),
("SiddanthEmani", "kyros"),
("arfoux", "clash-rule-providers"),
("SprkFade", "sstv-iptv"),
("DDonlien", "clash-config"),
("pacnpal", "tunnelsmith"),
("yuanxiawan", "freevless"),
("SQMUSIC", "ss"),
("sub-store-org", "Sub-Store"),
("SSK015", "SSK015"),
("wd210010", "only_for_happly"),
("Scholarpei", "Clash-Ruleset"),
("diyros", "edgetunnel"),
("xawir", "warp"),
("Omid-0x0x0x", "vless"),
("bowoarunika", "OISD-for-Clash"),
("jdnei", "mojie"),
("noxi401", "vpn-server-provider"),
("kninetimmy", "Free-AI-SSD"),
("mabellemos", "banco-rabbitmq-subscriber"),
("Argh94", "ProxyProwler"),
("azatabd", "v2ray_fetch"),
("khathapyt-rgb", "ssb"),
("lchw1", "my-proxy-sub"),
("centergaspipe", "ulysses-for-macos-ss16"),
("hongCchao", "GlobalMedia-ClashRule"),
("keincarrillo", "SSE-Web"),
("JessyeKessia", "MessageHub"),
("JessyeKessia", "NotificationHub"),
("iseeyoou26-wq", "CryNet-SysTems-VPN-vless"),
("weivina", "flzt-auto-checkin"),
("HelenTim", "collectNodes"),
("TheCrowCreature", "v2rayExtractor"),
("gooseteam-hackers", "GooseVPN"),
("monkey6468", "69yun69"),
("461884421", "ssh_v9"),
("silvan2077", "SaaSShortLink"),
("AntiC1019", "metacubex_clash-shadowrocket"),
("kcgp007", "v2ray-rules-dat_direct-list_convert"),
("3yed-61", "V2rayCollector"),
("Jamin-sutton", "sse1"),
("chen08209", "FlClash"),
("sflaser", "sslaserservice"),
("aabdala31", "Abdala"),
("lestday-LAB", "Wikidot-CDN-Mirror"),
("mrnii", "ssInvestorpkg"),
("DragonSSS", "DragonSSS"),
("kort0881", "proxy-auto-checker"),
("ssrsub", "ssr"),
("vanashia", "SSR2Mihomo"),
("zccing", "china_route"),
("clashv2rayu", "clashv2rayu.github.io"),
("bostonidentity", "ssh-fleet-vscode"),
("filip2cz", "minecraft-ssfs-stats"),
("wubozh", "clash-sub-pages"),
("Amith7721", "Cognitive_Claw"),
("TeeSQL", "teesql-data-sidecar"),
("eapolinario", "ssh-microvm"),
("zcalifornia-ph", "sssp-modern"),
("elyobelyob", "bin-cal"),
("shabane", "kamaji"),
("wgetnz", "clash"),
("ChamikaSamaraweera", "laravel-3x-ui-manager"),
("philgaeng", "chatbot_ssh"),
("uesleibros", "wasabi"),
("3inker", "v2ray-subscription"),
("YashMayanil", "WanderLust-Airbnb-Clone"),
("jenkinsci", "docker-ssh-agent"),
("wildflare", "sshftp"),
("CG-spring", "airport-rec-bugog3"),
("clashhub-net", "airport-rec-x79132"),
("Kokko00", "Bio_SSG"),
("ssttest", "sstt-tienda"),
("nhatminh-sv", "PTHB260316_SS4_MD2_exc6"),
("AmirrezaFarnamTaheri", "ConfigStream"),
("atyonekilla", "torrent-block-rw"),
("Nemu-x", "privWL-clash"),
("SSUpick", "SSUPICK_BE"),
("free18", "v2ray"),
("arfahmahmud", "codex-context-editor-proxy"),
("abdallahhaytham", "AbdallahHaytham"),
("Roshan-Peter", "Job-Serach"),
("nhatminh-sv", "PTHB26310_SS2_MD2_exc5"),
("Bowen-Zheng-99", "joint-ssmt"),
("abusaeeidx", "TazaProxy-Troxy"),
("hnyongli-droid", "improved-octo-memory"),
("UIngarsoe", "SSISM_Intel_Sentinel"),
("nhatminh-sv", "PTHB26310_SS4_MD2_exc4"),
("Amirrezaheydari81", "free-v2ray-for-iran"),
("Mugassn-Victor", "proxy"),
("StartHex", "SSH-Agent-Hub"),
("ar4kiara", "proxy"),
("jundayou", "ssw-status"),
("kyson-dev", "proxy-builder"),
("mumuer1024", "clash-rules"),
("v2raynnodes", "clashfree"),
("zhuang-xd", "my-clash-node"),
("BigBadPapa", "sec-proxy"),
("HakurouKen", "free-node"),
("salient-sss", "salient-sss"),
("zaiyin", "metaclsh-scraper"),
("Mcloud136", "v2node"),
("S8Y", "mullvad-pac"),
("cmontage", "proxyrules-cm"),
("nhatminh-sv", "PTHB26310_SS4_MD2_exc3"),
("stdlib-js", "blas-ext-base-ndarray-ssumkbn2"),
("stdlib-js", "blas-ext-base-ndarray-ssumpw"),
("Chief-Engineer", "SS14-Uptime"),
("Ryucmd", "mihomo-rule"),
("TinkerHost", "upptime-free-hosting-central-servers"),
("dinger114", "proxy"),
("mobinsamadir", "ivpn-servers"),
("neverbiasu", "Awesome-ComfyUI-Video"),
("rokoman", "tor_node_list"),
("stdlib-js", "blas-ext-base-ndarray-ssumkbn"),
("AvaterClasher", "AvaterClasher"),
("CyTeknoloji", "VpnServer"),
("SnapdragonLee", "SystemProxy"),
("esmelimited23", "Cloud-Native-Load-Balancer"),
("nthack", "Shadowrocket-ADBlock-Rules-Easy"),
("xxx3-lab", "ahiteo-vpn"),
("inoribea", "patchomo"),
("Galmanus", "ssl-spec"),
("clashv2ray-hub", "clashfree"),
("cys92096", "python-xray-argo"),
("sinahosseini379", "Clash-config"),
("stdlib-js", "blas-ext-base-ndarray-ssum"),
("drsoft-oss", "proxymetrics"),
("idtheo", "V2Ray-CleanIPs-Servers"),
("ihyall", "sing-box-rules"),
("mahoskye", "vs-code-ssl-formatter"),
("stdlib-js", "blas-ext-base-ndarray-ssumors"),
("tannguyen28092007-ops", "SS8-DATA"),
("AndyYuenOk", "airport-summary"),
("DRIII33", "bumble-dates-ssot-portfolio"),
("NimbuSHh", "ClashRules"),
("austinjohnson03", "ss-db"),
("foliageSea", "ssh_tool"),
("hezhijie0327", "GFWList2PAC"),
("shirok1", "rules.nix"),
("dominicarrojado", "sg-alerts"),
("Llama1100", "Service-Mesh-Controller"),
("conanlu1104", "mihomo-geo-SubConverter"),
("nodesfree", "clashnode"),
("ssprasad-cyber", "ssprasad-cyber"),
("yokeay", "gidy-client"),
("Cremattsd", "rnlp-proxy"),
("Delight0628", "codex-opensource-provider"),
("plowsof", "check-monero-seed-nodes"),
("nodesfree", "v2raynode"),
("thorkx", "hockey-proxy"),
("JackSSads", "JackSSads"),
("UplandJacob", "Upland-HA-Addons"),
("lingyuanzhicheng", "railgun-ipsync"),
("mingcheng", "faure.sh"),
("Potterli20", "trojan-go-fork"),
("SHAHBBBB", "V2ray-collector"),
("YangLang116", "auto_gen"),
("vAHiD55555", "vLess"),
("CharlesPikachu", "freeproxy"),
("clashnodev2ray", "clashnodev2ray.github.io"),
("codeking-ai", "cligate"),
("in-ci", "clash_rules_merged"),
("ningjx", "Clash-Rules"),
("vluma", "free-vpn2clash"),
("xiongjiwei", "mcp-ssh"),
("SierraPacificGroup", "SSUI-Framework"),
("epa127", "ssh-epark73-akdeng"),
("ma5bah", "ssh_mcp"),
("shivanshsinghsengar", "BizScope-ai"),
("2949282402", "ssh_mobile"),
("ABDALRZAQ345", "ABDALRZAQ345"),
("DukeMehdi", "FreeList-V2ray-Configs"),
("Tyguy9", "VPN-Filter"),
("mahdisandughdaran-sys", "vless-reality-collector"),
("mr-ssc", "mr-ssc"),
("afr0700", "ProxyList"),
("chatgpt-helper-tech", "airport-access"),
("ssarammoller", "ssara"),
("mbaily", "lists_and_prices"),
("123jjck", "cdn-ip-ranges"),
("FGWong", "clash_config"),
("Katrinaannija", "ss.lv"),
("RenanPhilip", "EstatisticasRouboFurto_SSP"),
("Vepashka94", "vpngate-mirror"),
("jcabi", "jcabi-ssh"),
("3yed-61", "MTP-Collector"),
("Airuop", "cross"),
("Yorlg", "WebSSH"),
("feng-yifan", "token-proxy"),
("lhbbingzi", "clash-rules"),
("Vann-Dev", "proxy-list"),
("YavieAzka", "clash-tabola-bale"),
("sseydaltin", "sseydaltin"),
("stdlib-js", "blas-base-ndarray-sswap"),
("tosayn386-dotcom", "ai-news-proxy"),
("vrnobody", "V2RayGCon"),
("zoreu", "proxyssl"),
("kongkong7777", "github-enterprise-ai-proxy"),
("Leonardo2757", "Elemental-Clash"),
("ParrotXray", "ParrotXray"),
("RandomlyZay", "SSS-Wiki-Scraper"),
("liMilCo", "v2r"),
("Roywaller", "update-clash"),
("awwy1222", "clash-sub"),
("clash-s", "clash-s.github.io"),
("Her0x27", "v2ray.geodats"),
("linlyzly", "yuanfen-ai-calculator"),
("sserada", "sserada"),
("Maximusssr8", "ManusMajorka"),
("berquist", "sst-build-conf"),
("jdnei", "mitce"),
("ma3uk", "russia-clash-rules"),
("2dust", "v2rayNG"),
("jdnei", "peiqianjichang"),
("thuymieu44-alt", "luyen-tap-ss3"),
("3nerg0n", "vless-parser"),
("ThinkWatchProject", "ThinkWatch"),
("YoujunZhao", "SSH-FS-Codex"),
("aisystant", "ssm2025"),
("arandomguyhere", "Proxy-Hound"),
("iasds", "qubes-clash-gateway"),
("jdnei", "naiyun"),
("Libraryworm", "clash-"),
("jdnei", "bygcloud"),
("BlacKSnowDot0", "Proxy-Pulse"),
("jdnei", "ctc"),
("jdnei", "flyingbird"),
("keerthimamidipaka", "college-discovery"),
("nomyself1990", "clash-rules"),
("FanchangWang", "clash_config"),
("Searching96", "ssrf-demo"),
("apt-gh", "pantheon"),
("jdnei", "FlowerCloud"),
("jdnei", "WgetCloud"),
("jdnei", "liangxin"),
("luongkun", "McSsCheck-"),
("Hatedatastructures", "Prism"),
("Stepan2222000", "clash-rulesets"),
("ts-sf", "fly"),
("DwaftPainter", "ss2-accommodation-finder-api"),
("jdnei", "JiChangTuiJian"),
("K-nobata", "ss2"),
("asaf1n", "EGISZ-Proxy-Reports-Airflow"),
("jasonliu2333", "grok-subscribe-blacklist"),
("jdnei", "naixi"),
("jdnei", "yifen"),
("Snuffy2", "sshwifty"),
("arshiacomplus", "v2rayExtractor"),
("jlintvet", "SSTv2"),
("PedroLucas-ss", "PedroLucas-ss"),
("Wwuyi123", "CF-Proxyip"),
("v2rayA", "v2raya-scoop"),
("crossxx-labs", "free-proxy"),
("serebrena", "vless"),
("Brosiie", "marduk"),
("VetriTheRetri", "ssb-decomp-re"),
("YFTree", "ClashNodes"),
("jingjiangy", "SsPlatform"),
("v2raynnodes", "v2raynnodes.github.io"),
("CCJ623", "clash-rules"),
("mzyui", "proxy-list"),
("taikwong", "clash"),
("lonecale", "Rules"),
("lwmacct", "260509-ssh-agent"),
("mini-insurance", "ssi-db"),
("spkprsnts", "vless-client"),
("nirala01", "TrickySSC"),
("yegetables", "clash-and-dns-config"),
("shaoyouvip", "free"),
("shichongzheng", "v2rayfree"),
("sodardyjiber", "DailyProxyCheck"),
("opti4riponty-arch", "VLESS-Co"),
("yjdwbj", "build-firmware-by-action"),
("HuangYurong123", "p-configs"),
("Ultimate-Hosts-Blacklist", "SSH_attackers_probers"),
("afutemp", "vscode-ssh"),
("sbaker333", "netskope-sse-troubleshooting"),
("sshcrack", "sshcrack"),
("omidiyanto", "crustoxy"),
("VovaplusEXP", "p-configs"),
("godaddy", "homebrew-sshenc"),
("godaddy", "scoop-sshenc"),
("mullvad", "mullvadvpn-app"),
("shekelstrong", "nemo-blog"),
("mc256", "honkai-rule-server"),
("souzaalfa", "Souza-ss"),
("LittleRey", "clash-yaml"),
("BranislavMateas", "measurecamp-calendar-scraper"),
("Dragonsky9999", "Rubik-sSim"),
("ipexnet", "ipexiq-learn-ssr"),
("joinvolunteerpeace", "anime-card-clash-ze89"),
("vless-reality", "vless-reality.github.io"),
("HansZ8", "SSH-PortForward"),
("Jsnzkpg", "Jsnzkpg"),
("BLUE0818", "gpt-image-2-SSE"),
("HaiDuong2035", "MM_SS13_CSLD"),
("Magnoliar", "SSUBB"),
("lmfying", "cf-vless"),
("HaiDuong2035", "vdcb1_SS13_CSDL"),
("wpyok168", "c2m"),
("HaiDuong2035", "vdcb2_SS13_CSDL"),
("leesuncom", "clash-mosdns"),
("meehua", "1panel-ssl-uploader"),
("xxAlizzamxx", "FincaOS_Trojan_Horse"),
("HaiDuong2035", "sangTao_SS13_CSDL"),
("HaiDuong2035", "vdnc_SS13_CSDL"),
("NZNL31", "Shadowrocket-Ad-DNS-Leak-Rules"),
("joinvolunteerpeace", "anime-card-clash-lm82"),
("mahdibland", "ShadowsocksAggregator"),
("mahdibland", "V2RayAggregator"),
("somiibo", "youtube-bot"),
("zhusaidong", "clashgithub"),
("2OTT", "Free-Nodes"),
("HaiDuong2035", "BTTH_SS13_CSDL"),
("KingCrab1990", "clashrule"),
("SSHOC", "sshompitor"),
("chuluosen", "crdeckbuilder"),
("miracle-desk", "clash_rule-provider"),
("kzb12580", "Prism"),
("nymtech", "nym-vpn-client"),
("s-theo", "Theo-Docs"),
("sscs-ose", "sscs-chipathon-2026"),
("dinoz0rg", "proxy-list"),
("wuyaos", "OpenClash-Rules"),
("ichiro-ss", "ichiro-ss"),
("joinvolunteerpeace", "anime-card-clash-xb36"),
("timesky", "clash-swatcher"),
("wbenit", "CF-vless"),
("yabalababoom", "ygkkk_vless_auto"),
("Mari-222", "Clash-Royale"),
("CipherSlinger", "sslspeedyup"),
("SunsetMkt", "anti-ip-attribution"),
("lureiny", "v2raymg-ip-node"),
("twj0", "subseek"),
("wekingchen", "Generate-and-Backup-SSL-Certificates"),
("RobertoCampero", "SSFrontend"),
("sarvanpat", "SSIPTV"),
("vitalybulganin", "serialize-list-nodes"),
("sshunuo", "sshunuo.github.io"),
("AngelSSJR", "AngelSSJR"),
("Passimx", "vpn-payments"),
("wuqb2i4f", "xray-config-toolkit"),
("madeye", "BaoLianDeng"),
("testemetodos", "J-ssyca---Hayanny---expert"),
("thirtysixpw", "v2ray-reaper"),
("xibanyahu", "phppachong-freenode"),
("minipie217", "sspxcdo"),
("spacehamagent", "ssvpthetford2026"),
("ssvlabs", "ssv"),
("Achuma88", "Primary-School"),
("Sakuta-io", "Vless"),
("billerbeck-lab", "ssign"),
("zhou-jian-qq", "Clash-Hub"),
("Moocow9m", "tor_entrypoint_list"),
("NoTalkTech", "xrayctl"),
("i1986o", "mtg-cal"),
("111pointer111", "moyu_sign"),
("hjtr7mymht-dot", "WOA_AutoBot"),
("jzrqs", "node-subscribe"),
("koagaroon", "ssaHdrify-tauri"),
("007dimkos", "dimmy-energized-adblock"),
("1ssb", "1ssb.github.io"),
("shanta4100", "ssgpt6.com"),
("sszgr", "sszgr"),
("venturecrane", "ss-console"),
("Byteflux", "magos"),
("ssvlabs", "ssv-subgraph"),
("ljhq553", "OpenClash-Setup"),
("munechi", "ssh_connect_github_actions_to_aws"),
("Maximilian741", "OFR2SSRS"),
("yass033", "CLASH-ROYALE"),
("dueckminor", "go-sshtunnel"),
("khelias", "khe-ai-adventure"),
("kristof-mattei", "endless-ssh-rs"),
("syamsul18782", "xray2026"),
("Maklith", "Kitopia"),
("Acs2World", "Clash_Rules"),
("pjrpjr9003-svg", "SS"),
("Alan222G", "jjk-cursed-clash"),
("Chunlion", "VPS-Optimize"),
("kristof-mattei", "endless-ssh-rs-with-web"),
("dairon2", "SG-SST-Colombia"),
("qitry", "Qimi-API"),
("russ1217", "ssh-audio-player"),
("Verilean", "sparkle"),
("jubishop", "podhaven"),
("oaslananka-lab", "mcp-ssh-tool"),
("pankajpatel", "list-repos"),
("Makale25", "cloudflare-dns-worker"),
("Pasimand", "v2ray-config-agg"),
("jeliasrm", "req-replace"),
("DoomTiger", "MikuBoxForAndroid"),
("MuhammadUnaiz", "export-followers-instagram"),
("Suraj24w", "backlink-analyzer"),
("apippp11", "automatic-backlink-indexer"),
("bated-genuscricetus536", "webhook-proxy"),
("bombasisi4-debug", "my-vless-"),
("mohamedbelasy", "LfsProxy"),
("ssp-remscheid", "ssp-rs-content"),
("dperalta86", "ssl-agenda-clases"),
("linuxhobby", "autoinstallv2ray"),
("linuxhobby", "xray-v2ray-install"),
("nma12323", "snip"),
("ArthurZhou", "zline_sso"),
("KitanoSakurana", "BakaClashRules"),
("Levisubartesian416", "chines"),
("LiMingda-101212", "Proxy-Pool-Actions"),
("M-Matias-C", "SSM"),
("Sihabho2566", "SeansLifeArchive_Images_Clash-of-Clans_Y2026"),
("jacobax", "snippets"),
("oaslananka", "mcp-ssh-tool"),
("topvpnnode", "topvpnnode.github.io"),
("zeusxprime", "ssh"),
("Alex123Aaaaaa", "windows"),
("ItalyPaleAle", "traefik-forward-auth"),
("Likely-kinsman623", "Bitscoper_SSTV_Icecast_Broadcaster"),
("Zangadze1101", "Convert"),
("free-vmess", "free-vmess.github.io"),
("mahazoualedji595", "secure_multisite_vpn"),
("Chondrinvolubility888", "Privacy-Relay-System"),
("freeqv2ray", "freeqv2ray.github.io"),
("southpart302", "vless-wizard"),
("Dichgrem", "subhatch"),
("Fewgenusdendroaspis337", "v2rayN"),
("Loaila1680", "parse-sse"),
("clashsky", "clashsky.github.io"),
("thaikhan9717", "3x-ui"),
("Thunderous-cauliflower413", "DeSSyPHER"),
("fmjnax", "dynamic-proxy"),
("Anthon3284", "IKESS"),
("Fatherless-costusoil269", "ProxyMod"),
("clashzhuanxian", "clashzhuanxian.github.io"),
("vpnjihe", "vpnjihe.github.io"),
("Flexvent", "AioProx"),
("Hjsosn", "FireWall-Blocks"),
("TuanMinPay", "live-proxy"),
("johncenadududu", "pytorch-simsiam-contrastive-ssl"),
("kanokphol3013", "RSN"),
("sakata114", "work"),
("sandyemousy17", "wireguard-hook"),
("shekelstrong", "vpn_bot"),
("bien000", "the-watcher-ssr"),
("SAQLAINComsats", "the-watcher-ssr"),
("henrijaime", "Flutter-Awesome-Dialogs"),
("idkdevoo", "intercept-wave-upstream"),
("lingga1997", "full-stack-proxy-nginx-n8n-for-everyone-with-docker-compose"),
("macssr", "macssr.github.io"),
("pjrpjr9003-svg", "SSS"),
("ssalinassilvio", "ssalinassilvio"),
("DIGYXL", "venom"),
("RicardoSouzaCruz", "fusion-ssh"),
("adesh777", "axios"),
("aljihadhasan220", "ssstiktok"),
("bach999-vamous", "Kimi-K2"),
("folksreptilian850", "SSM-PC"),
("gtaiv005", "PublicProxyList"),
("touhedulislam", "k8s-proxy"),
("tudo123112312", "wireguard"),
("vpnmama", "vpnmama.github.io"),
("vpnzhuanxian", "vpnzhuanxian.github.io"),
("Dawang8-ai", "ssq-smart-pick"),
("Hash-Ag", "libsocks"),
("Mide-IT", "cdn-ip-ranges"),
("Parth3199", "10ssoonBase"),
("diflow95400", "x-evolution"),
("neshat73", "proxycache"),
("ErTmannobom", "terraform-aws-vpc-peering"),
("Neamul09", "sstu-bot"),
("Roberto7771", "sso-ui-cdn"),
("SPARTAN2006", "is-in-ssh"),
("bobzhengzihao-droid", "ss--"),
("pete731", "sati"),
("pkssssss", "alpine-vless"),
("v2rayumac", "v2rayumac.github.io"),
("Mahdi951-pro", "ssc2k26"),
("Nancykharbanda", "ssh-tutorial-fr"),
("ahmedzaik", "Pi-Hole-Setup"),
("mrkpjc", "castari-proxy"),
("nagelboi", "DDOS47"),
("apindipsi22", "Securing-SSH-Access-on-Proxmox-VE-9"),
("clashdoor", "clashdoor.github.io"),
("daniel-trachtenberg", "trojan-traffic"),
("gsyunip", "ispip"),
("timmyzai", "arrowfish-wiki"),
("trtyr", "AgentSSH"),
("vpnsouthafrica", "vpnsouthafrica.github.io"),
("Delta-Kronecker", "ProtonVPN-WireGuard-configuration"),
("anooshali201", "CryptoLens"),
("feixingzhou", "clash-subscription"),
("free-clashx", "free-clashx.github.io"),
("mGentel1309", "Vpn"),
("soumyaranjanmahunta1", "ssc-gd"),
("TIGERs-Mannheim", "ssl-game-controller-maven"),
("guanzhi", "GmSSL"),
("JesterW365", "Clash_Rulesets_Template"),
("S1ssiXD", "S1ssiXD.github.io"),
("clashmianfei", "clashmianfei.github.io"),
("julxxy", "smart-proxy-rules"),
("netio896", "v2raysub"),
("tobileng", "vless-ws-cdn-tunnel-setup"),
("hvwin8", "autojiedian"),
("kubuszok", "ssg"),
("lottev1991", "DroidKiSS"),
("naseem499379", "mihomo_yamls"),
("olajos299-sys", "sss"),
("saqi9912", "homelab-vpn-journey"),
("zlylong", "proxygw"),
("Harinavalona-web", "XWan"),
("aa-proxy", "aa-proxy-rs"),
("adan202", "Abelssoft-SSD-Fresh-Latest-Patch"),
("ahmedmagdy0000", "NORD"),
("freeclash-node", "freeclash-node.github.io"),
("hwdsl2", "docker-wireguard"),
("rominznew", "sscom-telegram-bot"),
("swargaseemasalesteam-ux", "swargaseema-sss-cab-booking-portal"),
("AJlv420", "VPN-BlackBox-Checker"),
("Alvin9999-newpac", "Sing-Box-Plus"),
("DeepakMudili", "cf-ssl-check"),
("Niekeisha", "business-gemini-pool"),
("Preethamvarma007", "privacy-first-network"),
("Ps-Student-Catalog-Team", "NetworkRepairs"),
("Raffyn2", "python-api-base"),
("csd-lab-163", "Clash-verge-deb-for-ubuntu"),
("evgenyzh", "iinv-xray-releases"),
("hwdsl2", "docker-openvpn"),
("pingbiqi", "shoujixinhaopingbiqi"),
("veelenga", "aws-sso-mcp"),
("wasimeahmed98-coder98", "clash-converter"),
("Jha0rahul", "Business-OpenAPI"),
("Wjl1224734792", "visual-primitives-mcp"),
("clash-v2ray", "clash-v2ray.github.io"),
("jiedianjichang", "jiedianjichang.github.io"),
("omar-campos", "ShumeloSSH"),
("peptang12", "pingap-docker-provider"),
("pingbiqi", "GPS-shield-jammer-cellphone-signal-blocker"),
("sherwrj", "ssbvcfgas"),
("free-ssr-clash", "free-ssr-clash.github.io"),
("whaiyang", "vless-onekey"),
("zobay", "Laravel-SslCommerz"),
("chukwu-patrick", "five-worker"),
("dryqhxa", "split-tunneling-vpn"),
("josonzhou-maker", "hiddify-app"),
("v2raynwindows", "v2raynwindows.github.io"),
("zeyadjabo", "clash-of-captains"),
("Re0XIAOPA", "ToolStore"),
("cnfreevpn", "cnfreevpn.github.io"),
("hwdsl2", "docker-headscale"),
("hwdsl2", "docker-ipsec-vpn-server"),
("ighce56", "nordvpn-security-analysis"),
("jetwalk", "japan-sub"),
("linhang945", "Clash-Rule-Converter"),
("zhf883680", "clash-subscription-manager"),
("Menaka-J", "Xray_Classification_ViT"),
("braenmendes", "ssf"),
("jeric765", "wireguard"),
("pingbiqi", "Mobile-Phone-Signal-Jammer-5G-LTE-Shielding-System-Pro"),
("tuijianjiedian", "tuijianjiedian.github.io"),
("EkkoG", "clash-meta-alpha-for-openclash"),
("QuiteAFancyEmerald", "InvisiProxy"),
("Sabariranil", "nashvpn"),
("Snishil", "Fisch-Script"),
("bg-grira53", "sql-server-security-audit"),
("electron-v2ray", "Telegram-Config-Dumpr"),
("vpn-online", "vpn-online.github.io"),
("XXX5X", "iptables"),
("emmanuel-tientcheu", "esports-clash"),
("fwge291", "nordvpn-split-tunneling"),
("topproxy", "topproxy.github.io"),
("Fishin09", "GodzillaNodeJsPayload"),
("Max-42", "garage-ssh"),
("TarekBN", "luci-app-ech-workers"),
("alimalik122", "chest-xray-covid19-classification"),
("fanqiang8", "fanqiang8.github.io"),
("hpv35370", "prime-video-vpn-unblock"),
("matrixsy", "cf_ech_worker"),
("newbie-learn-coding", "free-proxy-list"),
("pogiako123pak", "go-ssh"),
("webunblocker", "free-proxy-list"),
("Faateemaa", "SnippetForge"),
("RasputinofThrace", "VerDix"),
("RedHatInsights", "uhc-auth-proxy"),
("Rislinstiligo23", "sss"),
("StarBobis", "SSMT4-Documents"),
("Yularzhi", "geosite_russia"),
("denniszlei", "smartdns-domain-lists"),
("gloriadeng", "clash-"),
("ikyx414", "nordvpn-china-firewall"),
("mtp370", "coffee-shop-vpn-security"),
("xrkorz", "clash-verge-rules-sync-template"),
("4evergr8", "mihomoR"),
("ENAHSIN", "mqttstuff"),
("Filterrr", "AdBlock_Rule_For_Clash"),
("Grifexdev", "CR-aiogram-bot"),
("NicoMancinelli", "pi-travel-router"),
("fanqiangba", "fanqiangba.github.io"),
("mano4now", "plant-protect"),
("mskwlc6", "nordvpn-linux-setup"),
("vkpandey82", "mfpublicinfo"),
("AYMANE-GYM", "mise-setup-verification-action"),
("Azarscientist", "ssi-protocol-oss"),
("Babaproates", "php-text-validator-lib"),
("SheddingNeurology", "ACL4SSR"),
("abrar699979", "Fortnite-Mobile-SSL-Bypass"),
("vpnlaoshi", "vpnlaoshi.github.io"),
("2026ssm", "SSM-App"),
("MRISOON", "instagram-comments-replies-and-subscribers-scraper-no-cookie"),
("Shxd0w", "SSDLC_test"),
("WillyMS21", "Cloudflare-Bybass-CDP-Chromium"),
("ahfni7", "nordvpn-gaming-ping"),
("clash-v2ray-free", "clash-v2ray-free.github.io"),
("spider1605", "cf-workflow-rollback"),
("Ahmdrady", "CloudLab"),
("ahlembnhsn", "An0m0s-VPN"),
("alexanderersej", "fanqiang"),
("vpn-client", "vpn-client.github.io"),
("Crown-Commercial-Service", "conclave-ssso-ui"),
("SHADOWWINGZ69", "ECH-CF"),
("SukrithTripathii", "ThreadPoolExecChain"),
("cheo87", "vless-all-in-one"),
("eliashaeussler", "sse"),
("pcfreevpn", "pcfreevpn.github.io"),
("rancher", "remotedialer-proxy"),
("clashxpro", "clashxpro.github.io"),
("cxddgtb", "2026Clash"),
("maiclash", "maiclash.github.io"),
("petrpstepanov-svg", "kp-ssd"),
("pr-poehali-dev", "telegram-vpn-bot-1"),
("DafaSya", "ios-developer-agents"),
("camer1111", "ss.com-vacancy-search-python"),
("gdfsnhsw", "AutoClash"),
("opermancode", "nemochat-SS"),
("pnv06", "betterclaude-workers"),
("zhiwoxing", "auto-ss-sub"),
("ShubhashSharma", "ssl-2026-shubhash"),
("amirebni", "con"),
("moinugare19", "ssh-client-mcp"),
("sushazhi", "clash"),
("vpnfenxiang", "vpnfenxiang.github.io"),
("wowhulson", "jichangtuijian"),
("Abdelmalik9", "microservices-lab"),
("ZHDeveloper", "clash-nodes"),
("fortniteseason6", "LoonLab"),
("marvinli001", "ClashMax"),
("monosans", "proxy-scraper-checker"),
("palamist", "win-mediakey-lolbin"),
("MunMunMiao", "headscale-ui"),
("Paxxs", "clash-skk"),
("clashdaily", "clashdaily.github.io"),
("colhoes1337", "local-ssl-automate"),
("ferrarigamer458italia", "metube"),
("gkc1186", "bbc-iplayer-vpn"),
("kort0881", "vpn-aggregator"),
("kylepeart21", "get-icmp9-node"),
("BH116", "ConfigGuard"),
("GCS-SSC", "gcs-ssc"),
("GCS-SSC", "gcs-ssc-extensions"),
("MeAkash77", "CertMate-Certificate-Lifecycle-Management-SSL-TLS-Automation-Platform"),
("Michigan5", "oports"),
("Nopekszz", "mssh"),
("SaharSaam", "juziyun"),
("aawf86", "vpn-selection-guide"),
("awnua15", "nordvpn-netflix-spain"),
("clashxnode", "clashxnode.github.io"),
("haha123BC52", "SOCKS5-Proxies"),
("mayank164", "loveFreeTools"),
("pero082", "wg-orchestrator"),
("7abian", "ss"),
("LukePham163", "docker-compose-servarr-with-gluetun"),
("abdul841434", "telegram-gpt-template"),
("skycoin", "skywire"),
("Munna89", "homelab-horizon"),
("anthonysgro", "geospoof"),
("jessi-2023", "homebrew-tap"),
("kriya-8620", "ssl-certificate-dashboard"),
("pagpva50", "vpn-comparison-nordvpn-surfshark-protonvpn"),
("ssr-clash-v2ray", "ssr-clash-v2ray.github.io"),
("arshveer1208", "ssh-brute-force-splunk"),
("dailivpn", "dailivpn.github.io"),
("dhayanand-ss", "dhayanand-ss"),
("dsccccc", "clashfree"),
("hwdsl2", "docker-litellm"),
("kittykittenkittykat", "SSH"),
("manavkushwaha10", "apple-health"),
("theMavionx", "Clash"),
("Lokmandev", "codenex-ai-api-proxy"),
("abxian", "proxy"),
("ada20204", "clash-override-chain-proxy"),
("bucissss", "Xray-VPN-OneClick"),
("jkCXf9X4", "ssp4sim"),
("python-net-dev", "network-test"),
("vpnformac", "vpnformac.github.io"),
("yovfnu5", "public-wifi-vpn-security"),
("Kineki07", "tuicr"),
("VersaVin", "CF-Workers-UsagePanel"),
("clashfenxiang", "clashfenxiang.github.io"),
("cygdeo13", "windows-vpn-comparison"),
("ghanchisamajahmedabad-hash", "ssgmss-web-panel"),
("realbabafingo", "gatepath-threat-model"),
("rogerioritto", "clashroyale"),
("AdnannIrfan", "Chatting-App-Created-Using-Python-With-Flask-and-SSMS-Backend"),
("Jaymarenad", "aws-api-gateway-tools"),
("Mohamedafifi14", "canban_board"),
("Rm6B", "Best_free_news_api"),
("SSParzival", "SSParzival"),
("macosta88", "Splunk-Dashboard-for-SSH-Logs"),
("nptdzp932", "vpn-multi-device-comparison"),
("reminis0509-cyber", "llm-trace-lens"),
("whatisclash", "whatisclash.github.io"),
("zaishe-crypto", "Best-Tiktok-human-bot"),
("Kd-devv", "P-BOX"),
("ProxyScraper", "ProxyScraper"),
("Shadow-alpha", "Midterm_IC_OD_SS"),
("aaginxm", "router-vpn-nordlynx"),
("bsw1206", "ssafypjt"),
("database64128", "shadowsocks-go"),
("hacker7221", "ai-debates"),
("hiztin", "VLESS-PO-GRIBI"),
("kkoltongi99", "speedc"),
("oscarshrek9", "Cloud-Native-Load-Balancer"),
("v2ray-free", "v2ray-free.github.io"),
("webmastergom", "gmc-veraset-api"),
("yzuq44", "nordvpn-security-analysis"),
("Cat-Ling", "sing-box"),
("DSpace24", "stash"),
("Lore-Hex", "quill-router"),
("Surfboardv2ray", "TGProto"),
("Tusked", "IPcheck-workers"),
("free-v2ray-clash", "free-v2ray-clash.github.io"),
("lovedxc", "smartdns-rules-dat"),
("nikita29a", "FreeProxyList"),
("qbasyv", "vpn-speed-benchmark"),
("samnismolvel", "SS"),
("sleepinginsummer", "agent-ssh-cli"),
("AndrewImm-OP", "vpn-configs"),
("Argh94", "telegram-proxy-scraper"),
("clashvergegithub", "clashvergegithub.github.io"),
("genznet", "Genznet-VPN"),
("gifenero", "nordvpn-router-setup"),
("ircfspace", "XrayRefiner"),
("mourya11", "honghongcf-workers-vlesspanel-d1"),
("nehrabalar", "white_list_internet"),
("supravault", "SSA"),
("v2raynnodes", "v2rayclash"),
("weiguangchao", "Clash"),
("yosh95", "ssm-latent-rs"),
("BlazeAuraX", "ProxyForFree"),
("FractalizeR", "shadowrocket-configs"),
("T3stAcc", "V2Ray"),
("mixm228", "ip-address-vpn-nordvpn"),
("roriruri9370", "Whitelist-bypass"),
("v2raymianfei", "v2raymianfei.github.io"),
("Eloco", "free-proxy-raw"),
("MhdiTaheri", "V2rayCollector_Py"),
("ali-atghaei", "geo_ssdg"),
("birdwarp", "Iran-Anti-Filter-SingBox-2026"),
("bucanero2010", "letterboxd-justwatch-vpn"),
("gongchandang49", "TelegramV2rayCollector"),
("kirsre467", "vpn-comparison-nordvpn-protonvpn"),
("shinexus", "LearnToProgram"),
("whatisv2ray", "whatisv2ray.github.io"),
("DoraOtari", "slipstream"),
("ErrOzz", "clash-proxy-rules-gen"),
("FLAVIO3333", "ProxyForFree"),
("Freedom-Guard-Builder", "Freedom-Finder"),
("RDEENA", "ssb-psych-portal"),
("Rohit-Virkar", "DDoSSCAN"),
("WolfSahil", "Win32kHooker"),
("luckrats", "koolshare_ss_rule"),
("vpnfornetflix", "vpnfornetflix.github.io"),
("Larmstrong1127", "Doubly-Linked-List"),
("atgko", "ssbu-portfolio"),
("clashstair", "clashstair.github.io"),
("kingstreet637", "godscanner"),
("werea4947-sys", "day_ss"),
("DaPDOG", "ucp-proxy"),
("Dylan-Emanuel", "cloudflare-bypass-2026"),
("LaviHost", "proxy"),
("UMVERTH", "ssz-lensing"),
("goumaivpn", "goumaivpn.github.io"),
("justinechris", "chinawallvpn.github.io"),
("lqdflying", "cursorProxy"),
("xianyu-sheng", "mcp-vision-proxy"),
("alexshxyz", "subscribers_tracker"),
("appclash", "appclash.github.io"),
("salmanshaikh733", "sshaikh-notes"),
("DonJone", "proxy-configs"),
("YoulianBoshi", "vpn"),
("coralfletchercutters", "avast-security-for-uo84"),
("dmitriistekolnikov", "Free_vpns_for_Russ"),
("thuymieu44-alt", "Bai-tap-ss4"),
("Vergorini12", "simple-todo-list-mern"),
("clash-ssr", "clash-ssr.github.io"),
("gosuda", "ssh-chatter"),
("hamedp-71", "N_sub_cheker"),
("richdz12", "traffic-guard"),
("samarrajx", "SSC-Chakravyuh"),
("sisepuede-framework", "ssp_uganda_data"),
("sjensen39", "CRiSSP"),
("Anamalikay", "IPL-AUCTION-CLASH"),
("hydraponique", "roscomvpn-geoip"),
("nori-pixl", "ssAI-project"),
("pepitopere666", "WireTapper"),
("sushmi75", "ss"),
("theakres", "VPN"),
("yauvq25", "vpn-gaming-ping"),
("HECTORjoo", "openclaw-windows-hub"),
("LuisF-92", "Freedom-V2Ray"),
("MilanMishutushkin", "tailscale"),
("Raheem39", "cloudflare-tools"),
("Shazada0070", "nfqws2-keenetic"),
("balaharans2904", "Windows-11-Debloat-AI-Slop-Removal"),
("euank", "wirecage"),
("lerjtl", "Testfree"),
("moriela1", "zero"),
("nyt213", "police-chat-bot"),
("quesoXD12", "nordvpn-wg"),
("sunsc0rch", "reason_gatherer"),
("vancur2021", "my-clash-rule-provider"),
("Aioneas", "Surge"),
("Argh94", "Proxy-List"),
("Fggp09", "mullvad-connection-status"),
("LeonFH2005", "wireguard"),
("Pu-gong-ying", "clash"),
("Toothylol", "Kiro2api-Node"),
("connecting001", "blas-base-ssyr2"),
("hwanz", "SSR-V2ray-Trojan"),
("itgunqbf", "nordvpn-privacy-analysis"),
("mukeshkannan18", "SSHBot"),
("rtxdiv", "vpn"),
("sajkan81", "ecommerce-template"),
("sus112112", "PYDNS-Scanner"),
("uuv19741", "gaming-vpn-latency"),
("DDZ-K", "Fine-grained-routing---OpenClash"),
("DanybossGDpro", "router-vpn"),
("GuyZangi", "clash-residential-proxy-parser"),
("Racc2006", "RealityGhost"),
("chillobamb", "u9k_ssp0"),
("jesusmedrandam", "miniature-octo-palm-tree"),
("mayojw3", "vpn-comparison-nordvpn-expressvpn"),
("rowdy-ff", "javid-mask"),
("vpnsecurity", "vpnsecurity.github.io"),
("wukan1986", "cf-nodes-aggregator"),
("AhDuxng", "SSH-SCRIPT"),
("Colin3191", "kiro-proxy"),
("Coursa4lyfe", "NekoFlare"),
("duurlb480", "vpn-speed-benchmark"),
("Obama907", "theGoillot"),
("OpenNetCN", "clash"),
("arkaih", "VPS_BOT_X"),
("elcompastreaming18-svg", "Prison-Lift-Clash-Helper"),
("runetfreedom", "russia-v2ray-rules-dat"),
("tizijichang", "tizijichang.github.io"),
("Manueleue", "video-audit-platform"),
("amirebni", "proxy-collector-b"),
("andrewgunkel", "todoroki"),
("atou42", "agents-in-discord"),
("clash-ssr-node", "clash-ssr-node.github.io"),
("ember-01", "Clash-Aggregator"),
("sffmrm1", "nordvpn-linux-setup"),
("sotashimozono", "obsidian-remote-ssh"),
("trevortonh", "ssm_in0a"),
("vpnmianfei", "vpnmianfei.github.io"),
("1305a001-ctrl", "strategy-runners"),
("AHANOV-CORPORATION", "ljg-skill-xray-paper"),
("Jihad7x", "mie"),
("Lasertems", "AV-skip-Builder"),
("Thuongquanggg", "Proxy"),
("gxmskj20", "netflix-vpn-unblocking"),
("ssbaxys", "v2ray-configs"),
("ziyilam3999", "monday-bot"),
("MrBeert", "xray-ru-en"),
("SazErenos", "NekoBox"),
("bitesk782-wq", "ljg-skill-xray-book"),
("evgenyzh", "xray-manager"),
("fanqiangapp", "fanqiangapp.github.io"),
("feiniao25789", "vpn"),
("hamedcode", "port-based-v2ray-configs"),
("hector561", "linux-client"),
("jlintvet", "SST-Test"),
("knocid", "xto_97ss"),
("ogt-tools", "ogt-data-proxy"),
("rtwo2", "FastNodes"),
("sdfwch", "clash-config"),
("v2rayxfree", "v2rayxfree.github.io"),
("wr69", "auto-jichangbaohuo"),
("yrteresr", "ljg-skill-xray-article"),
("Anonym0usWork1221", "Free-Proxies"),
("DarkRoyalty", "shnajder-vpn-configs"),
("RainMeriloo", "cf-browser-cdp"),
("Sploo-Scripts", "TheWiz-PS5-Easy-FFpkg-Maker"),
("Vinfall", "VNDB-Calendar"),
("bigsilly94", "mtproto-installer"),
("mingko3", "socks5-clash-proxy"),
("nuggetenak", "Nugget-Nihongo-SSW-Konstruksi"),
("preetcse", "vless-xtls-vision-installer"),
("souzaalfa", "SOUZA-SS.js"),
("xCtersReal", "V2rayFree"),
("40OIL", "domain.club"),
("FloresJesus", "SS_RESTAURANT"),
("HaliFax-Desk", "WildChrysanthemum"),
("Nemka-cmd", "proxy"),
("Sereinfy", "Clash"),
("badhuamao", "FasterVPN-Auto"),
("bondarevaamelya", "token_ss"),
("feiniao1-VPN", "Node-Airport---VPN"),
("freessrclash", "freessrclash.github.io"),
("gitrecon1455", "fresh-proxy-list"),
("spincat", "SmartProxyPipeline"),
("9Knight9n", "v2ray-aggregator"),
("Argh73", "V2Ray-Vault"),
("ExteriorSerf17", "Linken-Sphere-2-Crack-2026"),
("Spellinfo", "sstop"),
("faizalcahyo", "sso_servanda"),
("j0rd1s3rr4n0", "api"),
("lalifeier", "proxy-scraper"),
("nmarun", "SSL_TLS"),
("tonystrak1001-ops", "free-vpn"),
("vpnbaba", "vpnbaba.github.io"),
("wr69", "auto-jichangqiandao"),
("yosik1992", "proxy-grabber."),
("Cellxv7", "testflight-lower-install"),
("GpuLieutenantView", "UrbanVPN-Crack-Latest-2026"),
("LustPriest", "proxy"),
("MixCoatl-44", "Proxy-Scanner"),
("SeizeSummonerTouch", "Kaspersky-Premium-2026"),
("Splitkraedge", "Windscribe-VPN-2026-ts"),
("mahmudzgr", "altin-proxy"),
("nfsarch33", "agentic-ecommerce-web"),
("scriptzteam", "AirVPNWatch"),
("scriptzteam", "NordVPNWatch"),
("Chainsholaud", "McAfee-Total-Protection-2026"),
("LinkPrinceLaud", "Windscribe-VPN-2026"),
("Mervohex", "Kunchi-Gambling-Keydrop-ClashGG-SkinClub-Predictor-Strategies"),
("Sequen0", "ssd-dispatch-tracker"),
("TG-NAV", "nodeshare"),
("TellerPiazza", "UrbanVPN-Crack-2026"),
("alberti12345", "pfopn-convert"),
("anayadora-100rit", "CyberGhost-VPN-2026"),
("elijah-hall-asdq1", "Clash-Verge-Rev-History"),
("fanshuiyu", "invisix"),
("googledslz", "multi-proxy-config_dslz"),
("kooker", "FreeSubsCheck"),
("nirbhay-design", "ODE-SSL"),
("sanmaojichan", "sanmaojichan.github.io"),
("skyvictordolmen", "Opera-VPN-2026"),
("thomas2liv", "3ss_yudl"),
("unxs397", "vpn-comparison-benchmark"),
("AmateurGenius", "zif-fhevm-ai-mega-skill"),
("Lumimojjav", "Chibi-Clash-Crypto-Game-Token-Api"),
("MaskaBOG", "clash-vless-auto"),
("bsk-sssmc", "sssds"),
("caown2", "nordvpn-mullvad-comparison"),
("dongchengjie", "airport"),
("funcra", "vg-mirror"),
("lvyuemeng", "scoop-cn"),
("menasamuel1835", "Pumpfun-Bundler"),
("mohameddorgham32", "open-wire"),
("relc112885", "aws-tally-backup-fsx-hybrid-architecture"),
("zbh360", "vpn-comparison-nordvpn-pia"),
("Anna4355", "aws-physical-server-hybrid-backup-architecture"),
("EliasRipley", "NADS-SSE"),
("LeeChiLeung", "SSH-BRIDGE"),
("Mrnobodysmkn", "Beta-Proxy-Lab"),
("RPSandyGaming", "awesome-terminal-for-ai"),
("SniperGoal", "mac-media-stack-advanced"),
("Taylor-cheater", "free-coding-models"),
("armoralbatrossstir", "Opera-VPN-Windows-2026"),
("bk88collab", "hiddify-app"),
("jb21cn", "proxy-subscription"),
("koteshwr-ra", "linux-mac"),
("noon21000", "Pure-VPN-Crack-2026"),
("sjtlehbie", "meow-ssh"),
("sumanrio", "mcp-atlassian-extended"),
("throneproj", "Throne"),
("wheelerboy", "azi_2ssm"),
("y7007y", "TG-Proxy-Hunter"),
("Boss-venkatesh", "Gost-Tunnel-Manager"),
("Delta-Kronecker", "V2ray-Config"),
("Driftteoutlet", "obsidian-for-windo-ss53"),
("LonLon-Labs", "SSHD_APWorld"),
("MatinGhanbari", "v2ray-configs"),
("Munachukwuw", "Best-Free-Proxys"),
("Princejona", "PinoyVPNAIOupdate"),
("THEzombiePL", "Anti-VPN-List"),
("chiy4728", "Vless_crawl"),
("clashtorwindows", "clashtorwindows.github.io"),
("cury-w", "proxy-all"),
("josebormey", "render-eltoque-proxy"),
("moni-SST", "sst-ams"),
("osf5816", "firestick-nordvpn-setup"),
("rahul-pandey0", "SSRd"),
("Aeryl", "node-utils-1771921901-4"),
("Arefgh72", "v2ray-proxy-pars-tester"),
("GhostPortTechnologies", "Ghostport-Phantom-OS"),
("KiryaScript", "white-lists"),
("Love-AronaPlana", "Automatic-VPN-Aggregation"),
("Paul236", "node-utils-1771917038-1"),
("Thiago12097", "gluetun-webui"),
("aprmns672", "vpn-comparison-2026"),
("cochystars", "FreeProxyProxy"),
("elijah-hall-asdq1", "V2rayN-History"),
("jnjal", "v2ray"),
("ncsurfus", "ssmlib"),
("tencentmusic", "cube-studio"),
("vasavibusetty", "DyberVPN"),
("BreezeBoulderMap", "Mullvad-VPN-Premium-Last-Version"),
("JeBance", "CheburNet"),
("JerryCW", "clash-rules"),
("Keliz271", "Lantern"),
("LineShogunSlat", "Proton-VPN-Crack-Latest"),
("S13LEDION", "idea-reality-mcp"),
("SSSSGGAAMMIINNGG", "devcontainer"),
("SoroushImanian", "BlackKnight"),
("dani9701", "python-apple-fm-sdk"),
("elmaliaa", "AdderBoard"),
("izytm265", "vpn-travel-security"),
("theavel", "free-vless-proxy"),
("yashlatiwal", "ssc-reddit-monitor"),
("Access-At", "proxy-list"),
("CB-X2-Jun", "Free-v2ray-node"),
("Chipsotrellis", "Proton-VPN-Crack-2026"),
("Dark675sfdsgfxh", "xray-reality-setup"),
("Moha-zh11", "codexapp-windows-rebuild"),
("Seeh-Saah", "awesome-free-proxy-list"),
("TopChina", "proxy-list"),
("arseniy700", "vpn-sub"),
("dgucxpmn", "nordvpn-nomad-comparison"),
("flclash-us", "airport-rec-jz6rj1"),
("jaimeautomatiza", "tle-proxy"),
("kiiyp23", "streaming-vpn-comparison"),
("marouchsail", "aigateway"),
("mmaksim9191", "my-vpn-configs"),
("onl35461-debug", "Free-ladder---VPN"),
("selfconjurerrelease", "Hamachi-Pro-Crack-2026"),
("tehrzky", "my-tv-v2ray"),
("wxglenovo", "1AdGuardHome-Rules-AutoMerge-"),
("ChaselDutt", "VPN-Deep-Test"),
("Excellenceehoist", "Mullvad-VPN-Premium-2026"),
("FrostChateau", "Windscribe-VPN-2026-go"),
("Micky203", "zenproxy"),
("SANTOSHPATIL2004", "Telegram-Proxy"),
("ThongLuc2k3", "Prompt-Guided-XRay-Segmentation"),
("WLget", "V2ray_free"),
("cloudmesh-ai", "cloudmesh-ai-vpn"),
("flclash-us", "airport-rec-7zktyw"),
("onl35461-debug", "Node-climbing-wall-ladder---VPN"),
("teknovpnhub", "v2ray-subscription"),
("zackprawaret", "MiddleFreeWare"),
("zerocluster", "proxy"),
("AlexMikhin951", "my-proxy-aggregator"),
("BrinkPrivate", "Surfshark-VPN-Crack-2026"),
("FLAT447", "v2ray-lists"),
("J-L33T", "vlesstj"),
("Jethro94", "nats-server"),
("Luisveloza", "api-manager"),
("SherlyKinan", "proxy-check"),
("ahmedhelala", "xuruowei-forever"),
("aiboboxx", "v2rayfree"),
("codeWithDiki", "cwd-toko-online"),
("free-nodes", "v2rayfree"),
("handeveloper1", "DailyProxy---Auto-Update-List"),
("k4vein", "miaoyu-proxy"),
("mazda4940original", "PortWorld"),
("miraali1372", "mirsub"),
("nilslockean", "ssgb-astro"),
("oinqq223", "vpn-comparison-nordvpn-expressvpn"),
("sibur1703-alt", "my-auto-vpn"),
("surdebmalya", "baud-news-ss"),
("yesh2002", "fastapi-presearch"),
("83646uguh", "Git-proxy"),
("Alex-010101", "raspberry-pi-media-stack"),
("AniketPaul44", "lextex-homelab"),
("Barabama", "FreeNodes"),
("Dapperdan1956", "GeminiOS"),
("FishyUK", "SSOHTP3.2"),
("OrionPotter", "free-proxy"),
("acymz", "AutoVPN"),
("aditya123-coder", "GoatsPass"),
("amanraj76105", "EasyProxiesV2"),
("annacriativars2", "synapse-protocol"),
("clashmianfeijiedian", "clashmianfeijiedian.github.io"),
("doxxcorp", "vpn-leaks"),
("feiniao1-VPN", "VPN-service"),
("fjb469", "nordvpn-dubai-uae"),
("khbmgh", "clasher"),
("kingorza2011-ctrl", "vpngate-servers"),
("mahdisandughdaran-sys", "V2ray-sub"),
("moksharth77", "mcp-remnawave"),
("mysistoken", "ghost-complete"),
("soenneker", "soenneker.cloudflare.ssl"),
("ssipankajsingh", "security-advisory-proxy"),
("zxsman", "clashfree"),
("AliEgeErzin", "ssaju"),
("Arefgh72", "v2ray-proxy-pars-tester-02"),
("MahanKenway", "Freedom-V2Ray"),
("Moatasemmofadal", "ssd"),
("NiCkLP76667", "Halt.rs"),
("ShapeRepresentative", "Error-0x80072ee7-Solutions-Windows"),
("Sobobo32", "cli-proxy-API-Center"),
("TrippyDawg", "tg-ws-proxy"),
("YawStar", "Proxy-Hunter"),
("horoshiyvpn-rus", "smart-vpn-sub"),
("l610128078", "sssss"),
("malfy-driller", "vpn-builder-"),
("myPOSpk", "whitelist_obhod"),
("saliniarjun", "EvilAP"),
("tairimehdi", "tcp-ip-attack-lab"),
("tiagorrg", "vless-checker"),
("tickmao", "Rules"),
("xuerake", "my-clash-sync"),
("4n0nymou3", "multi-proxy-config-fetcher"),
("Davi111776", "Overlord"),
("Holdkradesignate", "TotalAV-Pro-Activator-Crack"),
("IPParrot", "proxy_ips"),
("Jayysofficial", "redpill"),
("asakura42", "vss"),
("bgpeer", "icons"),
("bluereaper-2125", "max-list"),
("feiniaovpn", "Accelerator-Node---VPN"),
("grimvpn", "clash-convertor"),
("isra-osvaldo", "Evasion-SubAgents"),
("it-ypr", "sshtapigw-client"),
("jimmyqrg", "jimmyqrg.github.io"),
("kingorza2011-ctrl", "vpn-sub"),
("kort0881", "vpn-vless-configs-russia"),
("muhammadhamzaazhar", "Automated-Lungs-Disease-Detection-ChestXray14"),
("netbursarlead", "Opera-VPN-Latest"),
("nyeinkokoaung404", "multi-proxy-config-fetcher"),
("ppap54088", "ProxMO-RL"),
("sevcator", "5ubscrpt10n"),
("tideakatsukiendure", "Mullvad-VPN-Premium-Latest"),
("vakhov", "fresh-proxy-list"),
("Alexgood321", "my-proxy-raw-link-for-all"),
("CB-X2-Jun", "https-proxy"),
("DJOUD3148", "browser-extension"),
("Gr00ss", "Gr00ss"),
("Kadowms", "Sakura-Rat-Hvnc-Hidden-Browser-Remote-Administration-Trojan-Bot-Native"),
("Kelvin295", "cloakpipe"),
("Mrnobodysmkn", "Auto-proxy"),
("PSyC25-26", "PSyC-SS-03"),
("Temikus", "fastmail-cli-docker"),
("V2RayRoot", "V2Root-ConfigPilot"),
("Vadim287", "free-proxy"),
("Zaeem20", "FREE_PROXIES_LIST"),
("coffeegrind123", "awg-easy-rs"),
("kamzy01", "TG-WebApp-Proxy"),
("piotrv1001", "how-to-scrape-dhgate-in-nodejs"),
("qoqc161", "vpn-comparison-nordvpn-cyberghost"),
("razoshi", "v2ray-configs"),
("waila1", "apple-id-subscribe-ai"),
("Delta-Kronecker", "Tor-Bridges-Collector"),
("FLEXIY0", "matryoshka-vpn"),
("Surfboardv2ray", "Proxy-sorter"),
("TskFok", "sshx"),
("blsdncn", "MCFuzz"),
("cook369", "proxy-collect"),
("hubertfooted416", "clash-wsl-network-doctor"),
("niq0n0pin", "v2rayfree-nice-tracker"),
("plero75", "proxy-prim-render"),
("qwerty197688-blip", "max-proxy"),
("sb090", "tauri-plugin-macos-fps"),
("soumyaranjanjena007", "indonesia-gov-apis"),
("Beatrisadecisive305", "whoami"),
("Frostbound-northsea978", "api2cursor"),
("Shun234434334343", "supercli"),
("Straightedgeheathaster783", "NanoProxy"),
("Vanic24", "VPN"),
("bananasminecraftroblox192-glitch", "DEPI-SSIS-ETL-DWH-Project"),
("depollsoft", "MonkeySSH"),
("johopechh", "Clash"),
("kenshin-arch", "Meta-Business-Suite-SSL-Pinning-Bypass"),
("mummerfleshwound733", "sputniq"),
("poetic-macroglia442", "openclaw-desktop-launcher"),
("seejanm9990", "dynamo-shield"),
("tn3w", "TunnelBear-IPs"),
("wubingle-crypto", "bwh-hermes-agent"),
("xscosa400-wq", "universal-flutter-ssl-pinning"),
("xuyunxuyun", "SuperTeam"),
("0Pwny", "proxy-checker"),
("Alex-Brn", "v_deploy"),
("Axillaryfossaprize786", "github_copilot_openai_api_wrapper"),
("Bean5789", "bbd2api"),
("Drishtipixiee", "trinetra-rakshak-ssd"),
("I-r-a-j", "proxy"),
("NanoSoulEmpty", "Dolphin-Anty-Crack-2026"),
("Str3akoner", "UltraHiT"),
("cariconjugal320", "deepseek-claude-proxy"),
("cmepthuklolka1", "vpn-bot"),
("dmvait8534", "claude2api-deploy"),
("harmonic-desire485", "nebula"),
("outofprint-statesgeneral134", "the-infinite-crate"),
("pg-sharding", "spqr"),
("punez", "proxy-collector-a"),
("signgeneraldefeat56", "CyberGhost-VPN-Crack-2026"),
("toleuranus332", "KiteAI"),
("toyonakibirthtrauma50", "env-runner"),
("upperleopardpath", "urbanvpn-cracked-2026"),
("vyxb18", "smart-tv-vpn-setup"),
("warm-mannalichen723", "qclaw-skip-invite"),
("Blotchy-unbecomingness80", "openclaw-dae-skills"),
("BrandonPerez915", "CineList"),
("Catoptric-genusplatanthera273", "2-api"),
("ImJustSkilled", "porta"),
("Nnon605246", "singbox_ui"),
("Skyscraperfoxhound619", "markdown-ui-dsl"),
("adoptiongenuslemmus722", "chatgpt-creator"),
("jasil2215P", "ssmd_backend"),
("mmbateni", "armenia_v2ray_checker"),
("ninjastrikers", "nexus-nodes"),
("tczee36", "xmr-nodes"),
("Ariedeclivitous630", "vecgate"),
("Davidsonencyclical885", "Nova-Os"),
("Forceful-gluteusminimus381", "mqttgo_dashboard"),
("Julk8200", "Illuminate"),
("Phantriy4065", "ai-cost-optimizer"),
("PraveenMegh", "ssi-inventory"),
("ReliablyObserve", "Loki-VL-proxy"),
("Thirddegreegrocery830", "xr"),
("bnlp99", "nordvpn-security-review"),
("denmrnngp-cloud", "hiddify-steam-deck"),
("denmrnngp-cloud", "hiddify-steam-deck-vpn"),
("devops-igor", "amnezia-web-ui"),
("estebanbkk-glitch", "switch"),
("pandemic-xanthicacid21", "mcp-time-travel"),
("piqueriastrongbreeze520", "claude-and-codex-website"),
("sakha1370", "OpenRay"),
("spx7r2339-ux", "Ssp"),
("steam-100", "free-proxy-sub"),
("Exabyteasiaticbeetle444", "burrow"),
("Orthostatic-cassava481", "crypto-security-toolkit"),
("ad1239g", "token-saver"),
("amdevelopment-scripts", "my-sveltekit-template"),
("chengaopan", "AutoMergePublicNodes"),
("cxv-drift220", "mythic_tailscale"),
("evanyou0411-design", "zalo-agent-cli"),
("gameoplight-lgtm", "FlowSet"),
("longlon", "v2ray-config"),
("mamun1978", "__2026_03_14_chihlee_gemini__"),
("olcortesb", "s3rv3rl3ss"),
("skibiditoilet12341912-eng", "connaxis"),
("stantonadnexal355", "spark-clean"),
("Kingslywilling46", "ssbu-less-lag"),
("Liviastrange489", "easiest-claw"),
("Nosepythoninae912", "snip"),
("Re0XIAOPA", "AutoScrapeFreeNodes"),
("andreasvesaliusfringedpolygala893", "codex-manager"),
("deezertidal", "fee-based"),
("deezertidal", "freevpn"),
("edwinvizcarra1234591-max", "tg-ws-proxy-ANDROID"),
("hamdanalk3biii-ux", "kyprox"),
("ikuaidev", "ikuai-cli"),
("imegabiz", "DPI-Phantom"),
("jimmyk9573", "openwebui-ollama-proxy"),
("khaled4123e", "AIOS"),
("mlagifts2809", "ssa-my-social-security-browser-automation"),
("sarthakGudwani200", "Lucid-Subnet"),
("sunny9577", "proxy-scraper"),
("uncial-contingence591", "Openclaw_Free"),
("CCSH", "IPTV"),
("R3ZARAHIMI", "tg-v2ray-configs-every2h"),
("Semporia", "Clash"),
("Tod-weenieroast366", "coding-plan-mask"),
("Trivexion", "AsteriskPassword-Viewer"),
("Vortalitys", "PrivHunterAI-detects-access-vulnerabilities"),
("brandicoital992", "Awesome-Minecraft"),
("daktil888", "ocp"),
("gastonempathic658", "YouTube-to-Cloud-Downloader"),
("imegabiz", "Anonymous-ir-proxy-configs"),
("jackbayliss", "cloudflare-r2-rss"),
("milliammeterfamilyalligatoridae52", "fly-vpn"),
("p3tra3", "bandwidth-hero-proxy2"),
("prit3shnaik", "kitsune-proxy"),
("Analgesiamisuse629", "AntiDetection-ProxyBrowser-2026"),
("Audenesque-confession698", "fragment-tg"),
("AvenCores", "goida-vpn-configs"),
("Basidiomycetespanamaniancapital403", "workerd"),
("Mucose-genusalepisaurus901", "CTF-blog-downloader"),
("Paorwm", "Batch-Downloader-Crypter-FUD-UAC-Bypass"),
("Shayanthn", "V2ray-Tester-Pro"),
("Shootp5044", "gemini-mac-pilot"),
("Wassay380", "NaiveProxy"),
("acquainted-marsh585", "BackupX"),
("constanceintrauterine625", "MySearch-Proxy"),
("distributive-filter937", "royale_lab"),
("emanuele-em", "proxelar"),
("r2d4m0", "vless-parser"),
("rimisarker", "automated-3-tier-deployment"),
("ssplash65", "sspl"),
("svpjohji", "NECHAEV_VPN_AGGREGATOR"),
("z2531102845", "clash"),
("30nilupulthisaranga-bit", "aegis"),
("Albertarevolutionary289", "any-auto-register"),
("Beallenonindustrial63", "no-ai-in-nodejs-core"),
("Djawedc7304", "gea"),
("Islamnetz", "gmail-account-creator-bot-pro"),
("Paorwm", "Batch-Malware-Builder-FUD-Crypter-AV-UAC-Bypass"),
("Seantee9163", "money-news-station"),
("Shiovann2991", "ProtoCMiner"),
("SoftEtherVPN", "SoftEtherVPN"),
("absolutethresholdhsvii920", "mpp-proxy"),
("bollywoodhymanrickover646", "zoro"),
("divisible-stretcherparty41", "Predict-Fun-Farming-Bot"),
("feiniaovpn", "--VPN"),
("kalde5307", "omarchy-ibm-theme"),
("kravchenkosaveliy27-crypto", "my-vpn"),
("matiassppeed-stack", "gemini-watermark-remover-editghost"),
("motoneuronrijstafel442", "vless-xhttp"),
("redondoc", "wsj-zh-rss-proxy"),
("sternepenitentiary330", "google"),
("5a5ehw1-star", "ssq"),
("Evangelinchichi158", "Proxy-Scraper-2026-GUI"),
("Hidashimora", "free-vpn-anti-rkn"),
("Karlczernyvaporisation476", "S2A-Manager"),
("Micaelachesty584", "Citadel"),
("Rutherforddry602", "sha2-ecdsa"),
("SSSMC-web", "schedule.sssmc"),
("SevenworksDev", "proxy-list"),
("XigmaDev", "cf2tg"),
("despiteportablecomputer411", "proxy-ipv6-generator"),
("free-nodes", "clashfree"),
("gensyn", "ssh_command"),
("komutan234", "Proxy-List-Free"),
("krokmazagaga", "http-proxy-list"),
("lolandegrenadian150", "IntelliHybrid"),
("massimoalbertoli-arch", "school-calendar-proxy"),
("sdsdsdsdsdsihdkjsdjl", "cursoride2api"),
("trabict", "my-vpn-configs"),
("Fadouse", "clash-threat-intel"),
("Maxierepresentational96", "YaCV"),
("Phillippcarboniferous312", "My-Brain-Is-Full-Crew"),
("epappas", "llmtrace"),
("geometric-detection287", "Socat-Network-Operations-Manager"),
("huameiwei-vc", "stash-kr-proxy-auto-refresh"),
("i-Padla", "sbce"),
("injustice4934", "GitHub-Copilot-Free"),
("platonic-gaelic239", "Emby-In-One"),
("roderigoambiguous332", "MicroWARP"),
("xq25478", "OpenProxyRouter"),
("Armchaircounty801", "cc-weixin"),
("CROSS-T", "Linux.do-Accelerator"),
("Decreasingmonotonic-openendwrench955", "proxy-turn-vk-android"),
("Esethu1974", "sgproxy"),
("Jayant2007", "Mimir"),
("Mayurifag", "proxies-cfg"),
("NJMathwig", "qiaomu-markdown-proxy"),
("NtWriteCode", "ssh-honeypot"),
("arunsakthivel96", "proxyBEE"),
("diroxpatron12", "SubHunterX"),
("ipdssanggau", "cloudflare-Management"),
("partitive-comma396", "nayuyyyu"),
("salmanshaikh733", "sshaikh-dotfiles"),
("shadowy-pycoder", "go-http-proxy-to-socks"),
("Adamoktora", "imperium"),
("Aline001xx", "turk-arr-bridge"),
("DevRatoJunior", "cc-weixin"),
("Simprint", "simprint"),
("apify", "crawlee"),
("clerzg", "quick-argo-xray"),
("ilyaszdn", "Ladder"),
("malfy-driller", "vpn-builderV2"),
("ra7701", "aulite"),
("suba1653", "CFWarpTeamsProxy"),
("xiphiidaeequinox80", "mihomo-upstream-proxy-setup"),
("AbdallahMekky", "AbdallahMekky"),
("AlbiDR", "Clash-Manager"),
("Hearion", "qq-farm-automation"),
("Kelsibenzoic800", "sshtoolkit"),
("MarcoYou", "open-proxy-mcp"),
("OmniLLM", "omnillm"),
("Trillion-pinkandwhiteeverlasting354", "MyDVLD"),
("ZeroDeng01", "sublinkPro"),
("huangjunyin991-art", "ak-proxy"),
("kiet50524", "My-TW-Coverage"),
("ljrdominic-png", "misakaReborn"),
("lucaa7", "progetto-SSH"),
("mohamadfg-dev", "telegram-v2ray-configs-collector"),
("mukeshk3272", "Smart-Routing-Butler-for-OpenClaws"),
("oxley-z", "get_sse_etf_historical_data"),
("skinned-italianpeninsula990", "weclaw-proxy"),
("wallisthundering974", "xr-journal-query"),
("Julesfar710", "heimsense"),
("Muhammad4822", "freezeauto"),
("abdallahLokmene", "teamclaude"),
("arunprab", "ssmt"),
("lordi2809", "agent-infra-security"),
("piotrv1001", "how-to-scrape-walmart-listings-in-nodejs"),
("sreckoskocilic", "weeqlash"),
("vivianalaced749", "vk-calls-tunnel"),
("6arshid", "fuck-iran-filtering"),
("Divetrainer", "SSG"),
("Goodygoody-wisp580", "apple-health-analyst"),
("LING-0001", "Android_helper"),
("LeiyuG", "Clash"),
("Rimaglottidisspacewalk319", "claude-meter"),
("codonaft", "broadcastr"),
("hati4100", "oag"),
("loglux", "authmcp-gateway"),
("lothianregionophrysapifera132", "docker-openvpn"),
("masseuseherpetology481", "keygate"),
("ngngochienvinh07-crypto", "ngngochienvinh_it202_ss13_b1"),
("Buint1504", "Predict-Fun-Farming-Bot"),
("KaWaIDeSuNe", "xingjiabijichang"),
("Karenfsi188", "xray"),
("Silentely", "AdBlock-Acceleration"),
("broken-osmund815", "Polymarket-Trade-Bot"),
("fluxflapping699", "factory-cursor-bridge"),
("ngngochienvinh07-crypto", "ngngochienvinh_it202_ss13_b2"),
("ngngochienvinh07-crypto", "ngngochienvinh_it202_ss13_b3"),
("paul86Wilson", "ssdjis8aorobertsusan43271"),
("revenantguttaperchatree773", "Onvoyage-Ai-Testnet-farm"),
("sergi039", "sschess"),
("sgnaijtheuser", "proxy"),
("stevef1uk", "freeride"),
("swagsiamese37", "GVRT-Trading-Bot"),
("BielGodoi", "3LayersPersistence"),
("Ganeshk2018", "testpad-proxy"),
("Grassmacoun146", "CPA-OPEN"),
("Rhodawagnerian446", "docker-wireguard"),
("TheBharathProject", "sypher-api"),
("Zohuko71", "ferrox"),
("anniet5664", "webclaw-tls"),
("hardcopycortex461", "worker-bridge"),
("ilamafascista615", "kyma"),
("masx200", "feiniu-os-ssh-security-analysis"),
("ngngochienvinh07-crypto", "ngngochienvinh_it202_ss13_b4"),
("ngngochienvinh07-crypto", "ngngochienvinh_it202_ss13_b5"),
("ngngochienvinh07-crypto", "ngngochienvinh_it202_ss13_mm"),
("Margothermoplastic365", "waterwall-api-gateway"),
("Minded-nakuru841", "headscale-install"),
("SoliSpirit", "proxy-list"),
("aradhyagithub", "FLJopen"),
("bayvapourisable154", "Stratum"),
("hanteng", "ACM-article-SSbD-MVB"),
("magicspellnosejob374", "flaregun"),
("rci-prog", "registai-app"),
("ritchiearistotelian98", "docker-headscale"),
("HSG4338", "springboot-oauth2-sso-example"),
("IHK-ONE", "ISCC_Center"),
("Malvaceaefries86", "NetSniffer"),
("SSBMILanguageDepartment", "SSBMILanguageDepartment.github.io"),
("balukapilguru", "Teksacademy_SSR"),
("explorative-largemagellaniccloud775", "MF.Radius"),
("fadh24434", "webarsenal"),
("Asaza366", "iron-proxy"),
("Itci1146", "AME_Locomotion"),
("Nonpregnant-loss29", "not-claude-code-emulator"),
("abidi556", "doge-code"),
("elly5490", "telegram-proxy"),
("kanami09", "Copilot-Proxy"),
("marckrenn", "claude-code-changelog"),
("mayerhany32", "litchi_claude_code"),
("partout-io", "passepartout"),
("purecores", "Proxy-Rules"),
("tiendatdong", "hn-cntt1-dongnguyentiendat-ss13-it202-b1"),
("tiendatdong", "hn-cntt1-dongnguyentiendat-ss13-it202-b2"),
("tiendatdong", "hn-cntt1-dongnguyentiendat-ss13-it202-b3"),
("tiendatdong", "hn-cntt1-dongnguyentiendat-ss13-it202-btth"),
("yahoosony81-sys", "subscribe-pt"),
("5x45snwhbx-oss", "openai-nim-proxy"),
("AE86X", "Tronbot"),
("Claudiasinusoidal818", "OffensiveSET"),
("Dororecessed36", "telegram-auto-clone-download"),
("E-Sh4rk", "sstt"),
("Lowering-mechanism250", "ns"),
("Mralimoh", "Zephyr"),
("Yangxiaotian", "SSHChat"),
("officialputuid", "ProxyForEveryone"),
("rorafiftysix26", "First"),
("0funct0ry", "xwebs"),
("Ciara-Aa", "PROXY-free"),
("Elkraz", "ccxray"),
("EngangAman", "GptCrate"),
("Facilitairinfo", "SlothProxyV2-Public"),
("Foul-plastique636", "CC-Router"),
("Leos573", "node-curl-impersonate"),
("Scoreverb70", "NekoCheck"),
("SunBK201", "UA3F"),
("adeshra5646", "VLESS-XTLS-Reality-VPN"),
("asiahpolo", "keybo-photo-proxy"),
("bellasachs4-bit", "wiregui"),
("jonascolditz3-dot", "SSC-Database-Gen-Tool"),
("kort0881", "vpn-checker-backend"),
("mindstone", "Super-MCP"),
("mmbateni", "iran-proxy-checker"),
("tylero5029", "MasterDnsVPN-AndroidGG"),
("yashgoel-711", "To-Do-List-App"),
("CB-X2-Jun", "proxy-lists"),
("Competent-genuscanella687", "openclaw-billing-proxy"),
("Dipanwita-Mondal", "tunnel"),
("Ealasaidstupid494", "VeilScrape"),
("Jasperuric559", "Supervisor.skill"),
("alixblae550", "SecureTunnel"),
("commercesehoga", "ssc"),
("epigraphcommissioner131", "ai-one-click-beauty"),
("intell009", "proxy_list"),
("joy-deploy", "free-proxy-list"),
("lidiama9513", "goated"),
("rakibkumar151", "auto-proxy-updater"),
("thuannguyen23", "proxy-deepseek"),
("unnourished-calciumchannelblocker351", "HydraFlow"),
("Andy7152", "luci-app-minigate"),
("Bpcod8422", "Facebook-SSL-Pinning-Bypass-NonRoot"),
("CuteReimu", "sssplitmaker"),
("JoyousCode", "NppSSH"),
("Manans999", "ChromiumManager"),
("Robbynjazzy512", "opencode-local-provider"),
("canmi21", "vane"),
("crashed6767", "tor-proxy"),
("mommommy1960-lang", "mya-mprs-system"),
("proud-persiangulf507", "ripgrep-node"),
("sanasa-bank-baddegama", "nod"),
("Amy7007", "VPN-Detector"),
("Arjun99291", "telemt-panel"),
("Dldigisof3283", "copilot-api"),
("OxiBelt", "OxiBelt"),
("aaron4605", "context-optimizer"),
("davitaalliaceous7299", "FalixNodes"),
("ernestaweak8629", "yourvpndead"),
("nori-pixl", "ssai-copy"),
("ron33tui", "clash-merger"),
("shreyanxNova", "RKNHardering"),
("sketch7", "ssv.cli"),
("teraka3109", "hls-restream-proxy"),
("treasonking", "Capstone_Design"),
("tullextraterrestrial3175", "ClaudeCode-Model-Rotator"),
("volondsespel-png", "vpn-key-collector"),
("Gmsher5817", "domloggerpp-caido"),
("KaWaIDeSuNe", "dijiajichang"),
("cybelleweak1220", "green-campus-tracker"),
("jannasweetened9049", "SwizGuard"),
("lucas01feh", "oss-security-audit"),
("ssavnayt", "AWCFG-CONFIG-LIST"),
("trybyteful", "public-dns-directory"),
("youkatalo123-star", "ComfyUI_RH_VoxCPM"),
("2cydg", "knot"),
("Armillary-italy713", "Smart-Config-Kit"),
("Biologicaltimemistral1034", "nodris"),
("DowellHd", "ssb-web"),
("Jeffreycommon553", "HA-Optimizer"),
("Prasadchelated435", "windows-telegram-bot"),
("Rr3511167", "snix"),
("Scarecrowish-shoat5968", "ByeByeVPN"),
("Sprokitz", "all-deploy"),
("Teodoorpenal672", "baiqi-GhostReg"),
("Tuchit893", "social-fixed-ip-guide"),
("chase-roohms", "dev-stats"),
("jhosuemiscanvilchez", "ssh-api"),
("marklubin", "double-buffer-proxy"),
("shitless-secretor385", "ahr999-dataset"),
("virgiliomaxillary918", "cfnb"),
("Aplikasi-Berbasis-Platform-S1IF-11-04", "Pertemuan-3"),
("Areral", "ScarletDevil"),
("Doryeightsided72", "adblock-rust-manager"),
("Remyix123", "PiHole-Cloud-Wireguard-VPN-Orchestrator"),
("SSIvanov19", "ssivanov19"),
("Thor-jelly", "proxy"),
("VictorMaxWang", "childcare-smart"),
("aloplus", "AloPlusVPN"),
("aplus42", "codex_zhipu_proxy"),
("eooce", "Sing-box"),
("greenlandspinel496", "FlowDriver"),
("mariadelapazj2155", "nginx-proxy-manager-api"),
("rainwatershilling272", "Fortnite-Premium-External"),
("saltplainjobaction503", "sub-store-workers"),
("sonic0jd", "MasterHttpRelayVPN"),
("tranhailong012", "windsurf-tools"),
("vievieng761", "AJAS"),
("xuanranran", "rely"),
("zbxhaha", "go-task-scheduler"),
("Gerryoverlooking665", "Blooket-Bot-Flooder"),
("Lgutier9249", "SNI-XHTTP-V1.1"),
("Memooaren7891", "VSoft.AnsiConsole"),
("NotSoGoody", "SS_Liner"),
("Tieazide1959", "DNSly"),
("Unified-rosinbag197", "gh-relay"),
("Unopposable-starting193", "chatgpt-bridge"),
("Wheelernormandy677", "CF-IP-Scanner"),
("alisadeghiaghili", "v2ray-finder"),
("amuck-tie267", "SNI-XHTTP"),
("balaji-cse15", "gemi"),
("chantalunsupportable7191", "mhr-cfw"),
("kirtim8895", "awesome-privacy-tools"),
("kruton", "waterpoint-decafmud"),
("matsorton", "ss7_ru5q"),
("spayed-turkmen6590", "netlify-relay"),
("127gardo", "ProxyFit"),
("EkkoG", "clash-for-openclash-dist"),
("Intermolecular-sirdar532", "v2node"),
("NASEER-MAX", "ssSign.github.io"),
("Ray-Code-Cube", "7sshistoryyeear"),
("Secondary-offer942", "hamid-mahdavi-client"),
("anutmagang", "Free-HighQuality-Proxy-Socks"),
("batus5678", "mhr-ggate"),
("fleetstreetremit109", "Post-X-Premium.com-Automated-Post-Publishing"),
("itsanwar", "proxy-scraper-ak"),
("olympiangamesgenussynchytrium730", "dokploy-tailscale-webhook-relay"),
("stacksjs", "rpx"),
("wink-run", "local-llm-proxy"),
("wonglaitung", "fortune"),
("woshishiq1", "my-clash-sync"),
("APX103", "a2a_proxy"),
("Aethersailor", "Custom_OpenClash_Rules"),
("Alexander-vecos", "ssmt"),
("Frozoewn", "S500-RAT-HVNC-HAPP-HIdden-BROWSER-HRDP-REVERSE-PROXY-CRYPTO-MONITOR"),
("Hubaio", "Reverse-Proxy-Soruce-Code"),
("Mohammedcha", "ProxRipper"),
("NodePassProject", "Anywhere"),
("daneb255", "pkggate"),
("feiniao25789", "feiniao-vpn"),
("hguerrero", "datapath-workshop"),
("onl35461-debug", "Node-Airport---VPN"),
("vercel-user118", "universal-ai-proxy"),
("vovan046kursk-stack", "vless-list1"),
("9xN", "auto-ovpn"),
("Durgaa17", "cf-sg-proxies"),
("Ian-Lusule", "Proxies"),
("SukkaW", "Surge"),
("Xnuvers007", "free-proxy"),
("bin1site1", "V2rayFree"),
("deanmauriceellis-cloud", "LocationMapApp"),
("feiniao1-VPN", "Free-ladder---VPN"),
("masx200", "xray-core-nat-project"),
("mayday151", "douban-proxy"),
("onl35461-debug", "Wall-climbing-ladder-VPN"),
("rlaeodn1015-oss", "ssnim-request-landing"),
("shaa2020", "V2Ray-Automator"),
("torsuker", "xkr_ssoa"),
("yunusalemu", "Proxy-Manager"),
("Garmask", "SilverRAT-FULL-Source-Code"),
("Ian-Lusule", "Proxies-GUI"),
("M-logique", "Proxies"),
("MichaelPaddon", "aloha"),
("bonymalomalo", "vless-auto-update"),
("hunter-read", "lfg-bot-static"),
("liangshengyong", "LanWan"),
("scriptzteam", "AzireVPNWatch"),
("snowluwu", "droute"),
("souravbhuiyan12245-hue", "sstopup"),
("7c", "torfilter"),
("Alexey71", "opera-proxy"),
("Humayun1318", "QuickHire"),
("JY-Mar", "PxyRes"),
("MohamedFazil1406", "CachingProxy"),
("Pawdroid", "Free-servers"),
("RealFascinated", "PIA-Servers"),
("Scully34", "sscoe-dashboard"),
("bcst17", "proxy-manage"),
("crackbest", "V2ray-Config"),
("eliaxqm", "ssq_7sci"),
("junjun266", "FreeProxyGo"),
("maiyulao", "ResoHub"),
("mfonectrl-bit", "rss-proxy"),
("milchee", "vless_subs"),
("roosterkid", "openproxylist"),
("vase25bush", "vpn_x2c4"),
("Anjali-gola151", "Airbnb"),
("crolankawasaki", "Goida26-Clash"),
("darkflame265", "08_PathClash"),
("elliottophellia", "proxylist"),
("giuseppefabiani78-hash", "mepa-rdo-proxy"),
("kiyo-astro", "SSDL-SatPass-Notification"),
("petushokmaxorka-ai", "aivus-vpn"),
("sleeplu40", "me5_1ss7"),
("360solutionsbe", "bc-mcp-proxy"),
("HNGM-HP", "sssh"),
("Kingrane", "vless_test"),
("SoliSpirit", "SolVPN"),
("jwilsoncha", "xwh_y4ss"),
("kingowow", "Kingo-vpn"),
("mfuu", "v2ray"),
("nori-pixl", "ssai-server"),
("partnermbp", "VLESS_RUS"),
("pavinommal", "ssm_m6my"),
("qq547820639", "tiktok-ad-video-skill"),
("Buch5303", "ssc-v2"),
("Danil6395", "FigusVPN"),
("Kirillo4ka", "eavevpn-configs"),
("SpriteStudio", "SSPlayerForGodot"),
("SyaiYesMom", "Credential-Harvesting-Session-Hijacking-Bot-from-SSO-Universitas-Duta-Bangsa"),
("ThaminduDisnaZ", "Esena-News-Github-Bot"),
("cloudskytian", "acl4ssr2autoproxy"),
("erhaem", "sslproxies-scraper"),
("feiniaovpn", "Office---VPN"),
("mmm1h", "clashconfig"),
("theriturajps", "proxy-list"),
("v2raynnodes", "v2rayfree"),
("wenxig", "free-nodes-sub"),
("yootor", "ACL4SSR"),
("ayon-ssp", "ayon-ssp"),
("gbagliesi", "cms-sst-report"),
("junkurihara", "rust-rpxy"),
("jy02739245", "ssh_tools"),
("legeiger", "mensa-to-ical"),
("stevendodd", "clash-clan-manager"),
("stylehouse", "leproxy"),
("trxd", "trojan"),
("youfoundamin", "V2rayCollector"),
("Leon406", "SubCrawler"),
("Open-Copilot-Proxy", "Copilot_Proxy"),
("Yam3DLife", "vpn-subscriptions"),
("arseniy700", "MSC-VPN"),
("learnodishahelp-cmd", "sscdash"),
("lexariley", "v2ray"),
("lm705", "vair"),
("partout-io", "partout"),
("supercrypto1984", "api-benchmark-monitor"),
("10ium", "V2RayAggregator"),
("GubernievS", "AntiZapret-VPN"),
("Master-Mind-007", "Auto-Parse-Proxy"),
("SSL-ACTX", "SSL-ACTX"),
("blog1703", "tgonline"),
("goauthentik", "authentik"),
("luxxuria", "harvester"),
("mhghco", "v2ray-hub"),
("mock-server", "mockserver-monorepo"),
("nomadturk", "vpn-adblock"),
("patel-Asan", "SSC1"),
("rasool083", "v2ray-sub"),
("zy19970", "siteproxy"),
("7228227hhh", "Tutorial-on-Setting-Up-a-Personal-VPN-Proxy"),
("Desstroyerrr", "ATmega328P_SSD1306_Driver"),
("Kitti1337", "passepartoutkit"),
("PatNei", "esport-ics"),
("Silvester13-SOS", "clash-war-analytics"),
("SriSathyaSaiVidyaVahini", "SSSVV-landing"),
("Udhayakumar-SS", "https---github.com-Udhayakumar-SS-Workconnect"),
("V2RayRoot", "V2RayConfig"),
("anatolykvochur62-sys", "sslbrute.sh"),
("atajanofficila", "vpn-server-list"),
("cstreit03", "CoC-Stats"),
("feiniao1-VPN", "Free-Accelerator---VPN"),
("feiniaovpn", "Node-Airport-VPN"),
("mikealmeida1721", "SSEE_UNIFICADO"),
("miladtahanian", "Config-Collector"),
("naivon85-source", "VPN"),
("trxd", "xray"),
("Argh73", "VpnConfigCollector"),
("Bd-Mutant7", "SSRF_Vulnerable_Lab"),
("Damaonly", "android-worker"),
("askalf", "dario"),
("dequar", "deqwl"),
("faeton", "ip.unt1.com"),
("feiniao1-VPN", "Airport-node-VPN"),
("feiniaovpn", "Free-Airport---VPN"),
("jtmdrums", "ssg-brassandbonect-deploy"),
("miladtahanian", "V2RayScrapeByCountry"),
("qindinp", "keypool"),
("tetratorus", "llm-proxy"),
("wenxig", "dongtai-sub"),
("VPJayasinghe", "Proxymaze1"),
("anatolykoptev", "oxpulse-partner-edge"),
("dorrin-sot", "V2RAY_CONFIGS_POOL-Processor"),
("dpsserver", "VPNCONFIG"),
("eltaigon", "SSH_Honeypot_Project_Pshitt"),
("juanjian7", "majesticVPN"),
("pog7x", "vpn-configs"),
("subscribey48-code", "my-vpn-mirror"),
("tglaoshiji", "nodeshare"),
("thomaswetzler", "vLLM-Sleep-Proxy"),
("wyattowalsh", "proxywhirl"),
("FL-Penly", "proxy-gate"),
("Oliveira3d", "free-ip-stresser-booter"),
("Sean-Vibes", "NYSvibes_news_SS"),
("XIXV2RAY", "XIX-v2ray"),
("XigmaDev", "proxy"),
("aniyan-chekkan", "Proxy-Grabber-v2.4.5"),
("coolMetal179", "OpenSS"),
("fdciabdul", "Vpngate-Scraper-API"),
("hugosoons-bot", "rijnsburgje-proxy"),
("kopyie", "v2ray-scanner"),
("openlay", "openlay-vpn-release"),
("pruje", "ssh-notify"),
("qwetq601-cell", "sssp"),
("sengshinlee", "hosts"),
("stvlynn", "KumoApp"),
("xq1337", "proxy-list1337"),
("yonghengdiao", "Merge-bot-Gui"),
("AvhiMaz", "ss"),
("addadi", "aws-vpn-saml"),
("almahmudkhalif", "telnet-vs-ssh-network-security-lab"),
("danteu", "wahlrecht-cal"),
("darklord-end", "-Graphene-VPN"),
("feiniaovpn", "Free-VPN"),
("feiniaovpn", "Game-Accelerator---VPN"),
("kringemega", "VlessParser"),
("mizmazegt1-design", "auto-vpngate-configs"),
("mritunjay499", "effect-cluster-via-sst"),
("nyeinkokoaung404", "V2ray-Configs"),
("scriptzteam", "IVPNWatch"),
("shriganeshchoudhari", "SSO-app"),
("Hamedzah", "vpn_config"),
("Therealwh", "MTPproxyLIST"),
("TranquilouhXD", "ea-Surface-Temperature-SST-Analysis-for-Climate-Studies"),
("YG-Blue", "v2ray-subscription"),
("barry-far", "V2ray-Config"),
("eliudyy1", "smarthr-ui"),
("jathurT", "ProxyMaze-Phase1"),
("llollo6613-art", "hostex-proxy"),
("mariasaragih", "secure-mail-server-docs"),
("prima32", "warp-config-generator-vercel"),
("tomasaap", "python-ai-agent-frameworks-demos"),
("trxd", "v2ray"),
("wisebobo", "clashNodes"),
("Argh94", "V2RayAutoConfig"),
("Justinsobased", "rem-community"),
("MAHDI-143", "proxy-checker"),
("RKPchannel", "RKP_bypass_configs"),
("RayanAhmadKhan", "PRISM"),
("proxygenerator1", "ProxyGenerator"),
("qist", "xray-ui"),
("yarikkyzym", "blas-base-wasm-sswap"),
("AirLinkVPN1", "AirLinkVPN"),
("CELIO404", "print-markdown-so-easy"),
("CloudTool", "proxy_share"),
("FIRESTRYK", "chatgpt-website.github.io"),
("Firmfox", "Proxify"),
("MohsenReyhani", "vless-subscriptions"),
("SimoneErrigo", "Janus"),
("addadi", "aws-vpn-scripts"),
("bytedecode", "bytesflows"),
("feiniaovpn", "Shared-VPN"),
("matheust4455-glitch", "roblox-proxy"),
("militarandroid", "cybersecurity_hack"),
("monosans", "proxy-list"),
("noob-master-cell", "Gatekeeper"),
("rrmmxxuu", "Custom-Clash-Sub-Convert-Config"),
("scriptzteam", "PrivateInternetAccessWatch"),
("REVERSEDCD", "jobspy-api"),
("globlord", "AIstudioProxyAPI"),
("vilage777", "my-vpn-su"),
("wildoaksapothecaryadmin", "squarespace-api-proxy"),
("Abby-1019", "Ssy"),
("Arama120517", "scoop-proxy"),
("DustinWin", "dustinwin.github.io"),
("cxddgtb", "dljdsjq"),
("ignMaro", "new"),
("musiermoore", "oksana-vpn-bot"),
("trxd", "shadowsocks-rust"),
("v2fly", "domain-list-community"),
("Engieeeboiz", "Fedora_OS"),
("Mugundhn88", "UBUNTU-SERVER_OS"),
("PuddinCat", "BestClash"),
("TraceDesigns", "MegaETH-Faucet"),
("Tsprnay", "Proxy-lists"),
("atulranjanz", "Swatted-Webhook-Spammer"),
("epicentr", "aerodrome-ical-proxy"),
("nasnet-community", "nasnet-panel"),
("peedy2495", "ssh-screen-curfew"),
("unh4cked", "v2rayshop"),
("Cwen233666", "ssd_study"),
("Denchic-2009", "xray-checked-configs"),
("Emmanuel66h", "Xray-core"),
("Roop81", "Interlink-Multi-Bot"),
("SkitterDsg", "ThatsAppMQTTDebugger"),
("aldebaran1805", "EtchDNS"),
("c-jayden", "resip"),
("davidbro06", "Football-proxy"),
("dmeshechkov", "vpn-subscriptions"),
("imagepit", "multi-ssg-sites"),
("krishjaat995", "SMM-Panel-Bulk-Action-Bot"),
("ksenkovsolo", "HardVPN-bypass-WhiteLists-"),
("qozx", "cursor-grpc"),
("riconcayy123", "mexc-private-api"),
("ryryss2-dev", "vpn-iperf-monitor"),
("xElKaNoNx", "ProxyContractImplementation"),
("zhangjinghencongming", "DisasterInsightAI"),
("Abby-1019", "SSY-G1"),
("DAVIGNA", "kilo"),
("Devcore321", "wg-easy"),
("SaloniSS", "SaloniSS"),
("Zover1337", "vless-free-whtielist"),
("kaitranntt", "ccs"),
("tvmbra", "Jetspeedvpn"),
("wangyingbo", "v2rayse_sub"),
("Haidzai", "claude-code-proxy"),
("Tofu1304", "nextjs-sst-starter"),
("ZeroAlloc-Net", "ZeroAlloc.Cache"),
("conoro", "reddit-rss-proxy"),
("libnyanpasu", "clash-nyanpasu"),
("msgithub1", "localflare"),
("onl35461-debug", "Accelerator-node-ladder---VPN"),
("zenjan1", "sshs"),
("EDDY7688", "openvpn-over-icmp"),
("Prince8382", "WanderLust"),
("Redaghafir", "sslcheck"),
("Sibusiso6", "proxy-list"),
("VestobVeyn", "Proxy-HTTP-SOCKS-Get-Pool"),
("ZintbbKos", "Youtube-Like-Comment-Subs-View"),
("aaradhyashingru1130", "Face-Recognition-Based-Attendence-System"),
("captianzo", "School-Management"),
("child9527", "clash-latest"),
("luke-03-11", "jvm-pybind"),
("modrinthmodification-create", "ownedvpn"),
("nandev04", "EasyList"),
("125jkop", "SSD_BABP"),
("Dmitriy190424", "instruction"),
("SSACLAB", "SSAC_FRONTEND"),
("Surfboardv2ray", "test-psi"),
("Thatguysnothim", "react-nextjs-ssr-onerror-img-issue-fix"),
("Unfix2310", "ssip"),
("VOID-Anonymity", "V.O.I.D-VPN_Bypass"),
("chaitanya-327", "ai-goofish"),
("hidougaming", "vpn-server-manager"),
("lishi0105", "frp-automic"),
("liulilittle", "ucp"),
("qolbudr", "proxy-checker"),
("raghutiwari554-source", "rarestudy-proxy"),
("shubhamshendre", "Free-Proxies"),
("sudhans3", "amp-server"),
("swileran", "v2ray-config-collector"),
("zxf725106", "proxy-pool-chou"),
("AxLeRage10", "noteapp"),
("Garmode3073", "zapret-docker"),
("OnePointOnly", "helios-testnet-network"),
("SkillSnap-Learning", "ss3"),
("ZEPO228", "Vortex-vpn"),
("alif123458833", "app-ss"),
("artproxz", "telegram-proxy-redirect"),
("gauravlamba78", "FreeChat"),
("jkhdjkhd", "Cloudflare-Accel"),
("ngthdong", "vpn"),
("paperbasee", "postgres-ssl"),
("robintw", "sse_powercuts"),
("tentangsaya78", "ssdc-theme"),
("tonykslee", "ClashCookies"),
("wardnet", "wardnet"),
("worldmarketing02-design", "proxy-master-list"),
("ShiroRikka", "Clash.Meta-Script"),
("eiler2005", "ghostroute"),
("iplocate", "free-proxy-list"),
("lewis617", "clash-cfg"),
("rzielenski", "clash-of-clubs"),
("status-vpn", "status-vpn.github.io"),
("ydsgangge-ux", "daidi"),
("Atoshison", "vpn"),
("Cram10", "frmz"),
("Idkwhattona", "OpenAI-Compatible-API-Proxy-for-Z"),
("MCPMeter", "mcpmeter-proxy"),
("Saka2e", "AzadiHub"),
("Stipool", "npvtuijian"),
("Zhao242", "ShanYangProxyApps"),
("alfianapriansyadp", "logging-monitoring"),
("ankitgupta2107", "Reverse-Proxy-Soruce-Code"),
("feiniao1-VPN", "Node-based-VPN"),
("fun90", "AirOpsCat"),
("hcd233", "aris-proxy-api"),
("igareck", "vpn-configs-for-russia"),
("luanbonito02", "windows"),
("ludivor", "ssiptv"),
("lyqnihao", "proxy"),
("northwood-labs", "aws-sso-manager"),
("qopq1366", "VlessConfig"),
("sdfnh", "fanqiang"),
("sydasif", "litellm-proxy"),
("tomicechen", "GUI-Projects"),
("trio666", "proxy-checker"),
("ttblstr", "sslv-telegram-monitor"),
("yourssu", "ssufid-sites"),
("456564", "yolov8-rk3588"),
("Epodonios", "v2ray-configs"),
("GilvanS", "historico-clash-roayle"),
("GunnerInflate", "SSE-Pandora-Behaviour-Engine-Plus"),
("Ilyacom4ik", "free-v2ray-2026"),
("Marek93739", "mega-ssh-udp"),
("MeALiYeYe", "ProxyConfigFiles"),
("Youth787", "SSAFY_Algorithm_Study"),
("abhayforsure", "ai-wechat-api"),
("daffwt221", "homelab-raspberry-network-stack"),
("frozensmile94", "vless-sub"),
("kudryash0vv", "kudryash0vv.YKTFLOW"),
("roadnich", "ru-v2ray-sub"),
("scsmods-js", "nginx-ssl-auto"),
("7p7268t25c-lab", "my-first-program"),
("Apisit2536", "vpn-telegram-bot"),
("Borges005", "ai-proxy"),
("HikerX", "yunfan_subscribe"),
("WP2-Danikusuma", "AgentX"),
("antonme", "ipnames"),
("hackerhoon", "toon-proxy"),
("peng-123258", "python-argo"),
("prathvikothari", "HLS-Proxy-Worker"),
("sangosbanikz", "proxy-pool"),
("strikersam", "local-llm-server"),
("10yanhon", "clash-sub"),
("Au1rxx", "free-vpn-subscriptions"),
("IvanLi-CN", "proxy-broker"),
("NANDHARAJ5", "ai-access"),
("NiceVPN123", "NiceVPN"),
("RealDefenderSqueeze", "Hamachi-Pro-Crack-Windows-2026"),
("Sanji-code-10", "Klokai-mega-DX"),
("Spotas", "Ai-rewrite"),
("TOMIBABY", "freevpn"),
("Wind7077", "yml-vless"),
("andigwandi", "free-proxy"),
("cgy530627", "Proton-VPN"),
("forchatgptmeowmeow-star", "my-vpn-keys"),
("iwh3n", "tg-proxy"),
("peasoft", "NoMoreWalls"),
("rostamimohammadamin8-dot", "Starlink-V2ray-Scanner"),
("zhangbinhui", "claude-max-proxy"),
("Centaurbenpulse", "Mullvad-VPN-Premium-Windows-2026"),
("JuanAirala", "freedom"),
("RollingGo-AI", "Rollinggo-hotel-price-monitor-skill"),
("Samuray49", "awesome-ai-agent-testing"),
("WLget", "V2Ray_configs_64"),
("itsyebekhe", "PSG"),
("kasesm", "Free-Config"),
("mauricegift", "free-proxies"),
("ono-kojiro", "ssl_samples"),
("subaru12109", "ssh-ai-chat"),
("ALIILAPRO", "Proxy"),
("CubeCashierCleanse", "NordVPN-License-2026"),
("Davoyan", "xray-routing"),
("DisplayAdvance", "UrbanVPN-New-Crack-2026"),
("LoneKingCode", "panbox"),
("MK-aii", "jetbrains-ai-proxy"),
("ab6357020", "Free"),
("akapzg", "Unver"),
("ali13788731", "vpn"),
("amirkma", "proxykma"),
("avbak", "symmetrical-spork"),
("bq2015", "FreeProxies"),
("canadice", "ssl-index"),
("ebrasha", "cidr-ip-ranges-by-country"),
("hansenlandun-prog", "freeproxy-node-sub"),
("ilya-120", "vpn-tester"),
("muks999", "Clash-Vless-convert"),
("plsn1337", "white-vless"),
("singgel", "bgw"),
("socks5-proxy", "socks5-proxy.github.io"),
("solovyov-jenya2004", "all_subs"),
("toml66l", "fanqiang"),
("3aboody", "vscode-extension-downloader"),
("AlterSolutions", "tornodes_lists"),
("ErcinDedeoglu", "proxies"),
("George3d", "OpenAI-Compatible-API-Proxy-for-Z"),
("LUXE-STORE", "cfnew"),
("Sarthaknagne17", "laravel-ai-mapper"),
("samidii", "ACYBER-Wayback-Machine-Downloader"),
("tomaasz", "litellm-free-models-proxy"),
("y-Adrian", "db-proxy"),
("Casper-Tech-ke", "casper-free-proxies"),
("MaYBeNTs", "VoidGate"),
("REIJI007", "AdBlock_Rule_For_Clash"),
("Siva1327", "CF-Workers-BPSUB"),
("muhammadmehdi1656", "ldap_bofs"),
("AfnanLakhair", "notionSSH"),
("Alice8Flandre", "k2think2api"),
("Bes-js", "public-proxy-list"),
("Hill-1024", "simpleUI"),
("KaringX", "clashmi"),
("Leavend", "SSO_Kali"),
("Mannitou", "ChameleonUltraHACS"),
("alphaa1111", "proxyscraper"),
("coralfletchercutters", "intego-mac-interne-pt70"),
("maycon", "tor-nodes-list"),
("mmpx12", "proxy-list"),
("parserpp", "ip_ports"),
("sandrasocial", "sselfie-9g"),
("andersonssilva2", "Task-Tracker-API"),
("fldyown", "mojie"),
("soapbucket", "sbproxy"),
("theSolution12", "ssh-deply-demo"),
("fldyown", "clash"),
("mivindhani", "Discord-Passwordless-Token-Changer"),
("neoiwr", "WS-Proxy-Server"),
("raphaelgoetter", "clash"),
("vsvavan2", "vpn-config-rkn"),
("xiangyuw1", "vless-reality-conf"),
("xtrcode", "ovpn.com-ip-grabber"),
("Behrad122", "findface-bridge"),
("Delta-Kronecker", "Downloader"),
("ShatakVPN", "ConfigForge-V2Ray"),
("Skillter", "ProxyGather"),
("danmaifu", "mianfeijiedian"),
("mohadnor", "Auto-deploy-sap-and-keepalive"),
("nicatnesibli", "pingoo"),
("sshuoguo", "sshuoguo.github.io"),
("therealaleph", "Iran-configs"),
("xiaoniucode", "etp"),
("Taxi88", "ant-and-apples"),
("ganev11", "SSTrader"),
("marcelz0", "uTPro"),
("onlymeoneme", "v2ray_subs"),
("r5r3", "s32p-proxy"),
("suiyuebaobao", "raypilot-xray-panel"),
("yoshikanguyen", "BTVN_SS12"),
("AlchemyLink", "raven-dashboard"),
("Kotpilota", "ssu-138"),
("Ohayo18", "NekoBoxForAndroid"),
("TeALO36", "ProxyInHA"),
("XiaozhiChenshi", "A-ssemball"),
("amberpepper", "ProxyWeave"),
("eyaorganization", "To-do-App"),
("harismy", "BotVPN"),
("jeongwoo1020", "SST-electricity_Risk_Management"),
("masx200", "proxy_system_research_report"),
("mikuji98", "BiG-Hacking"),
("moonfruit", "sing-rules"),
("Kwiatek7", "i8Relay"),
("MRebati", "vpn-master"),
("MustafaBaqer", "VestraNet-Nodes"),
("bo2so", "karoo"),
("mzwaterski", "calendar-subscribe-feed"),
("yonheeee", "SSAFYHome"),
("Manyan06", "HoneyShield-Intelligent-SSH-Honeypot-IMS"),
("SoliSpirit", "v2ray-configs"),
("chnnic", "SSH-Hardening"),
("fyvri", "fresh-proxy-list"),
("gurudeb123", "ai-sdk-chrome-extension"),
("kenzok8", "openwrt-clashoo"),
("stormsia", "proxy-list"),
("watchttvv", "free-proxy-list"),
("yuanjv", "proxy-urls"),
("0xAbolfazl", "PyroConfig"),
("Bob1817", "mimo-bridge-desktop"),
("Filterrr", "FlClash"),
("SantiSouto", "CVV-checkers"),
("Tharindu-Nimsara", "proxymaze-cyphersentinels"),
("VP01596", "vless-top15"),
("devojony", "ClashSub"),
("jeremypadrinox", "go-whatsapp-worker-redis-ssedashboard"),
("licheng527", "Free-servers"),
("logoministerroad", "Windscribe-VPN-2026-ba"),
("nandapoxy", "proxy-server"),
("navodj", "proxy-maze"),
("proxifly", "free-proxy-list"),
("pwhkk", "pyxy"),
("shadowsocks", "ech-tls-tunnel"),
("vungocbaobao", "v2ray-config-finder-tg-bot"),
("Abhhinav02", "golang-advanced"),
("Innerplonote", "Mullvad-VPN-Premium-2026"),
("LuisBraLo", "PPHAS_SIS_SSR"),
("MdSadiqMd", "TraceZero"),
("Telegram-FZ-LLC", "Telegram-Proxy"),
("brahimelgarouaoui", "RL-Name-Changer"),
("charefabdelrazak", "nonstop"),
("giantswarm", "muster"),
("heinhtetzaw346", "sshu"),
("liqiangsky", "clash-proxies"),
("rankedcs", "Myvlesses"),
("ulgerf16", "COSMICA-Proxy"),
("uwilleer", "vitok"),
("Aditya-Konda", "prox"),
("Ferchoxx23", "aws-sso-workstations"),
("TechSpiritSS", "TechSpiritSS"),
("YaltaVPN", "YaltaVPNConfigs"),
("cloxkzii", "worker"),
("goncalorosa96", "codemode-mcp"),
("jshir700", "subconverter-MetaCubeX"),
("lanzm", "MetaFetch"),
("s-theo", "vpnnav.net"),
("vrzdrb", "unified-mihomo-rulesets"),
("ArtemAfonasyev", "hentai-goida-subscription"),
("AyandaMajola01", "muon"),
("Dwarka-soni-9630", "PFS"),
("Maskkost93", "kizyak-vpn-4.0"),
("Metric265", "proxya"),
("MrMarble", "proxy-list"),
("Potterli20", "hosts"),
("Zephyr236", "proxy_collector"),
("Zero-Bug-Freinds", "ai-api-usage-monitor"),
("akshaymishra78600", "proxy-gem-noload"),
("alireza-rezaee", "tor-nodes"),
("carloandremoreyra", "XX"),
("ebrasha", "free-v2ray-public-list"),
("esanacore", "SSH_DeviceManager"),
("genyleap", "GenyConnect"),
("hyjack-00", "-clash_subscription_public"),
("mehdihoore", "TestVpnGateServers"),
("mheidari98", ".proxy"),
("sacreations", "Proxy-Monitor"),
("tepo18", "online-sshmax98"),
("yoiambugger", "auto-vless-config"),
("Alvin9999-newpac", "fanqiang"),
("AndLaynes", "clash-dashboard-v2"),
("HasithaErandika", "proxy-maze"),
("MrAbolfazlNorouzi", "iran-configs"),
("SSMG4", "SSR"),
("Stefen-io", "n9r-dockerized-deployment"),
("Veid09", "vless-list"),
("adsikramlink", "proxy"),
("ajaysharma1258", "sshmx"),
("ali13788731", "proxy"),
("amantestingforbugs", "sslscannerv4"),
("fugary", "simple-boot-mock-server"),
("gsamuele78", "R-studioConf"),
("kanam150901", "namm.901"),
("kort0881", "telegram-proxy-collector"),
("notfaj", "ester"),
("rico-cell", "clash-proxy-sub"),
("serdarseseogullari", "fpl-reminder"),
("snakem982", "proxypool"),
("vmheaven", "VMHeaven.io-Free-Proxy-List"),
("xyfqzy", "free-nodes"),
("AlexanderAvks", "transformer-xray"),
("AlxVoropaev", "informer_bot"),
("Estarking57", "Scripts"),
("GUDU01", "Avast-SecureLine-VPN-Working"),
("HamoonSoleimani", "Pr0xySh4rk"),
("OfficeDev", "Office-Addin-Taskpane-SSO"),
("UVA-Course-Explorer", "course-data"),
("YourAverageSimbaFan", "node-boot-test-framework"),
("avion121", "V2RayDaily"),
("bpanco", "youtube-bot-basma"),
("charlesndirutu33", "dnskip"),
("dr-andytseng", "afl-calendar-feeds"),
("feiniao1-VPN", "Wall-Climbing-Accelerator---VPN"),
("gslege", "CloudflareIP"),
("iamolivierdrabek", "whereami"),
("lhhkuki", "deepseek-proxy-manager"),
("mohammmdmdmkdmewof", "v2rayConfigsForYou"),
("muhnawaz", "Web_Restaurant_frontend"),
("shervinofpersia", "VPN-client-last-releases"),
("ssbanerje", "ssbanerje"),
("triposat", "amazon-price-monitor"),
("Amiin-key", "ssm2027"),
("Epodonios", "bulk-xray-v2ray-vless-vmess-...-configs"),
("LancelotRar", "free-subs"),
("ZORfree", "proxy_pool_wasmer"),
("armanridho", "ProxyJson-toYaml"),
("badhuamao", "my-v2ray-checker"),
("feiniaovpn", "feiniao-VPN"),
("gibson25D", "POXY-CLI"),
("h4rm0n1c", "quantzhai"),
("kuoizong881681", "aether-vpn"),
("mmalmi", "nostr-vpn"),
("ooocode", "CoreProxyServer"),
("sherlockhomes-max", "youtube-viewer-bot"),
("sholdee", "caddy-proxy-cloudflare"),
("terraform-ibm-modules", "terraform-ibm-client-to-site-vpn"),
("video05", "vpn-qr"),
("Baraninathan", "AirBridge"),
("Cepreu54", "vless-clean"),
("Darkelmoov", "goida-vpn-configs"),
("Eibwen", "podcast-proxy"),
("F0rc3Run", "F0rc3Run"),
("NiREvil", "vless"),
("Rusl2023", "vpn-alive-check"),
("SkzfXrolo", "AsperSS"),
("Tom-Riddle09", "proxy_server"),
("V2RAYCONFIGSPOOL", "V2RAY_SUB"),
("balookrd", "outline-ws-rust"),
("hackstergirlrocks", "devlies"),
("judawu", "nsx"),
("larsontrey720", "gemma-retry-proxy"),
("ssaaaammm", "ssaaaammm"),
("vahid162", "proxy-address-mining"),
("waiswadaniel24", "ssewasswa-api"),
("xiaoji235", "airport-free"),
("FoolVPN-ID", "Nautica"),
("MhdiTaheri", "V2rayCollector"),
("Mr-Meshky", "vify"),
("Szan203", "panda-vpn-pro"),
("TheSpeedX", "PROXY-List"),
("VampXDH", "MyProxy"),
("Vepashka94", "vpngate_web"),
("Vinaykumar023", "pub_wake_lxc"),
("Watfaq", "clash-rs"),
("cfsfguyet787856", "Minecraft-Server-Finder"),
("claudianus", "clco-helper"),
("claudianus", "clco-proxy"),
("danielfree19", "proxydock"),
("g-hunter-g", "awesome-vpn"),
("halc8312", "SStory"),
("muskd79", "proxy-manager-telebot"),
("Abalayan27", "v2ray"),
("BhaveshGavande23", "calculator"),
("Dimasssss", "free_telemt_servers"),
("Icy-Senpal", "bypass-all"),
("IngeniousCrab", "tornado-core"),
("Swift-tunnel", "swifttunnel-app"),
("TakgoAgency", "scrape-data-from-instagram"),
("Treetippakae", "instagram-data-scraper"),
("V2RAYCONFIGSPOOL", "SLIPNET_SUB"),
("V2RAYCONFIGSPOOL", "TELEGRAM_PROXY_SUB"),
("Wyr-Hub", "WyrVPN-Lite"),
("ansh826-alt", "ant-vpn"),
("ayshwaryee", "ssb-website-main"),
("caryyu0306", "proxy-list"),
("chmoralla-code", "cynework-ai-proxy"),
("ebrasha", "abdal-proxy-hub"),
("gautam-pahlawat", "DOD"),
("hello-world-1989", "cn-news"),
("igikukik59", "Proxy-Google-Checker"),
("jester4411", "amnezia-vpn"),
("lexariley", "v2ray-test"),
("llaravell", "clash-rules"),
("lyc-aon", "codex-session-manager"),
("mc-marcocheng", "site-to-rss"),
("mdabushayem62", "plex-playlists"),
("parsamrrelax", "auto-warp-config"),
("ssg-create", "ssg-dashboard-data"),
("v0id9", "vpn-configs"),
("Access-At", "proxy-scraping"),
("Danialsamadi", "v2go"),
("KRYYYYYYYYYYYYYYYYYYY", "xray-uuid-checker"),
("MariusDouahoudeh", "patient-registration-system"),
("MrViSiOn", "ssha"),
("Pxys-io", "DailyProxyList"),
("Pxys-io", "proxylistdaily"),
("Surfboardv2ray", "TGParse"),
("TheFlipper-spec", "VPNMY"),
("ahmafadli73-design", "ssukaltim"),
("alihusains", "sstp-vpn"),
("aloramiaa", "Vpngate"),
("arasongiyvymjlndejkkhcbay", "evm-storage-layout-analyzer"),
("databay-labs", "free-proxy-list"),
("elanski", "proxy-preflight"),
("expressalaki", "ExpressVPN"),
("fastasfuck-net", "VPN-List"),
("gamecentre7x2", "Api-Proxy"),
("grobomo", "llm-token-proxy"),
("ishalumi", "proxy-node-collector"),
("jqmzfj", "wg-clash-admin"),
("kokulanK", "ProxyMaze-26"),
("mahdisandughdaran-sys", "-My-SS2022-Collector"),
("marshall888666", "free_clash_subscribe"),
("sckang76", "SSU_CODE"),
("sharkfan824", "vscode-remote-vibe-coding"),
("themiralay", "Proxy-List-World"),
("tokenpak", "tokenpak"),
("vanodevium", "node-framework-stars"),
("10ium", "multi-proxy-config-fetcher"),
("A-K-6", "v2ray_scrapper_repo"),
("AutumnVN", "ssleaderboard"),
("ENTERPILOT", "GoModel"),
("Jadelinda81", "export-list-of-instagram-followers"),
("Kotlas23412", "proxy-checker"),
("Obedbrako", "in-memory-pubsub"),
("OfficeDev", "Office-Addin-TaskPane-SSO-JS"),
("RaineMtF", "v2rayse"),
("Reid-Vin", "OpenClash_Custom_Rules_for_ios_rule_script"),
("TheHotCodes", "HotVpn"),
("TwilgateLabs", "inhive-rules"),
("ZhurinDanil", "clash-sub"),
("aarnold-livefront", "IoTSpy"),
("akbarali123A", "proxy_scraper"),
("claude89757", "free_https_proxies"),
("dhanasekardr", "traffic-ui-open-source"),
("gfpcom", "free-proxy-list"),
("inimulky", "doh-proxy-worker"),
("jackrun123", "v2ray_configs"),
("jasgues", "nodejs-proxy-server2"),
("krishn11x", "ACL-Next"),
("kuciybes", "vpn-clash-rules"),
("nicky8258", "content_replace"),
("partnermbp", "RUS_VLESS"),
("sinavm", "SVM"),
("zloi-user", "hideip.me"),
("AhmedAj22", "best-backlink-analyzer"),
("Aman9690", "clash-config-editor"),
("Granulationcard598", "backlink-analyzer"),
("HankNovic", "ProxyClean"),
("Harshitshukla2003", "SSE-Server"),
("JHC000abc", "ProxyParseForSing-box"),
("Leonhard333", "foxcloud"),
("NishaMax", "ProxyMaze"),
("RioMMO", "ProxyFree"),
("Yo0l0", "ssss"),
("adop1344-bot", "LetoVPN_free"),
("aleatorio600", "backlink-tracking-software"),
("devitsentulcity", "ahtapot"),
("dpangestuw", "Free-Proxy"),
("maxstev72", "Zero-Trust-Auth-Service"),
("sweengineeringlabs", "edge"),
("yiohoohoo2026", "format-proxy"),
("Andrejewild", "myvpn"),
("Jacky-Yeeo", "Shadowroclet-Rules"),
("SAILFISH-PTE-LTD", "MetroVPN-Windows"),
("Saravanars07", "MplsL3Vpn"),
("ShadowException", "VPN"),
("Yassir8888", "trading-bot-proxy"),
("mikealmeida1721", "SSEE"),
("testbebranin-prog", "v2node"),
("Infisical", "agent-vault"),
("LalatinaHub", "Mineral"),
("adaskitkleilrociftey", "solidity-proxy-upgrade"),
("alialieghar-b", "proxy"),
("iboxz", "free-v2ray-collector"),
("mhzarchini", "clash-royale-emote-detector"),
("purpletigerlzhlcgg", "ethereum-event-tracker"),
("r4sso", "r4sso"),
("ramram33", "Ram-v2ray-configs"),
("rezapix-cmd", "vless-checker-55"),
("topsuperv", "ss"),
("SenumiCosta", "proxymaze26"),
("andreabranca", "Telegram-Downloader-Tools"),
("miladtahanian", "V2RayCFGTesterPro")
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
