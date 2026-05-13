<!-- README.md (نسخه فارسی) -->
<div align="center" style="margin-bottom: 20px;">
  <a href="https://github.com/MohammadBahemmat/V2ray-Collector/blob/main/README.EN.md">
    <img src="https://img.shields.io/badge/Read_in-English-009688?style=for-the-badge&logo=readthedocs" alt="Read in English">
  </a>
</div>

<body>
<div class="container">

<!-- ====== ردیف نشان‌های اطلاعاتی پروژه ====== -->
<div align="center" style="margin-bottom: 15px;">

<!-- Python Version -->
<img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">

<!-- License -->
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge&logo=open-source-initiative" alt="License">

<!-- Requirements -->
<a href="https://github.com/MohammadBahemmat/V2ray-Collector/blob/main/config/requirements.txt">
    <img src="https://img.shields.io/badge/Requirements-txt-critical?style=for-the-badge&logo=pypi" alt="Requirements">
</a>

<!-- Platform -->
<img src="https://img.shields.io/badge/Platform-GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions" alt="GitHub Actions">

</div>

<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<div class="container">

<img src="https://github.com/MohammadBahemmat/V2ray-Collector/actions/workflows/collector.yml/badge.svg" alt="Collector Status">



<h1>🚀 جمع‌آوری‌کننده کانفیگ V2Ray — اشتراک پروکسی رایگان و خودکار</h1>

<p>
<strong>یک گردآورنده‌ی هوشمند، بدون وابستگی و فوق‌العاده بهینه برای جمع‌آوری خودکار کانفیگ‌های V2Ray و پروتکل‌های مشابه.</strong><br>
این پروژه با بهره‌گیری هم‌زمان از <strong>مخازن گیتهاب</strong> و <strong>کانال‌های عمومی تلگرام</strong> (بدون نیاز به API، ربات یا شماره تلفن)، قدرتمندترین منبع کانفیگ‌های رایگان را فراهم می‌کند. تمام فرآیندها به‌صورت <strong>کاملاً خودکار</strong> روی GitHub Actions اجرا می‌شوند.
</p>
<p>
چیزی که این پروژه را از سایر جمع‌آوری‌کننده‌ها متمایز می‌کند، <strong>معماری یکپارچه، مدیریت هوشمند Rate Limit با توکن‌های دوگانه، و خروجی‌های تفکیک‌شده و همیشه تازه</strong> است.
</p>


<hr>

<!-- ویژگی‌های متمایز -->


<h2>✨ ویژگی‌های متمایز</h2>
<table>
<thead>
<tr><th>ویژگی</th><th>توضیح</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>🎯 جمع‌آوری دوگانه (گیتهاب + تلگرام)</strong></td>
    <td>اسکن هوشمند مخازن گیتهاب <strong>و</strong> واکشی کانال‌های عمومی تلگرام (<code>t.me/s</code>) بدون هیچ وابستگی به API، ربات یا شماره تلفن. هر دو منبع در یک دیتابیس مشترک با هم ادغام می‌شوند.</td>
</tr>
<tr>
    <td><strong>🗂️ خروجی‌های تفکیک‌شده</strong></td>
    <td>علاوه بر فایل جامع <code>all_servers.txt</code>، کانفیگ‌ها به‌طور خودکار بر اساس پروتکل (<code>vmess_servers.txt</code>، <code>vless_servers.txt</code> و...) دسته‌بندی و ذخیره می‌شوند.</td>
</tr>
<tr>
    <td><strong>💾 ذخیره‌سازی هوشمند و بدون تکرار</strong></td>
    <td>در هر اجرا، فقط کانفیگ‌های جدید به فایل اضافه می‌شوند. هیچ کانفیگ تکراری در خروجی وجود ندارد و رشد بی‌رویه فایل‌ها کاملاً کنترل می‌شود.</td>
</tr>
<tr>
    <td><strong>🪙 مدیریت Rate Limit با توکن‌های دوگانه</strong></td>
    <td>با استفاده از یک PAT کلاسیک و یک GitHub App، سقف درخواست‌های Core به صورت چرخشی مدیریت می‌شود و اسکریپت هرگز با خطای ۴۰۳ متوقف نمی‌شود.</td>
</tr>
<tr>
    <td><strong>⏱️ بازه‌ی زمانی ۱۵ دقیقه‌ای</strong></td>
    <td>فقط مخازنی که در ۱۵ دقیقه‌ی گذشته push خورده‌اند اسکن می‌شوند (قابل تنظیم با <code>MAX_AGE_HOURS</code>). از تلگرام نیز جدیدترین پست‌ها دریافت می‌شود.</td>
</tr>
<tr>
    <td><strong>🌿 Branch Discovery با حافظه‌ی دائمی</strong></td>
    <td>شاخه‌های جدید کشف‌شده در فایل <code>discovered_branches.json</code> ذخیره می‌شوند و در اجراهای بعدی مستقیماً بررسی می‌شوند.</td>
</tr>
<tr>
    <td><strong>🧩 Checkpoint (ادامه پس از هر نوع توقف)</strong></td>
    <td>حتی اگر برق قطع شود یا Rate Limit تمام شود، اجرای بعدی دقیقاً از همان نقطه ادامه می‌یابد.</td>
</tr>
<tr>
    <td><strong>🗃️ پایگاه داده‌ی SQLite</strong></td>
    <td>همه‌ی کانفیگ‌های یکتا در یک دیتابیس محلی (<code>collector.db</code>) ذخیره می‌شوند و از پردازش تکراری URLها جلوگیری می‌شود.</td>
</tr>
<tr>
    <td><strong>🔒 عدم وابستگی به تلگرام (API)</strong></td>
    <td>برخلاف ۹۰٪ پروژه‌های مشابه، این کلکتور برای دریافت کانفیگ از تلگرام به <strong>هیچ‌گونه API، ربات یا شماره تلفنی</strong> نیاز ندارد و از نسخه‌ی تحت وب (<code>t.me/s</code>) استفاده می‌کند.</td>
</tr>
<tr>
    <td><strong>🚀 اجرای کاملاً خودکار و رایگان</strong></td>
    <td>کل سیستم با یک فایل Workflow روی GitHub Actions رایگان اجرا می‌شود و نیازی به هیچ سرور خارجی ندارد.</td>
</tr>
</tbody>
</table>

<hr>

<!-- نیازمندی‌ها -->


<h2>📦 پیش‌نیازها (Requirements)</h2>
<ul>
    <li><strong>Git</strong> نصب شده روی سیستم (برای clone کردن مخزن)</li>
    <li>Python 3.10 یا بالاتر</li>
    <li>
        کتابخانه‌های موجود در <code>requirements.txt</code>:
        <pre class="ltr-block">pip install -r config/requirements.txt</pre>
    </li>
    <li>
        یکی از موارد زیر برای احراز هویت گیتهاب:
        <ul>
            <li>یک <strong>Personal Access Token (classic)</strong> با دسترسی <code>repo</code> و <code>workflow</code> (برای اسکن گیتهاب)، <strong>یا</strong></li>
            <li>یک <strong>GitHub App</strong> نصب‌شده روی مخزن (برای امنیت بالاتر)</li>
        </ul>
    </li>
</ul>

<hr>

<!-- تنظیمات -->


<h2>⚙️ تنظیمات (Configuration)</h2>
<p>تمام پارامترهای کلیدی در دیکشنری <code>CONFIG_DEFAULTS</code> در فایل <code>collector_git.py</code> قابل تنظیم هستند. مهم‌ترین آن‌ها:</p>

<table>
<thead>
<tr><th>پارامتر</th><th>مقدار پیش‌فرض</th><th>توضیح</th></tr>
</thead>
<tbody>
<tr><td><code>MAX_AGE_HOURS</code></td><td><code>0.25</code></td><td>فقط مخازنی که در ۱۵ دقیقه‌ی گذشته push داشته‌اند اسکن شوند</td></tr>
<tr><td><code>TARGET_CORE_CONSUMPTION</code></td><td><code>5000</code></td><td>حداکثر Core API مجاز (برای توقف خودکار)</td></tr>
<tr><td><code>MAX_FILE_BYTES</code></td><td><code>10 * 1024 * 1024</code></td><td>حداکثر حجم فایل قابل دانلود (۱۰ مگابایت)</td></tr>
<tr><td><code>GENERAL_CONCURRENT_REQUESTS</code></td><td><code>80</code></td><td>تعداد دانلود هم‌زمان فایل‌ها</td></tr>
<tr><td><code>MAX_RECURSION_DEPTH</code></td><td><code>0</code></td><td>عمق دنبال کردن لینک‌های اشتراک</td></tr>
<tr><td><code>CHECKPOINT_FILE</code></td><td><code>checkpoint.json</code></td><td>فایل ذخیره‌ی پیشرفت</td></tr>
<tr><td><code>DISCOVERED_BRANCHES_FILE</code></td><td><code>discovered_branches.json</code></td><td>فایل ذخیره‌ی شاخه‌های جدید</td></tr>
</tbody>
</table>

<div class="highlight">
<strong>🔐 تنظیم Secrets در گیتهاب:</strong> برای استفاده از توکن‌های دوگانه، این مقادیر را در <strong>Settings</strong> &gt; <strong>Secrets and variables</strong> &gt; <strong>Actions</strong> تعریف کنید:
<pre class="ltr-block">
GH_TOKEN              → Personal Access Token (classic)
GH_APP_ID             → App ID برنامه‌ی گیتهاب شما
GH_APP_PRIVATE_KEY    → کلید خصوصی برنامه‌ی گیتهاب
</pre>
</div>

<hr>



<h2>🧩 راه‌اندازی سریع (Quick Start)</h2>
<p>اگر می‌خواهید همین پروژه را برای خودتان کپی و اجرا کنید:</p>
<ol>
    <li>مخزن را Fork کنید (دکمه Fork در بالای صفحه گیتهاب)</li>
    <li>مخزن Fork شده را Clone کنید:
        <pre class="ltr-block">git clone https://github.com/YOUR_USERNAME/V2ray-Collector.git
cd V2ray-Collector</pre>
    </li>
    <li>نیازمندی‌های پایتون را نصب کنید:
        <pre class="ltr-block">pip install -r config/requirements.txt</pre>
    </li>
    <li>فایل <code>.env</code> را با توکن گیتهاب خود مطابق <code>config/.env.example</code> ایجاد کنید.</li>
    <li>فایل <code>channels.txt</code> را با کانال‌های تلگرام دلخواه پر کنید.</li>
    <li>یک بار اسکریپت را به صورت دستی اجرا کنید تا همه چیز تست شود:
        <pre class="ltr-block">python src/collector_git.py</pre>
    </li>
</ol>
<hr>

<!-- اجرای دستی -->


<h2>🚀 اجرای دستی</h2>
<p>برای اجرای جمع‌آورنده‌ی گیتهاب (بدون بخش تلگرام)، کافیست در ترمینال دستور زیر را اجرا کنید:</p>
<pre class="ltr-block">python src/collector_git.py</pre>
<p>برای اجرای جمع‌آورنده‌ی تلگرام به‌تنهایی:</p>
<pre class="ltr-block">python src/telegram_collector.py</pre>
<ul>
    <li><strong>اجرای اول</strong> (با دیتابیس خالی) ممکن است ۱۰ تا ۱۵ دقیقه طول بکشد.</li>
    <li><strong>اجراهای بعدی</strong> به دلیل وجود دیتابیس پر، بسیار سریع‌تر هستند.</li>
</ul>

<hr>

<!-- اجرای خودکار -->


<h2>🤖 راه‌اندازی اجرای خودکار با GitHub Actions</h2>

<h3>۱. فایل Workflow</h3>
<p>پروژه به صورت پیش‌فرض با یک فایل YAML در مسیر <code>.github/workflows/collector.yml</code> اجرا می‌شود که:
<ul>
    <li>از طریق <strong>workflow_dispatch</strong> (اجرای دستی یا زنجیره‌ای) آغاز می‌شود و پس از هر اجرا، اجرای بعدی را به طور خودکار فرا می‌خواند.</li>
    <li>ابتدا کانفیگ‌های جدید را از <strong>تلگرام</strong> دریافت می‌کند.</li>
    <li>سپس مخازن <strong>گیتهاب</strong> را اسکن می‌کند.</li>
    <li>با استفاده از <strong>توکن‌های دوگانه</strong>، فشار Rate Limit را بین دو منبع تقسیم می‌کند.</li>
    <li>در نهایت، خروجی‌ها را ادغام، تفکیک و در مخزن ذخیره می‌کند.</li>
</ul>
</p>

<h3>۲. دریافت فایل‌های خروجی</h3>
<p>پس از اولین اجرای موفق، می‌توانید از لینک‌های ابتدای همین صفحه برای دریافت فایل‌ها استفاده کنید. این فایل‌ها را می‌توان مستقیماً در کلاینت V2Ray خود (مانند v2rayN، Nekobox یا Hiddify) بارگذاری کرد.</p>

<h3>۳. افزودن کانال‌های تلگرام</h3>
<p>فایل <code>channels.txt</code> در ریشه‌ی پروژه، فهرست کانال‌های عمومی تلگرام را نگهداری می‌کند (هر خط یک شناسه، بدون <code>@</code>). برای افزودن کانال جدید، کافیست شناسه‌ی آن را در یک خط جدید اضافه کنید.</p>

<hr>

<!-- خروجی‌ها -->
<h2>📁 فایل‌های خروجی</h2>
<table>
<thead>
<tr><th>فایل</th><th>توضیح</th><th>لینک مستقیم</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>all_servers.txt</strong></td>
    <td>تمامی کانفیگ‌های یکتای جدید در هر اجرا (گیتهاب + تلگرام)</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/all_servers.txt"><img src="https://img.shields.io/badge/Download-All_Configs-blue?style=flat-square&logo=textpattern" alt="All Configs"></a></td>
</tr>
<tr>
    <td><strong>vmess_servers.txt</strong></td>
    <td>فقط کانفیگ‌های VMess</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/vmess_servers.txt"><img src="https://img.shields.io/badge/Download-VMess-EF7F1A?style=flat-square&logo=v" alt="VMess"></a></td>
</tr>
<tr>
    <td><strong>vless_servers.txt</strong></td>
    <td>فقط کانفیگ‌های VLESS</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/vless_servers.txt"><img src="https://img.shields.io/badge/Download-VLESS-00BFFF?style=flat-square&logo=v" alt="VLESS"></a></td>
</tr>
<tr>
    <td><strong>trojan_servers.txt</strong></td>
    <td>فقط کانفیگ‌های Trojan</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/trojan_servers.txt"><img src="https://img.shields.io/badge/Download-Trojan-2E8B57?style=flat-square&logo=trove" alt="Trojan"></a></td>
</tr>
<tr>
    <td><strong>hysteria_servers.txt</strong></td>
    <td>فقط کانفیگ‌های Hysteria</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/hysteria_servers.txt"><img src="https://img.shields.io/badge/Download-Hysteria-8A2BE2?style=flat-square&logo=h" alt="Hysteria"></a></td>
</tr>
<tr>
    <td><strong>hysteria2_servers.txt</strong></td>
    <td>فقط کانفیگ‌های Hysteria2</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/hysteria2_servers.txt"><img src="https://img.shields.io/badge/Download-Hysteria2-9400D3?style=flat-square&logo=h" alt="Hysteria2"></a></td>
</tr>
<tr>
    <td><strong>tuic_servers.txt</strong></td>
    <td>فقط کانفیگ‌های TUIC</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/tuic_servers.txt"><img src="https://img.shields.io/badge/Download-TUIC-FF69B4?style=flat-square&logo=t" alt="TUIC"></a></td>
</tr>
<tr>
    <td><strong>ss_servers.txt</strong></td>
    <td>فقط کانفیگ‌های Shadowsocks</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/ss_servers.txt"><img src="https://img.shields.io/badge/Download-Shadowsocks-4682B4?style=flat-square&logo=s" alt="Shadowsocks"></a></td>
</tr>
<tr>
    <td><strong>ssr_servers.txt</strong></td>
    <td>فقط کانفیگ‌های SSR</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/ssr_servers.txt"><img src="https://img.shields.io/badge/Download-SSR-5F9EA0?style=flat-square&logo=s" alt="SSR"></a></td>
</tr>
<tr>
    <td><strong>socks_servers.txt</strong></td>
    <td>فقط کانفیگ‌های SOCKS</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/socks_servers.txt"><img src="https://img.shields.io/badge/Download-SOCKS-8B4513?style=flat-square&logo=s" alt="SOCKS"></a></td>
</tr>
<tr>
    <td><strong>socks5_servers.txt</strong></td>
    <td>فقط کانفیگ‌های SOCKS5</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/servers/socks5_servers.txt"><img src="https://img.shields.io/badge/Download-SOCKS5-A0522D?style=flat-square&logo=s" alt="SOCKS5"></a></td>
</tr>
</tbody>
</table>
<p>همه‌ی فایل‌ها در هر اجرا به‌روزرسانی می‌شوند و فقط شامل کانفیگ‌های یکتا و جدید هستند. اگر فایلی حجم بالایی داشت، می‌توانید از نسخه‌های تفکیک‌شده استفاده کنید.</p>

<hr>

<!-- ساختار فایل‌ها -->
<h2>🗂️ ساختار فایل‌های پروژه</h2>
<pre class="ltr-block">
.
├── .github/
│   └── workflows/
│       ├── collector.yml              # گردش‌کار اصلی (اجرای یکپارچه خودکار)
│       └── cleaner_temp.yml           # گردش‌کار موقت برای پاکسازی کانال‌های تلگرام
│
├── src/
│   ├── collector_git.py               # اسکریپت اصلی جمع‌آوری از گیتهاب
│   ├── telegram_collector.py          # اسکریپت جمع‌آوری از تلگرام (بدون API)
│   ├── split_links.py                 # شکستن لینک‌های چسبیده
│   ├── dedup_configs.py               # حذف تکراری‌های هوشمند
│   ├── rebuild_protocols.py           # بازسازی فایل‌های پروتکل از روی all_servers.txt تمیز
│   └── channel_cleaner.py             # اسکریپت کمکی برای پاکسازی کانال‌های تلگرام
│
├── config/
│   ├── requirements.txt               # وابستگی‌های پایتون
│   ├── .gitignore                     # فایل‌های نادیده گرفته‌شده
│   └── .env.example                   # نمونه فایل متغیرهای محیطی
│
├── data/                              # فایل‌های داده و گزارش‌ها
│   ├── channels.txt                   # فهرست کانال‌های تلگرام (ورودی)
│   ├── channel_report.txt             # گزارش تعداد کانفیگ‌های استخراج‌شده از هر کانال
│   ├── checkpoint.json                # فایل ذخیره‌ی پیشرفت (Checkpoint)
│   ├── discovered_branches.json       # شاخه‌های جدید کشف‌شده
│   ├── repo_report.txt                # گزارش تعداد کانفیگ‌های استخراج‌شده از هر مخزن گیتهاب
│   ├── token_state.txt                # شمارنده‌ی چرخش توکن
│   ├── channels_cleaned.txt           # (تولیدشده) خروجی پاک‌سازی‌شده کانال‌های معتبر
│   └── invalid_channels.txt           # (تولیدشده) کانال‌های نامعتبر
│
├── servers/                           # فایل‌های تفکیک‌شده بر اساس پروتکل
│   ├── vmess_servers.txt              # کانفیگ‌های VMess
│   ├── vless_servers.txt              # کانفیگ‌های VLESS
│   ├── trojan_servers.txt             # کانفیگ‌های Trojan
│   ├── ss_servers.txt                 # کانفیگ‌های Shadowsocks
│   ├── ssr_servers.txt                # کانفیگ‌های SSR
│   ├── hysteria_servers.txt           # کانفیگ‌های Hysteria
│   ├── hysteria2_servers.txt          # کانفیگ‌های Hysteria2
│   ├── tuic_servers.txt               # کانفیگ‌های TUIC
│   ├── socks_servers.txt              # کانفیگ‌های SOCKS
│   └── socks5_servers.txt             # کانفیگ‌های SOCKS5
│
├── for Developers/                     # نسخه‌های کامل و قدیمی برای توسعه‌دهندگان
│   └── collector_git_Fullversion
│   └── channels_Fullversion.txt
│
├── all_servers.txt                     # تمام کانفیگ‌های یکتای جدید در هر اجرا (گیتهاب + تلگرام)
├── README.md                           # مستندات فارسی
└── README.EN.md                        # مستندات انگلیسی
</pre>
<hr>

<!-- مقایسه -->
<h2>📊 مقایسه با سایر Collectorهای معروف گیتهاب</h2>
<p>پس از بررسی ده‌ها پروژه‌ی مطرح در گیتهاب، جدول زیر تفاوت‌های کلیدی را نشان می‌دهد. در انتها نیز نام پروژه‌های شاخص در هر حوزه آمده است.</p>

<table>
<thead>
<tr><th>معیار</th><th>این پروژه</th><th>سایر پروژه‌ها</th></tr>
</thead>
<tbody>
<tr><td><strong>منبع جمع‌آوری</strong></td><td><strong>گیتهاب + تلگرام (بدون API)</strong></td><td>اکثراً فقط یکی از این دو</td></tr>
<tr><td><strong>مدیریت Rate Limit</strong></td><td><strong>توکن‌های دوگانه (PAT + App)</strong></td><td>ابتدایی یا تک‌توکن</td></tr>
<tr><td><strong>خروجی تفکیک‌شده</strong></td><td>✅ دارد</td><td>❌ اغلب یک فایل کلی</td></tr>
<tr><td><strong>ذخیره‌سازی هوشمند</strong></td><td>✅ (بدون تکرار)</td><td>❌ بازنویسی کامل</td></tr>
<tr><td><strong>Checkpoint (ادامه پس از توقف)</strong></td><td>✅ دارد</td><td>❌ در هیچ پروژه‌ای دیده نشد</td></tr>
<tr><td><strong>پایگاه داده (SQLite)</strong></td><td>✅ دارد</td><td>❌ اکثراً فایل متنی</td></tr>
<tr><td><strong>جمع‌آوری از تلگرام بدون API</strong></td><td>✅ (از طریق t.me/s)</td><td>❌ نیازمند Telethon/ربات</td></tr>
<tr><td><strong>Branch Discovery</strong></td><td>✅ دارد</td><td>❌</td></tr>
<tr><td><strong>توقف در سقف Core</strong></td><td>✅ بله</td><td>❌ خیر</td></tr>
<tr><td><strong>اجرای رایگان روی Actions</strong></td><td>✅ بله</td><td>✅ بله</td></tr>
</tbody>
</table>

<h3>🔍 پروژه‌های شاخص در هر حوزه</h3>
<table>
<thead>
<tr><th>حوزه</th><th>نام پروژه</th><th>توضیح کوتاه</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>جمع‌آوری از گیتهاب</strong></td>
    <td>
        <a href="https://github.com/mahdibland/V2RayAggregator" target="_blank">mahdibland/V2RayAggregator</a><br>
        <a href="https://github.com/swileran/v2ray-config-collector" target="_blank">swileran/v2ray-config-collector</a><br>
        <a href="https://github.com/MahanKenway/Freedom-V2Ray" target="_blank">MahanKenway/Freedom-V2Ray</a>
    </td>
    <td>مخازن شناخته‌شده‌ای که فقط از گیتهاب جمع‌آوری می‌کنند</td>
</tr>
<tr>
    <td><strong>جمع‌آوری از تلگرام</strong></td>
    <td>
        <a href="https://github.com/Surfboardv2ray/TGParse" target="_blank">Surfboardv2ray/TGParse</a><br>
        <a href="https://github.com/Kolandone/v2raycollector" target="_blank">Kolandone/v2raycollector</a><br>
        <a href="https://github.com/denxv/TGV2RayScraper" target="_blank">denxv/TGV2RayScraper</a><br>
        <a href="https://github.com/MhdiTaheri/V2rayCollector" target="_blank">MhdiTaheri/V2rayCollector</a>
    </td>
    <td>پروژه‌هایی که فقط از کانال‌های تلگرام جمع‌آوری می‌کنند</td>
</tr>
<tr>
    <td><strong>هر دو (گیتهاب + تلگرام)</strong></td>
    <td>
        <a href="https://github.com/wzdnzd/aggregator" target="_blank">wzdnzd/aggregator</a><br>
        <a href="https://github.com/SoroushImanian/BlackKnight" target="_blank">SoroushImanian/BlackKnight</a>
    </td>
    <td>پروژه‌هایی که از هر دو منبع استفاده می‌کنند، اما معمولاً برای تلگرام به API نیاز دارند</td>
</tr>
</tbody>
</table>

<hr>

<!-- خطاهای رایج -->
<h2>❗ خطاهای رایج و راه‌حل</h2>

<details>
<summary><strong>خطای <code>Resource not accessible by integration</code></strong></summary>
<p>این خطا معمولاً به دلیل عدم دسترسی <code>workflow</code> در توکن کلاسیک رخ می‌دهد. مطمئن شوید توکن <code>GH_TOKEN</code> شما دارای دسترسی <code>repo</code> و <code>workflow</code> باشد.</p>
</details>

<details>
<summary><strong>خطای <code>403 / 429 (Rate limit)</code> در لاگ</strong></summary>
<p>اسکریپت به‌طور خودکار Sleep کرده و مجدداً تلاش می‌کند. این بخشی از عملکرد عادی است. اگر مکرراً رخ داد، <code>MAX_AGE_HOURS</code> را بیشتر کنید.</p>
</details>

<details>
<summary><strong>کانال‌های تلگرام یافت نشدند</strong></summary>
<ul>
    <li>مطمئن شوید فایل <code>channels.txt</code> در ریشه‌ی پروژه وجود دارد.</li>
    <li>شناسه‌ها باید عمومی (Public) باشند.</li>
    <li>برای بررسی سلامت کانال‌ها، می‌توانید از ورک‌فلوی <code>Temp Channel Cleaner</code> استفاده کنید.</li>
</ul>
</details>

<details>
<summary><strong>فایل خروجی آپدیت نمی‌شود</strong></summary>
<ul>
    <li>مطمئن شوید Secrets با نام‌های صحیح تنظیم شده‌اند.</li>
    <li>بررسی کنید که مرحله‌ی <code>Commit and push updated files</code> در Workflow بدون خطا اجرا شده باشد.</li>
</ul>
</details>

<hr>

<!-- مشارکت -->
<h2>🙏 مشارکت و توسعه</h2>
<p>
پیشنهادات، گزارش باگ‌ها، مخازن جدید برای اضافه شدن به لیست <code>MANUAL_REPOS_TO_SCAN</code>، یا کانال‌های تلگرام جدید برای فایل <code>channels.txt</code> را می‌توانید از طریق <strong>Pull Request</strong> یا <strong>Issue</strong> با ما به اشتراک بگذارید.<br>
برای توسعه‌دهندگان: لطفاً پیش از ارسال تغییرات، یک اجرای آزمایشی روی سیستم خود انجام دهید.
</p>

<hr>

<!-- قدردانی -->
<h2>💡 قدردانی</h2>
<p>ایده‌ی استفاده از <code>t.me/s</code> برای دسترسی به کانال‌های تلگرام بدون نیاز به API از پروژه‌های متن‌بازی مانند <code>Kolandone/v2raycollector</code> و <code>MhdiTaheri/V2rayCollector</code> الهام گرفته شده است. از تمام توسعه‌دهندگانی که دانش خود را به اشتراک می‌گذارند سپاسگزاریم.</p>

<hr>

<!-- مجوز -->
<h2>📄 مجوز</h2>
<p>این پروژه تحت مجوز <strong>MIT</strong> منتشر شده است. استفاده، ویرایش و توزیع آزاد است.</p>

</div>

<!-- keywords: v2ray collector, v2ray config, vmess vless trojan, free v2ray, 
     v2ray subscription, proxy config collector, telegram v2ray, 
     github actions collector, hysteria2 tuic, shadowsocks collector, 
     جمع آوری کانفیگ V2Ray, کانفیگ رایگان V2Ray, وی‌پی‌ان رایگان -->

</body>
</html>
