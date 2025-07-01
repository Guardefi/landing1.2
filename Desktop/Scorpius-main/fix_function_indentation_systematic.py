#!/usr/bin/env python3
"""
Systematic Fix: Function Indentation Errors
Fixes the specific pattern where class definitions follow function definitions without proper indentation
"""

import os
import re
from pathlib import Path

def fix_function_indentation_error(file_path):
    """Fix function indentation issues - specifically class Result after function definitions"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        if not content.strip():
            return False
            
        original_content = content
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for function definition pattern
            if re.match(r'^\s*(async def|def)\s+\w+.*:\s*$', line):
                fixed_lines.append(line)
                i += 1
                
                # Check the next non-empty line
                while i < len(lines):
                    next_line = lines[i]
                    
                    if next_line.strip() == '':
                        fixed_lines.append(next_line)
                        i += 1
                        continue
                    
                    # If it's "class Result:" or similar, it should be indented
                    if re.match(r'^class\s+\w+.*:\s*$', next_line.strip()):
                        # Add proper indentation (8 spaces for nested class)
                        fixed_lines.append('        ' + next_line.strip())
                        i += 1
                        
                        # Handle the class body
                        while i < len(lines):
                            class_line = lines[i]
                            
                            if class_line.strip() == '':
                                fixed_lines.append(class_line)
                                i += 1
                                continue
                            
                            # Check if this line is part of the class body
                            stripped = class_line.strip()
                            if (stripped.startswith(('similarity_score', 'confidence', 'processing_time', 'status_code')) or
                                stripped in ['return Result()', 'pass'] or
                                re.match(r'def\s+\w+', stripped)):
                                # Indent as class body (12 spaces)
                                fixed_lines.append('            ' + stripped)
                                i += 1
                            else:
                                # Not part of class body, break and continue
                                break
                        
                        # Add return statement if missing
                        if i < len(lines) and 'return' not in lines[i-1]:
                            fixed_lines.append('        return Result()')
                        break
                    else:
                        # Regular line after function, keep as is
                        fixed_lines.append(next_line)
                        i += 1
                        break
            else:
                # Not a function definition, keep as is
                fixed_lines.append(line)
                i += 1
        
        fixed_content = '\n'.join(fixed_lines)
        
        # Only write if changes were made
        if fixed_content != original_content:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(fixed_content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def find_files_with_indentation_errors():
    """Find Python test files that likely have the indentation error"""
    project_root = Path(__file__).parent
    test_files = []
    
    # Search for test files in common directories
    test_dirs = ['tests', 'backend', 'packages', 'services', 'reporting', 'monitoring']
    
    for test_dir in test_dirs:
        dir_path = project_root / test_dir
        if dir_path.exists():
            # Find all Python test files
            for pattern in ['test_*.py', '*_test.py', '*test*.py']:
                test_files.extend(list(dir_path.rglob(pattern)))
    
    return list(set(test_files))  # Remove duplicates

def main():
    """Main execution function"""
    print(">> Systematic Function Indentation Fix")
    print("=" * 50)
    
    test_files = find_files_with_indentation_errors()
    total_files = len(test_files)
    processed_files = 0
    fixed_files = 0
    
    for file_path in test_files:
        try:
            if fix_function_indentation_error(file_path):
                relative_path = str(file_path).replace(str(Path(__file__).parent), '').lstrip('\\/')
                print(f"[FIXED] {relative_path}")
                fixed_files += 1
            processed_files += 1
        except Exception as e:
            relative_path = str(file_path).replace(str(Path(__file__).parent), '').lstrip('\\/')
            print(f"[ERROR] {relative_path}: {e}")
    
    print(f"\n[SUMMARY] Processed {processed_files}/{total_files} files")
    print(f"[SUMMARY] Fixed {fixed_files} files with function indentation issues")
    print(f"[SUMMARY] Success rate: {(processed_files/total_files)*100 if total_files > 0 else 0:.1f}%")
    
    return fixed_files

if __name__ == "__main__":
    fixed_count = main()
    print(f"\n[COMPLETE] Fixed {fixed_count} files with function indentation issues")
