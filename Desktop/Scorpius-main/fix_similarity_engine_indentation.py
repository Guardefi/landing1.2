#!/usr/bin/env python3
"""
Targeted Fix for SimilarityEngine Indentation Issues
Fixes the specific indentation pattern causing most failures
"""

import re
from pathlib import Path

def fix_globals_similarity_engine_indentation(content):
    """Fix specific indentation issue with SimilarityEngine in globals().update()"""
    lines = content.split('\n')
    fixed_lines = []
    
    in_globals_block = False
    globals_base_indent = 0
    
    for i, line in enumerate(lines):
        # Detect start of globals().update() block
        if 'globals().update(' in line and '{' in line:
            in_globals_block = True
            globals_base_indent = len(line) - len(line.lstrip())
            fixed_lines.append(line)
            continue
        
        # Detect end of globals().update() block
        if in_globals_block and line.strip() == '})':
            in_globals_block = False
            # Ensure proper indentation for closing
            fixed_lines.append(' ' * globals_base_indent + '})')
            continue
        
        # Fix indentation within the globals block
        if in_globals_block and line.strip():
            # Check for the specific problematic patterns
            if ("'SimilarityEngine':" in line or 
                "'MultiDimensionalComparison':" in line or
                "'TestClient':" in line or
                "'BytecodeNormalizer':" in line):
                
                # Force correct indentation (base + 4 spaces)
                content_part = line.strip()
                correct_line = ' ' * (globals_base_indent + 4) + content_part
                fixed_lines.append(correct_line)
            else:
                # For other lines in globals block, ensure consistent indentation
                if line.strip() and not line.strip().startswith('#'):
                    content_part = line.strip()
                    correct_line = ' ' * (globals_base_indent + 4) + content_part
                    fixed_lines.append(correct_line)
                else:
                    fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def process_file(file_path):
    """Process a single test file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply the targeted fix
        content = fix_globals_similarity_engine_indentation(content)
        
        # Only write if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed SimilarityEngine indentation"
        else:
            return True, "No indentation issues found"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Fix SimilarityEngine indentation in all test files"""
    
    # Target the specific files mentioned in the error output
    problematic_files = [
        "backend/Bytecode/tests/test_normalizer.py",
        "backend/decorators/tests/test_decorators.py", 
        "backend/honeypot/test_comprehensive.py",
        "backend/honeypot/tests/test_honeypot.py",
        "backend/honeypot/tests/test_risk_level.py",
        "backend/honeypot/tests/test_static_engine.py",
        "backend/mempool/test_api_startup.py",
        "backend/mempool/test_database_api.py",
        # Add more as identified
    ]
    
    # Also find all Python test files
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
    
    print(f"🔧 Fixing SimilarityEngine indentation in {len(test_files)} test files...")
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
    print(f"🎯 SIMILARITY ENGINE INDENTATION FIX SUMMARY")
    print(f"Total files processed: {len(test_files)}")
    print(f"Files fixed: {fixed_count}")
    print(f"Errors: {error_count}")
    print(f"Success rate: {(len(test_files) - error_count) / len(test_files) * 100:.1f}%")

if __name__ == "__main__":
    main() 