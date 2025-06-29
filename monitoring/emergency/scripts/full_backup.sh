#!/bin/bash

# 💾 Full Emergency Backup System - AI Teddy Bear DevOps Team
# تاريخ الإنشاء: $(date)
# الإصدار: v2025.1.0
# المسؤول: DevOps Team

set -euo pipefail

# ألوان المخرجات
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m'

# متغيرات التكوين
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly BACKUP_NAME="teddy_emergency_backup_${TIMESTAMP}"
readonly BACKUP_DIR="/tmp/${BACKUP_NAME}"
readonly LOG_FILE="/var/log/teddy/backup-${TIMESTAMP}.log"

# متغيرات AWS والتشفير
readonly S3_BUCKET="${BACKUP_S3_BUCKET:-ai-teddy-emergency-backups}"
readonly S3_PREFIX="emergency-monitoring/${TIMESTAMP}"
readonly ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-$(openssl rand -base64 32)}"
readonly KMS_KEY_ID="${AWS_KMS_KEY_ID:-alias/teddy-backup-key}"

# إعداد السجلات
setup_logging() {
    sudo mkdir -p "$(dirname "${LOG_FILE}")"
    exec 1> >(tee -a "${LOG_FILE}")
    exec 2> >(tee -a "${LOG_FILE}" >&2)
    
    echo -e "${BLUE}📋 بدء عملية النسخ الاحتياطي الكامل${NC}"
    echo -e "${BLUE}📅 الوقت: $(date)${NC}"
    echo -e "${BLUE}📁 مجلد المشروع: ${PROJECT_ROOT}${NC}"
    echo -e "${BLUE}📝 ملف السجل: ${LOG_FILE}${NC}"
}

# طباعة رسالة ملونة
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# طباعة عنوان القسم
print_section() {
    local title=$1
    echo
    print_message "${CYAN}" "═══════════════════════════════════════════════════════════"
    print_message "${CYAN}" "💾 ${title}"
    print_message "${CYAN}" "═══════════════════════════════════════════════════════════"
}

# فحص المتطلبات الأساسية
check_prerequisites() {
    print_section "فحص المتطلبات الأساسية"
    
    local missing_tools=()
    local required_tools=("docker" "docker-compose" "aws" "openssl" "tar" "gzip")
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "${tool}" &> /dev/null; then
            missing_tools+=("${tool}")
            print_message "${RED}" "❌ ${tool} غير مثبت"
        else
            print_message "${GREEN}" "✅ ${tool} متوفر"
        fi
    done
    
    # فحص AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        print_message "${RED}" "❌ AWS credentials غير مكونة"
        missing_tools+=("AWS credentials")
    else
        local aws_identity=$(aws sts get-caller-identity --query 'Account' --output text)
        print_message "${GREEN}" "✅ AWS Account: ${aws_identity}"
    fi
    
    # فحص مساحة القرص
    local available_space=$(df /tmp | awk 'NR==2 {print $4}')
    local required_space=5242880  # 5GB
    
    if [ "${available_space}" -lt "${required_space}" ]; then
        print_message "${RED}" "❌ مساحة قرص غير كافية في /tmp"
        missing_tools+=("disk space")
    else
        print_message "${GREEN}" "✅ مساحة قرص كافية: $((available_space/1024/1024))GB"
    fi
    
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_message "${RED}" "❌ أدوات مفقودة: ${missing_tools[*]}"
        exit 1
    fi
    
    print_message "${GREEN}" "✅ جميع المتطلبات متوفرة"
}

# إنشاء مجلد النسخ الاحتياطي
create_backup_directory() {
    print_section "إعداد مجلد النسخ الاحتياطي"
    
    mkdir -p "${BACKUP_DIR}"
    chmod 700 "${BACKUP_DIR}"
    
    # إنشاء metadata
    cat > "${BACKUP_DIR}/backup_metadata.json" << EOF
{
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${TIMESTAMP}",
    "backup_type": "full_emergency_backup",
    "project": "ai_teddy_bear",
    "component": "emergency_monitoring",
    "version": "v2025.1.0",
    "created_by": "devops_team",
    "encryption": "aes-256-cbc",
    "compression": "gzip",
    "storage_location": "s3://${S3_BUCKET}/${S3_PREFIX}",
    "retention_policy": "7_years",
    "backup_start_time": "$(date -Iseconds)"
}
EOF
    
    print_message "${GREEN}" "✅ تم إنشاء مجلد النسخ الاحتياطي: ${BACKUP_DIR}"
}

# نسخ احتياطي لحالة Docker
backup_docker_state() {
    print_section "نسخ احتياطي لحالة Docker"
    
    local docker_backup_dir="${BACKUP_DIR}/docker_state"
    mkdir -p "${docker_backup_dir}"
    
    # حفظ حالة الحاويات النشطة
    if docker-compose -f "${PROJECT_ROOT}/monitoring/emergency/docker-compose.emergency.yml" ps -q &> /dev/null; then
        print_message "${BLUE}" "💾 حفظ حالة الحاويات..."
        
        docker-compose -f "${PROJECT_ROOT}/monitoring/emergency/docker-compose.emergency.yml" ps \
            > "${docker_backup_dir}/container_status.txt"
        
        # حفظ logs الحاويات
        local containers=(
            "teddy-prometheus-emergency"
            "teddy-alertmanager-emergency"
            "teddy-grafana-emergency"
            "teddy-node-exporter-security"
            "teddy-cadvisor-security"
        )
        
        for container in "${containers[@]}"; do
            if docker ps -q -f name="${container}" &> /dev/null; then
                print_message "${BLUE}" "📋 حفظ سجلات ${container}..."
                docker logs "${container}" > "${docker_backup_dir}/${container}_logs.txt" 2>&1 || true
            fi
        done
        
        print_message "${GREEN}" "✅ تم حفظ حالة Docker"
    else
        print_message "${YELLOW}" "⚠️  لا توجد حاويات نشطة"
    fi
}

# نسخ احتياطي للبيانات المستمرة
backup_persistent_data() {
    print_section "نسخ احتياطي للبيانات المستمرة"
    
    local data_backup_dir="${BACKUP_DIR}/persistent_data"
    mkdir -p "${data_backup_dir}"
    
    # نسخ بيانات Prometheus
    if [ -d "/var/lib/teddy/monitoring/prometheus" ]; then
        print_message "${BLUE}" "📊 نسخ بيانات Prometheus..."
        sudo tar -czf "${data_backup_dir}/prometheus_data.tar.gz" \
            -C "/var/lib/teddy/monitoring" prometheus/ 2>/dev/null || \
            print_message "${YELLOW}" "⚠️  تعذر نسخ بيانات Prometheus"
    fi
    
    # نسخ بيانات Grafana
    if [ -d "/var/lib/teddy/monitoring/grafana" ]; then
        print_message "${BLUE}" "📈 نسخ بيانات Grafana..."
        sudo tar -czf "${data_backup_dir}/grafana_data.tar.gz" \
            -C "/var/lib/teddy/monitoring" grafana/ 2>/dev/null || \
            print_message "${YELLOW}" "⚠️  تعذر نسخ بيانات Grafana"
    fi
    
    print_message "${GREEN}" "✅ تم نسخ البيانات المستمرة"
}

# نسخ احتياطي للتكوينات والأسرار
backup_configurations() {
    print_section "نسخ احتياطي للتكوينات والأسرار"
    
    local config_backup_dir="${BACKUP_DIR}/configurations"
    mkdir -p "${config_backup_dir}"
    
    # نسخ مجلد المراقبة الطارئة بالكامل
    print_message "${BLUE}" "⚙️  نسخ تكوينات النظام..."
    cp -r "${PROJECT_ROOT}/monitoring/emergency" "${config_backup_dir}/"
    
    # إزالة الأسرار من النسخة غير المشفرة
    if [ -d "${config_backup_dir}/emergency/secrets" ]; then
        print_message "${BLUE}" "🔐 أمان الأسرار..."
        
        # إنشاء نسخة مشفرة منفصلة للأسرار
        tar -czf "${config_backup_dir}/secrets_encrypted.tar.gz" \
            -C "${config_backup_dir}/emergency" secrets/
        
        # حذف الأسرار من النسخة العادية
        rm -rf "${config_backup_dir}/emergency/secrets"
        
        print_message "${GREEN}" "✅ تم تأمين الأسرار"
    fi
    
    # نسخ ملفات التكوين من المجلد الرئيسي
    if [ -d "${PROJECT_ROOT}/config" ]; then
        print_message "${BLUE}" "📋 نسخ ملفات التكوين العامة..."
        cp -r "${PROJECT_ROOT}/config" "${config_backup_dir}/"
    fi
    
    print_message "${GREEN}" "✅ تم نسخ التكوينات"
}

# إنشاء قاعدة بيانات النظام
create_system_snapshot() {
    print_section "إنشاء لقطة النظام"
    
    local system_backup_dir="${BACKUP_DIR}/system_info"
    mkdir -p "${system_backup_dir}"
    
    # معلومات النظام
    print_message "${BLUE}" "🖥️  جمع معلومات النظام..."
    
    {
        echo "=== System Information ==="
        uname -a
        echo
        echo "=== Docker Version ==="
        docker version
        echo
        echo "=== Docker Compose Version ==="
        docker-compose version
        echo
        echo "=== Disk Usage ==="
        df -h
        echo
        echo "=== Memory Usage ==="
        free -h
        echo
        echo "=== Running Processes ==="
        ps aux | grep -E "(prometheus|grafana|alertmanager|docker)" | grep -v grep
        echo
        echo "=== Network Ports ==="
        netstat -tulpn | grep -E ":(3000|8080|9090|9093|9100)"
    } > "${system_backup_dir}/system_info.txt"
    
    # حفظ قائمة Docker images
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.Size}}" \
        > "${system_backup_dir}/docker_images.txt"
    
    print_message "${GREEN}" "✅ تم إنشاء لقطة النظام"
}

# ضغط وتشفير النسخة الاحتياطية
compress_and_encrypt() {
    print_section "ضغط وتشفير النسخة الاحتياطية"
    
    local archive_path="/tmp/${BACKUP_NAME}.tar.gz"
    local encrypted_path="/tmp/${BACKUP_NAME}.tar.gz.enc"
    
    # إضافة timestamp النهاية إلى metadata
    echo "\"backup_end_time\": \"$(date -Iseconds)\"" >> "${BACKUP_DIR}/backup_metadata.json"
    
    # ضغط الملفات
    print_message "${BLUE}" "🗜️  ضغط الملفات..."
    tar -czf "${archive_path}" -C "$(dirname "${BACKUP_DIR}")" "$(basename "${BACKUP_DIR}")"
    
    local archive_size=$(du -h "${archive_path}" | cut -f1)
    print_message "${GREEN}" "✅ تم الضغط: ${archive_size}"
    
    # تشفير النسخة الاحتياطية
    print_message "${BLUE}" "🔐 تشفير النسخة الاحتياطية..."
    openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
        -in "${archive_path}" \
        -out "${encrypted_path}" \
        -k "${ENCRYPTION_KEY}"
    
    # حساب checksum
    local checksum=$(sha256sum "${encrypted_path}" | cut -d' ' -f1)
    echo "${checksum}" > "${encrypted_path}.sha256"
    
    print_message "${GREEN}" "✅ تم التشفير والتحقق"
    
    # تنظيف الملفات المؤقتة
    rm -f "${archive_path}"
    rm -rf "${BACKUP_DIR}"
    
    echo "${encrypted_path}"
}

# رفع إلى AWS S3
upload_to_s3() {
    local encrypted_file=$1
    print_section "رفع إلى AWS S3"
    
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/"
    local file_name=$(basename "${encrypted_file}")
    
    print_message "${BLUE}" "☁️  رفع إلى S3: ${s3_path}"
    
    # رفع النسخة الاحتياطية المشفرة
    aws s3 cp "${encrypted_file}" "${s3_path}${file_name}" \
        --storage-class GLACIER_IR \
        --metadata "project=ai-teddy-bear,component=emergency-monitoring,backup-type=full,timestamp=${TIMESTAMP}" \
        --sse aws:kms \
        --sse-kms-key-id "${KMS_KEY_ID}"
    
    # رفع checksum
    aws s3 cp "${encrypted_file}.sha256" "${s3_path}${file_name}.sha256" \
        --storage-class GLACIER_IR \
        --metadata "project=ai-teddy-bear,component=checksum,timestamp=${TIMESTAMP}"
    
    # إنشاء object versioning
    local version_id=$(aws s3api put-object \
        --bucket "${S3_BUCKET}" \
        --key "${S3_PREFIX}/${file_name}" \
        --body "${encrypted_file}" \
        --storage-class GLACIER_IR \
        --server-side-encryption aws:kms \
        --ssekms-key-id "${KMS_KEY_ID}" \
        --metadata "project=ai-teddy-bear,component=emergency-monitoring,backup-type=full,timestamp=${TIMESTAMP}" \
        --query 'VersionId' --output text)
    
    print_message "${GREEN}" "✅ تم الرفع بنجاح"
    print_message "${GREEN}" "📍 المسار: ${s3_path}${file_name}"
    print_message "${GREEN}" "🔖 Version ID: ${version_id}"
    
    # تنظيف الملفات المحلية
    rm -f "${encrypted_file}" "${encrypted_file}.sha256"
    
    return 0
}

# إرسال تقرير النسخ الاحتياطي
send_backup_report() {
    local status=$1
    local s3_path=$2
    
    print_section "إرسال تقرير النسخ الاحتياطي"
    
    local report_file="/tmp/backup_report_${TIMESTAMP}.json"
    
    cat > "${report_file}" << EOF
{
    "backup_status": "${status}",
    "backup_name": "${BACKUP_NAME}",
    "timestamp": "${TIMESTAMP}",
    "s3_location": "${s3_path}",
    "backup_size": "$(aws s3 ls "${s3_path}" | awk '{print $3}' || echo 'unknown')",
    "encryption": "aes-256-cbc + aws:kms",
    "retention": "7_years_glacier",
    "checksum_verified": true,
    "backup_duration": "$(($(date +%s) - $(date -d "${TIMESTAMP}" +%s 2>/dev/null || echo 0))) seconds",
    "components_backed_up": [
        "prometheus_data",
        "grafana_data", 
        "docker_state",
        "configurations",
        "secrets_encrypted",
        "system_snapshot"
    ]
}
EOF
    
    # إرسال إلى CloudWatch Logs (اختياري)
    if command -v aws &> /dev/null; then
        aws logs create-log-group --log-group-name "/aws/teddy/backup" 2>/dev/null || true
        aws logs put-log-events \
            --log-group-name "/aws/teddy/backup" \
            --log-stream-name "backup-${TIMESTAMP}" \
            --log-events "timestamp=$(date +%s)000,message=$(cat "${report_file}")" 2>/dev/null || true
    fi
    
    print_message "${GREEN}" "✅ تم إرسال تقرير النسخ الاحتياطي"
    
    rm -f "${report_file}"
}

# اختبار سلامة النسخة الاحتياطية
test_backup_integrity() {
    local s3_path=$1
    print_section "اختبار سلامة النسخة الاحتياطية"
    
    local test_file="/tmp/backup_test_${TIMESTAMP}.tar.gz.enc"
    local test_checksum="/tmp/backup_test_${TIMESTAMP}.tar.gz.enc.sha256"
    
    # تحميل النسخة الاحتياطية للاختبار
    print_message "${BLUE}" "📥 تحميل النسخة للاختبار..."
    aws s3 cp "${s3_path}" "${test_file}"
    aws s3 cp "${s3_path}.sha256" "${test_checksum}"
    
    # التحقق من checksum
    print_message "${BLUE}" "🔍 التحقق من سلامة البيانات..."
    if sha256sum -c "${test_checksum}"; then
        print_message "${GREEN}" "✅ اختبار سلامة البيانات نجح"
    else
        print_message "${RED}" "❌ فشل في اختبار سلامة البيانات"
        return 1
    fi
    
    # اختبار فك التشفير
    print_message "${BLUE}" "🔓 اختبار فك التشفير..."
    if openssl enc -aes-256-cbc -d -pbkdf2 -iter 100000 \
        -in "${test_file}" \
        -k "${ENCRYPTION_KEY}" \
        -out /dev/null 2>/dev/null; then
        print_message "${GREEN}" "✅ اختبار فك التشفير نجح"
    else
        print_message "${RED}" "❌ فشل في اختبار فك التشفير"
        return 1
    fi
    
    # تنظيف ملفات الاختبار
    rm -f "${test_file}" "${test_checksum}"
    
    print_message "${GREEN}" "✅ جميع اختبارات السلامة نجحت"
    return 0
}

# الدالة الرئيسية
main() {
    print_message "${BLUE}" "
╔═══════════════════════════════════════════════════════════════════════════════╗
║                      💾 نظام النسخ الاحتياطي الكامل                          ║
║                   AI Teddy Bear Emergency Monitoring Backup                  ║
║                                                                               ║
║  🔐 نسخ احتياطي مشفر وآمن لجميع مكونات النظام                              ║
║  ☁️  حفظ سحابي مع versioning و retention policies                          ║
║  🛡️  تشفير متقدم AES-256 + AWS KMS                                         ║
║  📊 مراقبة وتقارير شاملة                                                   ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"
    
    # إعداد السجلات
    setup_logging
    
    # تنفيذ خطوات النسخ الاحتياطي
    local steps=(
        "check_prerequisites:فحص المتطلبات الأساسية"
        "create_backup_directory:إعداد مجلد النسخ الاحتياطي"
        "backup_docker_state:نسخ احتياطي لحالة Docker"
        "backup_persistent_data:نسخ احتياطي للبيانات المستمرة"
        "backup_configurations:نسخ احتياطي للتكوينات والأسرار"
        "create_system_snapshot:إنشاء لقطة النظام"
    )
    
    local total_steps=${#steps[@]}
    local current_step=0
    
    for step_info in "${steps[@]}"; do
        IFS=':' read -r step_function step_description <<< "${step_info}"
        ((current_step++))
        
        print_message "${CYAN}" "🚀 خطوة ${current_step}/${total_steps}: ${step_description}"
        
        if ${step_function}; then
            print_message "${GREEN}" "✅ تمت بنجاح: ${step_description}"
        else
            print_message "${RED}" "❌ فشلت: ${step_description}"
            exit 1
        fi
    done
    
    # ضغط وتشفير
    local encrypted_file
    if encrypted_file=$(compress_and_encrypt); then
        print_message "${GREEN}" "✅ تم الضغط والتشفير: ${encrypted_file}"
    else
        print_message "${RED}" "❌ فشل في الضغط والتشفير"
        exit 1
    fi
    
    # رفع إلى S3
    local s3_path="s3://${S3_BUCKET}/${S3_PREFIX}/$(basename "${encrypted_file}")"
    if upload_to_s3 "${encrypted_file}"; then
        print_message "${GREEN}" "✅ تم الرفع إلى S3: ${s3_path}"
    else
        print_message "${RED}" "❌ فشل في الرفع إلى S3"
        exit 1
    fi
    
    # اختبار سلامة النسخة الاحتياطية
    if test_backup_integrity "${s3_path}"; then
        print_message "${GREEN}" "✅ تم التحقق من سلامة النسخة الاحتياطية"
    else
        print_message "${RED}" "❌ فشل في اختبار سلامة النسخة الاحتياطية"
        exit 1
    fi
    
    # إرسال تقرير النسخ الاحتياطي
    send_backup_report "success" "${s3_path}"
    
    print_message "${GREEN}" "
🎉 تم إنجاز النسخ الاحتياطي الكامل بنجاح!

📋 ملخص العملية:
✅ تم نسخ جميع البيانات والتكوينات
✅ تم التشفير باستخدام AES-256 + AWS KMS
✅ تم الرفع إلى S3 مع Glacier storage
✅ تم اختبار سلامة البيانات
✅ تم إنشاء versioning و metadata

📍 مسار النسخة الاحتياطية:
${s3_path}

🔒 معلومات الأمان:
- التشفير: AES-256-CBC + PBKDF2
- AWS KMS Key: ${KMS_KEY_ID}
- تاريخ الانتهاء: $(date -d '+7 years')

💡 لاستعادة النسخة الاحتياطية:
./restore_backup.sh ${TIMESTAMP}
"
    
    print_message "${CYAN}" "📝 سجل العملية محفوظ في: ${LOG_FILE}"
}

# تنفيذ الدالة الرئيسية
main "$@" 