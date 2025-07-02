@echo off
echo 🧸 AI Teddy Bear - Local Server Setup
echo ===================================

echo 📋 Installing Docker Desktop...
echo Please download Docker Desktop from: https://docker.com/products/docker-desktop
pause

echo 📋 Setting environment variables...
set POSTGRES_PASSWORD=TeddyLocal2025!
set REDIS_PASSWORD=TeddyRedisLocal!
set JWT_SECRET_KEY=TeddyJWT-Local-Secret-Key-32-Chars
set ENCRYPTION_KEY=TeddyLocal-Encryption-32-Chars-Key
set OPENAI_API_KEY=sk-your-openai-api-key-here
set FRONTEND_URL=http://localhost:8000

echo 📋 Getting your external IP...
curl -s ifconfig.me > temp_ip.txt
set /p EXTERNAL_IP=<temp_ip.txt
del temp_ip.txt

echo 🌐 Your external IP: %EXTERNAL_IP%
echo 📝 Use this IP for ESP32: %EXTERNAL_IP%

echo 🚀 Starting services...
docker-compose -f src/docker-compose.prod.yml up -d

echo ⏳ Waiting for services...
timeout /t 30

echo 🎉 Server is running!
echo ================================
echo 🌐 Local Access: http://localhost:8000
echo 🌐 External Access: http://%EXTERNAL_IP%:8000
echo 📖 API Docs: http://localhost:8000/docs
echo 📊 Grafana: http://localhost:3000
echo 
echo 🔧 ESP32 Configuration:
echo const char* server_ip = "%EXTERNAL_IP%";
echo const char* api_endpoint = "http://%EXTERNAL_IP%:8000";
echo 
echo Press any key to view logs...
pause
docker-compose -f src/docker-compose.prod.yml logs -f 