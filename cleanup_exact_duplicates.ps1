# PowerShell Script للحذف الآمن للملفات المكررة
# تم إنشاؤه بواسطة ExactDuplicateFinder

$deletedCount = 0
$freedSpace = 0

Write-Information "🧹 بدء حذف الملفات المكررة..." -InformationAction Continue


Write-Output ""
Write-Information "✅ تم الانتهاء!" -InformationAction Continue
Write-Information "📊 الملفات المحذوفة: $deletedCount" -InformationAction Continue
Write-Information "💾 المساحة المحررة: $([math]::Round($freedSpace/1MB, 2)) MB" -InformationAction Continue
