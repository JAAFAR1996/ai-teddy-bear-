# 🧹 AI Teddy Bear Project Cleanup Script
# تنظيف شامل وآمن للمشروع
# المسؤول: Senior Software Engineer

param(
    [switch]$DryRun = $false,
    [switch]$Force = $false,
    [string]$BackupPath = "project_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
)

# إعداد اللوان والعرض
$host.UI.RawUI.WindowTitle = "AI Teddy Bear Project Cleanup"
Write-Host "🧸 AI Teddy Bear Project Cleanup Script" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan

# متغيرات الإحصائيات
$totalFilesDeleted = 0
$totalSpaceFreed = 0
$startTime = Get-Date

# إنشاء نسخة احتياطية إذا لم تكن DryRun
if (-not $DryRun -and -not $Force) {
    Write-Host "📦 إنشاء نسخة احتياطية..." -ForegroundColor Yellow
    if (-not (Test-Path $BackupPath)) {
        New-Item -ItemType Directory -Path $BackupPath | Out-Null
    }
    
    # نسخ الملفات المهمة فقط
    $importantPaths = @(
        "src/",
        "config/",
        "requirements.txt",
        "package.json",
        "README.md"
    )
    
    foreach ($path in $importantPaths) {
        if (Test-Path $path) {
            $destination = Join-Path $BackupPath $path
            if (Test-Path $path -PathType Container) {
                xcopy /s /e /h /i $path $destination > $null
            } else {
                Copy-Item $path $destination
            }
        }
    }
    Write-Host "✅ تم إنشاء النسخة الاحتياطية: $BackupPath" -ForegroundColor Green
}

# دالة لحذف الملفات بأمان
function Remove-SafelyWithStats {
    param(
        [string]$Path,
        [string]$Reason = "ملف غير مهم"
    )
    
    if (Test-Path $Path) {
        try {
            $fileSize = (Get-Item $Path).Length
            $script:totalSpaceFreed += $fileSize
            
            if ($DryRun) {
                Write-Host "🔍 [DRY RUN] سيتم حذف: $Path ($Reason)" -ForegroundColor Yellow
            } else {
                Remove-Item $Path -Force -Recurse
                Write-Host "✅ تم حذف: $Path" -ForegroundColor Green
            }
            $script:totalFilesDeleted++
        } catch {
            Write-Host "❌ خطأ في حذف: $Path - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

# دالة لحذف الملفات بالنمط
function Remove-FilesByPattern {
    param(
        [string]$Pattern,
        [string]$Reason = "ملفات غير مهمة"
    )
    
    $files = Get-ChildItem -Path . -Filter $Pattern -Recurse
    foreach ($file in $files) {
        Remove-SafelyWithStats -Path $file.FullName -Reason $Reason
    }
}

Write-Host "`n🗑️ بدء تنظيف الملفات..." -ForegroundColor Cyan

# 1. حذف ملفات العروض التوضيحية
Write-Host "`n1️⃣ حذف ملفات العروض التوضيحية..." -ForegroundColor Yellow
$demoFiles = @(
    "scripts/demo_distributed_ai.py",
    "scripts/demo_edge_ai.py", 
    "scripts/demo_multi_layer_cache.py",
    "src/dashboards/dashboard-demo.tsx",
    "src/dashboards/dashboard-demo-runner.py",
    "src/testing/quick_demo.py",
    "tests/ai_test_demo.py",
    "src/compliance/compliance_demo.py",
    "src/application/services/moderation_integration_example.py",
    "src/application/services/audio/voice_service_demo.py",
    "src/presentation/api/graphql/demo_graphql_federation.py",
    "src/infrastructure/observability/demo_results_summary.py"
)

foreach ($file in $demoFiles) {
    Remove-SafelyWithStats -Path $file -Reason "ملف عرض توضيحي"
}

# 2. حذف التقارير المولدة تلقائياً
Write-Host "`n2️⃣ حذف التقارير المولدة تلقائياً..." -ForegroundColor Yellow
$reportFiles = @(
    "ai_testing_demo_report.json",
    "advanced_streaming_refactoring_report.md",
    "cleanup_analysis_report.md",
    "code_cleanup_report.md",
    "project_analysis_report.md",
    "quick_cleanup_report.md",
    "exact_duplicates_report.json",
    "exact_duplicates_report.md"
)

foreach ($file in $reportFiles) {
    Remove-SafelyWithStats -Path $file -Reason "تقرير مولد تلقائياً"
}

# 3. حذف سكريبتات التحليل
Write-Host "`n3️⃣ حذف سكريبتات التحليل..." -ForegroundColor Yellow
$analysisScripts = @(
    "scripts/advanced_deep_analyzer.py",
    "scripts/advanced_directories_analyzer.py",
    "scripts/comprehensive_project_analyzer.py",
    "scripts/comprehensive_cleanup_analyzer.py",
    "scripts/comprehensive_architecture_analyzer.py",
    "scripts/find_exact_duplicates.py",
    "scripts/quick_cleanup_analyzer.py",
    "scripts/cleanup_ddd_duplicates.py",
    "scripts/git_secrets_cleanup.py",
    "scripts/verify_ddd_structure.py",
    "scripts/generate_docs.py",
    "scripts/check_render_setup.py"
)

foreach ($file in $analysisScripts) {
    Remove-SafelyWithStats -Path $file -Reason "سكريبت تحليل"
}

# 4. حذف الاختبارات التطويرية
Write-Host "`n4️⃣ حذف الاختبارات التطويرية..." -ForegroundColor Yellow
$testFiles = @(
    "tests/test_simple.py",
    "tests/test_integration.py",
    "tests/test_basic_functionality.py",
    "tests/test_comprehensive_backend.py",
    "tests/test_comprehensive_frontend.py",
    "tests/simple_sanity_check.py",
    "test_parent_dashboard_refactoring.py"
)

foreach ($file in $testFiles) {
    Remove-SafelyWithStats -Path $file -Reason "اختبار تطويري"
}

# 5. حذف الملفات المؤقتة والتخزين المؤقت
Write-Host "`n5️⃣ حذف الملفات المؤقتة..." -ForegroundColor Yellow
Remove-FilesByPattern -Pattern "*.pyc" -Reason "ملف Python مؤقت"
Remove-FilesByPattern -Pattern "*.pyo" -Reason "ملف Python مؤقت"
Remove-FilesByPattern -Pattern "*.log" -Reason "ملف سجل"
Remove-FilesByPattern -Pattern "*.tmp" -Reason "ملف مؤقت"
Remove-FilesByPattern -Pattern "*.cache" -Reason "ملف تخزين مؤقت"

# 6. حذف المجلدات المؤقتة
Write-Host "`n6️⃣ حذف المجلدات المؤقتة..." -ForegroundColor Yellow
$tempDirs = @(
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".coverage",
    "htmlcov"
)

foreach ($dir in $tempDirs) {
    if (Test-Path $dir) {
        Remove-SafelyWithStats -Path $dir -Reason "مجلد مؤقت"
    }
}

# 7. حذف الملفات المكررة الواضحة
Write-Host "`n7️⃣ حذف الملفات المكررة الواضحة..." -ForegroundColor Yellow

# البحث عن الملفات المكررة باستخدام hash
$hashTable = @{}
Get-ChildItem -Path . -File -Recurse | ForEach-Object {
    if ($_.Length -gt 100 -and $_.Extension -in @('.py', '.js', '.ts', '.json')) {
        $hash = Get-FileHash $_.FullName -Algorithm MD5
        if ($hashTable.ContainsKey($hash.Hash)) {
            $existing = $hashTable[$hash.Hash]
            
            # اختر الملف الأقل أهمية للحذف
            if ($_.FullName -like "*test*" -or $_.FullName -like "*demo*") {
                Remove-SafelyWithStats -Path $_.FullName -Reason "ملف مكرر"
            } elseif ($existing -like "*test*" -or $existing -like "*demo*") {
                Remove-SafelyWithStats -Path $existing -Reason "ملف مكرر"
                $hashTable[$hash.Hash] = $_.FullName
            }
        } else {
            $hashTable[$hash.Hash] = $_.FullName
        }
    }
}

# 8. تنظيف الملفات الفارغة
Write-Host "`n8️⃣ حذف الملفات الفارغة..." -ForegroundColor Yellow
Get-ChildItem -Path . -File -Recurse | Where-Object {$_.Length -eq 0} | ForEach-Object {
    Remove-SafelyWithStats -Path $_.FullName -Reason "ملف فارغ"
}

# 9. تنظيف المجلدات الفارغة
Write-Host "`n9️⃣ حذف المجلدات الفارغة..." -ForegroundColor Yellow
do {
    $emptyDirs = Get-ChildItem -Path . -Directory -Recurse | Where-Object {(Get-ChildItem $_.FullName -Recurse).Count -eq 0}
    foreach ($dir in $emptyDirs) {
        Remove-SafelyWithStats -Path $dir.FullName -Reason "مجلد فارغ"
    }
} while ($emptyDirs.Count -gt 0)

# إحصائيات النهاية
$endTime = Get-Date
$duration = $endTime - $startTime
$spaceMB = [math]::Round($totalSpaceFreed / 1MB, 2)

Write-Host "`n🎉 تم إكمال التنظيف بنجاح!" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Green
Write-Host "📊 الإحصائيات:" -ForegroundColor Cyan
Write-Host "  • الملفات المحذوفة: $totalFilesDeleted" -ForegroundColor White
Write-Host "  • المساحة المحررة: $spaceMB MB" -ForegroundColor White
Write-Host "  • الوقت المستغرق: $($duration.TotalSeconds) ثانية" -ForegroundColor White

if (-not $DryRun) {
    Write-Host "  • النسخة الاحتياطية: $BackupPath" -ForegroundColor White
}

Write-Host "`n✅ المشروع أصبح أكثر نظافة وكفاءة!" -ForegroundColor Green
Write-Host "🚀 يمكنك الآن تشغيل المشروع بأداء محسّن" -ForegroundColor Green

# تشغيل اختبار سريع للتأكد من سلامة المشروع
Write-Host "`n🔍 اختبار سلامة المشروع..." -ForegroundColor Yellow
$criticalFiles = @(
    "src/__init__.py",
    "requirements.txt",
    "src/main.py"
)

$allCriticalExist = $true
foreach ($file in $criticalFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "⚠️ ملف مهم مفقود: $file" -ForegroundColor Red
        $allCriticalExist = $false
    }
}

if ($allCriticalExist) {
    Write-Host "✅ جميع الملفات المهمة موجودة" -ForegroundColor Green
} else {
    Write-Host "❌ بعض الملفات المهمة مفقودة - تحقق من النسخة الاحتياطية" -ForegroundColor Red
}

Write-Host "`n🏁 انتهى التنظيف!" -ForegroundColor Cyan 