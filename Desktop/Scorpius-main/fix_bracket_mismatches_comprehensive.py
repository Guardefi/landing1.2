#!/usr/bin/env python3
"""
Comprehensive Bracket Mismatch Fix Script
Addresses all bracket/parenthesis mismatch patterns identified in test output
"""

import re
from pathlib import Path

def fix_bracket_mismatches(content):
    """Fix various bracket mismatch patterns"""
    lines = content.split('\n')
    fixed_lines = []
    
    bracket_stack = []
    brace_stack = []
    paren_stack = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Count brackets in this line
        open_brackets = line.count('[')
        close_brackets = line.count(']')
        open_braces = line.count('{')
        close_braces = line.count('}')
        open_parens = line.count('(')
        close_parens = line.count(')')
        
        # Fix specific common patterns
        
        # Pattern 1: Closing brace } instead of closing bracket ]
        if (line.strip() == '}' and 
            len([l for l in lines[max(0, i-20):i] if '[' in l]) > 
            len([l for l in lines[max(0, i-20):i] if ']' in l])):
            indent = len(line) - len(line.lstrip())
            line = ' ' * indent + ']'
        
        # Pattern 2: Closing bracket ] instead of closing brace }
        elif (line.strip() == ']' and 
              len([l for l in lines[max(0, i-20):i] if '{' in l]) > 
              len([l for l in lines[max(0, i-20):i] if '}' in l])):
            indent = len(line) - len(line.lstrip())
            line = ' ' * indent + '}'
        
        # Pattern 3: Mixed bracket/brace in same line
        elif ']' in line and '}' in line:
            # Check context to determine correct bracket type
            recent_lines = lines[max(0, i-10):i]
            open_context_brackets = sum(l.count('[') for l in recent_lines)
            close_context_brackets = sum(l.count(']') for l in recent_lines)
            open_context_braces = sum(l.count('{') for l in recent_lines)
            close_context_braces = sum(l.count('}') for l in recent_lines)
            
            # If we have more open brackets than closed, prioritize closing brackets
            if open_context_brackets > close_context_brackets:
                line = line.replace('}', ']')
            elif open_context_braces > close_context_braces:
                line = line.replace(']', '}')
        
        # Pattern 4: Fix specific error patterns from test output
        # '}' does not match opening '[' 
        if i > 0 and line.strip() == '}':
            # Look back for unmatched opening bracket
            for j in range(i-1, max(-1, i-20), -1):
                if '[' in lines[j] and ']' not in lines[j]:
                    indent = len(line) - len(line.lstrip())
                    line = ' ' * indent + ']'
                    break
        
        # Pattern 5: ']' does not match opening '{'
        elif i > 0 and line.strip() == ']':
            # Look back for unmatched opening brace
            for j in range(i-1, max(-1, i-20), -1):
                if '{' in lines[j] and '}' not in lines[j]:
                    indent = len(line) - len(line.lstrip())
                    line = ' ' * indent + '}'
                    break
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_unterminated_strings(content):
    """Fix unterminated triple-quoted strings"""
    lines = content.split('\n')
    fixed_lines = []
    
    in_triple_quote = False
    quote_type = None
    
    for i, line in enumerate(lines):
        # Check for triple quotes
        if '"""' in line:
            triple_count = line.count('"""')
            if triple_count % 2 == 1:  # Odd number means opening or closing
                if not in_triple_quote:
                    in_triple_quote = True
                    quote_type = '"""'
                else:
                    in_triple_quote = False
                    quote_type = None
        
        # If we're at the end of file and still in a triple quote, close it
        if i == len(lines) - 1 and in_triple_quote:
            if line.strip() and not line.strip().endswith('"""'):
                line += '\n"""'
            elif not line.strip():
                line = '"""'
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_unmatched_parentheses(content):
    """Fix unmatched parentheses patterns"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix pattern: patch("...") followed by ) on next line
        if (i < len(lines) - 1 and 
            'patch(' in line and 
            lines[i + 1].strip().startswith(') as ')):
            # Remove the extra closing paren from the patch line
            if line.rstrip().endswith(')'):
                # Check if this is the extra parenthesis
                open_count = line.count('(')
                close_count = line.count(')')
                if close_count > open_count:
                    line = line.rstrip()[:-1]  # Remove last character if it's )
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_file(file_path):
    """Process a single test file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes in order
        content = fix_bracket_mismatches(content)
        content = fix_unterminated_strings(content)
        content = fix_unmatched_parentheses(content)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed bracket mismatches"
        else:
            return True, "No bracket issues found"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Fix bracket mismatches in all test files"""
    
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
    
    print(f"🔧 Fixing bracket mismatches in {len(test_files)} test files...")
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
    print(f"🎯 BRACKET MISMATCH FIX SUMMARY")
    print(f"Total files processed: {len(test_files)}")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {(len(test_files) - error_count) / len(test_files) * 100:.1f}%")

if __name__ == "__main__":
    main() 