# 🔐 HashiCorp Vault Windows Deployment
# Senior DevOps Engineer: جعفر أديب
# PowerShell script for Windows environment

param(
    [string]$VaultToken = "myroot",
    [switch]$SkipDocker = $false
)

Write-Host "🚀 بدء نشر HashiCorp Vault Infrastructure..." -ForegroundColor Green

# Check prerequisites
Write-Host "🔍 فحص المتطلبات..." -ForegroundColor Yellow

if (-not $SkipDocker) {
    try {
        docker --version | Out-Null
        Write-Host "✅ Docker متوفر" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Docker غير مثبت أو غير متاح" -ForegroundColor Red
        exit 1
    }
}

# Set environment variables
Write-Host "🔧 إعداد متغيرات البيئة..." -ForegroundColor Yellow
$env:VAULT_ROOT_TOKEN = $VaultToken
$env:VAULT_ADDR = "http://localhost:8200"

# Create vault directories
Write-Host "📁 إنشاء مجلدات Vault..." -ForegroundColor Yellow
$vaultDirs = @(
    "vault\data",
    "vault\config", 
    "vault\logs",
    "vault\policies",
    "consul\data",
    "backup\vault"
)

foreach ($dir in $vaultDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  📂 تم إنشاء: $dir" -ForegroundColor Gray
    }
}

# Create Vault policies
Write-Host "📜 إنشاء سياسات Vault..." -ForegroundColor Yellow

$readPolicy = @'
# AI Teddy Bear - Read Policy
path "ai-teddy/*" {
  capabilities = ["read", "list"]
}

path "ai-teddy/data/*" {
  capabilities = ["read", "list"]
}
'@

$adminPolicy = @'
# AI Teddy Bear - Admin Policy  
path "ai-teddy/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "ai-teddy/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}
'@

$readPolicy | Out-File -FilePath "vault\policies\ai-teddy-read.hcl" -Encoding UTF8
$adminPolicy | Out-File -FilePath "vault\policies\ai-teddy-admin.hcl" -Encoding UTF8

Write-Host "✅ تم إنشاء السياسات" -ForegroundColor Green

# Start Vault with Docker
if (-not $SkipDocker) {
    Write-Host "🐳 بدء تشغيل Vault مع Docker..." -ForegroundColor Yellow
    
    # Stop existing container
    docker stop ai-teddy-vault 2>$null
    docker rm ai-teddy-vault 2>$null
    
    # Start Vault container
    $dockerCmd = @(
        "run", "-d",
        "--name", "ai-teddy-vault",
        "--cap-add=IPC_LOCK",
        "-p", "8200:8200",
        "-e", "VAULT_DEV_ROOT_TOKEN_ID=$VaultToken",
        "-e", "VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200",
        "-v", "$PWD\vault\data:/vault/data",
        "-v", "$PWD\vault\policies:/vault/policies",
        "hashicorp/vault:1.17.2"
    )
    
    & docker @dockerCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Vault container بدأ بنجاح" -ForegroundColor Green
    } else {
        Write-Host "❌ فشل في بدء Vault container" -ForegroundColor Red
        exit 1
    }
    
    # Wait for Vault to be ready
    Write-Host "⏳ انتظار جاهزية Vault..." -ForegroundColor Yellow
    $maxAttempts = 30
    $attempt = 0
    
    do {
        Start-Sleep -Seconds 2
        try {
            $response = Invoke-RestMethod -Uri "$env:VAULT_ADDR/v1/sys/health" -Method Get -ErrorAction SilentlyContinue
            if ($response) {
                Write-Host "✅ Vault جاهز ويعمل" -ForegroundColor Green
                break
            }
        }
        catch {
            # Continue waiting
        }
        $attempt++
    } while ($attempt -lt $maxAttempts)
    
    if ($attempt -eq $maxAttempts) {
        Write-Host "❌ Vault لم يصبح جاهزاً في الوقت المحدد" -ForegroundColor Red
        exit 1
    }
    
    # Configure Vault
    Write-Host "🔧 تكوين Vault..." -ForegroundColor Yellow
    
    # Enable KV secrets engine
    docker exec ai-teddy-vault vault secrets enable -path=ai-teddy kv-v2
    
    # Upload policies
    docker exec ai-teddy-vault vault policy write ai-teddy-read /vault/policies/ai-teddy-read.hcl
    docker exec ai-teddy-vault vault policy write ai-teddy-admin /vault/policies/ai-teddy-admin.hcl
    
    Write-Host "✅ تم تكوين Vault" -ForegroundColor Green
}

# Display summary
Write-Host ""
Write-Host "📋 ملخص النشر:" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host "Vault URL: $env:VAULT_ADDR" -ForegroundColor White
Write-Host "Root Token: $VaultToken" -ForegroundColor White
Write-Host ""
Write-Host "🔑 الخطوات التالية:" -ForegroundColor Yellow
Write-Host "1. اختبار الاتصال: curl $env:VAULT_ADDR/v1/sys/health" -ForegroundColor Gray
Write-Host "2. تشغيل نقل الأسرار: python scripts\migrate_secrets.py --vault-token $VaultToken" -ForegroundColor Gray
Write-Host "3. إعداد تطبيقك لاستخدام Vault" -ForegroundColor Gray
Write-Host ""
Write-Host "🎉 تم نشر Vault بنجاح!" -ForegroundColor Green 