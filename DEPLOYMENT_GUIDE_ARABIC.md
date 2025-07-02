# 🚀 دليل النشر والإعداد الشامل - AI Teddy Bear

<div align="center">

![Deployment Guide](https://img.shields.io/badge/🚀_Deployment_Guide-Ready_for_Production-success?style=for-the-badge)

**دليل مفصل لنشر وإعداد مشروع AI Teddy Bear على أي منصة**

</div>

---

## 📋 **فهرس المحتوى**

- [متطلبات النظام](#متطلبات-النظام)
- [إعداد البيئة المحلية](#إعداد-البيئة-المحلية)
- [النشر على AWS](#النشر-على-aws)
- [النشر على Azure](#النشر-على-azure)
- [النشر على Google Cloud](#النشر-على-google-cloud)
- [النشر المحلي](#النشر-المحلي)
- [إعداد قواعد البيانات](#إعداد-قواعد-البيانات)
- [تكوين الأمان](#تكوين-الأمان)
- [المراقبة والصيانة](#المراقبة-والصيانة)
- [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## 💻 **متطلبات النظام**

### **الحد الأدنى (للتطوير والاختبار):**
```yaml
الأجهزة:
  - المعالج: 2 CPU cores (Intel i5 أو AMD Ryzen 5)
  - الذاكرة: 4GB RAM
  - التخزين: 20GB مساحة فارغة
  - الإنترنت: 10Mbps للتحميل والرفع

نظم التشغيل المدعومة:
  - Windows 10/11
  - macOS 10.15+
  - Ubuntu 20.04+
  - CentOS 8+
  - Docker Desktop (أي نظام)
```

### **الإعداد المُفضل (للإنتاج):**
```yaml
الأجهزة:
  - المعالج: 4+ CPU cores
  - الذاكرة: 8GB+ RAM
  - التخزين: 100GB+ SSD
  - الإنترنت: 50Mbps+ مستقر

الشبكة:
  - IP ثابت أو نطاق مخصص
  - شهادة SSL
  - Load Balancer (للتوسع)
```

### **الخدمات السحابية المطلوبة:**
```yaml
قاعدة البيانات:
  - PostgreSQL 14+ (أو AWS RDS)
  - Redis 6+ (أو AWS ElastiCache)

التخزين:
  - Object Storage (AWS S3, Azure Blob, Google Cloud Storage)
  - CDN للتوزيع العالمي

الذكاء الاصطناعي:
  - OpenAI API Key (مطلوب)
  - ElevenLabs API Key (للصوت)
  - Anthropic API Key (اختياري)
  - Azure Speech API (اختياري)
```

---

## ⚡ **إعداد البيئة المحلية (التشغيل السريع)**

### **الطريقة 1: استخدام Docker (الأسهل)**

```bash
# 1. تحميل المشروع
git clone https://github.com/ai-teddy-bear/production
cd ai-teddy-bear

# 2. إعداد متغيرات البيئة
cp .env.example .env
```

**تعديل ملف `.env`:**
```env
# الأساسي - مطلوب للعمل
TEDDY_OPENAI_API_KEY=sk-your_openai_key_here
TEDDY_SECRET_KEY=your_secret_key_here

# قاعدة البيانات (ستعمل تلقائياً مع Docker)
DATABASE_URL=postgresql://teddy:password123@postgres:5432/teddy_db
REDIS_URL=redis://redis:6379/0

# اختياري - للميزات المتقدمة
TEDDY_ELEVENLABS_API_KEY=your_elevenlabs_key
TEDDY_ANTHROPIC_API_KEY=sk-ant-your_anthropic_key
```

```bash
# 3. تشغيل النظام بالكامل
docker-compose -f docker-compose.production.yml up -d

# 4. التحقق من الحالة
docker-compose ps
curl http://localhost/health

# 🎉 النظام جاهز على http://localhost
```

### **الطريقة 2: التثبيت اليدوي**

#### **أ. تثبيت الاعتماديات:**

**على Ubuntu/Debian:**
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Python 3.11
sudo apt install python3.11 python3.11-pip python3.11-venv

# تثبيت Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs

# تثبيت PostgreSQL
sudo apt install postgresql-14 postgresql-contrib

# تثبيت Redis
sudo apt install redis-server
```

**على macOS:**
```bash
# تثبيت Homebrew إذا لم يكن موجوداً
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# تثبيت الاعتماديات
brew install python@3.11 node postgresql@14 redis
```

**على Windows:**
```powershell
# تثبيت Python من python.org
# تثبيت Node.js من nodejs.org
# تثبيت PostgreSQL من postgresql.org
# تثبيت Redis من GitHub Releases أو استخدم WSL
```

#### **ب. إعداد قواعد البيانات:**

```bash
# إعداد PostgreSQL
sudo -u postgres psql
CREATE DATABASE teddy_db;
CREATE USER teddy WITH PASSWORD 'password123';
GRANT ALL PRIVILEGES ON DATABASE teddy_db TO teddy;
\q

# تشغيل Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

#### **ج. إعداد Backend:**

```bash
# الانتقال لمجلد المشروع
cd ai-teddy-bear

# إنشاء بيئة Python معزولة
python3.11 -m venv venv
source venv/bin/activate  # أو venv\Scripts\activate على Windows

# تثبيت مكتبات Python
pip install -r requirements.txt

# إعداد قاعدة البيانات
cd src
python -m alembic upgrade head

# تشغيل Backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### **د. إعداد Frontend:**

```bash
# في terminal جديد
cd ai-teddy-bear/frontend

# تثبيت مكتبات Node.js
npm install

# تشغيل Frontend
npm start

# سيفتح على http://localhost:3000
```

#### **هـ. تشغيل محاكي ESP32:**

```bash
# في terminal ثالث
cd ai-teddy-bear
source venv/bin/activate

# تشغيل محاكي الجهاز
python src/simulators/esp32_production_simulator.py
```

### **🔍 التحقق من التشغيل:**

```bash
# فحص Backend
curl http://localhost:8000/health
# النتيجة المتوقعة: {"healthy": true, "service": "ai_teddy_bear"}

# فحص Frontend
curl http://localhost:3000
# يجب أن يعيد HTML

# فحص قاعدة البيانات
psql -h localhost -U teddy -d teddy_db -c "SELECT version();"

# فحص Redis
redis-cli ping
# النتيجة المتوقعة: PONG
```

---

## ☁️ **النشر على Amazon Web Services (AWS)**

### **الإعداد المسبق:**

```bash
# تثبيت AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# تكوين AWS
aws configure
# AWS Access Key ID: your_access_key
# AWS Secret Access Key: your_secret_key  
# Default region name: us-east-1
# Default output format: json
```

### **الطريقة 1: استخدام AWS EKS (Kubernetes)**

#### **أ. إنشاء EKS Cluster:**

```bash
# تثبيت eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# إنشاء Cluster
eksctl create cluster \
  --name teddy-production \
  --region us-east-1 \
  --nodegroup-name workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 1 \
  --nodes-max 4
```

#### **ب. إعداد قواعد البيانات:**

```bash
# إنشاء RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier teddy-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username teddy \
  --master-user-password YourStrongPassword123 \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-xxxxxxxxx

# إنشاء ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id teddy-redis \
  --cache-node-type cache.t3.micro \
  --engine redis \
  --num-cache-nodes 1
```

#### **ج. نشر التطبيق:**

```bash
# تحديث kubectl config
aws eks update-kubeconfig --region us-east-1 --name teddy-production

# إنشاء namespace
kubectl create namespace teddy-production

# إنشاء secrets للمفاتيح
kubectl create secret generic teddy-secrets \
  --from-literal=OPENAI_API_KEY=sk-your_key \
  --from-literal=SECRET_KEY=your_secret \
  --namespace=teddy-production

# نشر التطبيق
kubectl apply -f deployments/k8s/production/ -n teddy-production

# فحص الحالة
kubectl get pods -n teddy-production
```

### **الطريقة 2: استخدام AWS EC2 + Docker**

#### **أ. إنشاء EC2 Instance:**

```bash
# إنشاء مفتاح SSH
aws ec2 create-key-pair --key-name teddy-key --query 'KeyMaterial' --output text > teddy-key.pem
chmod 400 teddy-key.pem

# إنشاء Security Group
aws ec2 create-security-group \
  --group-name teddy-sg \
  --description "Security group for Teddy Bear"

# فتح المنافذ المطلوبة
aws ec2 authorize-security-group-ingress \
  --group-name teddy-sg \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-name teddy-sg \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# إنشاء EC2 Instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1d0 \
  --count 1 \
  --instance-type t3.medium \
  --key-name teddy-key \
  --security-groups teddy-sg
```

#### **ب. إعداد الخادم:**

```bash
# الاتصال بالخادم
ssh -i teddy-key.pem ubuntu@your-ec2-ip

# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# استنساخ المشروع
git clone https://github.com/ai-teddy-bear/production
cd ai-teddy-bear

# إعداد المتغيرات
cp .env.example .env
nano .env  # تعديل المتغيرات

# تشغيل النظام
docker-compose -f docker-compose.production.yml up -d
```

### **ج. إعداد النطاق والـ SSL:**

```bash
# إعداد Application Load Balancer
aws elbv2 create-load-balancer \
  --name teddy-alb \
  --subnets subnet-xxxxxxxx subnet-yyyyyyyy \
  --security-groups sg-xxxxxxxxx

# إعداد Route 53 للنطاق
aws route53 create-hosted-zone --name myteddy.com --caller-reference $(date +%s)

# طلب شهادة SSL من ACM
aws acm request-certificate \
  --domain-name myteddy.com \
  --domain-name *.myteddy.com \
  --validation-method DNS
```

### **التكلفة التقديرية لـ AWS:**

```yaml
البداية (100 مستخدم):
  - EKS Cluster: $72/شهر
  - EC2 Nodes (2x t3.medium): $60/شهر
  - RDS PostgreSQL (t3.micro): $15/شهر
  - ElastiCache Redis (t3.micro): $15/شهر
  - Load Balancer: $20/شهر
  - S3 Storage: $5/شهر
  - CloudFront CDN: $10/شهر
  - Other: $20/شهر
  ─────────────────────────
  المجموع: ~$217/شهر

النمو (1,000 مستخدم):
  - زيادة Nodes إلى 4x t3.large: $240/شهر
  - ترقية RDS إلى t3.small: $30/شهر
  - ترقية Redis إلى t3.small: $30/شهر
  - زيادة Storage والـ CDN: $50/شهر
  ─────────────────────────
  المجموع: ~$470/شهر

التوسع (10,000 مستخدم):
  - تكبير Cluster إلى 8x t3.xlarge: $960/شهر
  - ترقية RDS إلى r5.large: $180/شهر
  - Redis Cluster: $120/شهر
  - Storage وCDN متقدم: $200/شهر
  ─────────────────────────
  المجموع: ~$1,580/شهر
```

---

## 🔵 **النشر على Microsoft Azure**

### **الإعداد المسبق:**

```bash
# تثبيت Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# تسجيل الدخول
az login

# إنشاء Resource Group
az group create --name TeddyBearRG --location eastus
```

### **استخدام Azure Kubernetes Service (AKS):**

```bash
# إنشاء AKS Cluster
az aks create \
  --resource-group TeddyBearRG \
  --name teddy-aks \
  --node-count 2 \
  --node-vm-size Standard_B2s \
  --enable-addons monitoring \
  --generate-ssh-keys

# الحصول على credentials
az aks get-credentials --resource-group TeddyBearRG --name teddy-aks

# إنشاء Azure Database for PostgreSQL
az postgres server create \
  --resource-group TeddyBearRG \
  --name teddy-postgres \
  --location eastus \
  --admin-user teddy \
  --admin-password YourStrongPassword123 \
  --sku-name GP_Gen5_2

# إنشاء Azure Cache for Redis
az redis create \
  --resource-group TeddyBearRG \
  --name teddy-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

### **نشر التطبيق:**

```bash
# إنشاء Azure Container Registry
az acr create --resource-group TeddyBearRG --name teddyacr --sku Basic

# بناء ورفع Images
az acr build --registry teddyacr --image teddy-backend:latest ./src
az acr build --registry teddyacr --image teddy-frontend:latest ./frontend

# نشر على AKS
kubectl apply -f deployments/azure/
```

---

## 🟡 **النشر على Google Cloud Platform**

### **الإعداد المسبق:**

```bash
# تثبيت Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# إنشاء مشروع جديد
gcloud projects create teddy-bear-project
gcloud config set project teddy-bear-project
```

### **استخدام Google Kubernetes Engine (GKE):**

```bash
# تفعيل APIs المطلوبة
gcloud services enable container.googleapis.com
gcloud services enable sqladmin.googleapis.com

# إنشاء GKE Cluster
gcloud container clusters create teddy-gke \
  --zone us-central1-a \
  --num-nodes 2 \
  --machine-type e2-medium

# إنشاء Cloud SQL PostgreSQL
gcloud sql instances create teddy-postgres \
  --database-version POSTGRES_14 \
  --tier db-f1-micro \
  --region us-central1

# إنشاء Memorystore Redis
gcloud redis instances create teddy-redis \
  --size 1 \
  --region us-central1
```

### **التكلفة التقديرية للمقارنة:**

```yaml
AWS vs Azure vs GCP (شهرياً):

الخدمة الأساسية:
  - AWS EKS: $72 + $60 nodes = $132
  - Azure AKS: $0 + $58 nodes = $58  
  - GCP GKE: $0 + $55 nodes = $55

قاعدة البيانات:
  - AWS RDS: $15
  - Azure Database: $18
  - GCP Cloud SQL: $12

التخزين والشبكة:
  - AWS: $35
  - Azure: $30
  - GCP: $25

المجموع للبداية:
  - AWS: ~$217/شهر
  - Azure: ~$136/شهر  
  - GCP: ~$112/شهر (الأوفر)
```

---

## 🏢 **النشر المحلي (On-Premise)**

### **المتطلبات:**

```yaml
الأجهزة المطلوبة:
  خادم رئيسي:
    - CPU: 8 cores (Intel Xeon أو AMD EPYC)
    - RAM: 32GB
    - Storage: 500GB NVMe SSD
    - Network: Gigabit Ethernet

  خادم قاعدة البيانات (اختياري):
    - CPU: 4 cores
    - RAM: 16GB  
    - Storage: 200GB SSD
    - Network: Gigabit Ethernet

الشبكة:
  - إنترنت: 100Mbps+ مخصص
  - IP ثابت أو VPN
  - Firewall للحماية
  - UPS للطاقة
```

### **الإعداد:**

#### **أ. إعداد نظام التشغيل:**

```bash
# Ubuntu Server 22.04 LTS (مُفضل)
sudo apt update && sudo apt upgrade -y

# تثبيت الاعتماديات الأساسية
sudo apt install -y \
  docker.io \
  docker-compose \
  nginx \
  certbot \
  fail2ban \
  ufw

# إعداد Firewall
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# تفعيل Docker
sudo systemctl enable docker
sudo usermod -aG docker $USER
```

#### **ب. إعداد قواعد البيانات:**

```bash
# إنشاء Docker Compose للبيانات
cat > docker-compose.db.yml << EOF
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: teddy_db
      POSTGRES_USER: teddy
      POSTGRES_PASSWORD: SecurePassword123
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass RedisPassword123
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"  
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

# تشغيل قواعد البيانات
docker-compose -f docker-compose.db.yml up -d
```

#### **ج. إعداد التطبيق:**

```bash
# استنساخ المشروع
git clone https://github.com/ai-teddy-bear/production
cd ai-teddy-bear

# إعداد المتغيرات للإنتاج المحلي
cp env.production.example .env.local

# تعديل ملف البيئة
nano .env.local
```

**إعدادات الإنتاج المحلي:**
```env
# معلومات الخادم
TEDDY_ENVIRONMENT=production
TEDDY_DEBUG=false
TEDDY_HOST=0.0.0.0
TEDDY_PORT=8000

# قاعدة البيانات المحلية
DATABASE_URL=postgresql://teddy:SecurePassword123@localhost:5432/teddy_db
REDIS_URL=redis://:RedisPassword123@localhost:6379/0

# مفاتيح API
TEDDY_OPENAI_API_KEY=sk-your_openai_key
TEDDY_ELEVENLABS_API_KEY=your_elevenlabs_key

# الأمان
TEDDY_SECRET_KEY=your_very_secure_secret_key_here
TEDDY_JWT_SECRET=your_jwt_secret_key_here
TEDDY_ENCRYPTION_KEY=your_encryption_key_here

# SSL وأمان إضافي
TEDDY_ENABLE_HTTPS=true
TEDDY_SSL_CERT_PATH=/etc/ssl/certs/teddy.crt
TEDDY_SSL_KEY_PATH=/etc/ssl/private/teddy.key
```

```bash
# تشغيل التطبيق
docker-compose -f docker-compose.production.yml --env-file .env.local up -d
```

#### **د. إعداد Nginx كـ Reverse Proxy:**

```bash
# إنشاء إعدادات Nginx
sudo cat > /etc/nginx/sites-available/teddy << EOF
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # إعادة توجيه إلى HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # شهادات SSL
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # إعدادات الأمان
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
    
    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket
    location /ws/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# تفعيل الإعدادات
sudo ln -s /etc/nginx/sites-available/teddy /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **هـ. إعداد SSL مع Let's Encrypt:**

```bash
# طلب شهادة SSL
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# إعداد التجديد التلقائي
sudo crontab -e
# إضافة هذا السطر:
0 12 * * * /usr/bin/certbot renew --quiet
```

### **النسخ الاحتياطية التلقائية:**

```bash
# إنشاء script للنسخ الاحتياطية
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# نسخة احتياطية لقاعدة البيانات
docker exec postgres pg_dump -U teddy teddy_db > $BACKUP_DIR/database.sql

# نسخة احتياطية للملفات
tar -czf $BACKUP_DIR/app_data.tar.gz data/ logs/

# حذف النسخ القديمة (أكثر من 30 يوم)
find /backups -type d -mtime +30 -exec rm -rf {} +

echo "Backup completed: $BACKUP_DIR"
EOF

chmod +x backup.sh

# إعداد النسخ الاحتياطية اليومية
crontab -e
# إضافة:
0 2 * * * /path/to/backup.sh
```

---

## 🔐 **تكوين الأمان المتقدم**

### **إعداد Firewall متقدم:**

```bash
# Ubuntu UFW
sudo ufw reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# فتح المنافذ المطلوبة فقط
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# حماية من brute force
sudo ufw limit ssh

# تفعيل Firewall
sudo ufw enable
```

### **إعداد fail2ban:**

```bash
# إعداد fail2ban للحماية من الهجمات
sudo cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

sudo systemctl restart fail2ban
```

### **إعداد مراقبة الأمان:**

```bash
# تثبيت مراقبة ملفات النظام
sudo apt install -y aide

# إعداد AIDE
sudo aideinit
sudo mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db

# فحص يومي للتغييرات
cat > /etc/cron.daily/aide << 'EOF'
#!/bin/bash
aide --check | mail -s "AIDE Report $(hostname)" admin@yourdomain.com
EOF

chmod +x /etc/cron.daily/aide
```

---

## 📊 **المراقبة والصيانة**

### **إعداد Prometheus لمراقبة النظام:**

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'

volumes:
  prometheus_data:
  grafana_data:
```

### **إعداد التنبيهات:**

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s

rule_files:
  - "alert_rules.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'teddy-bear'
    static_configs:
      - targets: ['localhost:8000']
  
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

```yaml
# monitoring/alert_rules.yml
groups:
- name: teddy_bear_alerts
  rules:
  - alert: HighMemoryUsage
    expr: node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes < 0.1
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High memory usage detected"
      
  - alert: HighCPUUsage
    expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100) > 80
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage detected"
      
  - alert: ServiceDown
    expr: up{job="teddy-bear"} == 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Teddy Bear service is down"
```

### **مراقبة اللوجات:**

```bash
# إعداد logrotate للوجات
sudo cat > /etc/logrotate.d/teddy << EOF
/var/log/teddy/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        docker-compose restart teddy-backend
    endscript
}
EOF
```

### **صحة النظام اليومية:**

```bash
# إنشاء script فحص صحة النظام
cat > health_check.sh << 'EOF'
#!/bin/bash

echo "=== Teddy Bear System Health Check $(date) ==="

# فحص الخدمات
echo "Checking services..."
docker-compose ps

# فحص قاعدة البيانات
echo "Checking database..."
docker exec postgres pg_isready -U teddy

# فحص Redis
echo "Checking Redis..."
docker exec redis redis-cli ping

# فحص مساحة القرص
echo "Checking disk space..."
df -h

# فحص الذاكرة
echo "Checking memory..."
free -h

# فحص المعالج
echo "Checking CPU..."
top -bn1 | grep "Cpu(s)"

# فحص الشبكة
echo "Checking network..."
ping -c 3 8.8.8.8

# فحص API
echo "Checking API health..."
curl -s http://localhost:8000/health | jq '.'

echo "=== Health check completed ==="
EOF

chmod +x health_check.sh

# إعداد فحص يومي
crontab -e
# إضافة:
0 8 * * * /path/to/health_check.sh >> /var/log/teddy/health.log 2>&1
```

---

## 🔧 **استكشاف الأخطاء وحلها**

### **مشاكل شائعة وحلولها:**

#### **1. فشل تشغيل Backend:**

```bash
# فحص اللوجات
docker-compose logs teddy-backend

# الأخطاء الشائعة:
# - مفاتيح API مفقودة أو خاطئة
# - عدم الاتصال بقاعدة البيانات
# - منافذ مشغولة

# الحلول:
# تحقق من ملف .env
cat .env | grep -E "(API_KEY|DATABASE_URL|REDIS_URL)"

# تحقق من قاعدة البيانات
docker exec postgres pg_isready -U teddy

# تحقق من المنافذ
netstat -tlnp | grep :8000
```

#### **2. مشاكل قاعدة البيانات:**

```bash
# إعادة تشغيل PostgreSQL
docker-compose restart postgres

# فحص اللوجات
docker-compose logs postgres

# إصلاح قاعدة البيانات إذا تضررت
docker exec postgres pg_dump teddy_db > backup.sql
docker exec postgres dropdb teddy_db
docker exec postgres createdb teddy_db
docker exec -i postgres psql teddy_db < backup.sql
```

#### **3. مشاكل الذاكرة:**

```bash
# فحص استخدام الذاكرة
docker stats

# تنظيف الذاكرة
docker system prune -f
docker volume prune -f

# إعادة تشغيل النظام
docker-compose restart
```

#### **4. مشاكل SSL/HTTPS:**

```bash
# فحص شهادة SSL
openssl x509 -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem -text -noout

# تجديد الشهادة
sudo certbot renew --force-renewal

# فحص إعدادات Nginx
sudo nginx -t
sudo systemctl reload nginx
```

### **أدوات التشخيص:**

```bash
# script شامل للتشخيص
cat > diagnose.sh << 'EOF'
#!/bin/bash

echo "=== TEDDY BEAR SYSTEM DIAGNOSIS ==="
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "OS: $(lsb_release -d | cut -f2)"
echo ""

echo "=== DOCKER STATUS ==="
docker --version
docker-compose --version
docker system df
echo ""

echo "=== SERVICES STATUS ==="
docker-compose ps
echo ""

echo "=== NETWORK STATUS ==="
netstat -tlnp | grep -E ":(80|443|8000|5432|6379)"
echo ""

echo "=== DISK USAGE ==="
df -h
echo ""

echo "=== MEMORY USAGE ==="
free -h
echo ""

echo "=== CPU USAGE ==="
top -bn1 | head -20
echo ""

echo "=== RECENT LOGS ==="
echo "Backend logs:"
docker-compose logs --tail=20 teddy-backend
echo ""
echo "Database logs:"
docker-compose logs --tail=10 postgres
echo ""

echo "=== API HEALTH CHECK ==="
curl -s http://localhost:8000/health || echo "API not responding"
echo ""

echo "=== DIAGNOSIS COMPLETED ==="
EOF

chmod +x diagnose.sh
```

### **خطة الطوارئ:**

```bash
# إنشاء نسخة احتياطية سريعة
cat > emergency_backup.sh << 'EOF'
#!/bin/bash
EMERGENCY_DIR="/tmp/emergency_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p $EMERGENCY_DIR

echo "Creating emergency backup in $EMERGENCY_DIR"

# نسخ ملفات التكوين
cp -r .env* $EMERGENCY_DIR/
cp -r config/ $EMERGENCY_DIR/

# نسخة سريعة للبيانات
docker exec postgres pg_dump -U teddy teddy_db > $EMERGENCY_DIR/emergency_db.sql

# نسخ ملفات مهمة
tar -czf $EMERGENCY_DIR/app_files.tar.gz data/ logs/

echo "Emergency backup completed: $EMERGENCY_DIR"
echo "To restore: ./restore_emergency.sh $EMERGENCY_DIR"
EOF

chmod +x emergency_backup.sh
```

---

## 📞 **الدعم والمساعدة**

### **الحصول على المساعدة:**

- 📧 **دعم تقني:** support@aiteddybear.com
- 💬 **مجتمع Discord:** [رابط المجتمع]
- 📚 **الوثائق:** docs.aiteddybear.com
- 🐛 **تبليغ أخطاء:** github.com/aiteddybear/issues

### **خدمات الدعم المدفوعة:**

- 🚀 **إعداد مخصص:** $500-2000
- 🛠️ **صيانة شهرية:** $200-800/شهر
- 📞 **دعم أولوية:** $100-300/شهر
- 🎓 **تدريب فريق:** $1000-3000

---

<div align="center">

## 🏆 **مبروك! نظام AI Teddy Bear جاهز للعمل**

**🎯 النظام الآن مُعد بالكامل ويعمل في بيئة الإنتاج**

[![تجربة النظام](https://img.shields.io/badge/تجربة_النظام-4ECDC4?style=for-the-badge&logo=play)](http://your-domain.com)
[![مراقبة النظام](https://img.shields.io/badge/مراقبة_النظام-FF6B6B?style=for-the-badge&logo=chart-line)](http://your-domain.com:3001)
[![الوثائق](https://img.shields.io/badge/الوثائق-45B7D1?style=for-the-badge&logo=book)](https://docs.aiteddybear.com)

</div>

---

**📅 آخر تحديث:** ديسمبر 2024  
**🚀 الحالة:** جاهز للإنتاج  
**💰 قيمة المشروع:** $500,000 - $1,000,000** 