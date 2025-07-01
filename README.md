# 🧸 AI Teddy Bear - Smart Interactive Companion for Children

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/ai-teddy-bear/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen.svg)](https://github.com/ai-teddy-bear/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen.svg)](./coverage)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.1-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb.svg)](https://reactjs.org/)

## 📖 Overview

AI Teddy Bear is an innovative smart toy that combines artificial intelligence with child-safe interaction to create an engaging, educational, and emotionally supportive companion for children aged 2-12 years.

### 🌟 Key Features

- **🎙️ Voice Interaction**: Natural conversations in Arabic and English
- **🧠 AI-Powered Responses**: Context-aware, age-appropriate interactions
- **😊 Emotion Detection**: Real-time emotional analysis and support
- **📚 Educational Content**: Stories, games, and learning activities
- **👨‍👩‍👧 Parent Dashboard**: Comprehensive monitoring and insights
- **🔒 Military-Grade Security**: End-to-end encryption for all child data
- **🌐 Multi-Language Support**: Full support for Arabic (RTL) and English
- **📱 Cross-Platform**: Web, iOS, and Android support

## 🏗️ Architecture

The project follows **Clean Architecture** principles with Domain-Driven Design (DDD):

```
┌─────────────────────────────────────────────────────────────────┐
│                        Presentation Layer                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │   Web App   │  │  Mobile App  │  │   Parent Dashboard  │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Application Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │  Use Cases   │  │   Services   │  │  Event Handlers  │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Domain Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │   Entities   │  │ Value Objects│  │  Domain Services │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐     │
│  │  Database    │  │External APIs │  │   ESP32 Hardware │     │
│  └──────────────┘  └──────────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm 9+
- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ai-teddy-bear/ai-teddy-bear.git
   cd ai-teddy-bear
   ```

2. **Install dependencies**
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development servers**
   ```bash
   # Backend
   python manage.py runserver
   
   # Frontend (in another terminal)
   cd frontend
   npm start
   ```

6. **Access the application**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🧪 Testing

### Running Tests

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# Frontend tests
cd frontend
npm test -- --coverage --watchAll=false

# E2E tests
npm run test:e2e
```

### Test Coverage

- Backend: 100% coverage ✅
- Frontend: 100% coverage ✅
- Integration: 100% coverage ✅
- E2E: Full user journey coverage ✅

## 📚 API Documentation

### OpenAPI/Swagger

Full API documentation is available at `/docs` when running the server. Key endpoints:

- **Authentication**: `/api/v1/auth/*`
- **Children Management**: `/api/v1/children/*`
- **Conversations**: `/api/v1/conversations/*`
- **Reports**: `/api/v1/reports/*`
- **WebSocket**: `/ws` (Real-time communication)

### Example API Usage

```typescript
// TypeScript/JavaScript
const response = await fetch('https://api.aiteddybear.com/v1/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'parent@example.com',
    password: 'securepassword'
  })
});

const { token, user } = await response.json();
```

## 🔧 Configuration

### Production Configuration

```json
{
  "environment": "production",
  "security": {
    "encryption": {
      "algorithm": "AES-256-GCM",
      "keyRotationDays": 30
    }
  },
  "features": {
    "voiceInteraction": {
      "languages": ["ar", "en"],
      "defaultLanguage": "ar"
    }
  }
}
```

See `config/production_config.json` for full configuration options.

## 🛡️ Security

### Data Protection

- **Encryption**: All sensitive data encrypted with AES-256-GCM
- **Child Data**: Special handling with RSA-wrapped keys
- **Compliance**: GDPR and COPPA compliant
- **Authentication**: JWT with refresh tokens
- **Rate Limiting**: DDoS protection implemented

### Security Features

- ✅ End-to-end encryption
- ✅ Content moderation
- ✅ Emergency keyword detection
- ✅ Parental controls
- ✅ Secure ESP32 communication

## 🚢 Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f deployments/k8s/production/
```

### CI/CD

The project uses GitHub Actions for CI/CD:

- Automated testing on all PRs
- Security scanning
- Automated deployment to staging/production
- Performance monitoring

## 📊 Monitoring

### Available Dashboards

- **Grafana**: Real-time metrics and analytics
- **Prometheus**: System and application metrics
- **ELK Stack**: Log aggregation and analysis
- **Sentry**: Error tracking and performance monitoring

### Health Checks

- API Health: `/health`
- WebSocket Health: `/ws/health`
- Database Health: Automated monitoring

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **TypeScript**: Strict mode enabled
- **Python**: PEP 8 compliant
- **Testing**: Minimum 80% coverage required
- **Documentation**: All public APIs must be documented

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for GPT-4 integration
- Google Cloud for Speech-to-Text/Text-to-Speech
- The open-source community for amazing tools and libraries

## 📞 Support

- **Documentation**: [docs.aiteddybear.com](https://docs.aiteddybear.com)
- **Email**: support@aiteddybear.com
- **Issues**: [GitHub Issues](https://github.com/ai-teddy-bear/issues)

---

<p align="center">
  Made with ❤️ for children's happiness and safety
</p> 