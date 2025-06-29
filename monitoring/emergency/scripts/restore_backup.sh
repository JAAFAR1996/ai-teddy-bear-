#!/bin/bash

# 🔄 Emergency Backup Restore System - AI Teddy Bear DevOps Team
# الإصدار: v2025.1.0

set -euo pipefail

# متغيرات التكوين
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
readonly RESTORE_TIMESTAMP="${1:-$(date +%Y%m%d_%H%M%S)}"

# متغيرات AWS
readonly S3_BUCKET="${BACKUP_S3_BUCKET:-ai-teddy-emergency-backups}"
readonly S3_PREFIX="emergency-monitoring/${RESTORE_TIMESTAMP}"
readonly ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-}"

# ألوان المخرجات
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

print_message() {
    echo -e "${1}${2}${NC}"
}

# عرض المساعدة
show_help() {
    cat << EOF
🔄 Emergency Backup Restore System

الاستخدام:
    ./restore_backup.sh [TIMESTAMP]

الخيارات:
    TIMESTAMP    تاريخ النسخة الاحتياطية (مثال: 20241231_120000)
    
متغيرات البيئة:
    BACKUP_S3_BUCKET           مجموعة S3 للنسخ الاحتياطية
    BACKUP_ENCRYPTION_KEY      مفتاح التشفير

أمثلة:
    ./restore_backup.sh 20241231_120000
    ./restore_backup.sh latest
    
للحصول على قائمة النسخ المتوفرة:
    ./restore_backup.sh --list
EOF
}

# عرض قائمة النسخ المتوفرة
list_backups() {
    print_message "${BLUE}" "📋 البحث عن النسخ الاحتياطية المتوفرة..."
    
    aws s3 ls "s3://${S3_BUCKET}/emergency-monitoring/" --recursive | \
        grep "\.tar\.gz\.enc$" | \
        awk '{print $4}' | \
        sed 's|emergency-monitoring/||' | \
        sed 's|/.*||' | \
        sort -u | \
        head -20
}

# فحص المتطلبات
check_requirements() {
    print_message "${BLUE}" "🔍 فحص المتطلبات..."
    
    local tools=("aws" "openssl" "tar" "docker" "docker-compose")
    for tool in "${tools[@]}"; do
        if ! command -v "${tool}" &> /dev/null; then
            print_message "${RED}" "❌ ${tool} غير مثبت"
            exit 1
        fi
    done
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_message "${RED}" "❌ AWS credentials غير مكونة"
        exit 1
    fi
    
    if [ -z "${ENCRYPTION_KEY}" ]; then
        print_message "${RED}" "❌ مفتاح التشفير غير محدد (BACKUP_ENCRYPTION_KEY)"
        exit 1
    fi
    
    print_message "${GREEN}" "✅ جميع المتطلبات متوفرة"
}

# تحميل النسخة الاحتياطية
download_backup() {
    print_message "${BLUE}" "📥 تحميل النسخة الاحتياطية..."
    
    local backup_file="teddy_emergency_backup_${RESTORE_TIMESTAMP}.tar.gz.enc"
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/${backup_file}"
    local local_file="/tmp/${backup_file}"
    local checksum_file="/tmp/${backup_file}.sha256"
    
    # التحقق من وجود النسخة
    if ! aws s3 ls "${s3_path}" &> /dev/null; then
        print_message "${RED}" "❌ النسخة الاحتياطية غير موجودة: ${s3_path}"
        return 1
    fi
    
    # تحميل النسخة الاحتياطية
    aws s3 cp "${s3_path}" "${local_file}"
    aws s3 cp "${s3_path}.sha256" "${checksum_file}"
    
    # التحقق من سلامة الملف
    if sha256sum -c "${checksum_file}"; then
        print_message "${GREEN}" "✅ تم تحميل النسخة بنجاح"
    else
        print_message "${RED}" "❌ فشل في التحقق من سلامة الملف"
        return 1
    fi
    
    echo "${local_file}"
}

# فك التشفير والضغط
decrypt_extract() {
    local encrypted_file=$1
    print_message "${BLUE}" "🔓 فك التشفير والضغط..."
    
    local decrypted_file="/tmp/$(basename "${encrypted_file}" .enc)"
    local extract_dir="/tmp/restore_${RESTORE_TIMESTAMP}"
    
    # فك التشفير
    if openssl enc -aes-256-cbc -d -pbkdf2 -iter 100000 \
        -in "${encrypted_file}" -out "${decrypted_file}" -k "${ENCRYPTION_KEY}"; then
        print_message "${GREEN}" "✅ تم فك التشفير"
    else
        print_message "${RED}" "❌ فشل في فك التشفير - تحقق من مفتاح التشفير"
        return 1
    fi
    
    # فك الضغط
    mkdir -p "${extract_dir}"
    tar -xzf "${decrypted_file}" -C "${extract_dir}"
    
    # تنظيف
    rm -f "${encrypted_file}" "${decrypted_file}" "${encrypted_file}.sha256"
    
    echo "${extract_dir}"
}

# إيقاف النظام الحالي
stop_current_system() {
    print_message "${BLUE}" "⏹️  إيقاف النظام الحالي..."
    
    if docker-compose -f "${PROJECT_ROOT}/monitoring/emergency/docker-compose.emergency.yml" ps -q &> /dev/null; then
        docker-compose -f "${PROJECT_ROOT}/monitoring/emergency/docker-compose.emergency.yml" down
        print_message "${GREEN}" "✅ تم إيقاف النظام"
    else
        print_message "${YELLOW}" "⚠️  النظام غير نشط"
    fi
}

# نسخ احتياطي للنظام الحالي
backup_current_system() {
    print_message "${BLUE}" "💾 نسخ احتياطي للنظام الحالي..."
    
    local backup_current="/tmp/current_system_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "${backup_current}"
    
    # نسخ التكوينات الحالية
    if [ -d "${PROJECT_ROOT}/monitoring/emergency" ]; then
        cp -r "${PROJECT_ROOT}/monitoring/emergency" "${backup_current}/"
    fi
    
    # نسخ البيانات المستمرة
    if [ -d "/var/lib/teddy/monitoring" ]; then
        sudo tar -czf "${backup_current}/current_data.tar.gz" \
            -C "/var/lib/teddy" monitoring/ 2>/dev/null || true
    fi
    
    print_message "${GREEN}" "✅ نسخة احتياطية محفوظة في: ${backup_current}"
    echo "${backup_current}"
}

# استعادة التكوينات
restore_configurations() {
    local restore_dir=$1
    print_message "${BLUE}" "⚙️  استعادة التكوينات..."
    
    local backup_data_dir=$(find "${restore_dir}" -name "teddy_emergency_backup_*" -type d | head -1)
    
    if [ -z "${backup_data_dir}" ]; then
        print_message "${RED}" "❌ لم يتم العثور على بيانات النسخة الاحتياطية"
        return 1
    fi
    
    # استعادة ملفات التكوين
    if [ -d "${backup_data_dir}/configurations/emergency" ]; then
        rm -rf "${PROJECT_ROOT}/monitoring/emergency"
        cp -r "${backup_data_dir}/configurations/emergency" "${PROJECT_ROOT}/monitoring/"
        print_message "${GREEN}" "✅ تم استعادة التكوينات"
    fi
    
    # استعادة الأسرار المشفرة
    if [ -f "${backup_data_dir}/configurations/secrets_encrypted.tar.gz" ]; then
        mkdir -p "${PROJECT_ROOT}/monitoring/emergency/secrets"
        tar -xzf "${backup_data_dir}/configurations/secrets_encrypted.tar.gz" \
            -C "${PROJECT_ROOT}/monitoring/emergency/"
        print_message "${GREEN}" "✅ تم استعادة الأسرار"
    fi
}

# استعادة البيانات المستمرة
restore_persistent_data() {
    local restore_dir=$1
    print_message "${BLUE}" "📊 استعادة البيانات المستمرة..."
    
    local backup_data_dir=$(find "${restore_dir}" -name "teddy_emergency_backup_*" -type d | head -1)
    
    # إنشاء مجلدات البيانات
    sudo mkdir -p /var/lib/teddy/monitoring/{prometheus,grafana}
    
    # استعادة بيانات Prometheus
    if [ -f "${backup_data_dir}/persistent_data/prometheus_data.tar.gz" ]; then
        sudo tar -xzf "${backup_data_dir}/persistent_data/prometheus_data.tar.gz" \
            -C "/var/lib/teddy/monitoring/"
        sudo chown -R 65534:65534 /var/lib/teddy/monitoring/prometheus
        print_message "${GREEN}" "✅ تم استعادة بيانات Prometheus"
    fi
    
    # استعادة بيانات Grafana
    if [ -f "${backup_data_dir}/persistent_data/grafana_data.tar.gz" ]; then
        sudo tar -xzf "${backup_data_dir}/persistent_data/grafana_data.tar.gz" \
            -C "/var/lib/teddy/monitoring/"
        sudo chown -R 472:472 /var/lib/teddy/monitoring/grafana
        print_message "${GREEN}" "✅ تم استعادة بيانات Grafana"
    fi
}

# بدء النظام المستعاد
start_restored_system() {
    print_message "${BLUE}" "🚀 بدء النظام المستعاد..."
    
    cd "${PROJECT_ROOT}/monitoring/emergency"
    
    # تشغيل النظام
    docker-compose -f docker-compose.emergency.yml up -d
    
    # انتظار بدء الخدمات
    sleep 30
    
    # فحص حالة الخدمات
    local services=("9090" "9093" "3000")
    local failed_services=()
    
    for port in "${services[@]}"; do
        if curl -sf "http://localhost:${port}/" >/dev/null 2>&1 || \
           curl -sf "http://localhost:${port}/metrics" >/dev/null 2>&1 || \
           curl -sf "http://localhost:${port}/-/healthy" >/dev/null 2>&1; then
            print_message "${GREEN}" "✅ خدمة المنفذ ${port} تعمل"
        else
            failed_services+=("${port}")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_message "${GREEN}" "✅ جميع الخدمات تعمل بنجاح"
        return 0
    else
        print_message "${YELLOW}" "⚠️  بعض الخدمات لا تستجيب: ${failed_services[*]}"
        return 1
    fi
}

# الدالة الرئيسية
main() {
    # التحقق من المعاملات
    case "${RESTORE_TIMESTAMP}" in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "--list"|"-l")
            list_backups
            exit 0
            ;;
        "latest")
            RESTORE_TIMESTAMP=$(list_backups | tail -1)
            if [ -z "${RESTORE_TIMESTAMP}" ]; then
                print_message "${RED}" "❌ لا توجد نسخ احتياطية متوفرة"
                exit 1
            fi
            ;;
    esac
    
    print_message "${BLUE}" "
╔══════════════════════════════════════════════════════╗
║           🔄 استعادة النسخة الاحتياطية             ║
║         AI Teddy Bear Emergency Restore             ║
╚══════════════════════════════════════════════════════╝
"
    
    print_message "${BLUE}" "📅 استعادة النسخة: ${RESTORE_TIMESTAMP}"
    
    check_requirements
    
    # نسخ احتياطي للنظام الحالي
    local current_backup
    current_backup=$(backup_current_system)
    
    # إيقاف النظام الحالي
    stop_current_system
    
    # تحميل النسخة الاحتياطية
    local encrypted_file
    encrypted_file=$(download_backup)
    
    # فك التشفير والضغط
    local restore_dir
    restore_dir=$(decrypt_extract "${encrypted_file}")
    
    # استعادة التكوينات والبيانات
    restore_configurations "${restore_dir}"
    restore_persistent_data "${restore_dir}"
    
    # بدء النظام المستعاد
    if start_restored_system; then
        print_message "${GREEN}" "
🎉 تم استعادة النسخة الاحتياطية بنجاح!

📅 النسخة المستعادة: ${RESTORE_TIMESTAMP}
🔗 Prometheus: http://localhost:9090
🔗 Grafana: http://localhost:3000
🔗 Alertmanager: http://localhost:9093

💾 النسخة الاحتياطية للنظام السابق: ${current_backup}
"
    else
        print_message "${RED}" "❌ فشل في بدء النظام المستعاد"
        print_message "${YELLOW}" "💡 يمكن استعادة النظام السابق من: ${current_backup}"
        exit 1
    fi
    
    # تنظيف الملفات المؤقتة
    rm -rf "${restore_dir}"
    
    print_message "${BLUE}" "✅ تم الانتهاء من عملية الاستعادة"
}

# تشغيل الدالة الرئيسية
main "$@" 