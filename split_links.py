import sys
import re

# لیست پروتکل‌های شناخته‌شده
known_schemes = [
    'vless', 'vmess', 'ss', 'shadowsocks', 'trojan',
    'tuic', 'juicity', 'ssr', 'socks', 'socks5',
    'hysteria', 'hysteria2', 'hy2'
]

# ساخت regex برای پیدا کردن دقیق "scheme://"
pattern = re.compile(
    r'(' + '|'.join(re.escape(s) for s in known_schemes) + r')://',
    re.IGNORECASE
)

def extract_proxy_links(line):
    links = []
    matches = list(pattern.finditer(line))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(line)
        link = line[start:end]
        links.append(link)

    return links

def main():
    if len(sys.argv) != 2:
        print("Usage: python split_links.py <filename>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = input_file + ".tmp"

    extracted_links = []

    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            line = line.rstrip('\n\r')
            if not line.strip():
                continue
            links_in_line = extract_proxy_links(line)
            extracted_links.extend(links_in_line)

    with open(output_file, 'w', encoding='utf-8', newline='\n') as outfile:
        for link in extracted_links:
            outfile.write(link + '\n')

    # جایگزینی فایل اصلی با فایل تمیز
    import os
    os.replace(output_file, input_file)
    print(f"Split completed. {len(extracted_links)} lines written to {input_file}")

if __name__ == "__main__":
    main()
