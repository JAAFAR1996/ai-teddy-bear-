#!/bin/bash

# 🚨 Quick Emergency Monitoring Deployment
# AI Teddy Bear Security Team - Fast Deploy Script v2025.1

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONITORING_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

print_message() {
    echo -e "${1}${2}${NC}"
}

print_header() {
    echo
    print_message "${BLUE}" "═══════════════════════════════════════════"
    print_message "${BLUE}" "🔧 ${1}"
    print_message "${BLUE}" "═══════════════════════════════════════════"
}

# فحص متطلبات أساسية
check_requirements() {
    print_header "فحص المتطلبات الأساسية"
    
    local missing=()
    
    command -v docker >/dev/null 2>&1 || missing+=("Docker")
    command -v docker-compose >/dev/null 2>&1 || missing+=("Docker Compose")
    
    if [ ${#missing[@]} -ne 0 ]; then
        print_message "${RED}" "❌ أدوات مفقودة: ${missing[*]}"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_message "${RED}" "❌ خدمة Docker غير نشطة"
        exit 1
    fi
    
    print_message "${GREEN}" "✅ المتطلبات متوفرة"
}

# إنشاء الأسرار الأساسية
generate_secrets() {
    print_header "إنشاء الأسرار الآمنة"
    
    local secrets_dir="${MONITORING_DIR}/secrets"
    mkdir -p "${secrets_dir}"
    chmod 700 "${secrets_dir}"
    
    # كلمة مرور Grafana
    if [ ! -f "${secrets_dir}/grafana-admin-password.txt" ]; then
        openssl rand -base64 32 > "${secrets_dir}/grafana-admin-password.txt"
        chmod 600 "${secrets_dir}/grafana-admin-password.txt"
        print_message "${GREEN}" "✅ تم إنشاء كلمة مرور Grafana"
    fi
    
    # مفتاح Grafana السري
    if [ ! -f "${secrets_dir}/grafana-secret-key.txt" ]; then
        openssl rand -base64 64 > "${secrets_dir}/grafana-secret-key.txt"
        chmod 600 "${secrets_dir}/grafana-secret-key.txt"
        print_message "${GREEN}" "✅ تم إنشاء مفتاح Grafana السري"
    fi
    
    # كلمة مرور قاعدة البيانات
    if [ ! -f "${secrets_dir}/postgres-grafana-password.txt" ]; then
        openssl rand -base64 32 > "${secrets_dir}/postgres-grafana-password.txt"
        chmod 600 "${secrets_dir}/postgres-grafana-password.txt"
        print_message "${GREEN}" "✅ تم إنشاء كلمة مرور قاعدة البيانات"
    fi
    
    print_message "${GREEN}" "✅ تم إنشاء جميع الأسرار"
}

# إنشاء المجلدات المطلوبة
create_directories() {
    print_header "إنشاء المجلدات المطلوبة"
    
    local dirs=(
        "${MONITORING_DIR}/grafana/dashboards"
        "${MONITORING_DIR}/grafana/provisioning/datasources"
        "${MONITORING_DIR}/grafana/provisioning/dashboards"
        "${MONITORING_DIR}/prometheus/rules"
        "${MONITORING_DIR}/alertmanager/templates"
        "/var/lib/teddy/monitoring/prometheus"
        "/var/lib/teddy/monitoring/grafana"
    )
    
    for dir in "${dirs[@]}"; do
        if [[ "$dir" == /var/lib/* ]]; then
            sudo mkdir -p "$dir"
        else
            mkdir -p "$dir"
        fi
    done
    
    # تعديل الصلاحيات
    sudo chown -R 65534:65534 /var/lib/teddy/monitoring/prometheus 2>/dev/null || true
    sudo chown -R 472:472 /var/lib/teddy/monitoring/grafana 2>/dev/null || true
    
    print_message "${GREEN}" "✅ تم إنشاء جميع المجلدات"
}

# إنشاء تكوين Grafana الأساسي
create_grafana_config() {
    print_header "إنشاء تكوين Grafana"
    
    # تكوين مصدر البيانات
    cat > "${MONITORING_DIR}/grafana/provisioning/datasources/prometheus.yml" << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus-Emergency
    type: prometheus
    access: proxy
    url: http://prometheus-emergency:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: 5s
      queryTimeout: 60s
EOF
    
    # تكوين لوحات القيادة
    cat > "${MONITORING_DIR}/grafana/provisioning/dashboards/dashboards.yml" << 'EOF'
apiVersion: 1
providers:
  - name: 'Emergency Security'
    orgId: 1
    folder: 'Security'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
EOF
    
    print_message "${GREEN}" "✅ تم إنشاء تكوين Grafana"
}

# إنشاء قواعد التنبيه الأساسية
create_alert_rules() {
    print_header "إنشاء قواعد التنبيه"
    
    cat > "${MONITORING_DIR}/prometheus/rules/security_alerts.yml" << 'EOF'
groups:
  - name: security_critical
    interval: 5s
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 2m
        labels:
          severity: warning
          category: system
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for more than 2 minutes"
          
      - alert: HighMemoryUsage
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 85
        for: 5m
        labels:
          severity: warning
          category: system
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 85% for more than 5 minutes"
          
      - alert: DiskSpaceLow
        expr: (1 - (node_filesystem_avail_bytes{fstype!="tmpfs"} / node_filesystem_size_bytes{fstype!="tmpfs"})) * 100 > 90
        for: 5m
        labels:
          severity: critical
          category: system
        annotations:
          summary: "Low disk space"
          description: "Disk usage is above 90%"
EOF
    
    print_message "${GREEN}" "✅ تم إنشاء قواعد التنبيه"
}

# نشر النظام
deploy_system() {
    print_header "نشر نظام المراقبة الطارئة"
    
    cd "${MONITORING_DIR}"
    
    # إيقاف النظام السابق إن وجد
    docker-compose -f docker-compose.emergency.yml down -v 2>/dev/null || true
    
    # سحب أحدث الصور
    print_message "${BLUE}" "🐳 سحب صور Docker..."
    docker-compose -f docker-compose.emergency.yml pull
    
    # تشغيل النظام
    print_message "${BLUE}" "🚀 تشغيل النظام..."
    docker-compose -f docker-compose.emergency.yml up -d
    
    print_message "${GREEN}" "✅ تم نشر النظام"
}

# فحص صحة النظام
health_check() {
    print_header "فحص صحة النظام"
    
    local services=(
        "9090:Prometheus"
        "9093:Alertmanager"
        "3000:Grafana"
        "9100:Node Exporter"
        "8080:cAdvisor"
    )
    
    sleep 15  # انتظار بدء الخدمات
    
    for service in "${services[@]}"; do
        IFS=':' read -r port name <<< "${service}"
        
        for i in {1..10}; do
            if curl -sf "http://localhost:${port}/" >/dev/null 2>&1 || 
               curl -sf "http://localhost:${port}/metrics" >/dev/null 2>&1 ||
               curl -sf "http://localhost:${port}/-/healthy" >/dev/null 2>&1; then
                print_message "${GREEN}" "✅ ${name} يعمل بشكل صحيح"
                break
            elif [ $i -eq 10 ]; then
                print_message "${RED}" "❌ ${name} لا يستجيب"
            else
                sleep 3
            fi
        done
    done
}

# طباعة معلومات الوصول
show_access_info() {
    print_header "معلومات الوصول للنظام"
    
    local grafana_password=$(cat "${MONITORING_DIR}/secrets/grafana-admin-password.txt" 2>/dev/null || echo "غير متوفر")
    
    cat << EOF

🎯 URLs الوصول:
───────────────────────────────────────────
📊 Prometheus:    http://localhost:9090
🚨 Alertmanager:  http://localhost:9093
📈 Grafana:       http://localhost:3000
🖥️  Node Exporter: http://localhost:9100
📦 cAdvisor:      http://localhost:8080

🔐 بيانات تسجيل الدخول:
───────────────────────────────────────────
👤 مستخدم Grafana:     admin
🔑 كلمة مرور Grafana:   ${grafana_password}

🔧 أوامر الإدارة:
───────────────────────────────────────────
▶️  بدء النظام:    cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml up -d
⏹️  إيقاف النظام:   cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml stop
🔄 إعادة تشغيل:    cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml restart
📊 حالة الخدمات:   cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml ps
📋 عرض السجلات:   cd ${MONITORING_DIR} && docker-compose -f docker-compose.emergency.yml logs -f

⚠️  ملاحظات مهمة:
───────────────────────────────────────────
🔒 احفظ كلمة مرور Grafana في مكان آمن
🛡️  النظام مكون للمراقبة الأمنية المكثفة
📈 التنبيهات تعمل كل 5 ثواني للاستجابة السريعة
🔧 يمكن تخصيص قواعد التنبيه في: ${MONITORING_DIR}/prometheus/rules/

EOF
}

# الدالة الرئيسية
main() {
    print_message "${YELLOW}" "
╔═══════════════════════════════════════════════════════════════════════════════╗
║                   🚨 نظام المراقبة الطارئة - النشر السريع                      ║
║                 AI Teddy Bear - Emergency Monitoring Quick Deploy            ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"
    
    # تنفيذ خطوات النشر
    check_requirements
    generate_secrets
    create_directories
    create_grafana_config
    create_alert_rules
    deploy_system
    health_check
    show_access_info
    
    print_message "${GREEN}" "
🎉 تم نشر نظام المراقبة الطارئة بنجاح!

🛡️  النظام جاهز للمراقبة الأمنية على مدار الساعة
💡 استخدم URLs أعلاه للوصول للخدمات
"
}

# تشغيل الدالة الرئيسية
main "$@" 