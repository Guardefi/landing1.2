#!/usr/bin/env python3
"""
Targeted Fix for Indentation Errors
Fixes the specific 'SimilarityEngine': MockSimilarityEngine indentation pattern
"""

import re
from pathlib import Path
import glob

def fix_globals_indentation(content):
    """Fix indentation in globals().update() calls"""
    lines = content.split('\n')
    fixed_lines = []
    
    in_globals_block = False
    base_indent = 0
    
    for i, line in enumerate(lines):
        # Detect start of globals().update() block
        if 'globals().update(' in line:
            in_globals_block = True
            base_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Detect end of globals().update() block
        if in_globals_block and line.strip() == '})':
            in_globals_block = False
            # Fix the closing brace indentation
            fixed_lines.append(' ' * base_indent + '})')
            continue
        
        # Fix indentation within the globals block
        if in_globals_block and line.strip():
            # Common patterns to fix
            if ("'SimilarityEngine':" in line or 
                "'MultiDimensionalComparison':" in line or
                "'TestClient':" in line or
                "'BytecodeNormalizer':" in line):
                
                # Ensure proper indentation (base + 4 spaces)
                content_part = line.strip()
                fixed_line = ' ' * (base_indent + 4) + content_part
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_bracket_mismatches(content):
    """Fix common bracket mismatch patterns"""
    # Fix pattern: } at end of list that should be ]
    content = re.sub(r'(\s+)\}\s*$', r'\1]', content, flags=re.MULTILINE)
    
    # Fix pattern: ] at end of dict that should be }
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Look for lines that end with ] but are likely dict endings
        if (line.strip() == ']' and i > 0 and 
            any('{' in lines[j] for j in range(max(0, i-10), i)) and
            sum(line.count('{') for line in lines[max(0, i-10):i]) > 
            sum(line.count('}') for line in lines[max(0, i-10):i])):
            # Replace ] with }
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(' ' * indent + '}')
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_file(file_path):
    """Process a single test file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_globals_indentation(content)
        content = fix_bracket_mismatches(content)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed indentation and brackets"
        else:
            return True, "No changes needed"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Fix indentation errors in all test files"""
    
    # Find all Python test files
    test_patterns = [
        "**/test_*.py",
        "**/*_test.py", 
        "**/tests/*.py",
        "**/tests/**/*.py"
    ]
    
    test_files = set()
    for pattern in test_patterns:
        test_files.update(Path('.').rglob(pattern))
    
    # Filter out backup files and excluded patterns
    excluded = ['fix_', 'test_runner', '.backup', '__pycache__']
    test_files = [f for f in test_files if not any(ex in str(f) for ex in excluded)]
    
    print(f"🔧 Fixing indentation errors in {len(test_files)} test files...")
    print("=" * 60)
    
    fixed_count = 0
    error_count = 0
    
    for i, test_file in enumerate(sorted(test_files), 1):
        print(f"[{i:2d}/{len(test_files):2d}] Processing: {test_file.name}")
        
        success, message = process_file(test_file)
        
        if success:
            if "Fixed" in message:
                fixed_count += 1
                print(f"  ✓ {message}")
            else:
                print(f"  - {message}")
        else:
            error_count += 1
            print(f"  ✗ {message}")
    
    print("\n" + "=" * 60)
    print(f"🎯 INDENTATION FIX SUMMARY")
    print(f"Total files processed: {len(test_files)}")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {(len(test_files) - error_count) / len(test_files) * 100:.1f}%")

if __name__ == "__main__":
    main() 