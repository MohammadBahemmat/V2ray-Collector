<!-- README.md (English Version) -->
<div align="center" style="margin-bottom: 20px;">
  <a href="https://github.com/MohammadBahemmat/V2ray-Collector/blob/main/README.fa.md">
    <img src="https://img.shields.io/badge/Read_in-Farsi-FF5722?style=for-the-badge&logo=readthedocs" alt="Read in Farsi">
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
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
<div class="container">

<img src="https://github.com/MohammadBahemmat/V2ray-Collector/actions/workflows/collector.yml/badge.svg" alt="Collector Status">

<h1>🚀 V2ray Collector</h1>

<p>
<strong>An intelligent, dependency-free, and highly optimized collector for automated harvesting of V2Ray configs and similar protocols.</strong><br>
This project leverages <strong>GitHub repositories</strong> and <strong>public Telegram channels</strong> simultaneously (without needing any API, bot, or phone number) to provide the most powerful source of free configs. All processes run <strong>fully automatically</strong> on GitHub Actions.
</p>
<p>
What sets this project apart from other collectors is its <strong>unified architecture, intelligent Rate Limit management with dual tokens, and always-fresh, categorized outputs</strong>.
</p>

<hr>

<!-- Distinctive Features -->
<h2>✨ Distinctive Features</h2>
<table>
<thead>
<tr><th>Feature</th><th>Description</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>🎯 Dual Collection (GitHub + Telegram)</strong></td>
    <td>Intelligent scanning of GitHub repositories <strong>and</strong> fetching of public Telegram channels (<code>t.me/s</code>) without any dependency on API, bot, or phone number. Both sources are merged into a shared database.</td>
</tr>
<tr>
    <td><strong>🗂️ Categorized Outputs</strong></td>
    <td>In addition to the comprehensive <code>all_servers.txt</code>, configs are automatically categorized by protocol (<code>vmess_servers.txt</code>, <code>vless_servers.txt</code>, etc.) and saved.</td>
</tr>
<tr>
    <td><strong>💾 Smart Deduplication & Storage</strong></td>
    <td>Only new configs are added to the file in each run. No duplicate configs exist in the output, and file growth is completely controlled.</td>
</tr>
<tr>
    <td><strong>🪙 Dual-Token Rate Limit Management</strong></td>
    <td>Using a classic PAT and a GitHub App, Core request limits are cyclically managed, and the script never hits a 403 error.</td>
</tr>
<tr>
    <td><strong>⏱️ 15-Minute Time Window</strong></td>
    <td>Only repositories pushed to in the last 15 minutes are scanned (adjustable via <code>MAX_AGE_HOURS</code>). The latest posts are fetched from Telegram as well.</td>
</tr>
<tr>
    <td><strong>🌿 Branch Discovery with Persistent Memory</strong></td>
    <td>Newly discovered branches are saved in <code>discovered_branches.json</code> and directly checked in subsequent runs.</td>
</tr>
<tr>
    <td><strong>🧩 Checkpoint (Resume After Any Stop)</strong></td>
    <td>Even if power goes out or Rate Limit runs out, the next run will continue exactly from where it stopped.</td>
</tr>
<tr>
    <td><strong>🗃️ SQLite Database</strong></td>
    <td>All unique configs are stored in a local database (<code>collector.db</code>), preventing duplicate URL processing.</td>
</tr>
<tr>
    <td><strong>🔒 No Telegram API Dependency</strong></td>
    <td>Unlike 90% of similar projects, this collector does <strong>not require any API, bot, or phone number</strong> for Telegram – it uses the web version (<code>t.me/s</code>).</td>
</tr>
<tr>
    <td><strong>🚀 Completely Automated & Free</strong></td>
    <td>The whole system runs on a single free GitHub Actions workflow, with no external server needed.</td>
</tr>
</tbody>
</table>

<hr>

<!-- Requirements -->
<h2>📦 Requirements</h2>
<ul>
    <li><strong>Git</strong> installed on your system (to clone the repository)</li>
    <li>Python 3.10 or higher</li>
    <li>
        Libraries listed in <code>requirements.txt</code>:
        <pre class="ltr-block">pip install -r config/requirements.txt</pre>
    </li>
    <li>
        One of the following for GitHub authentication:
        <ul>
            <li>A <strong>Personal Access Token (classic)</strong> with <code>repo</code> and <code>workflow</code> scopes (for GitHub scanning), <strong>or</strong></li>
            <li>A <strong>GitHub App</strong> installed on the repository (for higher security)</li>
        </ul>
    </li>
</ul>

<hr>

<!-- Configuration -->
<h2>⚙️ Configuration</h2>
<p>All key parameters are adjustable in the <code>CONFIG_DEFAULTS</code> dictionary inside <code>collector_git.py</code>. The most important ones are:</p>

<table>
<thead>
<tr><th>Parameter</th><th>Default Value</th><th>Description</th></tr>
</thead>
<tbody>
<tr><td><code>MAX_AGE_HOURS</code></td><td><code>0.25</code></td><td>Only scan repositories that have been pushed to in the last 15 minutes</td></tr>
<tr><td><code>TARGET_CORE_CONSUMPTION</code></td><td><code>5000</code></td><td>Maximum allowed Core API calls (for automatic stop)</td></tr>
<tr><td><code>MAX_FILE_BYTES</code></td><td><code>10 * 1024 * 1024</code></td><td>Maximum downloadable file size (10 MB)</td></tr>
<tr><td><code>GENERAL_CONCURRENT_REQUESTS</code></td><td><code>80</code></td><td>Number of simultaneous file downloads</td></tr>
<tr><td><code>MAX_RECURSION_DEPTH</code></td><td><code>0</code></td><td>Depth of following subscription links</td></tr>
<tr><td><code>CHECKPOINT_FILE</code></td><td><code>checkpoint.json</code></td><td>Progress save file</td></tr>
<tr><td><code>DISCOVERED_BRANCHES_FILE</code></td><td><code>discovered_branches.json</code></td><td>File to store newly discovered branches</td></tr>
</tbody>
</table>

<div class="highlight">
<strong>🔐 Setting Secrets on GitHub:</strong> To use dual tokens, define these values in <strong>Settings</strong> &gt; <strong>Secrets and variables</strong> &gt; <strong>Actions</strong>:
<pre class="ltr-block">
GH_TOKEN              → Personal Access Token (classic)
GH_APP_ID             → Your GitHub App ID
GH_APP_PRIVATE_KEY    → Private key of your GitHub App
</pre>
</div>

<hr>

<h2>🧩 Quick Start</h2>
<p>If you want to copy and run this project for yourself:</p>
<ol>
    <li>Fork the repository (use the Fork button at the top of the GitHub page)</li>
    <li>Clone the forked repository:
        <pre class="ltr-block">git clone https://github.com/YOUR_USERNAME/V2ray-Collector.git
cd V2ray-Collector</pre>
    </li>
    <li>Install Python dependencies:
        <pre class="ltr-block">pip install -r config/requirements.txt</pre>
    </li>
    <li>Create a <code>.env</code> file with your GitHub token, following the template in <code>config/.env.example</code>.</li>
    <li>Fill <code>channels.txt</code> with the Telegram channels you want to monitor.</li>
    <li>Run the collector once manually to test everything:
        <pre class="ltr-block">python src/collector_git.py</pre>
    </li>
</ol>
<hr>

<!-- Manual Execution -->
<h2>🚀 Manual Execution</h2>
<p>To run the GitHub collector alone (without Telegram), simply execute the following command in your terminal:</p>
<pre class="ltr-block">python src/collector_git.py</pre>
<p>To run the Telegram collector alone:</p>
<pre class="ltr-block">python src/telegram_collector.py</pre>
<ul>
    <li><strong>First run</strong> (with empty database) may take 10 to 15 minutes.</li>
    <li><strong>Subsequent runs</strong> are much faster due to the populated database.</li>
</ul>

<hr>

<!-- Automated Execution -->
<h2>🤖 Automated Execution with GitHub Actions</h2>

<h3>1. Workflow File</h3>
<p>The project runs by default using a YAML file at <code>.github/workflows/collector.yml</code> which:
<ul>
    <li>Starts via <strong>workflow_dispatch</strong> (manual or chained execution) and automatically triggers the next run after completion.</li>
    <li>First fetches new configs from <strong>Telegram</strong>.</li>
    <li>Then scans <strong>GitHub</strong> repositories.</li>
    <li>Uses <strong>dual tokens</strong> to distribute Rate Limit pressure.</li>
    <li>Finally merges, categorizes, and saves the outputs into the repository.</li>
</ul>
</p>

<h3>2. Retrieving Output Files</h3>
<p>After the first successful run, you can use the links at the top of this page to download the files. These files can be directly loaded into your V2Ray client (such as v2rayN, Nekobox, or Hiddify).</p>

<h3>3. Adding Telegram Channels</h3>
<p>The file <code>channels.txt</code> in the project root maintains the list of public Telegram channels (one identifier per line, without <code>@</code>). To add a new channel, simply insert its identifier on a new line.</p>

<hr>

<!-- Output Files -->
<h2>📁 Output Files</h2>
<table>
<thead>
<tr><th>File</th><th>Description</th><th>Direct Link</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>all_servers.txt</strong></td>
    <td>All unique new configs per run (GitHub + Telegram)</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/all_servers.txt"><img src="https://img.shields.io/badge/Download-All_Configs-blue?style=flat-square&logo=textpattern" alt="All Configs"></a></td>
</tr>
<tr>
    <td><strong>vmess_servers.txt</strong></td>
    <td>VMess configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/vmess_servers.txt"><img src="https://img.shields.io/badge/Download-VMess-EF7F1A?style=flat-square&logo=v" alt="VMess"></a></td>
</tr>
<tr>
    <td><strong>vless_servers.txt</strong></td>
    <td>VLESS configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/vless_servers.txt"><img src="https://img.shields.io/badge/Download-VLESS-00BFFF?style=flat-square&logo=v" alt="VLESS"></a></td>
</tr>
<tr>
    <td><strong>trojan_servers.txt</strong></td>
    <td>Trojan configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/trojan_servers.txt"><img src="https://img.shields.io/badge/Download-Trojan-2E8B57?style=flat-square&logo=trove" alt="Trojan"></a></td>
</tr>
<tr>
    <td><strong>hysteria_servers.txt</strong></td>
    <td>Hysteria configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/hysteria_servers.txt"><img src="https://img.shields.io/badge/Download-Hysteria-8A2BE2?style=flat-square&logo=h" alt="Hysteria"></a></td>
</tr>
<tr>
    <td><strong>hysteria2_servers.txt</strong></td>
    <td>Hysteria2 configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/hysteria2_servers.txt"><img src="https://img.shields.io/badge/Download-Hysteria2-9400D3?style=flat-square&logo=h" alt="Hysteria2"></a></td>
</tr>
<tr>
    <td><strong>tuic_servers.txt</strong></td>
    <td>TUIC configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/tuic_servers.txt"><img src="https://img.shields.io/badge/Download-TUIC-FF69B4?style=flat-square&logo=t" alt="TUIC"></a></td>
</tr>
<tr>
    <td><strong>ss_servers.txt</strong></td>
    <td>Shadowsocks configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/ss_servers.txt"><img src="https://img.shields.io/badge/Download-Shadowsocks-4682B4?style=flat-square&logo=s" alt="Shadowsocks"></a></td>
</tr>
<tr>
    <td><strong>ssr_servers.txt</strong></td>
    <td>SSR configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/ssr_servers.txt"><img src="https://img.shields.io/badge/Download-SSR-5F9EA0?style=flat-square&logo=s" alt="SSR"></a></td>
</tr>
<tr>
    <td><strong>socks_servers.txt</strong></td>
    <td>SOCKS configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/socks_servers.txt"><img src="https://img.shields.io/badge/Download-SOCKS-8B4513?style=flat-square&logo=s" alt="SOCKS"></a></td>
</tr>
<tr>
    <td><strong>socks5_servers.txt</strong></td>
    <td>SOCKS5 configs only</td>
    <td><a href="https://raw.githubusercontent.com/MohammadBahemmat/V2ray-Collector/main/socks5_servers.txt"><img src="https://img.shields.io/badge/Download-SOCKS5-A0522D?style=flat-square&logo=s" alt="SOCKS5"></a></td>
</tr>
</tbody>
</table>
<p>All files are updated on every run and contain only unique, new configs. If a file becomes too large, you can use the split versions instead.</p>

<hr>

<!-- Project Structure -->
<h2>🗂️ Project Structure</h2>
<pre class="ltr-block">
.
├── .github/
│   └── workflows/
│       ├── collector.yml              # Main workflow (unified automatic execution)
│       └── cleaner_temp.yml           # Temporary workflow for cleaning Telegram channels
│
├── src/
│   ├── collector_git.py               # Main GitHub collector script
│   ├── telegram_collector.py          # Telegram collector script (no API)
│   ├── split_links.py                 # Split joined links
│   ├── dedup_configs.py               # Intelligent deduplication
│   └── rebuild_protocols.py           # Rebuild protocol files from cleaned all_servers.txt
│
├── config/
│   ├── requirements.txt               # Python dependencies
│   ├── .gitignore                     # Ignored files
│   └── .env.example                   # Sample environment variables file
│
├── for Developers/                     # Full and old versions for developers
│   └── collector_git_Fullversion
│
├── README.md                           # Project documentation
├── channels.txt                        # Telegram channel list (input)
├── channels_cleaned.txt                # Cleaned output of valid channels
├── invalid_channels.txt                # Invalid channels
├── channel_cleaner.py                  # Helper script for cleaning channels
│
├── all_servers.txt                     # All unique configs (GitHub + Telegram)
├── vmess_servers.txt                   # VMess configs
├── vless_servers.txt                   # VLESS configs
├── trojan_servers.txt                  # Trojan configs
├── ss_servers.txt                      # Shadowsocks configs
├── ssr_servers.txt                     # SSR configs
├── hysteria_servers.txt                # Hysteria configs
├── hysteria2_servers.txt               # Hysteria2 configs
├── tuic_servers.txt                    # TUIC configs
├── socks_servers.txt                   # SOCKS configs
├── socks5_servers.txt                  # SOCKS5 configs
│
├── checkpoint.json                     # Progress save file (Checkpoint)
├── discovered_branches.json            # Newly discovered branches
├── channel_report.txt                  # Report of configs extracted per channel
├── repo_report.txt                     # Report of configs extracted per GitHub repository
└── token_state.txt                     # Token rotation counter
</pre>

<hr>

<!-- Comparison -->
<h2>📊 Comparison with Other Well-Known GitHub Collectors</h2>
<p>After examining dozens of prominent projects on GitHub, the table below shows the key differences. The names of notable projects in each category are also listed at the end.</p>

<table>
<thead>
<tr><th>Criterion</th><th>This Project</th><th>Other Projects</th></tr>
</thead>
<tbody>
<tr><td><strong>Collection Source</strong></td><td><strong>GitHub + Telegram (no API)</strong></td><td>Mostly only one of the two</td></tr>
<tr><td><strong>Rate Limit Management</strong></td><td><strong>Dual tokens (PAT + App)</strong></td><td>Basic or single-token</td></tr>
<tr><td><strong>Categorized Output</strong></td><td>✅ Yes</td><td>❌ Often a single general file</td></tr>
<tr><td><strong>Smart Deduplication</strong></td><td>✅ Yes (no duplicates)</td><td>❌ Complete rewrite</td></tr>
<tr><td><strong>Checkpoint (Resume after stop)</strong></td><td>✅ Yes</td><td>❌ Not seen in any project</td></tr>
<tr><td><strong>SQLite Database</strong></td><td>✅ Yes</td><td>❌ Mostly plain text files</td></tr>
<tr><td><strong>Telegram Collection Without API</strong></td><td>✅ (via t.me/s)</td><td>❌ Requires Telethon/bot</td></tr>
<tr><td><strong>Branch Discovery</strong></td><td>✅ Yes</td><td>❌</td></tr>
<tr><td><strong>Stop at Core Limit</strong></td><td>✅ Yes</td><td>❌ No</td></tr>
<tr><td><strong>Free Execution on Actions</strong></td><td>✅ Yes</td><td>✅ Yes</td></tr>
</tbody>
</table>

<h3>🔍 Notable Projects by Category</h3>
<table>
<thead>
<tr><th>Category</th><th>Project Name</th><th>Brief Description</th></tr>
</thead>
<tbody>
<tr>
    <td><strong>GitHub Collectors</strong></td>
    <td>
        <a href="https://github.com/mahdibland/V2RayAggregator" target="_blank">mahdibland/V2RayAggregator</a><br>
        <a href="https://github.com/swileran/v2ray-config-collector" target="_blank">swileran/v2ray-config-collector</a><br>
        <a href="https://github.com/MahanKenway/Freedom-V2Ray" target="_blank">MahanKenway/Freedom-V2Ray</a>
    </td>
    <td>Well-known repositories that collect only from GitHub</td>
</tr>
<tr>
    <td><strong>Telegram Collectors</strong></td>
    <td>
        <a href="https://github.com/Surfboardv2ray/TGParse" target="_blank">Surfboardv2ray/TGParse</a><br>
        <a href="https://github.com/Kolandone/v2raycollector" target="_blank">Kolandone/v2raycollector</a><br>
        <a href="https://github.com/denxv/TGV2RayScraper" target="_blank">denxv/TGV2RayScraper</a><br>
        <a href="https://github.com/MhdiTaheri/V2rayCollector" target="_blank">MhdiTaheri/V2rayCollector</a>
    </td>
    <td>Projects that collect only from Telegram channels</td>
</tr>
<tr>
    <td><strong>Both (GitHub + Telegram)</strong></td>
    <td>
        <a href="https://github.com/wzdnzd/aggregator" target="_blank">wzdnzd/aggregator</a><br>
        <a href="https://github.com/SoroushImanian/BlackKnight" target="_blank">SoroushImanian/BlackKnight</a>
    </td>
    <td>Projects that use both sources, but usually need an API for Telegram</td>
</tr>
</tbody>
</table>

<hr>

<!-- Common Errors -->
<h2>❗ Common Errors and Solutions</h2>

<details>
<summary><strong>Error: <code>Resource not accessible by integration</code></strong></summary>
<p>This error usually occurs because the classic token lacks the <code>workflow</code> scope. Make sure your <code>GH_TOKEN</code> has both <code>repo</code> and <code>workflow</code> permissions.</p>
</details>

<details>
<summary><strong>Error: <code>403 / 429 (Rate limit)</code> in log</strong></summary>
<p>The script automatically sleeps and retries. This is normal. If it happens frequently, increase <code>MAX_AGE_HOURS</code>.</p>
</details>

<details>
<summary><strong>Telegram channels not found</strong></summary>
<ul>
    <li>Make sure the <code>channels.txt</code> file exists in the project root.</li>
    <li>Identifiers must be public.</li>
    <li>You can use the <code>Temp Channel Cleaner</code> workflow to check channel health.</li>
</ul>
</details>

<details>
<summary><strong>Output file does not update</strong></summary>
<ul>
    <li>Ensure that the Secrets have the correct names.</li>
    <li>Check that the <code>Commit and push updated files</code> step in the Workflow ran without errors.</li>
</ul>
</details>

<hr>

<!-- Contribution -->
<h2>🙏 Contribution & Development</h2>
<p>
Suggestions, bug reports, new repositories to add to the <code>MANUAL_REPOS_TO_SCAN</code> list, or additional Telegram channels for the <code>channels.txt</code> file can be shared via <strong>Pull Request</strong> or <strong>Issue</strong>.<br>
For developers: please test your changes locally before submitting them.
</p>

<hr>

<!-- Acknowledgements -->
<h2>💡 Acknowledgements</h2>
<p>The idea of using <code>t.me/s</code> to access Telegram channels without an API was inspired by open-source projects such as <code>Kolandone/v2raycollector</code> and <code>MhdiTaheri/V2rayCollector</code>. We are grateful to all developers who share their knowledge.</p>

<hr>

<!-- License -->
<h2>📄 License</h2>
<p>This project is released under the <strong>MIT</strong> license. Use, modification, and distribution are free.</p>

</div>
</body>
</html>
