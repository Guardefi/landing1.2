# Cleanup Script for Unused Python Files
# This script safely deletes clearly unused/duplicate files

Write-Host "🧹 Scorpius Codebase Cleanup - Removing Unused Files" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Files to delete (safe deletions - duplicates and deprecated)
$filesToDelete = @(
    "backend\deprecated_flask\scorpius_backend.py",
    "backend\scorpius_backend.py",
    "backend\routes\mempool_routes_old.py",
    "backend\routes\mev_routes_old.py",
    "backend\routes\mempool_routes_new.py",
    "backend\routes\mev_routes_new.py",
    "backend\utils\backend\verify_backend.py",
    "backend\utils\backend\jobs\job_worker.py",
    "backend\utils\backend\jobs\task_orchestrator.py",
    "backend\jobs\job_worker.py",
    "backend\jobs\task_orchestrator.py"
)

$deletedCount = 0
$errorCount = 0

foreach ($file in $filesToDelete) {
    $fullPath = Join-Path $PWD $file

    if (Test-Path $fullPath) {
        try {
            Write-Host "🗑️  Deleting: $file" -ForegroundColor Yellow
            Remove-Item $fullPath -Force
            $deletedCount++
        }
        catch {
            Write-Host "❌ Error deleting $file : $_" -ForegroundColor Red
            $errorCount++
        }
    }
    else {
        Write-Host "⚠️  File not found: $file" -ForegroundColor Gray
    }
}

Write-Host "`n📊 Cleanup Summary:" -ForegroundColor Green
Write-Host "✅ Files deleted: $deletedCount" -ForegroundColor Green
Write-Host "❌ Errors: $errorCount" -ForegroundColor Red
Write-Host "⚠️  Files not found: $($filesToDelete.Count - $deletedCount - $errorCount)" -ForegroundColor Yellow

if ($deletedCount -gt 0) {
    Write-Host "`n🎉 Codebase cleanup completed successfully!" -ForegroundColor Green
    Write-Host "💡 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Review MEV bot components for integration" -ForegroundColor White
    Write-Host "   2. Check remaining test files for value" -ForegroundColor White
    Write-Host "   3. Run tests to ensure no broken imports" -ForegroundColor White
}

# Check for any remaining imports of deleted files
Write-Host "`n🔍 Checking for references to deleted files..." -ForegroundColor Cyan

$checkFiles = @(
    "scorpius_backend",
    "mempool_routes_old",
    "mev_routes_old",
    "job_worker"
)

foreach ($checkFile in $checkFiles) {
    $results = Select-String -Path "backend\*.py" -Pattern $checkFile -ErrorAction SilentlyContinue
    if ($results) {
        Write-Host "⚠️  Found references to '$checkFile':" -ForegroundColor Yellow
        $results | ForEach-Object { Write-Host "   $($_.Filename):$($_.LineNumber)" -ForegroundColor Gray }
    }
}

Write-Host "`n✨ Cleanup script completed!" -ForegroundColor Green
