# PowerShell Script للحذف الآمن للملفات المكررة
# تم إنشاؤه بواسطة ExactDuplicateFinder

$deletedCount = 0
$freedSpace = 0

Write-Host "🧹 بدء حذف الملفات المكررة..." -ForegroundColor Yellow


Write-Host ""
Write-Host "✅ تم الانتهاء!" -ForegroundColor Green
Write-Host "📊 الملفات المحذوفة: $deletedCount" -ForegroundColor Cyan
Write-Host "💾 المساحة المحررة: $([math]::Round($freedSpace/1MB, 2)) MB" -ForegroundColor Cyan
