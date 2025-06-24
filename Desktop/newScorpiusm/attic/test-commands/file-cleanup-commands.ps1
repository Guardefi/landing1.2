# File Cleanup and Organization Commands
# Commands for cleaning up unused files and organizing the codebase

Write-Host "🧹 File Cleanup Commands" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

Write-Host "`n📋 Available Commands:" -ForegroundColor Green

Write-Host "`n1. Analyze unused Python files:" -ForegroundColor Yellow
Write-Host "   python -c `"
import os
import ast
from pathlib import Path

def find_python_files():
    files = list(Path('backend').rglob('*.py'))
    return files

def check_imports(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        return imports
    except:
        return []

files = find_python_files()
print(f'Found {len(files)} Python files')
`"" -ForegroundColor Gray

Write-Host "`n2. Clean up unused files (safe deletions):" -ForegroundColor Yellow
Write-Host "   .\scripts\cleanup-unused-files.ps1" -ForegroundColor Gray

Write-Host "`n3. Check for broken imports after cleanup:" -ForegroundColor Yellow
Write-Host "   python -m py_compile backend\*.py" -ForegroundColor Gray

Write-Host "`n4. Search for specific file references:" -ForegroundColor Yellow
Write-Host "   Select-String -Path 'backend\*.py' -Pattern 'filename_to_check'" -ForegroundColor Gray

Write-Host "`n5. Find duplicate code patterns:" -ForegroundColor Yellow
Write-Host "   ruff check backend\ --select=F401,F811 # unused imports and redefined names" -ForegroundColor Gray

Write-Host "`n6. Analyze file sizes and complexity:" -ForegroundColor Yellow
Write-Host "   Get-ChildItem backend\*.py -Recurse | Sort-Object Length -Descending | Select-Object Name,Length,LastWriteTime | Format-Table" -ForegroundColor Gray

Write-Host "`n🎯 Recommended Cleanup Workflow:" -ForegroundColor Green
Write-Host "1. Run analysis to identify unused files" -ForegroundColor White
Write-Host "2. Execute safe cleanup script" -ForegroundColor White
Write-Host "3. Check for broken imports" -ForegroundColor White
Write-Host "4. Run tests to ensure functionality" -ForegroundColor White
Write-Host "5. Review MEV components for integration" -ForegroundColor White

Write-Host "`n⚠️  Always backup before running cleanup commands!" -ForegroundColor Red
