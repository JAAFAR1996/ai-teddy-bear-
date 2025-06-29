#!/bin/bash
#
# 🔐 HashiCorp Vault Infrastructure Setup
# Senior DevOps Engineer: جعفر أديب
# Enterprise-grade secrets management deployment
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
VAULT_VERSION="1.17.2"
CONSUL_VERSION="1.16.1"
VAULT_TOKEN="${VAULT_ROOT_TOKEN:-myroot}"
VAULT_ADDR="http://localhost:8200"

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

check_requirements() {
    log "🔍 فحص المتطلبات..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker غير مثبت. يرجى تثبيت Docker أولاً"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose غير مثبت"
    fi
    
    # Check Vault CLI (optional)
    if command -v vault &> /dev/null; then
        log "✅ Vault CLI موجود: $(vault version)"
    else
        warn "Vault CLI غير مثبت - سيتم استخدام Docker exec"
    fi
    
    log "✅ جميع المتطلبات متوفرة"
}

setup_environment() {
    log "🔧 إعداد البيئة..."
    
    # Create directories
    mkdir -p vault/{data,config,logs,policies}
    mkdir -p consul/data
    mkdir -p backup/vault
    
    # Generate Vault token if not provided
    if [ -z "${VAULT_ROOT_TOKEN:-}" ]; then
        VAULT_TOKEN=$(openssl rand -hex 16)
        export VAULT_ROOT_TOKEN="${VAULT_TOKEN}"
        log "🔐 تم إنشاء Vault token: ${VAULT_TOKEN}"
    fi
    
    # Create .env file for Docker Compose
    cat > .env.vault << EOF
VAULT_ROOT_TOKEN=${VAULT_TOKEN}
VAULT_VERSION=${VAULT_VERSION}
CONSUL_VERSION=${CONSUL_VERSION}
VAULT_ADDR=${VAULT_ADDR}
EOF
    
    log "✅ تم إعداد البيئة"
}

create_vault_policies() {
    log "📜 إنشاء سياسات Vault..."
    
    # AI Teddy Read Policy
    cat > vault/policies/ai-teddy-read.hcl << 'EOF'
# AI Teddy Bear - Read Policy
path "ai-teddy/*" {
  capabilities = ["read", "list"]
}

path "ai-teddy/data/*" {
  capabilities = ["read", "list"]
}

path "sys/mounts" {
  capabilities = ["read"]
}
EOF

    # AI Teddy Admin Policy
    cat > vault/policies/ai-teddy-admin.hcl << 'EOF'
# AI Teddy Bear - Admin Policy
path "ai-teddy/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "ai-teddy/data/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/mounts" {
  capabilities = ["read", "list"]
}

path "sys/mounts/ai-teddy" {
  capabilities = ["create", "read", "update", "delete"]
}
EOF

    # CI/CD Policy
    cat > vault/policies/ci-cd.hcl << 'EOF'
# CI/CD Pipeline Policy
path "ai-teddy/data/ci-cd/*" {
  capabilities = ["read"]
}

path "ai-teddy/data/config/*" {
  capabilities = ["read"]
}
EOF

    log "✅ تم إنشاء السياسات"
}

deploy_vault() {
    log "🚀 نشر HashiCorp Vault..."
    
    # Stop existing containers
    docker-compose -f docker-compose.vault.yml down 2>/dev/null || true
    
    # Start Vault infrastructure
    docker-compose -f docker-compose.vault.yml up -d
    
    # Wait for Vault to be ready
    log "⏳ انتظار جاهزية Vault..."
    for i in {1..30}; do
        if curl -s "${VAULT_ADDR}/v1/sys/health" > /dev/null 2>&1; then
            log "✅ Vault جاهز ويعمل"
            break
        fi
        sleep 2
    done
    
    if [ $i -eq 30 ]; then
        error "Vault لم يصبح جاهزاً في الوقت المحدد"
    fi
}

configure_vault() {
    log "🔧 تكوين Vault..."
    
    # Set Vault environment
    export VAULT_ADDR="${VAULT_ADDR}"
    export VAULT_TOKEN="${VAULT_TOKEN}"
    
    # Enable KV secrets engine
    docker exec ai-teddy-vault vault secrets enable -path=ai-teddy kv-v2
    
    # Upload policies
    for policy_file in vault/policies/*.hcl; do
        policy_name=$(basename "${policy_file}" .hcl)
        docker exec ai-teddy-vault vault policy write "${policy_name}" "/vault/policies/${policy_name}.hcl"
        log "📜 تم تحميل السياسة: ${policy_name}"
    done
    
    # Create auth methods
    docker exec ai-teddy-vault vault auth enable userpass
    
    # Create users
    docker exec ai-teddy-vault vault write auth/userpass/users/ai-teddy \
        password=secure-password \
        policies=ai-teddy-read
    
    docker exec ai-teddy-vault vault write auth/userpass/users/admin \
        password=admin-password \
        policies=ai-teddy-admin
    
    log "✅ تم تكوين Vault"
}

create_backup_script() {
    log "💾 إنشاء سكريبت النسخ الاحتياطي..."
    
    cat > scripts/backup_vault.sh << 'EOF'
#!/bin/bash
# Vault Backup Script

set -euo pipefail

BACKUP_DIR="backup/vault"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/vault_backup_${TIMESTAMP}.snap"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Create Vault snapshot
docker exec ai-teddy-vault vault operator raft snapshot save "/vault/data/backup_${TIMESTAMP}.snap"

# Copy to host
docker cp "ai-teddy-vault:/vault/data/backup_${TIMESTAMP}.snap" "${BACKUP_FILE}"

# Encrypt backup
openssl enc -aes-256-cbc -salt -in "${BACKUP_FILE}" -out "${BACKUP_FILE}.enc" -k "${VAULT_BACKUP_KEY:-defaultkey}"

# Clean up
rm "${BACKUP_FILE}"
docker exec ai-teddy-vault rm "/vault/data/backup_${TIMESTAMP}.snap"

echo "✅ تم إنشاء النسخة الاحتياطية: ${BACKUP_FILE}.enc"
EOF

    chmod +x scripts/backup_vault.sh
    log "✅ تم إنشاء سكريبت النسخ الاحتياطي"
}

setup_monitoring() {
    log "📊 إعداد المراقبة..."
    
    # Vault monitoring configuration
    cat > vault/config/monitoring.hcl << 'EOF'
telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = true
  telemetry {
    unauthenticated_metrics_access = true
  }
}
EOF

    log "✅ تم إعداد المراقبة"
}

run_tests() {
    log "🧪 تشغيل اختبارات Vault..."
    
    # Test Vault connectivity
    if ! curl -s "${VAULT_ADDR}/v1/sys/health" | grep -q "initialized"; then
        error "Vault غير متاح أو غير مهيأ"
    fi
    
    # Test secret operations
    docker exec ai-teddy-vault vault kv put ai-teddy/test secret=value
    docker exec ai-teddy-vault vault kv get ai-teddy/test
    docker exec ai-teddy-vault vault kv delete ai-teddy/test
    
    log "✅ اجتازت جميع الاختبارات"
}

print_summary() {
    log "📋 ملخص النشر:"
    echo ""
    echo -e "${BLUE}🔐 HashiCorp Vault Infrastructure${NC}"
    echo -e "${BLUE}====================================${NC}"
    echo -e "Vault URL: ${VAULT_ADDR}"
    echo -e "Vault UI: http://localhost:8000"
    echo -e "Consul UI: http://localhost:8500"
    echo -e "Root Token: ${VAULT_TOKEN}"
    echo ""
    echo -e "${YELLOW}🔑 Users Created:${NC}"
    echo -e "- ai-teddy (password: secure-password)"
    echo -e "- admin (password: admin-password)"
    echo ""
    echo -e "${GREEN}📜 Policies Available:${NC}"
    echo -e "- ai-teddy-read"
    echo -e "- ai-teddy-admin"
    echo -e "- ci-cd"
    echo ""
    echo -e "${RED}⚠️  Next Steps:${NC}"
    echo -e "1. Run: python scripts/migrate_secrets.py --vault-token ${VAULT_TOKEN}"
    echo -e "2. Configure your application to use Vault"
    echo -e "3. Set up automated backups"
    echo -e "4. Configure monitoring alerts"
}

main() {
    log "🚀 بدء نشر HashiCorp Vault Infrastructure..."
    
    check_requirements
    setup_environment
    create_vault_policies
    deploy_vault
    configure_vault
    create_backup_script
    setup_monitoring
    run_tests
    print_summary
    
    log "🎉 تم نشر Vault بنجاح!"
}

# Run main function
main "$@" 