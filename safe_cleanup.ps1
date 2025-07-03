# 🧹 AI Teddy Bear - Safe Project Cleanup Script
# تنظيف آمن ومستهدف للمشروع
# يحذف فقط الملفات المؤكدة الآمانة

param(
    [switch]$DryRun = $false,
    [switch]$CreateBackup = $true
)

Write-Host "🧸 AI Teddy Bear - Safe Project Cleanup" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$totalFiles = 0
$totalSpace = 0
$startTime = Get-Date

# إنشاء نسخة احتياطية للملفات المهمة
if ($CreateBackup -and -not $DryRun) {
    $backupDir = "project_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Write-Host "📦 Creating backup: $backupDir" -ForegroundColor Yellow
    
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # نسخ الملفات المهمة فقط
    $importantPaths = @("src/main.py", "requirements.txt", "config/")
    foreach ($path in $importantPaths) {
        if (Test-Path $path) {
            $dest = Join-Path $backupDir $path
            $destDir = Split-Path $dest -Parent
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item $path $dest -Recurse -Force
        }
    }
    Write-Host "✅ Backup created successfully" -ForegroundColor Green
}

function Remove-SafeFile {
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
                Write-Host "✅ Deleted: $Path" -ForegroundColor Green
            }
        } catch {
            Write-Host "❌ Error deleting: $Path" -ForegroundColor Red
        }
    }
}

Write-Host "`n🗑️  Starting safe cleanup..." -ForegroundColor Cyan

# 1. حذف ملفات Demo المؤكدة
Write-Host "`n1️⃣ Removing confirmed demo files..." -ForegroundColor Yellow

$confirmedDemoFiles = @(
    "scripts\demo_distributed_ai.py",
    "scripts\demo_edge_ai.py",
    "scripts\demo_multi_layer_cache.py",
    "src\dashboards\dashboard-demo.tsx",
    "src\dashboards\dashboard-demo-runner.py",
    "src\testing\quick_demo.py",
    "tests\ai_test_demo.py",
    "src\compliance\compliance_demo.py",
    "src\application\services\audio\voice_service_demo.py",
    "src\presentation\api\graphql\demo_graphql_federation.py",
    "src\infrastructure\observability\demo_results_summary.py",
    "src\ml\continuous_learning\continuous_learning_demo.py",
    "src\infrastructure\observability\observability_demo.py"
)

foreach ($file in $confirmedDemoFiles) {
    Remove-SafeFile -Path $file -Reason "Demo file"
}

# 2. حذف التقارير المولدة تلقائياً
Write-Host "`n2️⃣ Removing auto-generated reports..." -ForegroundColor Yellow

$reportFiles = @(
    "ai_testing_demo_report.json",
    "advanced_streaming_refactoring_report.md",
    "code_cleanup_report.md",
    "streaming_service_refactoring_report.md"
)

foreach ($file in $reportFiles) {
    Remove-SafeFile -Path $file -Reason "Generated report"
}

# 3. حذف ملفات Python Cache (الأكثر أماناً)
Write-Host "`n3️⃣ Removing Python cache files..." -ForegroundColor Yellow

# حذف ملفات .pyc بأمان (تجنب ملفات المشروع الأساسية)
Get-ChildItem -Path "venv" -Filter "*.pyc" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-SafeFile -Path $_.FullName -Reason "Python cache (venv)"
}

Get-ChildItem -Path ".venv" -Filter "*.pyc" -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-SafeFile -Path $_.FullName -Reason "Python cache (.venv)"
}

# حذف مجلدات __pycache__ في venv فقط
Get-ChildItem -Path "venv" -Name "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $fullPath = Join-Path "venv" $_
    Remove-SafeFile -Path $fullPath -Reason "Python cache directory (venv)"
}

Get-ChildItem -Path ".venv" -Name "__pycache__" -Recurse -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $fullPath = Join-Path ".venv" $_
    Remove-SafeFile -Path $fullPath -Reason "Python cache directory (.venv)"
}

# 4. حذف ملفات Log القديمة
Write-Host "`n4️⃣ Removing old log files..." -ForegroundColor Yellow

Get-ChildItem -Path "logs" -Filter "*.log" -ErrorAction SilentlyContinue | ForEach-Object {
    # حذف ملفات اللوج الأقدم من أسبوع
    if ($_.LastWriteTime -lt (Get-Date).AddDays(-7)) {
        Remove-SafeFile -Path $_.FullName -Reason "Old log file"
    }
}

# 5. حذف ملفات مؤقتة آمنة أخرى
Write-Host "`n5️⃣ Removing other safe temporary files..." -ForegroundColor Yellow

$safeTempFiles = @("*.tmp", "*.temp", "*.bak", "*.old")

foreach ($pattern in $safeTempFiles) {
    Get-ChildItem -Path . -Filter $pattern -Recurse -ErrorAction SilentlyContinue | ForEach-Object {
        # تجنب ملفات النظام المهمة
        if ($_.FullName -notmatch "(src\\main|config\\|requirements)" -and 
            $_.FullName -notmatch "(venv\\Scripts|\.venv\\Scripts)") {
            Remove-SafeFile -Path $_.FullName -Reason "Temporary file"
        }
    }
}

# 6. إحصائيات النهاية
$endTime = Get-Date
$duration = $endTime - $startTime
$spaceMB = [math]::Round($totalSpace / 1MB, 2)

Write-Host "`n🎉 Safe cleanup completed!" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host "📊 Statistics:" -ForegroundColor Cyan
Write-Host "  • Files processed: $totalFiles" -ForegroundColor White
Write-Host "  • Space freed: $spaceMB MB" -ForegroundColor White
Write-Host "  • Duration: $($duration.TotalSeconds) seconds" -ForegroundColor White

if ($DryRun) {
    Write-Host "`n🔍 This was a dry run - no files were actually deleted" -ForegroundColor Cyan
    Write-Host "Run without -DryRun to perform actual cleanup" -ForegroundColor Cyan
} else {
    Write-Host "`n✅ Project is now cleaner and more efficient!" -ForegroundColor Green
}

# 7. فحص سلامة المشروع
Write-Host "`n🔍 Project integrity check..." -ForegroundColor Yellow

$criticalFiles = @("src\main.py", "requirements.txt", "src\__init__.py")
$allCritical = $true

foreach ($file in $criticalFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file - OK" -ForegroundColor Green
    } else {
        Write-Host "⚠️  $file - Missing" -ForegroundColor Red
        $allCritical = $false
    }
}

if ($allCritical) {
    Write-Host "`n✅ All critical files are intact - Project is safe!" -ForegroundColor Green
} else {
    Write-Host "`n⚠️  Some critical files are missing - Check backup!" -ForegroundColor Red
}

Write-Host "`nCleanup finished successfully!" -ForegroundColor Cyan 