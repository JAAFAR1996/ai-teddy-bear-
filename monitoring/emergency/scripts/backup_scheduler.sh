#!/bin/bash

# ⏰ Emergency Backup Scheduler - AI Teddy Bear DevOps Team
# الإصدار: v2025.1.0

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly CRON_FILE="/etc/cron.d/teddy-emergency-backup"
readonly LOG_FILE="/var/log/teddy/backup-scheduler.log"

# ألوان المخرجات
readonly GREEN='\033[0;32m'
readonly BLUE='\033[0;34m'
readonly RED='\033[0;31m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m'

print_message() {
    echo -e "${1}${2}${NC}" | tee -a "${LOG_FILE}"
}

# عرض المساعدة
show_help() {
    cat << EOF
⏰ Emergency Backup Scheduler

الاستخدام:
    ./backup_scheduler.sh [COMMAND]

الأوامر:
    install     تثبيت النسخ الاحتياطية التلقائية
    uninstall   إلغاء النسخ الاحتياطية التلقائية
    status      عرض حالة الجدولة
    run-now     تشغيل نسخة احتياطية فورية
    
الجدولة المثبتة:
    - يومياً الساعة 2:00 صباحاً (نسخة كاملة)
    - كل 6 ساعات (نسخة تكوينات)
    - أسبوعياً (نسخة أرشيفية)
EOF
}

# تثبيت جدولة النسخ الاحتياطية
install_scheduler() {
    print_message "${BLUE}" "⏰ تثبيت جدولة النسخ الاحتياطية..."
    
    # التحقق من الصلاحيات
    if [ "$EUID" -ne 0 ]; then
        print_message "${RED}" "❌ يجب تشغيل السكريبت بصلاحيات root"
        exit 1
    fi
    
    # إنشاء مجلد السجلات
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    # إنشاء ملف cron
    cat > "${CRON_FILE}" << EOF
# AI Teddy Bear Emergency Backup Scheduler
# Managed by DevOps Team - Do not edit manually

# متغيرات البيئة
BACKUP_S3_BUCKET=ai-teddy-emergency-backups
BACKUP_ENCRYPTION_KEY=\$(openssl rand -base64 32)
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# نسخة احتياطية كاملة يومياً في 2:00 صباحاً
0 2 * * * root ${SCRIPT_DIR}/full_backup.sh >> ${LOG_FILE} 2>&1

# نسخة احتياطية للتكوينات كل 6 ساعات
0 */6 * * * root ${SCRIPT_DIR}/config_backup.sh >> ${LOG_FILE} 2>&1

# نسخة احتياطية أرشيفية أسبوعياً (الأحد 1:00 صباحاً)
0 1 * * 0 root ${SCRIPT_DIR}/archive_backup.sh >> ${LOG_FILE} 2>&1

# تنظيف النسخ القديمة شهرياً
0 3 1 * * root ${SCRIPT_DIR}/cleanup_old_backups.sh >> ${LOG_FILE} 2>&1

# فحص سلامة النسخ الاحتياطية أسبوعياً
0 4 * * 1 root ${SCRIPT_DIR}/verify_backups.sh >> ${LOG_FILE} 2>&1
EOF
    
    # تعديل صلاحيات الملف
    chmod 644 "${CRON_FILE}"
    
    # إعادة تحميل cron
    systemctl reload crond 2>/dev/null || systemctl reload cron 2>/dev/null || true
    
    print_message "${GREEN}" "✅ تم تثبيت جدولة النسخ الاحتياطية"
    print_message "${BLUE}" "📋 الجدولة:"
    print_message "${BLUE}" "   - نسخة كاملة: يومياً 2:00 صباحاً"
    print_message "${BLUE}" "   - نسخة تكوينات: كل 6 ساعات"
    print_message "${BLUE}" "   - نسخة أرشيفية: أسبوعياً (الأحد 1:00)"
    print_message "${BLUE}" "   - تنظيف: شهرياً"
    print_message "${BLUE}" "   - فحص سلامة: أسبوعياً"
}

# إلغاء جدولة النسخ الاحتياطية
uninstall_scheduler() {
    print_message "${BLUE}" "🗑️  إلغاء جدولة النسخ الاحتياطية..."
    
    if [ "$EUID" -ne 0 ]; then
        print_message "${RED}" "❌ يجب تشغيل السكريبت بصلاحيات root"
        exit 1
    fi
    
    if [ -f "${CRON_FILE}" ]; then
        rm -f "${CRON_FILE}"
        systemctl reload crond 2>/dev/null || systemctl reload cron 2>/dev/null || true
        print_message "${GREEN}" "✅ تم إلغاء جدولة النسخ الاحتياطية"
    else
        print_message "${YELLOW}" "⚠️  لا توجد جدولة مثبتة"
    fi
}

# عرض حالة الجدولة
show_status() {
    print_message "${BLUE}" "📊 حالة جدولة النسخ الاحتياطية:"
    
    if [ -f "${CRON_FILE}" ]; then
        print_message "${GREEN}" "✅ الجدولة مثبتة ونشطة"
        echo
        print_message "${BLUE}" "📋 المهام المجدولة:"
        grep -v "^#" "${CRON_FILE}" | grep -v "^$" | while read -r line; do
            echo "   ${line}"
        done
        echo
        
        # عرض آخر تشغيل
        if [ -f "${LOG_FILE}" ]; then
            print_message "${BLUE}" "📝 آخر سجلات النسخ الاحتياطية:"
            tail -10 "${LOG_FILE}" | sed 's/^/   /'
        fi
        
        # عرض المهام النشطة
        print_message "${BLUE}" "⏰ المهام النشطة في cron:"
        crontab -l 2>/dev/null | grep -i backup | sed 's/^/   /' || \
            print_message "${YELLOW}" "   لا توجد مهام في crontab المستخدم"
            
    else
        print_message "${RED}" "❌ الجدولة غير مثبتة"
    fi
}

# تشغيل نسخة احتياطية فورية
run_backup_now() {
    print_message "${BLUE}" "🚀 تشغيل نسخة احتياطية فورية..."
    
    # التحقق من وجود السكريبت
    if [ ! -f "${SCRIPT_DIR}/full_backup.sh" ]; then
        print_message "${RED}" "❌ سكريبت النسخ الاحتياطي غير موجود"
        exit 1
    fi
    
    # تشغيل النسخة الاحتياطية
    if "${SCRIPT_DIR}/full_backup.sh"; then
        print_message "${GREEN}" "✅ تم إنجاز النسخة الاحتياطية بنجاح"
    else
        print_message "${RED}" "❌ فشل في النسخة الاحتياطية"
        exit 1
    fi
}

# إنشاء سكريبت نسخ التكوينات
create_config_backup_script() {
    cat > "${SCRIPT_DIR}/config_backup.sh" << 'EOF'
#!/bin/bash
# نسخة احتياطية سريعة للتكوينات
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="${BACKUP_S3_BUCKET:-ai-teddy-emergency-backups}"
ENCRYPTION_KEY="${BACKUP_ENCRYPTION_KEY:-$(openssl rand -base64 32)}"

echo "$(date): بدء نسخة احتياطية للتكوينات..."

# نسخ التكوينات فقط
BACKUP_DIR="/tmp/config_backup_${TIMESTAMP}"
mkdir -p "${BACKUP_DIR}"

cp -r "$(dirname "$0")/../" "${BACKUP_DIR}/"
rm -rf "${BACKUP_DIR}/secrets" 2>/dev/null || true

# ضغط وتشفير
tar -czf "/tmp/config_${TIMESTAMP}.tar.gz" -C "$(dirname "${BACKUP_DIR}")" "$(basename "${BACKUP_DIR}")"
openssl enc -aes-256-cbc -salt -pbkdf2 -in "/tmp/config_${TIMESTAMP}.tar.gz" \
    -out "/tmp/config_${TIMESTAMP}.tar.gz.enc" -k "${ENCRYPTION_KEY}"

# رفع إلى S3
aws s3 cp "/tmp/config_${TIMESTAMP}.tar.gz.enc" \
    "s3://${S3_BUCKET}/configs/${TIMESTAMP}/" \
    --storage-class STANDARD_IA

# تنظيف
rm -rf "${BACKUP_DIR}" "/tmp/config_${TIMESTAMP}.tar.gz" "/tmp/config_${TIMESTAMP}.tar.gz.enc"

echo "$(date): تم إنجاز نسخة احتياطية للتكوينات"
EOF
    
    chmod +x "${SCRIPT_DIR}/config_backup.sh"
}

# إنشاء سكريبت النسخة الأرشيفية
create_archive_backup_script() {
    cat > "${SCRIPT_DIR}/archive_backup.sh" << 'EOF'
#!/bin/bash
# نسخة احتياطية أرشيفية طويلة المدى
set -euo pipefail

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="${BACKUP_S3_BUCKET:-ai-teddy-emergency-backups}"

echo "$(date): بدء النسخة الأرشيفية الأسبوعية..."

# تشغيل النسخة الكاملة مع حفظ أرشيفي
BACKUP_S3_BUCKET="${S3_BUCKET}" "$(dirname "$0")/full_backup.sh"

# نسخ إلى مجلد الأرشيف
aws s3 sync "s3://${S3_BUCKET}/emergency-monitoring/${TIMESTAMP}/" \
    "s3://${S3_BUCKET}/archive/$(date +%Y)/$(date +%m)/${TIMESTAMP}/" \
    --storage-class GLACIER

echo "$(date): تم إنجاز النسخة الأرشيفية"
EOF
    
    chmod +x "${SCRIPT_DIR}/archive_backup.sh"
}

# إنشاء سكريبت تنظيف النسخ القديمة
create_cleanup_script() {
    cat > "${SCRIPT_DIR}/cleanup_old_backups.sh" << 'EOF'
#!/bin/bash
# تنظيف النسخ الاحتياطية القديمة
set -euo pipefail

S3_BUCKET="${BACKUP_S3_BUCKET:-ai-teddy-emergency-backups}"
RETENTION_DAYS=30

echo "$(date): بدء تنظيف النسخ الاحتياطية القديمة..."

# حذف النسخ اليومية الأقدم من 30 يوم
aws s3 ls "s3://${S3_BUCKET}/emergency-monitoring/" | \
    awk '{print $2}' | \
    while read -r folder; do
        folder_date=$(echo "${folder}" | sed 's|/||g' | cut -c1-8)
        if [ -n "${folder_date}" ] && [ "${folder_date}" -lt "$(date -d "${RETENTION_DAYS} days ago" +%Y%m%d)" ]; then
            echo "حذف النسخة القديمة: ${folder}"
            aws s3 rm "s3://${S3_BUCKET}/emergency-monitoring/${folder}" --recursive
        fi
    done

echo "$(date): تم تنظيف النسخ القديمة"
EOF
    
    chmod +x "${SCRIPT_DIR}/cleanup_old_backups.sh"
}

# إنشاء سكريبت فحص سلامة النسخ
create_verify_script() {
    cat > "${SCRIPT_DIR}/verify_backups.sh" << 'EOF'
#!/bin/bash
# فحص سلامة النسخ الاحتياطية
set -euo pipefail

S3_BUCKET="${BACKUP_S3_BUCKET:-ai-teddy-emergency-backups}"

echo "$(date): بدء فحص سلامة النسخ الاحتياطية..."

# فحص آخر 7 نسخ احتياطية
aws s3 ls "s3://${S3_BUCKET}/emergency-monitoring/" | \
    sort -k2 -r | head -7 | \
    while read -r line; do
        folder=$(echo "${line}" | awk '{print $2}')
        backup_file=$(aws s3 ls "s3://${S3_BUCKET}/emergency-monitoring/${folder}" | grep "\.tar\.gz\.enc$" | awk '{print $4}')
        
        if [ -n "${backup_file}" ]; then
            echo "فحص النسخة: ${folder}${backup_file}"
            
            # التحقق من وجود checksum
            if aws s3 ls "s3://${S3_BUCKET}/emergency-monitoring/${folder}${backup_file}.sha256" &>/dev/null; then
                echo "✅ ${folder}: checksum موجود"
            else
                echo "❌ ${folder}: checksum مفقود"
            fi
            
            # التحقق من حجم الملف
            file_size=$(aws s3 ls "s3://${S3_BUCKET}/emergency-monitoring/${folder}${backup_file}" | awk '{print $3}')
            if [ "${file_size}" -gt 1000000 ]; then  # أكبر من 1MB
                echo "✅ ${folder}: حجم الملف مناسب (${file_size} bytes)"
            else
                echo "❌ ${folder}: حجم الملف صغير جداً (${file_size} bytes)"
            fi
        fi
    done

echo "$(date): تم إنجاز فحص سلامة النسخ الاحتياطية"
EOF
    
    chmod +x "${SCRIPT_DIR}/verify_backups.sh"
}

# الدالة الرئيسية
main() {
    local command="${1:-help}"
    
    case "${command}" in
        "install")
            install_scheduler
            create_config_backup_script
            create_archive_backup_script
            create_cleanup_script
            create_verify_script
            ;;
        "uninstall")
            uninstall_scheduler
            ;;
        "status")
            show_status
            ;;
        "run-now")
            run_backup_now
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            print_message "${RED}" "❌ أمر غير معروف: ${command}"
            show_help
            exit 1
            ;;
    esac
}

# تشغيل الدالة الرئيسية
main "$@" 