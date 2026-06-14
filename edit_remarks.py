import re
import sys

INPUT_FILE = "all_servers.txt"

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
except FileNotFoundError:
    print(f"خطا: فایل {INPUT_FILE} یافت نشد.")
    sys.exit(1)

if not lines:
    print(f"فایل {INPUT_FILE} خالی است، کاری انجام نشد.")
    sys.exit(0)

# لیستی برای نگهداری خطوط جدید با Remarkهای تغییر یافته
new_lines = []

for idx, line in enumerate(lines, start=1):
    line = line.strip()
    if not line:
        continue
    
    # تشخیص پروتکل کانفیگ (برای اضافه کردن به Remark)
    protocol = "unknown"
    match = re.match(r'^(\w+)://', line)
    if match:
        protocol = match.group(1).lower()
    
    # ساخت Remark جدید: نام پروتکل و شماره خط
    new_remark = f"{protocol} config #{idx}"
    
    # اضافه کردن Remark به انتهای لینک
    if '#' in line:
        # اگر از قبل Remark داشته باشد، جایگزین می‌شود
        new_line = re.sub(r'#.*$', f'#{new_remark}', line)
    else:
        # اگر Remark ندارد، به انتهای لینک اضافه می‌شود
        new_line = f"{line}#{new_remark}"
    
    new_lines.append(new_line)

# نوشتن خطوط جدید در فایل
with open(INPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print(f"✅ Remarkهای {len(new_lines)} کانفیگ در فایل {INPUT_FILE} با موفقیت به‌روزرسانی شدند.")
