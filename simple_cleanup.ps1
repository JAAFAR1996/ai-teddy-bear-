# Simple AI Teddy Bear Project Cleanup Script
param(
    [switch]$DryRun = $false
)

Write-Host "AI Teddy Bear Project Cleanup" -ForegroundColor Cyan
Write-Host "============================" -ForegroundColor Cyan

$totalFiles = 0
$totalSpace = 0

function Remove-FileWithStats {
    param([string]$Path, [string]$Reason)
    
    if (Test-Path $Path) {
        try {
            $size = (Get-Item $Path).Length
            $script:totalSpace += $size
            $script:totalFiles++
            
            if ($DryRun) {
                Write-Host "[DRY RUN] Will delete: $Path ($Reason)" -ForegroundColor Yellow
            } else {
                Remove-Item $Path -Force -Recurse
                Write-Host "Deleted: $Path" -ForegroundColor Green
            }
        } catch {
            Write-Host "Error deleting: $Path" -ForegroundColor Red
        }
    }
}

Write-Host "`nCleaning demo files..." -ForegroundColor Yellow

$demoFiles = @(
    "scripts\demo_distributed_ai.py",
    "scripts\demo_edge_ai.py",
    "scripts\demo_multi_layer_cache.py",
    "src\dashboards\dashboard-demo.tsx",
    "src\dashboards\dashboard-demo-runner.py",
    "src\testing\quick_demo.py",
    "tests\ai_test_demo.py",
    "src\compliance\compliance_demo.py"
)

foreach ($file in $demoFiles) {
    Remove-FileWithStats -Path $file -Reason "Demo file"
}

Write-Host "`nCleaning report files..." -ForegroundColor Yellow

$reportFiles = @(
    "ai_testing_demo_report.json",
    "advanced_streaming_refactoring_report.md",
    "cleanup_analysis_report.md",
    "code_cleanup_report.md"
)

foreach ($file in $reportFiles) {
    Remove-FileWithStats -Path $file -Reason "Generated report"
}

Write-Host "`nCleaning analysis scripts..." -ForegroundColor Yellow

$analysisFiles = @(
    "scripts\advanced_deep_analyzer.py",
    "scripts\comprehensive_project_analyzer.py",
    "scripts\find_exact_duplicates.py",
    "scripts\quick_cleanup_analyzer.py"
)

foreach ($file in $analysisFiles) {
    Remove-FileWithStats -Path $file -Reason "Analysis script"
}

Write-Host "`nCleaning temporary files..." -ForegroundColor Yellow

Get-ChildItem -Path . -Filter "*.pyc" -Recurse | ForEach-Object {
    Remove-FileWithStats -Path $_.FullName -Reason "Python cache"
}

Get-ChildItem -Path . -Filter "*.log" -Recurse | ForEach-Object {
    Remove-FileWithStats -Path $_.FullName -Reason "Log file"
}

$spaceMB = [math]::Round($totalSpace / 1MB, 2)

Write-Host "`nCleanup Summary:" -ForegroundColor Green
Write-Host "Files processed: $totalFiles" -ForegroundColor White
Write-Host "Space freed: $spaceMB MB" -ForegroundColor White

if ($DryRun) {
    Write-Host "`nThis was a dry run - no files were actually deleted" -ForegroundColor Cyan
} else {
    Write-Host "`nCleanup completed successfully!" -ForegroundColor Green
} 