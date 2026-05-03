<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

</head>
<body>
<div class="container">

<marquee behavior="scroll" direction="left" scrollamount="6" 
 style="height:4px; line-height:0; display:block; margin:10px 0;">
  <font color="#ff4d4d">█</font>
  <font color="#ff8c00">█</font>
  <font color="#ffd700">█</font>
  <font color="#32cd32">█</font>
  <font color="#1e90ff">█</font>
  <font color="#9370db">█</font>
  <font color="#ff4d4d">█</font>
  <font color="#ff8c00">█</font>
  <font color="#ffd700">█</font>
  <font color="#32cd32">█</font>
  <font color="#1e90ff">█</font>
  <font color="#9370db">█</font>
</marquee>

<h1>🚀 V2ray Collector</h1>

<p>
<strong>یک گردآورنده‌ی هوشمند، مقاوم و فوق‌العاده بهینه برای یافتن، اسکن و استخراج کانفیگ‌های V2Ray (و پروتکل‌های مشابه) از گیتهاب.</strong><br>
این پروژه با هدف <strong>پوشش حداکثری منابع</strong> و <strong>مدیریت دقیق محدودیت‌های API گیتهاب</strong> طراحی شده است و می‌تواند به‌صورت <strong>کاملاً خودکار</strong> روی GitHub Actions اجرا شود.
</p>
<p>
چیزی که این پروژه را از سایر جمع‌آوری‌کننده‌ها متمایز می‌کند، <strong>هوش مصنوعی جستجو در دل گیتهاب</strong> و <strong>احترام کامل به محدودیت‌های Rate Limit</strong> است.
</p>

<hr>
<!-- ویژگی‌های متمایز -->
<h2>✨ ویژگی‌های متمایز (چرا این Collector از بقیه بهتر است؟)</h2>
<table>
<thead>
<tr><th>ویژگی</th><th>توضیح</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>معماری مبتنی بر مخازن دستی (Manual-Only Mode)</strong></td>
    <td>تمام جستجوهای خودکار گیتهاب غیرفعال شده و فقط مخازن منتخب و قدرتمند اسکن می‌شوند. این کار سرعت را فوق‌العاده افزایش داده و مصرف Core را بهینه می‌کند.</td>
</tr>
<tr>
    <td><strong>Branch Discovery با حافظه‌ی دائمی</strong></td>
    <td>شاخه‌های جدید کشف‌شده در فایل <code>discovered_branches.json</code> ذخیره می‌شوند و در اجراهای بعدی مستقیماً بررسی می‌شوند تا مصرف Core کاهش یابد.</td>
</tr>
<tr>
    <td><strong>مدیریت بودجه‌ی Core API (Dynamic Cap)</strong></td>
    <td>تعداد مخازن اسکن‌شده به‌طور خودکار با میزان مصرف Core تنظیم می‌شود. اگر مصرف به ۵۰۰۰ برسد، <strong>بدون اتلاف وقت و Sleep بیهوده</strong> اسکن متوقف شده و خروجی ذخیره می‌شود.</td>
</tr>
<tr>
    <td><strong>Checkpoint (ادامه پس از هر نوع توقف)</strong></td>
    <td>حتی اگر برق قطع شود، اینترنت برود یا Rate Limit تمام شود، اجرای بعدی دقیقاً از همان نقطه ادامه می‌یابد. جستجوهای قبلی هرگز تکرار نمی‌شوند.</td>
</tr>
<tr>
    <td><strong>پایگاه داده‌ی SQLite</strong></td>
    <td>همه‌ی کانفیگ‌های یکتا در یک دیتابیس محلی (<code>collector.db</code>) ذخیره می‌شوند. پردازش تکراری URLها کاملاً حذف شده است.</td>
</tr>
<tr>
    <td><strong>فیلتر ساعتی دقیق</strong></td>
    <td>پارامتر <code>MAX_AGE_HOURS</code> فقط مخازنی را اسکن می‌کند که در بازه‌ی زمانی مشخص (مثلاً ۱ ساعت اخیر) push خورده باشند. مناسب برای اجراهای فوق‌سریع و دریافت محتوای فوق‌تازه.</td>
</tr>
<tr>
    <td><strong>توقف هوشمند در سقف Rate Limit</strong></td>
    <td>هم محدودیت <code>Core</code> (۵۰۰۰ در ساعت) و هم <code>Search</code> (۳۰ در دقیقه) به‌طور جداگانه مدیریت می‌شوند و اسکریپت هرگز به خطای ۴۰۳ برخورد نمی‌کند.</td>
</tr>
<tr>
    <td><strong>منابع منتخب و پربازده</strong></td>
    <td>مجموعه‌ای بزرگ از مخازن دستی که دائماً به‌روز می‌شوند و کانفیگ‌های تازه‌تری نسبت به جستجوی عمومی ارائه می‌دهند.</td>
</tr>
<tr>
    <td><strong>فیلتر خروجی و تقسیم‌بندی</strong></td>
    <td>امکان تولید فایل خروجی به صورت یکپارچه یا تقسیم‌شده به بخش‌های کوچک (مثلاً هر ۵۰۰۰ خط).</td>
</tr>
<tr>
    <td><strong>عدم وابستگی به تلگرام</strong></td>
    <td>بر خلاف ۹۰٪ پروژه‌های مشابه، این Collector مستقیماً از API گیتهاب تغذیه می‌کند و نیازی به حساب کاربری تلگرام، شماره مجازی یا مدیریت کانال‌ها ندارد.</td>
</tr>
</tbody>
</table>

<hr>

<!-- نیازمندی‌ها -->
<h2>📦 نیازمندی‌ها</h2>
<ul>
    <li>Python 3.10 یا بالاتر</li>
    <li>
        کتابخانه‌های موجود در <code>requirements.txt</code>:
        <pre class="ltr-block">pip install -r requirements.txt</pre>
    </li>
    <li>یک <a href="https://github.com/settings/tokens" target="_blank" rel="noopener">Personal Access Token (classic)</a> از گیتهاب با دسترسی <code>repo</code> و <code>workflow</code></li>
</ul>

<hr>

<!-- تنظیمات -->
<h2>⚙️ تنظیمات (Configuration)</h2>
<p>تمام پارامترهای قابل تنظیم در ابتدای فایل <code>collector_git.py</code> در دیکشنری <code>CONFIG_DEFAULTS</code> قرار دارند. مهم‌ترین آن‌ها:</p>

<table>
<thead>
<tr><th>پارامتر</th><th>مقدار پیش‌فرض</th><th>توضیح</th></tr>
</thead>
<tbody>
<tr><td><code>SEARCH_PERIOD_DAYS</code></td><td><code>0</code></td><td>تاریخچه‌ی جستجو (۰ = غیرفعال)</td></tr>
<tr><td><code>MAX_AGE_HOURS</code></td><td><code>1</code></td><td>فقط مخازنی که در این چند ساعت push داشته‌اند اسکن شوند</td></tr>
<tr><td><code>REPO_SEARCH_PAGES</code></td><td><code>0</code></td><td>صفحات جستجوی مخازن (۰ = غیرفعال)</td></tr>
<tr><td><code>CODE_SEARCH_PAGES</code></td><td><code>0</code></td><td>صفحات جستجوی کد (۰ = غیرفعال)</td></tr>
<tr><td><code>EXTRA_UPDATED_REPO_PAGES</code></td><td><code>0</code></td><td>صفحات جستجوی تکمیلی (۰ = غیرفعال)</td></tr>
<tr><td><code>MAX_RECURSION_DEPTH</code></td><td><code>0</code></td><td>عمق دنبال کردن لینک‌های اشتراک (۰ = قطع)</td></tr>
<tr><td><code>GENERAL_CONCURRENT_REQUESTS</code></td><td><code>80</code></td><td>تعداد دانلود هم‌زمان فایل‌ها</td></tr>
<tr><td><code>SEARCH_API_CONCURRENCY</code></td><td><code>3</code></td><td>تعداد کوئری‌های هم‌زمان جستجو</td></tr>
<tr><td><code>TARGET_CORE_CONSUMPTION</code></td><td><code>5000</code></td><td>حداکثر Core API مجاز (برای توقف خودکار)</td></tr>
<tr><td><code>MAX_FILE_BYTES</code></td><td><code>2 * 1024 * 1024</code></td><td>حداکثر حجم فایل قابل دانلود (۲ مگابایت)</td></tr>
<tr><td><code>CHECKPOINT_FILE</code></td><td><code>checkpoint.json</code></td><td>فایل ذخیره‌ی پیشرفت برای اجرای افزایشی</td></tr>
<tr><td><code>DISCOVERED_BRANCHES_FILE</code></td><td><code>discovered_branches.json</code></td><td>فایل ذخیره‌ی شاخه‌های جدید</td></tr>
</tbody>
</table>

<div class="highlight">
<strong>نکته مهم:</strong> توکن گیتهاب را باید در فایل <code>.env</code> با فرمت زیر قرار دهید:
<pre class="ltr-block">GITHUB_TOKEN=your_token_here</pre>
این فایل به‌دلیل وجود در <code>.gitignore</code> هرگز در مخزن ذخیره نمی‌شود.
</div>

<hr>

<!-- اجرای دستی -->
<h2>🚀 اجرای دستی</h2>
<p>کافیست در ترمینال دستور زیر را اجرا کنید:</p>
<pre class="ltr-block">python src/collector_git.py</pre>
<ul>
    <li><strong>اجرای اول</strong> (با دیتابیس خالی) ممکن است ۱۰ تا ۱۵ دقیقه طول بکشد.</li>
    <li><strong>اجراهای بعدی</strong> به دلیل وجود Checkpoint و دیتابیس پر، بسیار سریع‌تر هستند (اغلب <strong>زیر ۱ دقیقه</strong>).</li>
</ul>
<p>خروجی نهایی در فایل <code>daily_servers.txt</code> (روزانه) و <code>hourly_servers.txt</code> (ساعتی) ذخیره می‌شود.</p>

<hr>

<!-- اجرای خودکار با GitHub Actions -->
<h2>🤖 راه‌اندازی اجرای خودکار با GitHub Actions</h2>

<h3>۱. ساخت مخزن و آپلود فایل‌ها</h3>
<p>یک مخزن <strong>عمومی</strong> (Public) روی گیتهاب بسازید و تمام فایل‌های پروژه (شامل پوشه‌ی <code>.github/workflows/</code>) را در آن آپلود کنید.</p>

<h3>۲. تنظیم Secret</h3>
<ul>
    <li>به <strong>Settings</strong> &gt; <strong>Secrets and variables</strong> &gt; <strong>Actions</strong> بروید.</li>
    <li>یک <strong>New repository secret</strong> با نام <code>GH_TOKEN</code> بسازید.</li>
    <li>مقدار آن را توکن Personal Access Token (classic) خود قرار دهید.</li>
</ul>

<h3>۳. فعال‌سازی Workflowها</h3>
<p>دو فایل Workflow در مسیر <code>.github/workflows/</code> وجود دارند:</p>
<ul>
    <li><strong><code>collector_hourly.yml</code></strong> → هر <strong>یک ساعت</strong> اجرا می‌شود و فقط تغییرات جدید را جمع‌آوری می‌کند (اجرای افزایشی).</li>
    <li><strong><code>collector_daily.yml</code></strong> → هر <strong>روز یک‌بار</strong> (نیمه‌شب) Checkpoint را ریست کرده و یک اسکن کامل انجام می‌دهد.</li>
</ul>
<p>هر دو Workflow امکان اجرای دستی با دکمه‌ی <strong>Run workflow</strong> را نیز دارند.</p>

<h3>۴. تست اولیه</h3>
<p>برای اطمینان از درستی تنظیمات، به تب <strong>Actions</strong> بروید، روی <strong>Daily Collector</strong> کلیک کنید و <strong>Run workflow</strong> را بزنید. پس از اتمام اجرا، فایل <code>daily_servers.txt</code> در ریشه‌ی مخزن ظاهر می‌شود.</p>

<h3>۵. لینک خام خروجی</h3>
<p>پس از اولین اجرای موفق، فایل‌های خروجی از طریق این آدرس‌ها در دسترس خواهند بود:</p>
<pre class="ltr-block">
📅 روزانه: https://raw.githubusercontent.com/مشخصات-شما/main/daily_servers.txt
⏱️ ساعتی: https://raw.githubusercontent.com/مشخصات-شما/main/hourly_servers.txt
</pre>

<hr>

<!-- عملکرد و زمان اجرا -->
<h2>⏱️ عملکرد و زمان اجرا (تخمینی)</h2>
<table>
<thead>
<tr><th>حالت اجرا</th><th>زمان تقریبی</th><th>توضیح</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>اولین اجرا (کامل)</strong></td>
    <td>~۱۰-۱۵ دقیقه</td>
    <td>بدون دیتابیس، تمام مراحل انجام می‌شود</td>
</tr>
<tr>
    <td><strong>اجرای ساعتی (افزایشی)</strong></td>
    <td><strong>کمتر از ۱ دقیقه</strong></td>
    <td>Stage ۱ و ۲ فقط مخازن دستی که اخیراً push داشته‌اند را اسکن می‌کنند</td>
</tr>
<tr>
    <td><strong>اجرای روزانه (Full Scan)</strong></td>
    <td>~۱۰-۱۵ دقیقه</td>
    <td>Checkpoint ریست می‌شود و همه‌ی مخازن دستی از نو اسکن می‌شوند</td>
</tr>
</tbody>
</table>
<p>این اعداد بر اساس اجرا روی GitHub Actions (ubuntu-latest) و با توکن استاندارد است. با کاهش برخی پارامترها مانند <code>REPO_SEARCH_PAGES</code> و <code>GENERAL_CONCURRENT_REQUESTS</code> می‌توان زمان را حتی کمتر نیز کرد.</p>

<hr>

<!-- ساختار فایل‌ها -->
<h2>🗂️ ساختار فایل‌های پروژه</h2>
<pre class="ltr-block">
.
├── .github/
│   └── workflows/
│       ├── collector_hourly.yml   # Workflow اجرای ساعتی (افزایشی)
│       └── collector_daily.yml    # Workflow اجرای روزانه (کامل)
├── src/
│   ├── collector_git.py           # اسکریپت اصلی جمع‌آوری
│   ├── split_links.py             # شکستن لینک‌های چسبیده
│   ├── dedup_configs.py           # حذف تکراری‌های هوشمند
│   └── daily_reset.py             # پاک‌کننده‌ی Checkpoint
├── config/
│   ├── requirements.txt           # وابستگی‌های پایتون
│   ├── .gitignore                 # فایل‌های نادیده گرفته‌شده
│   └── .env.example               # نمونه فایل متغیرهای محیطی
├── README.md                      # مستندات پروژه
├── checkpoint.json                # فایل ذخیره‌ی پیشرفت
├── discovered_branches.json       # فایل ذخیره‌ی شاخه‌های جدید
├── daily_servers.txt              # فایل خروجی روزانه
└── hourly_servers.txt             # فایل خروجی ساعتی (در صورت وجود)
</pre>

<hr>

<!-- مقایسه با سایر Collectorها -->
<h2>📊 مقایسه با سایر Collectorهای معروف گیتهاب</h2>
<p>پس از بررسی بیش از ۴۰ پروژه‌ی مطرح (از جمله <code>mrvcoder/V2rayCollector</code>، <code>mahdibland/V2RayAggregator</code>، <code>swileran/v2ray-config-collector</code>، <code>MahanKenway/Freedom-V2Ray</code>، <code>wzdnzd/aggregator</code> و...)، جدول زیر تفاوت‌های کلیدی را نشان می‌دهد:</p>

<table>
<thead>
<tr><th>معیار</th><th>این پروژه</th><th>سایر پروژه‌ها</th></tr>
</thead>
<tbody>
<tr><td><strong>منبع اصلی جستجو</strong></td><td><strong>مخازن دستی منتخب</strong></td><td>اکثراً کانال‌های تلگرام یا جستجوی عمومی گیتهاب</td></tr>
<tr><td><strong>مدیریت Rate Limit</strong></td><td><strong>Core + Search با توقف هوشمند</strong></td><td>ابتدایی یا بدون مدیریت</td></tr>
<tr><td><strong>Checkpoint (ادامه پس از توقف)</strong></td><td>✅ دارد</td><td>❌ در هیچ پروژه‌ای دیده نشد</td></tr>
<tr><td><strong>پایگاه داده (SQLite)</strong></td><td>✅ دارد</td><td>❌ اکثراً فایل متنی</td></tr>
<tr><td><strong>Branch Discovery با ذخیره‌سازی</strong></td><td>✅ دارد</td><td>❌ فقط یک نمونه‌ی مشابه (wzdnzd/aggregator)</td></tr>
<tr><td><strong>خروجی افزایشی (فقط تازه‌ها)</strong></td><td>✅ (با Checkpoint)</td><td>❌</td></tr>
<tr><td><strong>جستجوی کد (Code Search)</strong></td><td>✅ دارد (غیرفعال پیش‌فرض)</td><td>❌ اغلب ندارند</td></tr>
<tr><td><strong>فیلتر ساعتی واقعی</strong></td><td>✅ بله (<code>MAX_AGE_HOURS</code>)</td><td>❌ خیر</td></tr>
<tr><td><strong>توقف در سقف Core</strong></td><td>✅ بله (بدون Sleep)</td><td>❌ خیر</td></tr>
<tr><td><strong>وابستگی به تلگرام</strong></td><td>❌ خیر</td><td>✅ تقریباً همه</td></tr>
<tr><td><strong>اجرای رایگان روی Actions</strong></td><td>✅ بله</td><td>✅ بله</td></tr>
</tbody>
</table>

<hr>

<!-- خطاهای رایج و راه‌حل -->
<h2>❗ خطاهای رایج و راه‌حل</h2>

<details>
<summary><strong>خطای <code>Secret names must not start with GITHUB_</code></strong></summary>
<p>نام Secret حتماً باید متفاوت باشد. مثلاً <code>GH_TOKEN</code> یا <code>MY_TOKEN</code> انتخاب کنید و در Workflowها به‌صورت <code>${{ secrets.GH_TOKEN }}</code> استفاده کنید.</p>
</details>

<details>
<summary><strong>خطای <code>No such file or directory: 'collector_git.py'</code></strong></summary>
<p>مطمئن شوید فایل اصلی دقیقاً <code>collector_git.py</code> نام دارد و در پوشه‌ی <code>src/</code> قرار دارد. اگر نام آن را تغییر داده‌اید، در خط <code>run: python src/collector_git.py</code> در Workflowها نیز اصلاح کنید.</p>
</details>

<details>
<summary><strong>هشدار <code>Node.js 20 actions are deprecated</code></strong></summary>
<p>این یک اخطار است و تأثیری در اجرا ندارد. برای رفع آن، نسخه‌ی actionها را به‌روز کنید: <code>actions/checkout@v5</code> و <code>actions/setup-python@v6</code>.</p>
</details>

<details>
<summary><strong>خطای <code>403 / 429 (Rate limit)</code> در لاگ</strong></summary>
<p>اسکریپت به‌طور خودکار ۶۱ ثانیه Sleep کرده و مجدداً تلاش می‌کند. این خطاها بخشی از عملکرد عادی هستند و نیاز به دخالت دستی ندارند. اگر بیش از حد تکرار شد، <code>SEARCH_API_CONCURRENCY</code> را کمتر کنید.</p>
</details>

<details>
<summary><strong>فایل خروجی آپدیت نمی‌شود</strong></summary>
<ul>
    <li>مطمئن شوید Secret با نام <code>GH_TOKEN</code> و دسترسی <code>repo</code> تنظیم شده است.</li>
    <li>بررسی کنید که در Workflow مرحله‌ی <code>Commit and push updated results</code> وجود دارد.</li>
    <li>اگر همچنان مشکل داشت، لاگ همان مرحله را برای بررسی ارسال کنید.</li>
</ul>
</details>

<hr>

<!-- مشارکت -->
<h2>🙏 مشارکت و توسعه</h2>
<p>
پیشنهادات، گزارش باگ‌ها و مخازن جدید برای اضافه شدن به لیست‌های <code>MANUAL_REPOS_TO_SCAN</code> یا <code>REPO_SEARCH_QUERIES</code> را می‌توانید از طریق <strong>Pull Request</strong> یا <strong>Issue</strong> با ما به اشتراک بگذارید.<br>
برای توسعه‌دهندگان: لطفاً پیش از ارسال تغییرات، یک اجرای آزمایشی روی سیستم خود انجام دهید.
</p>

<hr>

<!-- مجوز -->
<h2>📄 مجوز</h2>
<p>این پروژه تحت مجوز <strong>MIT</strong> منتشر شده است. استفاده، ویرایش و توزیع آزاد است.</p>

</div>
</body>
</html>
