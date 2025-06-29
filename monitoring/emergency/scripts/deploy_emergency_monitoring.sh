#!/bin/bash
# 🚨 Emergency Monitoring Deployment Script
# AI Teddy Bear Security Team - Critical Infrastructure Deployment
# تاريخ الإنشاء: $(date)
# الإصدار: v2025.1.0

set -euo pipefail  # فشل فوري عند أي خطأ

# ألوان للمخرجات
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly NC='\033[0m' # No Color

# متغيرات التكوين
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
readonly MONITORING_DIR="${PROJECT_ROOT}/monitoring/emergency"
readonly DEPLOYMENT_TIMESTAMP=$(date '+%Y%m%d_%H%M%S')
readonly LOG_FILE="/var/log/teddy/emergency-deployment-${DEPLOYMENT_TIMESTAMP}.log"
readonly BACKUP_DIR="/var/backups/teddy-monitoring/${DEPLOYMENT_TIMESTAMP}"

# إعداد السجلات
setup_logging() {
    # إنشاء مجلد السجلات إذا لم يكن موجود
    sudo mkdir -p "$(dirname "${LOG_FILE}")"
    sudo mkdir -p "${BACKUP_DIR}"
    
    # تمكين التسجيل المزدوج
    exec 1> >(tee -a "${LOG_FILE}")
    exec 2> >(tee -a "${LOG_FILE}" >&2)
    
    echo -e "${BLUE}📋 بدء تشغيل سكريبت النشر الطارئ${NC}"
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
    print_message "${CYAN}" "🔧 ${title}"
    print_message "${CYAN}" "═══════════════════════════════════════════════════════════"
}

# فحص المتطلبات الأساسية
check_prerequisites() {
    print_section "فحص المتطلبات الأساسية"
    
    local missing_tools=()
    
    # فحص الأدوات المطلوبة
    local required_tools=(
        "docker:Docker"
        "docker-compose:Docker Compose"
        "openssl:OpenSSL"
        "kubectl:Kubernetes CLI"
        "curl:cURL"
        "jq:JSON Processor"
    )
    
    for tool_info in "${required_tools[@]}"; do
        IFS=':' read -r tool_name tool_desc <<< "${tool_info}"
        if ! command -v "${tool_name}" &> /dev/null; then
            missing_tools+=("${tool_desc} (${tool_name})")
            print_message "${RED}" "❌ ${tool_desc} غير مثبت"
        else
            local version=$(${tool_name} --version 2>/dev/null | head -n1 || echo "غير معروف")
            print_message "${GREEN}" "✅ ${tool_desc}: ${version}"
        fi
    done
    
    # فحص Docker daemon
    if ! docker info >/dev/null 2>&1; then
        missing_tools+=("Docker Daemon (خدمة Docker غير نشطة)")
        print_message "${RED}" "❌ خدمة Docker غير نشطة"
    else
        print_message "${GREEN}" "✅ خدمة Docker نشطة"
    fi
    
    # فحص مساحة القرص
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local required_space=10485760  # 10GB بالكيلوبايت
    
    if [ "${available_space}" -lt "${required_space}" ]; then
        print_message "${RED}" "❌ مساحة قرص غير كافية. المطلوب: 10GB، المتاح: $((available_space/1024/1024))GB"
        missing_tools+=("مساحة قرص كافية (10GB على الأقل)")
    else
        print_message "${GREEN}" "✅ مساحة قرص كافية: $((available_space/1024/1024))GB"
    fi
    
    # فحص الذاكرة
    local available_memory=$(free -m | awk 'NR==2{print $7}')
    local required_memory=4096  # 4GB بالميجابايت
    
    if [ "${available_memory}" -lt "${required_memory}" ]; then
        print_message "${YELLOW}" "⚠️  ذاكرة منخفضة. المطلوب: 4GB، المتاح: ${available_memory}MB"
    else
        print_message "${GREEN}" "✅ ذاكرة كافية: ${available_memory}MB"
    fi
    
    # إنهاء إذا كانت هناك أدوات مفقودة
    if [ ${#missing_tools[@]} -ne 0 ]; then
        print_message "${RED}" "❌ أدوات مفقودة:"
        for tool in "${missing_tools[@]}"; do
            print_message "${RED}" "   - ${tool}"
        done
        print_message "${RED}" "يرجى تثبيت الأدوات المفقودة قبل المتابعة."
        exit 1
    fi
    
    print_message "${GREEN}" "✅ جميع المتطلبات متوفرة"
}

# إنشاء الشهادات الأمنية
generate_ssl_certificates() {
    print_section "إنشاء الشهادات الأمنية"
    
    local ssl_dir="${MONITORING_DIR}/ssl"
    local certs_dir="${ssl_dir}/certs"
    local private_dir="${ssl_dir}/private"
    
    # إنشاء المجلدات
    mkdir -p "${certs_dir}" "${private_dir}"
    chmod 700 "${private_dir}"
    
    # إنشاء CA Authority
    if [ ! -f "${private_dir}/ca-key.pem" ]; then
        print_message "${BLUE}" "🔐 إنشاء شهادة المرجع الأساسي (CA)..."
        
        openssl genrsa -out "${private_dir}/ca-key.pem" 4096
        openssl req -new -x509 -key "${private_dir}/ca-key.pem" \
            -out "${certs_dir}/ca.pem" -days 3650 \
            -subj "/C=SA/ST=Riyadh/L=Riyadh/O=TeddyBear Security/OU=Emergency Monitoring/CN=Teddy CA"
        
        print_message "${GREEN}" "✅ تم إنشاء شهادة المرجع الأساسي"
    else
        print_message "${YELLOW}" "⚠️  شهادة المرجع الأساسي موجودة مسبقاً"
    fi
    
    # إنشاء شهادات للخدمات
    local services=("prometheus" "grafana" "alertmanager")
    
    for service in "${services[@]}"; do
        if [ ! -f "${private_dir}/${service}-key.pem" ]; then
            print_message "${BLUE}" "🔐 إنشاء شهادة ${service}..."
            
            # إنشاء مفتاح خاص
            openssl genrsa -out "${private_dir}/${service}-key.pem" 2048
            
            # إنشاء طلب شهادة
            openssl req -new -key "${private_dir}/${service}-key.pem" \
                -out "${private_dir}/${service}.csr" \
                -subj "/C=SA/ST=Riyadh/L=Riyadh/O=TeddyBear Security/OU=Emergency Monitoring/CN=${service}.teddysecurity.ai"
            
            # إنشاء ملف التكوين للشهادة
            cat > "${private_dir}/${service}.conf" <<EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = SA
ST = Riyadh
L = Riyadh
O = TeddyBear Security
OU = Emergency Monitoring
CN = ${service}.teddysecurity.ai

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = ${service}.teddysecurity.ai
DNS.2 = ${service}-emergency
DNS.3 = localhost
IP.1 = 127.0.0.1
IP.2 = 172.20.0.1
EOF
            
            # توقيع الشهادة
            openssl x509 -req -in "${private_dir}/${service}.csr" \
                -CA "${certs_dir}/ca.pem" -CAkey "${private_dir}/ca-key.pem" \
                -CAcreateserial -out "${certs_dir}/${service}.pem" \
                -days 365 -extensions v3_req -extfile "${private_dir}/${service}.conf"
            
            # تنظيف الملفات المؤقتة
            rm "${private_dir}/${service}.csr" "${private_dir}/${service}.conf"
            
            print_message "${GREEN}" "✅ تم إنشاء شهادة ${service}"
        else
            print_message "${YELLOW}" "⚠️  شهادة ${service} موجودة مسبقاً"
        fi
    done
    
    # تعديل صلاحيات الملفات
    chmod 600 "${private_dir}"/*
    chmod 644 "${certs_dir}"/*
    
    print_message "${GREEN}" "✅ تم إنشاء جميع الشهادات الأمنية"
}

# إنشاء ملفات الأسرار
generate_secrets() {
    print_section "إنشاء الأسرار الآمنة"
    
    local secrets_dir="${MONITORING_DIR}/secrets"
    mkdir -p "${secrets_dir}"
    chmod 700 "${secrets_dir}"
    
    # قائمة الأسرار المطلوبة
    local secrets=(
        "grafana-admin-password:32"
        "grafana-secret-key:64"
        "postgres-grafana-password:32"
        "jwt-secret:64"
        "database-url:0"
    )
    
    for secret_info in "${secrets[@]}"; do
        IFS=':' read -r secret_name secret_length <<< "${secret_info}"
        local secret_file="${secrets_dir}/${secret_name}.txt"
        
        if [ ! -f "${secret_file}" ]; then
            print_message "${BLUE}" "🔑 إنشاء سر ${secret_name}..."
            
            if [ "${secret_length}" -gt 0 ]; then
                # إنشاء سر عشوائي
                openssl rand -base64 "${secret_length}" | tr -d '\n' > "${secret_file}"
            else
                # أسرار خاصة تحتاج تعبئة يدوية
                case "${secret_name}" in
                    "database-url")
                        echo "postgresql://grafana:$(cat ${secrets_dir}/postgres-grafana-password.txt)@postgres-grafana:5432/grafana?sslmode=require" > "${secret_file}"
                        ;;
                esac
            fi
            
            chmod 600 "${secret_file}"
            print_message "${GREEN}" "✅ تم إنشاء ${secret_name}"
        else
            print_message "${YELLOW}" "⚠️  ${secret_name} موجود مسبقاً"
        fi
    done
    
    print_message "${GREEN}" "✅ تم إنشاء جميع الأسرار"
}

# إنشاء قواعد التنبيه الأمنية
create_alert_rules() {
    print_section "إنشاء قواعد التنبيه الأمنية"
    
    local rules_dir="${MONITORING_DIR}/prometheus/rules"
    mkdir -p "${rules_dir}"
    
    # نسخ قواعد التنبيه من ConfigMap
    print_message "${BLUE}" "📋 نسخ قواعد التنبيه الأمنية..."
    
    # استخراج قواعد التنبيه من ConfigMap
    local configmap_file="${MONITORING_DIR}/kubernetes/emergency-monitoring-configmap.yaml"
    
    if [ -f "${configmap_file}" ]; then
        # استخراج قسم security-rules.yml من ConfigMap
        awk '/security-rules\.yml: \|/,/^[[:space:]]*[^[:space:]]/ {
            if (/security-rules\.yml: \|/) next
            if (/^[[:space:]]*[^[:space:]]/ && !/^[[:space:]]*groups:/) exit
            gsub(/^[[:space:]]{4}/, "")
            print
        }' "${configmap_file}" > "${rules_dir}/security_critical.yml"
        
        print_message "${GREEN}" "✅ تم نسخ قواعد التنبيه الأمنية"
    else
        print_message "${RED}" "❌ ملف ConfigMap غير موجود"
        exit 1
    fi
    
    # التحقق من صحة قواعد التنبيه
    print_message "${BLUE}" "🔍 التحقق من صحة قواعد التنبيه..."
    
    if docker run --rm -v "${rules_dir}:/rules" prom/prometheus:latest promtool check rules /rules/*.yml; then
        print_message "${GREEN}" "✅ قواعد التنبيه صحيحة"
    else
        print_message "${RED}" "❌ خطأ في قواعد التنبيه"
        exit 1
    fi
}

# نسخ احتياطي للتكوين الحالي
backup_current_config() {
    print_section "نسخ احتياطي للتكوين الحالي"
    
    # التحقق من وجود نشر سابق
    if docker-compose -f "${MONITORING_DIR}/docker-compose.emergency.yml" ps -q >/dev/null 2>&1; then
        print_message "${BLUE}" "💾 إنشاء نسخة احتياطية للنشر الحالي..."
        
        # إيقاف الخدمات
        docker-compose -f "${MONITORING_DIR}/docker-compose.emergency.yml" stop
        
        # نسخ احتياطي للبيانات
        local data_dirs=(
            "/var/lib/teddy/monitoring/prometheus"
            "/var/lib/teddy/monitoring/grafana"
        )
        
        for data_dir in "${data_dirs[@]}"; do
            if [ -d "${data_dir}" ]; then
                local backup_name=$(basename "${data_dir}")
                print_message "${BLUE}" "📦 نسخ احتياطي لـ ${backup_name}..."
                sudo cp -r "${data_dir}" "${BACKUP_DIR}/${backup_name}"
                print_message "${GREEN}" "✅ تم نسخ ${backup_name}"
            fi
        done
        
        print_message "${GREEN}" "✅ تم إنشاء النسخة الاحتياطية في ${BACKUP_DIR}"
    else
        print_message "${YELLOW}" "⚠️  لا يوجد نشر سابق"
    fi
}

# نشر النظام
deploy_monitoring_system() {
    print_section "نشر نظام المراقبة الطارئة"
    
    cd "${MONITORING_DIR}"
    
    # سحب الصور الجديدة
    print_message "${BLUE}" "🐳 سحب أحدث صور Docker..."
    docker-compose -f docker-compose.emergency.yml pull
    
    # إنشاء مجلدات البيانات
    print_message "${BLUE}" "📁 إنشاء مجلدات البيانات..."
    sudo mkdir -p /var/lib/teddy/monitoring/{prometheus,grafana}
    sudo chown -R 65534:65534 /var/lib/teddy/monitoring/prometheus
    sudo chown -R 472:472 /var/lib/teddy/monitoring/grafana
    
    # نشر النظام
    print_message "${BLUE}" "🚀 نشر نظام المراقبة..."
    docker-compose -f docker-compose.emergency.yml up -d
    
    # انتظار تشغيل الخدمات
    print_message "${BLUE}" "⏳ انتظار تشغيل الخدمات..."
    sleep 30
    
    # فحص حالة الخدمات
    print_message "${BLUE}" "🔍 فحص حالة الخدمات..."
    docker-compose -f docker-compose.emergency.yml ps
    
    print_message "${GREEN}" "✅ تم نشر النظام بنجاح"
}

# فحص صحة النظام
health_check() {
    print_section "فحص صحة النظام"
    
    local services=(
        "prometheus-emergency:9090:/-/healthy"
        "alertmanager-emergency:9093:/-/healthy"  
        "grafana-emergency:3000:/api/health"
        "node-exporter-security:9100:/metrics"
        "cadvisor-security:8080:/healthz"
    )
    
    local failed_services=()
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port endpoint <<< "${service_info}"
        
        print_message "${BLUE}" "🔍 فحص ${service_name}..."
        
        local max_attempts=10
        local attempt=1
        local success=false
        
        while [ ${attempt} -le ${max_attempts} ]; do
            if curl -s -f "http://localhost:${port}${endpoint}" >/dev/null 2>&1; then
                print_message "${GREEN}" "✅ ${service_name} يعمل بشكل صحيح"
                success=true
                break
            else
                print_message "${YELLOW}" "⏳ محاولة ${attempt}/${max_attempts} لـ ${service_name}..."
                sleep 5
                ((attempt++))
            fi
        done
        
        if [ "${success}" = false ]; then
            failed_services+=("${service_name}")
            print_message "${RED}" "❌ ${service_name} لا يعمل"
        fi
    done
    
    # تقرير النتائج
    if [ ${#failed_services[@]} -eq 0 ]; then
        print_message "${GREEN}" "✅ جميع الخدمات تعمل بشكل صحيح"
        return 0
    else
        print_message "${RED}" "❌ الخدمات التالية لا تعمل:"
        for service in "${failed_services[@]}"; do
            print_message "${RED}" "   - ${service}"
        done
        return 1
    fi
}

# تكوين Grafana
configure_grafana() {
    print_section "تكوين Grafana"
    
    local grafana_url="http://localhost:3000"
    local admin_password=$(cat "${MONITORING_DIR}/secrets/grafana-admin-password.txt")
    
    print_message "${BLUE}" "🔧 إعداد مصادر البيانات في Grafana..."
    
    # انتظار Grafana
    local max_wait=60
    local wait_time=0
    
    while ! curl -s "${grafana_url}/api/health" >/dev/null 2>&1; do
        if [ ${wait_time} -ge ${max_wait} ]; then
            print_message "${RED}" "❌ انتهت مهلة انتظار Grafana"
            return 1
        fi
        sleep 2
        ((wait_time+=2))
    done
    
    # إضافة مصدر بيانات Prometheus
    local datasource_config='{
        "name": "Prometheus-Emergency",
        "type": "prometheus",
        "url": "http://prometheus-emergency:9090",
        "access": "proxy",
        "isDefault": true,
        "basicAuth": false
    }'
    
    if curl -s -X POST \
        -H "Content-Type: application/json" \
        -u "admin:${admin_password}" \
        -d "${datasource_config}" \
        "${grafana_url}/api/datasources" >/dev/null 2>&1; then
        print_message "${GREEN}" "✅ تم إضافة مصدر بيانات Prometheus"
    else
        print_message "${YELLOW}" "⚠️  مصدر بيانات Prometheus موجود مسبقاً أو حدث خطأ"
    fi
    
    print_message "${GREEN}" "✅ تم تكوين Grafana"
}

# اختبار التنبيهات
test_alerts() {
    print_section "اختبار نظام التنبيهات"
    
    print_message "${BLUE}" "🧪 إرسال تنبيه اختبار..."
    
    # إرسال تنبيه اختبار إلى Alertmanager
    local test_alert='{
        "alerts": [
            {
                "labels": {
                    "alertname": "TestEmergencyAlert",
                    "severity": "info",
                    "category": "test"
                },
                "annotations": {
                    "summary": "Emergency monitoring system deployment test",
                    "description": "This is a test alert to verify the emergency monitoring system is working correctly."
                },
                "startsAt": "'$(date -Iseconds)'",
                "endsAt": "'$(date -d '+5 minutes' -Iseconds)'"
            }
        ]
    }'
    
    if curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "${test_alert}" \
        "http://localhost:9093/api/v1/alerts" >/dev/null 2>&1; then
        print_message "${GREEN}" "✅ تم إرسال تنبيه الاختبار"
    else
        print_message "${RED}" "❌ فشل في إرسال تنبيه الاختبار"
    fi
}

# طباعة معلومات الوصول
print_access_info() {
    print_section "معلومات الوصول للنظام"
    
    local admin_password=$(cat "${MONITORING_DIR}/secrets/grafana-admin-password.txt")
    
    cat << EOF

🎯 URLs للوصول للنظام:

📊 Prometheus (المراقبة):
   🔗 http://localhost:9090
   📝 مراقبة المقاييس والاستعلامات

🚨 Alertmanager (التنبيهات):
   🔗 http://localhost:9093  
   📝 إدارة التنبيهات والإشعارات

📈 Grafana (لوحات القيادة):
   🔗 http://localhost:3000
   👤 المستخدم: admin
   🔑 كلمة المرور: ${admin_password}

🖥️  Node Exporter (إحصائيات النظام):
   🔗 http://localhost:9100

📦 cAdvisor (إحصائيات الحاويات):
   🔗 http://localhost:8080

🛡️  Nginx WAF (جدار الحماية):
   🔗 http://localhost:80
   🔒 https://localhost:443

📋 الملفات المهمة:
   📁 مجلد التكوين: ${MONITORING_DIR}
   📝 ملف السجل: ${LOG_FILE}
   💾 النسخة الاحتياطية: ${BACKUP_DIR}
   🔐 الأسرار: ${MONITORING_DIR}/secrets/
   📜 الشهادات: ${MONITORING_DIR}/ssl/

🔧 أوامر إدارة النظام:
   ▶️  بدء النظام: cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml up -d
   ⏹️  إيقاف النظام: cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml stop
   🔄 إعادة تشغيل: cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml restart
   📊 حالة الخدمات: cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml ps
   📋 عرض السجلات: cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml logs -f

⚠️  ملاحظات أمنية مهمة:
   🔒 تم إنشاء شهادات SSL للاتصالات الآمنة
   🔑 تم إنشاء كلمات مرور قوية عشوائياً
   🛡️  النظام مكون للمراقبة الأمنية المكثفة
   📈 التنبيهات تعمل على فترات قصيرة للاستجابة السريعة

EOF
}

# الدالة الرئيسية
main() {
    print_message "${PURPLE}" "
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    🚨 نظام المراقبة الطارئة - AI Teddy Bear                     ║
║                      Emergency Monitoring System Deployment                    ║
║                                                                               ║
║  🛡️  نظام مراقبة أمنية متقدم للاستجابة الفورية للتهديدات                       ║
║  🔧 نشر تلقائي مع أعلى معايير الأمان                                           ║
║  📊 مراقبة مكثفة كل 5 ثوان                                                   ║
║  🚨 تنبيهات فورية للحوادث الحرجة                                             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"
    
    # التحقق من تشغيل السكريبت بصلاحيات مناسبة
    if [[ $EUID -eq 0 ]]; then
        print_message "${RED}" "❌ لا تشغل هذا السكريبت كـ root"
        exit 1
    fi
    
    # إعداد السجلات
    setup_logging
    
    # تنفيذ خطوات النشر
    local steps=(
        "check_prerequisites:فحص المتطلبات الأساسية"
        "backup_current_config:نسخ احتياطي للتكوين الحالي"
        "generate_ssl_certificates:إنشاء الشهادات الأمنية"
        "generate_secrets:إنشاء الأسرار الآمنة"
        "create_alert_rules:إنشاء قواعد التنبيه الأمنية"
        "deploy_monitoring_system:نشر نظام المراقبة"
        "health_check:فحص صحة النظام"
        "configure_grafana:تكوين Grafana"
        "test_alerts:اختبار التنبيهات"
    )
    
    local total_steps=${#steps[@]}
    local current_step=0
    
    for step_info in "${steps[@]}"; do
        IFS=':' read -r step_function step_description <<< "${step_info}"
        ((current_step++))
        
        print_message "${PURPLE}" "
🚀 خطوة ${current_step}/${total_steps}: ${step_description}"
        
        if ${step_function}; then
            print_message "${GREEN}" "✅ تمت بنجاح: ${step_description}"
        else
            print_message "${RED}" "❌ فشلت: ${step_description}"
            exit 1
        fi
    done
    
    # طباعة معلومات الوصول
    print_access_info
    
    print_message "${GREEN}" "
🎉 تم نشر نظام المراقبة الطارئة بنجاح!

📋 ملخص النشر:
✅ جميع الخدمات تعمل بشكل صحيح
✅ تم إنشاء الشهادات الأمنية
✅ تم تكوين التنبيهات الطارئة
✅ تم اختبار النظام بنجاح

🛡️  النظام جاهز للمراقبة الأمنية على مدار الساعة!
"
    
    print_message "${CYAN}" "💡 نصيحة: احفظ كلمة مرور Grafana في مكان آمن: $(cat "${MONITORING_DIR}/secrets/grafana-admin-password.txt")"
}

# تشغيل الدالة الرئيسية
main "$@" 