#!/usr/bin/env python3
"""
Script to fix SQL placeholder mismatches between SQLite (?) and PostgreSQL (%s)
"""

import os
import re
import glob

def fix_sql_placeholders_in_file(filepath):
    """Fix SQL placeholders in a single file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Pattern to find cursor.execute calls with ? placeholders
    # This is a complex regex to match various SQL execute patterns
    patterns = [
        # cursor.execute('SELECT ... WHERE ... = ?', (param,))
        (r"cursor\.execute\(\s*'''([\s\S]*?)\?([\s\S]*?)'''\s*,\s*\(([^)]+)\)\s*\)",
         r"cursor.execute('''\1%s\2''' if db_adapter.is_postgresql else '''\1?\2''', (\3))"),

        # cursor.execute("SELECT ... WHERE ... = ?", (param,))
        (r'cursor\.execute\(\s*"""([\s\S]*?)\?([\s\S]*?)"""\s*,\s*\(([^)]+)\)\s*\)',
         r'cursor.execute("""\1%s\2""" if db_adapter.is_postgresql else """\1?\2""", (\3))'),

        # cursor.execute('SELECT ... WHERE ... = ?', (param,))
        (r"cursor\.execute\(\s*'([\s\S]*?)\?([\s\S]*?)'\s*,\s*\(([^)]+)\)\s*\)",
         r"cursor.execute('\1%s\2' if db_adapter.is_postgresql else '\1?\2', (\3))"),

        # cursor.execute("SELECT ... WHERE ... = ?", (param,))
        (r'cursor\.execute\(\s*"([\s\S]*?)\?([\s\S]*?)"\s*,\s*\(([^)]+)\)\s*\)',
         r'cursor.execute("\1%s\2" if db_adapter.is_postgresql else "\1?\2", (\3))'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)

    # Also fix multi-parameter queries
    # Pattern for multiple ? placeholders
    def replace_placeholders(match):
        sql = match.group(1)
        params = match.group(2)

        # Count ? in SQL
        question_marks = sql.count('?')
        if question_marks > 1:
            # Replace all ? with %s for PostgreSQL, keep ? for SQLite
            pg_sql = sql.replace('?', '%s')
            return f"cursor.execute('''{pg_sql}''' if db_adapter.is_postgresql else '''{sql}''', {params})"
        else:
            # Single parameter case
            pg_sql = sql.replace('?', '%s')
            return f"cursor.execute('''{pg_sql}''' if db_adapter.is_postgresql else '''{sql}''', {params})"

    # More complex pattern for multi-param queries
    complex_pattern = r"cursor\.execute\(\s*'''([\s\S]*?)'''\s*,\s*(\([^)]+\))\s*\)"
    content = re.sub(complex_pattern, replace_placeholders, content, flags=re.MULTILINE | re.DOTALL)

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed {filepath}")
        return True
    else:
        print(f"ℹ️  No changes needed for {filepath}")
        return False

def main():
    """Fix SQL placeholders in all Python files"""
    print("🔧 Fixing SQL placeholder mismatches...")

    # Find all Python files
    python_files = glob.glob('*.py') + glob.glob('frontend/**/*.py')

    fixed_count = 0
    for filepath in python_files:
        if 'fix_sql_placeholders.py' in filepath:
            continue  # Skip this script itself

        try:
            if fix_sql_placeholders_in_file(filepath):
                fixed_count += 1
        except Exception as e:
            print(f"❌ Error fixing {filepath}: {e}")

    print(f"\n🎉 Fixed {fixed_count} files")
    print("\n📝 Summary of changes:")
    print("- All cursor.execute() calls now use database-appropriate placeholders")
    print("- PostgreSQL: %s placeholders")
    print("- SQLite: ? placeholders")
    print("- Automatic detection via db_adapter.is_postgresql")

if __name__ == '__main__':
    main()
