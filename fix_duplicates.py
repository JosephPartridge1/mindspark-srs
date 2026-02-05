#!/usr/bin/env python3
"""
Script to fix duplicate endpoint functions in app.py
"""

import re

def fix_duplicates():
    # Read the file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all get_next_word function definitions
    pattern = r'@app\.route\([^)]+\)\s*\n\s*def get_next_word\(\):.*?(?=\n\s*@app\.route|\n\s*def [a-zA-Z_]|$)'
    matches = re.findall(pattern, content, re.DOTALL)

    print(f"Found {len(matches)} get_next_word functions")

    if len(matches) > 1:
        # Keep the last one (most complete implementation)
        # Remove all but the last occurrence
        for i in range(len(matches) - 1):
            content = content.replace(matches[i], '', 1)

    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("Duplicates removed!")

if __name__ == '__main__':
    fix_duplicates()
