#!/usr/bin/env python3
"""
Async Migration Script for Scorpius Backend
Automatically migrates sync database operations to async patterns
Task 11: Backend Consistency
"""

import os
import re
import ast
import argparse
from pathlib import Path
from typing import List, Dict, Tuple


class AsyncMigrator:
    """Migrates synchronous database code to async patterns"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_modified = 0
        
        # Migration patterns: (sync_pattern, async_replacement, needs_await)
        self.migration_patterns = [
            # Session operations
            (r'session\.execute\(', 'await session.execute(', True),
            (r'session\.commit\(\)', 'await session.commit()', True),
            (r'session\.rollback\(\)', 'await session.rollback()', True),
            (r'session\.flush\(\)', 'await session.flush()', True),
            (r'session\.merge\(', 'await session.merge(', True),
            (r'session\.delete\(', 'await session.delete(', True),
            
            # Query operations
            (r'\.all\(\)', '.fetchall()', False),
            (r'\.first\(\)', '.fetchone()', False),
            (r'\.scalar\(\)', '.scalar()', False),
            
            # Session creation
            (r'from sqlalchemy\.orm import Session', 
             'from sqlalchemy.ext.asyncio import AsyncSession', False),
            (r'from sqlalchemy\.orm import sessionmaker',
             'from sqlalchemy.ext.asyncio import async_sessionmaker', False),
            (r'Session\(', 'AsyncSession(', False),
            (r'sessionmaker\(', 'async_sessionmaker(', False),
            
            # Engine creation
            (r'create_engine\(', 'create_async_engine(', False),
            (r'from sqlalchemy import create_engine',
             'from sqlalchemy.ext.asyncio import create_async_engine', False),
            
            # Context managers
            (r'with session\b', 'async with session', False),
        ]
        
        # Import additions needed for async
        self.async_imports = [
            'from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker',
            'import asyncio',
        ]
    
    def analyze_file(self, file_path: Path) -> Dict[str, List[dict]]:
        """Analyze a file for sync database operations"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return {}
        
        issues = {
            'sync_operations': [],
            'missing_async_imports': [],
            'function_needs_async': []
        }
        
        lines = content.split('\n')
        
        # Check each line for sync patterns
        for i, line in enumerate(lines, 1):
            for sync_pattern, _, _ in self.migration_patterns:
                if re.search(sync_pattern, line):
                    issues['sync_operations'].append({
                        'line': i,
                        'content': line.strip(),
                        'pattern': sync_pattern
                    })
        
        # Check for missing async imports
        if any('session.' in line for line in lines):
            has_async_import = any(
                'AsyncSession' in line or 'async_sessionmaker' in line
                for line in lines
            )
            if not has_async_import:
                issues['missing_async_imports'].append({
                    'suggestion': 'Add: from sqlalchemy.ext.asyncio import AsyncSession'
                })
        
        # Analyze AST for functions that need to be async
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if function has database operations but isn't async
                    has_db_ops = self._function_has_db_operations(node, content)
                    if has_db_ops and not self._is_async_function(node):
                        issues['function_needs_async'].append({
                            'function': node.name,
                            'line': node.lineno
                        })
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return issues
    
    def _function_has_db_operations(self, func_node: ast.FunctionDef, content: str) -> bool:
        """Check if function contains database operations"""
        func_lines = content.split('\n')[func_node.lineno-1:func_node.end_lineno]
        func_content = '\n'.join(func_lines)
        
        db_patterns = [
            r'session\.',
            r'\.execute\(',
            r'\.commit\(',
            r'\.query\(',
            r'\.all\(',
            r'\.first\(',
        ]
        
        return any(re.search(pattern, func_content) for pattern in db_patterns)
    
    def _is_async_function(self, node: ast.FunctionDef) -> bool:
        """Check if function is already async"""
        return isinstance(node, ast.AsyncFunctionDef)
    
    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single file to async patterns"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
        except (UnicodeDecodeError, PermissionError):
            return False
        
        modified_content = original_content
        changes_in_file = 0
        
        # Apply migration patterns
        for sync_pattern, async_replacement, needs_await in self.migration_patterns:
            if re.search(sync_pattern, modified_content):
                modified_content = re.sub(sync_pattern, async_replacement, modified_content)
                changes_in_file += 1
        
        # Add async imports if needed
        needs_async_imports = any(
            pattern in modified_content
            for pattern in ['AsyncSession', 'async_sessionmaker', 'create_async_engine']
        )
        
        if needs_async_imports and 'from sqlalchemy.ext.asyncio' not in modified_content:
            # Add imports after existing imports
            lines = modified_content.split('\n')
            import_line_idx = 0
            
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_line_idx = i + 1
            
            lines.insert(import_line_idx, 'from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine')
            modified_content = '\n'.join(lines)
            changes_in_file += 1
        
        # Write changes if not dry run
        if changes_in_file > 0:
            if not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                print(f"✅ Migrated {file_path} ({changes_in_file} changes)")
            else:
                print(f"🔍 Would migrate {file_path} ({changes_in_file} changes)")
            
            self.changes_made += changes_in_file
            self.files_modified += 1
            return True
        
        return False
    
    def scan_directory(self, directory: Path) -> Dict[str, List[dict]]:
        """Scan directory for files needing migration"""
        all_issues = {}
        
        for py_file in directory.rglob("*.py"):
            # Skip test files, deprecated files, and migration scripts
            if any(skip in str(py_file) for skip in [
                'test_', 'deprecated_', 'old_', '_old.py', 'fix_', 'migration'
            ]):
                continue
            
            issues = self.analyze_file(py_file)
            if any(issues.values()):
                all_issues[str(py_file)] = issues
        
        return all_issues
    
    def migrate_directory(self, directory: Path) -> None:
        """Migrate all files in directory"""
        print(f"🔄 {'Analyzing' if self.dry_run else 'Migrating'} {directory}")
        
        for py_file in directory.rglob("*.py"):
            # Skip files that shouldn't be migrated
            if any(skip in str(py_file) for skip in [
                'test_', 'deprecated_', 'old_', '_old.py', 'fix_', 'migration'
            ]):
                continue
            
            self.migrate_file(py_file)
        
        print(f"\n📊 Summary:")
        print(f"   Files modified: {self.files_modified}")
        print(f"   Total changes: {self.changes_made}")
    
    def generate_report(self, issues: Dict[str, List[dict]]) -> str:
        """Generate a migration report"""
        report = ["# Async Migration Report", ""]
        
        total_files = len(issues)
        total_operations = sum(len(file_issues['sync_operations']) for file_issues in issues.values())
        total_functions = sum(len(file_issues['function_needs_async']) for file_issues in issues.values())
        
        report.extend([
            f"## Summary",
            f"- Files with sync operations: {total_files}",
            f"- Total sync operations found: {total_operations}",
            f"- Functions needing async conversion: {total_functions}",
            ""
        ])
        
        for file_path, file_issues in issues.items():
            if any(file_issues.values()):
                report.append(f"### {file_path}")
                
                if file_issues['sync_operations']:
                    report.append("**Sync Operations:**")
                    for op in file_issues['sync_operations']:
                        report.append(f"- Line {op['line']}: `{op['content']}`")
                
                if file_issues['function_needs_async']:
                    report.append("**Functions needing async:**")
                    for func in file_issues['function_needs_async']:
                        report.append(f"- `{func['function']}()` at line {func['line']}")
                
                if file_issues['missing_async_imports']:
                    report.append("**Missing imports:**")
                    for imp in file_issues['missing_async_imports']:
                        report.append(f"- {imp['suggestion']}")
                
                report.append("")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Migrate sync database code to async patterns")
    parser.add_argument("--directory", "-d", type=str, default="backend", 
                       help="Directory to scan/migrate (default: backend)")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Only analyze, don't modify files (default)")
    parser.add_argument("--apply", action="store_true",
                       help="Apply migrations (opposite of --dry-run)")
    parser.add_argument("--report", "-r", type=str,
                       help="Generate report file (analysis only)")
    
    args = parser.parse_args()
    
    # Determine if we should apply changes
    dry_run = not args.apply
    
    directory = Path(args.directory)
    if not directory.exists():
        print(f"❌ Directory {directory} does not exist")
        return 1
    
    migrator = AsyncMigrator(dry_run=dry_run)
    
    if args.report:
        # Generate analysis report
        print("📋 Generating migration analysis report...")
        issues = migrator.scan_directory(directory)
        report = migrator.generate_report(issues)
        
        with open(args.report, 'w') as f:
            f.write(report)
        
        print(f"📄 Report saved to {args.report}")
        
        # Also print summary
        total_files = len(issues)
        if total_files > 0:
            print(f"\n⚠️  Found {total_files} files with sync database operations")
            print("Run with --apply to migrate them to async patterns")
        else:
            print("\n✅ No sync database operations found!")
    
    else:
        # Perform migration
        migrator.migrate_directory(directory)
        
        if dry_run:
            print("\n💡 This was a dry run. Use --apply to make actual changes.")
        else:
            print("\n✅ Migration completed!")
            print("🧪 Run tests to verify: pytest backend/tests/test_async_compliance.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
