#!/usr/bin/env python3
import sys

def merge(source_path, target_path):
    lines = set()
    for path in (source_path, target_path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        lines.add(line)
        except FileNotFoundError:
            pass
    sorted_lines = sorted(lines)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_lines) + '\n')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: merge_unique.py <source_file> <target_file>")
        sys.exit(1)
    merge(sys.argv[1], sys.argv[2])
